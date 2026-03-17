"""FastMCP server with CSRankings tools."""

from fastmcp import FastMCP

from .config import AREA_TITLES, resolve_area_spec
from .data import get_data
from .ranking import (
    get_institution_faculty,
    get_researcher_profile,
    rank_institutions,
    search_names,
)

mcp = FastMCP(
    "CSRankings",
    instructions=(
        "Provides CS department rankings based on CSRankings.org data. "
        "Use these tools to look up institution rankings by research area, "
        "find faculty members, and get researcher profiles with homepage URLs."
    ),
)


@mcp.tool()
def csrankings_rank(
    areas: list[str],
    region: str | None = None,
    year_start: int = 2015,
    year_end: int = 2025,
    top_n: int = 25,
) -> str:
    """Rank CS institutions by research area using geometric mean (matching csrankings.org).

    Args:
        areas: Research areas to rank by. Accepts slugs (e.g. "mlmining", "sec"),
               category names ("ai", "systems", "theory"), or human-readable names
               ("machine learning", "security"). Multiple areas use geometric mean.
        region: Filter by region. Options: "us", "europe", "asia", "canada",
                "northamerica", "australasia", "southamerica", "africa", or None for worldwide.
        year_start: Start year for publication window (inclusive).
        year_end: End year for publication window (inclusive).
        top_n: Number of top institutions to return.

    Returns:
        Markdown table with rank, institution, score, faculty count, region, country.
    """
    resolved = resolve_area_spec(areas)
    data = get_data()
    rankings = rank_institutions(data, resolved, region, year_start, year_end, top_n)

    if not rankings:
        return f"No results for areas={areas}, region={region}, years={year_start}-{year_end}."

    area_names = ", ".join(AREA_TITLES.get(a, a) for a in resolved)
    lines = [
        f"## CSRankings: {area_names}",
        f"Region: {region or 'Worldwide'} | Years: {year_start}–{year_end}\n",
        "| Rank | Institution | Score | Faculty | Region | Country |",
        "|------|------------|-------|---------|--------|---------|",
    ]
    for r in rankings:
        lines.append(
            f"| {r.rank} | {r.institution} | {r.score} | {r.faculty_count} "
            f"| {r.region} | {r.country} |"
        )
    return "\n".join(lines)


@mcp.tool()
def csrankings_institution(
    institution: str,
    areas: list[str] | None = None,
    year_start: int = 2015,
    year_end: int = 2025,
) -> str:
    """Get faculty list for an institution with per-area publication counts and homepage URLs.

    Args:
        institution: Exact institution name (use csrankings_search to find the exact name).
        areas: Filter by research areas (same format as csrankings_rank). None for all areas.
        year_start: Start year (inclusive).
        year_end: End year (inclusive).

    Returns:
        Markdown table with faculty name, homepage URL, Google Scholar ID, and area publication counts.
    """
    resolved = resolve_area_spec(areas) if areas else None
    data = get_data()
    faculty = get_institution_faculty(data, institution, resolved, year_start, year_end)

    if not faculty:
        return f"No faculty found for '{institution}'. Use csrankings_search to verify the institution name."

    lines = [
        f"## Faculty at {institution}",
        f"Years: {year_start}–{year_end}"
        + (f" | Areas: {', '.join(areas)}" if areas else "")
        + "\n",
        "| Name | Homepage | Scholar ID | Areas (adjustedcount) |",
        "|------|----------|------------|----------------------|",
    ]
    for f in faculty:
        area_str = ", ".join(f"{a}: {c:.1f}" for a, c in f.areas.items())
        scholar_link = (
            f"[Profile](https://scholar.google.com/citations?user={f.scholar_id})"
            if f.scholar_id
            else ""
        )
        lines.append(f"| {f.name} | {f.homepage} | {scholar_link} | {area_str} |")
    return "\n".join(lines)


@mcp.tool()
def csrankings_researcher(name: str) -> str:
    """Get detailed profile for a CS researcher including homepage and yearly publications.

    Args:
        name: Exact researcher name (use csrankings_search to find the exact name).

    Returns:
        Researcher profile with affiliation, homepage URL, Google Scholar link,
        and per-year per-area publication counts.
    """
    data = get_data()
    profile = get_researcher_profile(data, name)

    if profile is None:
        return f"Researcher '{name}' not found. Use csrankings_search to find the correct name."

    scholar_link = (
        f"https://scholar.google.com/citations?user={profile.scholar_id}"
        if profile.scholar_id
        else "N/A"
    )
    lines = [
        f"## {profile.name}",
        f"- **Affiliation**: {profile.affiliation}",
        f"- **Homepage**: {profile.homepage}",
        f"- **Google Scholar**: {scholar_link}",
        "",
        "### Publication History (adjustedcount)",
        "| Year | Area | Count |",
        "|------|------|-------|",
    ]
    for year, areas in profile.yearly_output.items():
        for area, count in sorted(areas.items(), key=lambda x: -x[1]):
            lines.append(f"| {year} | {AREA_TITLES.get(area, area)} | {count:.2f} |")
    return "\n".join(lines)


@mcp.tool()
def csrankings_search(query: str, max_results: int = 20) -> str:
    """Search for institutions or researchers by name (fuzzy substring match).

    Args:
        query: Search string (e.g. "Carnegie", "MIT", "Hinton").
        max_results: Maximum number of results to return.

    Returns:
        List of matching institutions and researchers with basic info.
    """
    data = get_data()
    results = search_names(data, query, max_results)

    if not results:
        return f"No results for '{query}'."

    lines = [f"## Search results for '{query}'\n"]
    for r in results:
        if r["type"] == "institution":
            lines.append(
                f"- **[Institution]** {r['name']} "
                f"({r['region']}, {r['country']}) — {r['homepage']}"
            )
        else:
            lines.append(
                f"- **[Researcher]** {r['name']} "
                f"@ {r['affiliation']} — {r['homepage']}"
            )
    return "\n".join(lines)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
