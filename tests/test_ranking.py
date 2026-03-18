"""Tests for ranking computation logic."""

import pandas as pd

from csrankings_mcp.data import CSRankingsData
from csrankings_mcp.ranking import (
    get_institution_faculty,
    get_researcher_profile,
    rank_institutions,
    search_names,
)


def _make_test_data() -> CSRankingsData:
    """Create minimal test data."""
    author_info = pd.DataFrame({
        "name": [
            "Alice", "Alice", "Bob", "Bob", "Charlie", "Charlie",
            "Alice", "Bob", "Dave", "Alice",
        ],
        "dept": [
            "MIT", "MIT", "MIT", "MIT", "Stanford", "Stanford",
            "MIT", "MIT", "University of Waterloo", "MIT",
        ],
        "venue": [
            "icml", "aaai", "nips", "ccs", "iclr", "ijcai",
            "icml", "icml", "icml", "kdd",
        ],
        "area": [
            "mlmining", "ai", "mlmining", "sec", "mlmining", "ai",
            "mlmining", "mlmining", "mlmining", "mlmining",
        ],
        "count": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        "adjustedcount": [0.5, 0.5, 1.0, 0.5, 0.8, 0.3, 0.5, 0.5, 0.7, 0.4],
        "year": [2020, 2020, 2020, 2021, 2020, 2021, 2021, 2022, 2020, 2020],
    })
    csrankings = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Dave"],
        "affiliation": ["MIT", "MIT", "Stanford", "University of Waterloo"],
        "homepage": [
            "https://alice.mit.edu",
            "https://bob.mit.edu",
            "https://charlie.stanford.edu",
            "https://dave.uwaterloo.ca",
        ],
        "scholarid": ["ALICE123", "BOB456", "CHARLIE789", "DAVE012"],
        "orcid": ["", "", "", ""],
    })
    institutions = pd.DataFrame({
        "institution": ["MIT", "Stanford", "University of Waterloo"],
        "region": ["northamerica", "northamerica", "northamerica"],
        "countryabbrv": ["us", "us", "ca"],
        "homepage": [
            "https://mit.edu",
            "https://stanford.edu",
            "https://uwaterloo.ca",
        ],
    })
    aliases = pd.DataFrame({"alias": [], "name": []})
    return CSRankingsData(
        author_info=author_info,
        csrankings=csrankings,
        institutions=institutions,
        aliases=aliases,
    )


def test_rank_single_area():
    data = _make_test_data()
    results = rank_institutions(data, ["mlmining"], year_start=2020, year_end=2022)
    assert len(results) == 3
    # MIT has most mlmining publications
    assert results[0].institution == "MIT"
    assert results[0].rank == 1


def test_rank_multiple_areas_geometric_mean():
    data = _make_test_data()
    results = rank_institutions(
        data, ["mlmining", "ai"], year_start=2020, year_end=2022
    )
    assert len(results) == 3
    # All institutions get a score (geometric mean with +1 smoothing)
    for r in results:
        assert r.score > 0


def test_rank_region_filter():
    data = _make_test_data()
    # US only — should exclude Waterloo (ca)
    results_us = rank_institutions(
        data, ["mlmining"], region="us", year_start=2020, year_end=2022
    )
    assert len(results_us) == 2
    us_names = {r.institution for r in results_us}
    assert "MIT" in us_names
    assert "Stanford" in us_names
    assert "University of Waterloo" not in us_names

    # Canada only
    results_ca = rank_institutions(
        data, ["mlmining"], region="canada", year_start=2020, year_end=2022
    )
    assert len(results_ca) == 1
    assert results_ca[0].institution == "University of Waterloo"

    # North America — includes both US and Canada
    results_na = rank_institutions(
        data, ["mlmining"], region="northamerica", year_start=2020, year_end=2022
    )
    assert len(results_na) == 3

    # Europe — none
    results_eu = rank_institutions(
        data, ["mlmining"], region="europe", year_start=2020, year_end=2022
    )
    assert len(results_eu) == 0


def test_institution_faculty():
    data = _make_test_data()
    faculty = get_institution_faculty(
        data, "MIT", areas=["mlmining"], year_start=2020, year_end=2022
    )
    assert len(faculty) == 2
    names = {f.name for f in faculty}
    assert "Alice" in names
    assert "Bob" in names
    # Check homepage is populated
    for f in faculty:
        assert f.homepage.startswith("https://")


def test_researcher_profile():
    data = _make_test_data()
    profile = get_researcher_profile(data, "Alice")
    assert profile is not None
    assert profile.affiliation == "MIT"
    assert profile.homepage == "https://alice.mit.edu"
    assert 2020 in profile.yearly_output
    assert "mlmining" in profile.yearly_output[2020]


def test_researcher_not_found():
    data = _make_test_data()
    profile = get_researcher_profile(data, "Nobody")
    assert profile is None


def test_search_institution():
    data = _make_test_data()
    results = search_names(data, "MIT")
    assert any(r["type"] == "institution" and "MIT" in r["name"] for r in results)


def test_search_researcher():
    data = _make_test_data()
    results = search_names(data, "Alice")
    assert any(r["type"] == "researcher" and r["name"] == "Alice" for r in results)


def test_rank_default_venues_exclude_next_tier():
    """Default ranking should exclude next-tier venues like KDD."""
    data = _make_test_data()
    # Alice has a KDD paper (adjustedcount=0.4) which is next-tier
    # Default venues should exclude it
    results_default = rank_institutions(
        data, ["mlmining"], year_start=2020, year_end=2022
    )
    # With KDD included explicitly
    results_with_kdd = rank_institutions(
        data, ["mlmining"], year_start=2020, year_end=2022,
        venues={"icml", "iclr", "nips", "kdd"},
    )
    mit_default = next(r for r in results_default if r.institution == "MIT")
    mit_with_kdd = next(r for r in results_with_kdd if r.institution == "MIT")
    # Score with KDD should be higher since Alice has extra KDD publication
    assert mit_with_kdd.score > mit_default.score


def test_rank_specific_venues():
    """Can rank using only specific venues."""
    data = _make_test_data()
    # Only count ICML papers
    results = rank_institutions(
        data, ["mlmining"], year_start=2020, year_end=2022,
        venues={"icml"},
    )
    assert len(results) >= 1
    # MIT has ICML papers, Stanford does not (only ICLR)
    mit = next(r for r in results if r.institution == "MIT")
    assert mit.score > 1.0
    stanford_results = [r for r in results if r.institution == "Stanford"]
    if stanford_results:
        assert stanford_results[0].score == 1.0  # no icml papers, score = (0+1)^1 = 1


def test_institution_faculty_venue_filter():
    """Faculty listing should respect venue filter."""
    data = _make_test_data()
    # Only CCS (default venue for sec)
    faculty = get_institution_faculty(
        data, "MIT", areas=["sec"], year_start=2020, year_end=2022,
        venues={"ccs"},
    )
    assert len(faculty) == 1
    assert faculty[0].name == "Bob"
