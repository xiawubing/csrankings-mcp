"""Tests for area resolution logic."""

import pytest

from csrankings_mcp.config import (
    AI_AREAS,
    ALL_AREAS,
    SYSTEMS_AREAS,
    THEORY_AREAS,
    resolve_area_spec,
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
    result = resolve_area_spec(["ai"])
    assert result == AI_AREAS
    assert resolve_area_spec(["systems"]) == SYSTEMS_AREAS
    assert resolve_area_spec(["theory"]) == THEORY_AREAS
    assert resolve_area_spec(["all"]) == ALL_AREAS


def test_resolve_multiple():
    result = resolve_area_spec(["ml", "security", "os"])
    assert result == ["mlmining", "sec", "ops"]


def test_resolve_deduplication():
    # "ai" category includes "mlmining", adding "ml" shouldn't duplicate
    result = resolve_area_spec(["ai", "ml"])
    assert result.count("mlmining") == 1


def test_resolve_unknown():
    with pytest.raises(ValueError, match="Unknown area"):
        resolve_area_spec(["nonexistent_area_xyz"])


def test_resolve_case_insensitive():
    assert resolve_area_spec(["Machine Learning"]) == ["mlmining"]
    assert resolve_area_spec(["AI"]) == AI_AREAS
    assert resolve_area_spec(["Security"]) == ["sec"]
