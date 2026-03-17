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
            "Alice", "Bob",
        ],
        "dept": [
            "MIT", "MIT", "MIT", "MIT", "Stanford", "Stanford",
            "MIT", "MIT",
        ],
        "area": [
            "mlmining", "ai", "mlmining", "sec", "mlmining", "ai",
            "mlmining", "mlmining",
        ],
        "count": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        "adjustedcount": [0.5, 0.5, 1.0, 0.5, 0.8, 0.3, 0.5, 0.5],
        "year": [2020, 2020, 2020, 2021, 2020, 2021, 2021, 2022],
    })
    csrankings = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "affiliation": ["MIT", "MIT", "Stanford"],
        "homepage": [
            "https://alice.mit.edu",
            "https://bob.mit.edu",
            "https://charlie.stanford.edu",
        ],
        "scholarid": ["ALICE123", "BOB456", "CHARLIE789"],
        "orcid": ["", "", ""],
    })
    institutions = pd.DataFrame({
        "institution": ["MIT", "Stanford"],
        "region": ["northamerica", "northamerica"],
        "countryabbrv": ["us", "us"],
        "homepage": ["https://mit.edu", "https://stanford.edu"],
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
    assert len(results) == 2
    # MIT has more mlmining publications
    assert results[0].institution == "MIT"
    assert results[1].institution == "Stanford"
    assert results[0].rank == 1
    assert results[1].rank == 2


def test_rank_multiple_areas_geometric_mean():
    data = _make_test_data()
    results = rank_institutions(
        data, ["mlmining", "ai"], year_start=2020, year_end=2022
    )
    assert len(results) == 2
    # Both institutions have publications in both areas
    for r in results:
        assert r.score > 0


def test_rank_region_filter():
    data = _make_test_data()
    results = rank_institutions(
        data, ["mlmining"], region="us", year_start=2020, year_end=2022
    )
    assert len(results) == 2  # Both are US
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
