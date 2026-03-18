"""Tests for area and venue resolution logic."""

import pytest

from csrankings_mcp.config import (
    AI_AREAS,
    ALL_AREAS,
    DEFAULT_VENUES,
    NEXT_TIER_VENUES,
    SYSTEMS_AREAS,
    THEORY_AREAS,
    VENUE_TO_AREA,
    get_area_venues,
    resolve_area_spec,
    resolve_venue_spec,
)


def test_resolve_slug():
    assert resolve_area_spec(["mlmining"]) == ["mlmining"]
    assert resolve_area_spec(["sec"]) == ["sec"]


def test_resolve_alias():
    assert resolve_area_spec(["machine learning"]) == ["mlmining"]
    assert resolve_area_spec(["security"]) == ["sec"]
    assert resolve_area_spec(["ML"]) == ["mlmining"]
    assert resolve_area_spec(["os"]) == ["ops"]
    assert resolve_area_spec(["pl"]) == ["plan"]
    assert resolve_area_spec(["se"]) == ["soft"]


def test_resolve_category():
    result = resolve_area_spec(["ai-all"])
    assert result == AI_AREAS
    assert resolve_area_spec(["systems"]) == SYSTEMS_AREAS
    assert resolve_area_spec(["theory"]) == THEORY_AREAS
    assert resolve_area_spec(["all"]) == ALL_AREAS


def test_resolve_ai_is_individual_area():
    """'ai' should resolve to the individual area, not the full AI category."""
    assert resolve_area_spec(["ai"]) == ["ai"]


def test_resolve_multiple():
    result = resolve_area_spec(["ml", "security", "os"])
    assert result == ["mlmining", "sec", "ops"]


def test_resolve_deduplication():
    # "ai-all" category includes "mlmining", adding "ml" shouldn't duplicate
    result = resolve_area_spec(["ai-all", "ml"])
    assert result.count("mlmining") == 1


def test_resolve_unknown():
    with pytest.raises(ValueError, match="Unknown area"):
        resolve_area_spec(["nonexistent_area_xyz"])


def test_resolve_case_insensitive():
    assert resolve_area_spec(["Machine Learning"]) == ["mlmining"]
    assert resolve_area_spec(["AI"]) == ["ai"]
    assert resolve_area_spec(["AI-all"]) == AI_AREAS
    assert resolve_area_spec(["Security"]) == ["sec"]


# --- Venue resolution tests ---


def test_next_tier_venues_defined():
    """Next-tier venues should be a subset of all venues."""
    assert NEXT_TIER_VENUES < set(VENUE_TO_AREA.keys())


def test_default_venues_exclude_next_tier():
    """Default venues should not include any next-tier venues."""
    assert DEFAULT_VENUES & NEXT_TIER_VENUES == set()
    assert DEFAULT_VENUES | NEXT_TIER_VENUES == set(VENUE_TO_AREA.keys())


def test_next_tier_specific_venues():
    """Verify specific next-tier venues match csrankings.org."""
    assert "kdd" in NEXT_TIER_VENUES      # mlmining
    assert "ndss" in NEXT_TIER_VENUES      # sec
    assert "ase" in NEXT_TIER_VENUES       # soft
    assert "issta" in NEXT_TIER_VENUES     # soft
    assert "oopsla" in NEXT_TIER_VENUES    # plan
    assert "icfp" in NEXT_TIER_VENUES      # plan
    assert "hpca" in NEXT_TIER_VENUES      # arch
    # These should NOT be next-tier
    assert "icml" not in NEXT_TIER_VENUES
    assert "ccs" not in NEXT_TIER_VENUES
    assert "icse" not in NEXT_TIER_VENUES


def test_resolve_venue_none():
    """None input should return None (use defaults)."""
    assert resolve_venue_spec(None) is None


def test_resolve_venue_slugs():
    result = resolve_venue_spec(["icml", "nips"])
    assert result == {"icml", "nips"}


def test_resolve_venue_aliases():
    result = resolve_venue_spec(["neurips", "usenix security"])
    assert result == {"nips", "usenixsec"}


def test_resolve_venue_all():
    result = resolve_venue_spec(["all"])
    assert result == set(VENUE_TO_AREA.keys())


def test_resolve_venue_all_with_area_filter():
    result = resolve_venue_spec(["all"], areas=["sec"])
    assert result == {"ccs", "oakland", "usenixsec", "ndss"}


def test_resolve_venue_default():
    result = resolve_venue_spec(["default"])
    assert result == DEFAULT_VENUES


def test_resolve_venue_next_tier():
    result = resolve_venue_spec(["next-tier"])
    assert result == NEXT_TIER_VENUES


def test_resolve_venue_next_tier_with_area():
    result = resolve_venue_spec(["next-tier"], areas=["soft"])
    assert result == {"ase", "issta"}


def test_resolve_venue_mixed():
    """Can combine specific venues with special values."""
    result = resolve_venue_spec(["default", "kdd"])
    assert "kdd" in result
    assert "icml" in result  # from default


def test_resolve_venue_unknown():
    with pytest.raises(ValueError, match="Unknown venue"):
        resolve_venue_spec(["nonexistent_venue"])


def test_get_area_venues_default():
    ml_venues = get_area_venues("mlmining")
    assert ml_venues == {"icml", "iclr", "nips"}
    assert "kdd" not in ml_venues

    sec_venues = get_area_venues("sec")
    assert sec_venues == {"ccs", "oakland", "usenixsec"}
    assert "ndss" not in sec_venues

    soft_venues = get_area_venues("soft")
    assert soft_venues == {"fse", "icse"}
    assert "ase" not in soft_venues


def test_get_area_venues_with_next_tier():
    ml_venues = get_area_venues("mlmining", include_next_tier=True)
    assert ml_venues == {"icml", "iclr", "nips", "kdd"}

    sec_venues = get_area_venues("sec", include_next_tier=True)
    assert sec_venues == {"ccs", "oakland", "usenixsec", "ndss"}

    soft_venues = get_area_venues("soft", include_next_tier=True)
    assert soft_venues == {"fse", "icse", "ase", "issta"}
