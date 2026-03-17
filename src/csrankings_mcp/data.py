"""Download, cache, and load CSRankings CSV data."""

import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import pandas as pd
from platformdirs import user_cache_dir

from .config import VENUE_TO_AREA

BASE_URL = "https://raw.githubusercontent.com/emeryberger/CSrankings/gh-pages/"

CSV_FILES = {
    "author_info": "generated-author-info.csv",
    "csrankings": "csrankings.csv",
    "institutions": "institutions.csv",
    "aliases": "dblp-aliases.csv",
}

CACHE_DIR = Path(user_cache_dir("csrankings-mcp"))
CACHE_TTL = 24 * 3600  # 24 hours


@dataclass
class CSRankingsData:
    """Loaded CSRankings data as pandas DataFrames."""

    author_info: pd.DataFrame  # name, dept, area, count, adjustedcount, year
    csrankings: pd.DataFrame  # name, affiliation, homepage, scholarid, orcid
    institutions: pd.DataFrame  # institution, region, countryabbrv, homepage
    aliases: pd.DataFrame  # alias, name


def _download_csv(filename: str) -> Path:
    """Download a CSV file if not cached or cache expired."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = CACHE_DIR / filename
    if cached.exists():
        age = time.time() - cached.stat().st_mtime
        if age < CACHE_TTL:
            return cached
    url = BASE_URL + filename
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
    cached.write_bytes(resp.content)
    return cached


def _load_csv(filename: str, **kwargs) -> pd.DataFrame:
    """Download (if needed) and load a CSV into a DataFrame."""
    path = _download_csv(filename)
    return pd.read_csv(path, **kwargs)


def load_data() -> CSRankingsData:
    """Load all CSRankings data. Uses file cache with 24h TTL."""
    author_info = _load_csv(
        CSV_FILES["author_info"],
        dtype={"name": str, "dept": str, "area": str, "year": int},
    )
    # Ensure numeric columns
    author_info["count"] = pd.to_numeric(author_info["count"], errors="coerce").fillna(0)
    author_info["adjustedcount"] = pd.to_numeric(
        author_info["adjustedcount"], errors="coerce"
    ).fillna(0)

    # Map venue slugs to parent area slugs
    author_info["area"] = author_info["area"].map(
        lambda v: VENUE_TO_AREA.get(v, v)
    )

    csrankings = _load_csv(
        CSV_FILES["csrankings"],
        dtype=str,
    )
    csrankings = csrankings.fillna("")

    institutions = _load_csv(
        CSV_FILES["institutions"],
        dtype=str,
    )
    institutions = institutions.fillna("")

    aliases = _load_csv(
        CSV_FILES["aliases"],
        dtype=str,
    )
    aliases = aliases.fillna("")

    return CSRankingsData(
        author_info=author_info,
        csrankings=csrankings,
        institutions=institutions,
        aliases=aliases,
    )


# Singleton
_data: CSRankingsData | None = None


def get_data() -> CSRankingsData:
    """Get or load the singleton CSRankingsData."""
    global _data
    if _data is None:
        _data = load_data()
    return _data
