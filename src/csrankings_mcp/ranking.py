"""Ranking computation using geometric mean (matching csrankings.org logic)."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import DEFAULT_VENUES
from .data import CSRankingsData


@dataclass
class InstitutionRanking:
    rank: int
    institution: str
    score: float
    faculty_count: int
    region: str
    country: str


@dataclass
class FacultyInfo:
    name: str
    homepage: str
    scholar_id: str
    pub_count: int  # total raw publication count (# Pubs)
    areas: dict[str, float]  # area slug → total adjustedcount


@dataclass
class ResearcherProfile:
    name: str
    affiliation: str
    homepage: str
    scholar_id: str
    yearly_output: dict[int, dict[str, float]]  # year → {area → adjustedcount}


def rank_institutions(
    data: CSRankingsData,
    areas: list[str],
    region: str | None = None,
    year_start: int = 2015,
    year_end: int = 2025,
    top_n: int = 25,
    venues: set[str] | None = None,
) -> list[InstitutionRanking]:
    """Rank institutions by geometric mean of area-wise adjusted publication counts.

    Geometric mean formula (matching csrankings.org):
        score = ((sum_area1 + 1) * (sum_area2 + 1) * ... * (sum_areaN + 1)) ^ (1/N)

    Args:
        venues: Set of venue slugs to include. None means use default venues
                (matching csrankings.org, excluding next-tier).
    """
    ai = data.author_info
    # Determine which venues to include
    active_venues = venues if venues is not None else DEFAULT_VENUES
    # Filter by year, areas, and venues
    mask = (
        ai["area"].isin(areas)
        & ai["venue"].isin(active_venues)
        & (ai["year"] >= year_start)
        & (ai["year"] <= year_end)
    )
    df = ai[mask].copy()

    if df.empty:
        return []

    # Filter by region if specified
    inst_df = data.institutions
    if region:
        region_lower = region.lower()
        # Map user-friendly names to canonical values
        friendly_map = {
            "usa": "us",
            "united states": "us",
            "canada": "ca",
            "uk": "gb",
            "north america": "northamerica",
            "south america": "southamerica",
            "eu": "europe",
        }
        canonical = friendly_map.get(region_lower, region_lower)

        # Continental regions → filter by region column
        # Everything else → treat as country abbreviation (matches csrankings.org)
        continental = {
            "northamerica", "europe", "asia",
            "australasia", "southamerica", "africa",
        }
        if canonical in ("world", "worldwide"):
            pass  # no filtering
        elif canonical in continental:
            valid_insts = set(
                inst_df[inst_df["region"].str.lower() == canonical]["institution"]
            )
            df = df[df["dept"].isin(valid_insts)]
        else:
            # Country code: us, ca, cn, gb, de, etc.
            valid_insts = set(
                inst_df[inst_df["countryabbrv"].str.lower() == canonical][
                    "institution"
                ]
            )
            df = df[df["dept"].isin(valid_insts)]

    if df.empty:
        return []

    # Sum adjustedcount per institution per area
    grouped = df.groupby(["dept", "area"])["adjustedcount"].sum().reset_index()

    # Pivot: institution × area
    pivot = grouped.pivot_table(
        index="dept", columns="area", values="adjustedcount", fill_value=0
    )

    # Ensure all requested areas are columns (fill missing with 0)
    for area in areas:
        if area not in pivot.columns:
            pivot[area] = 0.0

    # Geometric mean: prod((sum_area_i + 1))^(1/N)
    n_areas = len(areas)
    pivot_plus1 = pivot[areas] + 1
    scores = pivot_plus1.prod(axis=1).pow(1.0 / n_areas)

    # Count distinct faculty per institution
    faculty_counts = df.groupby("dept")["name"].nunique()

    # Build region/country lookup
    inst_region = dict(zip(inst_df["institution"], inst_df["region"]))
    inst_country = dict(zip(inst_df["institution"], inst_df["countryabbrv"]))

    # Sort by score descending
    scores = scores.sort_values(ascending=False)

    results = []
    for rank_idx, (inst, score) in enumerate(scores.head(top_n).items(), 1):
        results.append(
            InstitutionRanking(
                rank=rank_idx,
                institution=inst,
                score=round(float(score), 2),
                faculty_count=int(faculty_counts.get(inst, 0)),
                region=inst_region.get(inst, ""),
                country=inst_country.get(inst, ""),
            )
        )
    return results


def get_institution_faculty(
    data: CSRankingsData,
    institution: str,
    areas: list[str] | None = None,
    year_start: int = 2015,
    year_end: int = 2025,
    venues: set[str] | None = None,
) -> list[FacultyInfo]:
    """Get faculty list for an institution with per-area publication counts.

    Args:
        venues: Set of venue slugs to include. None means use default venues.
    """
    ai = data.author_info
    active_venues = venues if venues is not None else DEFAULT_VENUES
    mask = (
        (ai["dept"] == institution)
        & ai["venue"].isin(active_venues)
        & (ai["year"] >= year_start)
        & (ai["year"] <= year_end)
    )
    if areas:
        mask = mask & ai["area"].isin(areas)
    df = ai[mask]

    if df.empty:
        return []

    # Sum adjustedcount per faculty per area
    grouped = df.groupby(["name", "area"])["adjustedcount"].sum()

    # Sum raw publication count per faculty
    pub_counts = df.groupby("name")["count"].sum()

    # Build faculty info
    cs = data.csrankings
    faculty_lookup = {}
    for _, row in cs[cs["affiliation"] == institution].iterrows():
        faculty_lookup[row["name"]] = (
            row.get("homepage", ""),
            row.get("scholarid", ""),
        )

    results = []
    for name in grouped.index.get_level_values("name").unique():
        area_counts = grouped.loc[name].to_dict()
        homepage, scholar_id = faculty_lookup.get(name, ("", ""))
        results.append(
            FacultyInfo(
                name=name,
                homepage=homepage,
                scholar_id=scholar_id,
                pub_count=round(float(pub_counts.get(name, 0))),
                areas=dict(sorted(area_counts.items(), key=lambda x: -x[1])),
            )
        )

    # Sort by raw publication count descending (matching csrankings.org)
    results.sort(key=lambda f: (-f.pub_count, -sum(f.areas.values())))
    return results


def get_researcher_profile(
    data: CSRankingsData,
    name: str,
) -> ResearcherProfile | None:
    """Get detailed profile for a researcher."""
    cs = data.csrankings
    match = cs[cs["name"] == name]
    if match.empty:
        return None

    row = match.iloc[0]
    affiliation = row.get("affiliation", "")
    homepage = row.get("homepage", "")
    scholar_id = row.get("scholarid", "")

    ai = data.author_info
    pubs = ai[ai["name"] == name]

    yearly_output: dict[int, dict[str, float]] = {}
    for _, pub in pubs.iterrows():
        year = int(pub["year"])
        area = pub["area"]
        adj = float(pub["adjustedcount"])
        if year not in yearly_output:
            yearly_output[year] = {}
        yearly_output[year][area] = yearly_output[year].get(area, 0) + adj

    return ResearcherProfile(
        name=name,
        affiliation=affiliation,
        homepage=homepage,
        scholar_id=scholar_id,
        yearly_output=dict(sorted(yearly_output.items())),
    )


def search_names(
    data: CSRankingsData,
    query: str,
    max_results: int = 20,
) -> list[dict[str, str]]:
    """Fuzzy search for institutions and researchers by name."""
    query_lower = query.lower()
    results: list[dict[str, str]] = []

    # Search institutions
    for _, row in data.institutions.iterrows():
        inst = row["institution"]
        if query_lower in inst.lower():
            results.append({
                "type": "institution",
                "name": inst,
                "region": row.get("region", ""),
                "country": row.get("countryabbrv", ""),
                "homepage": row.get("homepage", ""),
            })

    # Search researchers
    matched_names: set[str] = set()
    for _, row in data.csrankings.iterrows():
        name = row["name"]
        if query_lower in name.lower() and name not in matched_names:
            matched_names.add(name)
            results.append({
                "type": "researcher",
                "name": name,
                "affiliation": row.get("affiliation", ""),
                "homepage": row.get("homepage", ""),
            })

    return results[:max_results]
