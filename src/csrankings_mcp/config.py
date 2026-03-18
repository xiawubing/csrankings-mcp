"""Area slug mappings and category definitions for CSRankings."""

# Venue (conference) slug → parent area slug
# Source: CSRankings.parentMap in csrankings.js (gh-pages branch)
VENUE_TO_AREA: dict[str, str] = {
    # AI
    "aaai": "ai",
    "ijcai": "ai",
    # Vision
    "cvpr": "vision",
    "eccv": "vision",
    "iccv": "vision",
    # ML / Data Mining
    "icml": "mlmining",
    "iclr": "mlmining",
    "kdd": "mlmining",
    "nips": "mlmining",
    # NLP
    "acl": "nlp",
    "emnlp": "nlp",
    "naacl": "nlp",
    # Web & Information Retrieval
    "sigir": "inforet",
    "www": "inforet",
    # Computer Architecture
    "asplos": "arch",
    "isca": "arch",
    "micro": "arch",
    "hpca": "arch",
    # Networks
    "nsdi": "comm",
    "sigcomm": "comm",
    # Security
    "ccs": "sec",
    "oakland": "sec",
    "usenixsec": "sec",
    "ndss": "sec",
    # Databases
    "vldb": "mod",
    "sigmod": "mod",
    "icde": "mod",
    "pods": "mod",
    # EDA
    "dac": "da",
    "iccad": "da",
    # Embedded Systems
    "emsoft": "bed",
    "rtas": "bed",
    "rtss": "bed",
    # HPC
    "sc": "hpc",
    "hpdc": "hpc",
    "ics": "hpc",
    # Mobile Computing
    "mobicom": "mobile",
    "mobisys": "mobile",
    "sensys": "mobile",
    # Measurement & Metrics
    "imc": "metrics",
    "sigmetrics": "metrics",
    # Operating Systems
    "osdi": "ops",
    "sosp": "ops",
    "eurosys": "ops",
    "fast": "ops",
    "usenixatc": "ops",
    # Programming Languages
    "popl": "plan",
    "pldi": "plan",
    "oopsla": "plan",
    "icfp": "plan",
    # Software Engineering
    "fse": "soft",
    "icse": "soft",
    "ase": "soft",
    "issta": "soft",
    # Graphics
    "siggraph": "graph",
    "siggraph-asia": "graph",
    "eurographics": "graph",
    # Theory
    "focs": "act",
    "soda": "act",
    "stoc": "act",
    # Cryptography
    "crypto": "crypt",
    "eurocrypt": "crypt",
    # Logic & Verification
    "cav": "log",
    "lics": "log",
    # Computational Biology
    "ismb": "bio",
    "recomb": "bio",
    # Economics & Computation
    "ec": "ecom",
    "wine": "ecom",
    # HCI
    "chiconf": "chi",
    "ubicomp": "chi",
    "uist": "chi",
    # Robotics
    "icra": "robotics",
    "iros": "robotics",
    "rss": "robotics",
    # Visualization
    "vis": "visualization",
    "vr": "visualization",
    # CS Education
    "sigcse": "csed",
}

# Next-tier venues: deselected by default on csrankings.org
# These are valid venues but not included in the default ranking computation.
NEXT_TIER_VENUES: set[str] = {
    "kdd",          # mlmining
    "ndss",         # sec
    "ase",          # soft
    "issta",        # soft
    "icde",         # mod
    "pods",         # mod
    "hpca",         # arch
    "eurosys",      # ops
    "fast",         # ops
    "usenixatc",    # ops
    "eurographics", # graph
    "icfp",         # plan
    "oopsla",       # plan
}

DEFAULT_VENUES: set[str] = set(VENUE_TO_AREA.keys()) - NEXT_TIER_VENUES

# Parent area slug → human-readable name
AREA_TITLES: dict[str, str] = {
    # AI
    "ai": "Artificial Intelligence",
    "vision": "Computer Vision",
    "mlmining": "Machine Learning",
    "nlp": "Natural Language Processing",
    "inforet": "Web & Information Retrieval",
    # Systems
    "arch": "Computer Architecture",
    "comm": "Computer Networks",
    "sec": "Computer Security",
    "mod": "Databases",
    "da": "Design Automation",
    "bed": "Embedded & Real-Time Systems",
    "hpc": "High-Performance Computing",
    "mobile": "Mobile Computing",
    "metrics": "Measurement & Perf. Analysis",
    "ops": "Operating Systems",
    "plan": "Programming Languages",
    "soft": "Software Engineering",
    # Theory
    "act": "Algorithms & Complexity",
    "crypt": "Cryptography",
    "log": "Logic & Verification",
    # Interdisciplinary
    "graph": "Computer Graphics",
    "chi": "Human-Computer Interaction",
    "robotics": "Robotics",
    "bio": "Computational Biology",
    "csed": "Computer Science Education",
    "visualization": "Visualization",
    "ecom": "Economics & Computation",
}

AI_AREAS: list[str] = ["ai", "vision", "mlmining", "nlp", "inforet"]
SYSTEMS_AREAS: list[str] = [
    "arch", "comm", "sec", "mod", "da", "bed", "hpc",
    "mobile", "metrics", "ops", "plan", "soft",
]
THEORY_AREAS: list[str] = ["act", "crypt", "log"]
INTERDISCIPLINARY_AREAS: list[str] = [
    "graph", "chi", "robotics", "bio", "csed", "visualization", "ecom",
]

ALL_AREAS: list[str] = AI_AREAS + SYSTEMS_AREAS + THEORY_AREAS + INTERDISCIPLINARY_AREAS

# Aliases for user convenience: lowered key → list of area slugs
_CATEGORY_ALIASES: dict[str, list[str]] = {
    "ai-all": AI_AREAS,
    "systems": SYSTEMS_AREAS,
    "sys": SYSTEMS_AREAS,
    "theory": THEORY_AREAS,
    "interdisciplinary": INTERDISCIPLINARY_AREAS,
    "all": ALL_AREAS,
}

# Individual area aliases (common alternative names → slug)
_AREA_ALIASES: dict[str, str] = {
    "machine learning": "mlmining",
    "ml": "mlmining",
    "security": "sec",
    "cybersecurity": "sec",
    "database": "mod",
    "databases": "mod",
    "db": "mod",
    "networks": "comm",
    "networking": "comm",
    "net": "comm",
    "os": "ops",
    "operating system": "ops",
    "operating systems": "ops",
    "pl": "plan",
    "programming language": "plan",
    "programming languages": "plan",
    "se": "soft",
    "software": "soft",
    "cv": "vision",
    "computer vision": "vision",
    "hci": "chi",
    "crypto": "crypt",
    "cryptography": "crypt",
    "algorithms": "act",
    "architecture": "arch",
    "graphics": "graph",
    "nlp": "nlp",
    "natural language processing": "nlp",
    "ir": "inforet",
    "information retrieval": "inforet",
    "web": "inforet",
    "robotics": "robotics",
    "robot": "robotics",
    "biology": "bio",
    "bioinformatics": "bio",
    "computational biology": "bio",
    "education": "csed",
    "cs education": "csed",
    "visualization": "visualization",
    "vis": "visualization",
    "eda": "da",
    "design automation": "da",
    "embedded": "bed",
    "embedded systems": "bed",
    "real-time": "bed",
    "mobile": "mobile",
    "mobile computing": "mobile",
    "measurement": "metrics",
    "performance": "metrics",
    "game theory": "ecom",
    "economics": "ecom",
    "logic": "log",
    "verification": "log",
}


def resolve_area_spec(specs: list[str]) -> list[str]:
    """Resolve user-provided area specs into canonical area slugs.

    Each spec can be:
    - A category name like "ai", "systems", "theory"
    - An area slug like "mlmining", "sec"
    - A human-readable alias like "machine learning", "security"

    Returns deduplicated list of area slugs.
    """
    result: list[str] = []
    for spec in specs:
        key = spec.strip().lower()
        if key in AREA_TITLES:
            result.append(key)
        elif key in _CATEGORY_ALIASES:
            result.extend(_CATEGORY_ALIASES[key])
        elif key in _AREA_ALIASES:
            result.append(_AREA_ALIASES[key])
        else:
            # Try partial match on area titles
            matched = False
            for slug, title in AREA_TITLES.items():
                if key in title.lower():
                    result.append(slug)
                    matched = True
                    break
            if not matched:
                raise ValueError(
                    f"Unknown area: '{spec}'. "
                    f"Valid areas: {', '.join(sorted(AREA_TITLES.keys()))}. "
                    f"Valid categories: ai-all, systems, theory, interdisciplinary, all."
                )
    # Deduplicate preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for a in result:
        if a not in seen:
            seen.add(a)
            deduped.append(a)
    return deduped


# Venue aliases for user convenience (lowercase → venue slug)
_VENUE_ALIASES: dict[str, str] = {
    "neurips": "nips",
    "s&p": "oakland",
    "ieee s&p": "oakland",
    "ieee sp": "oakland",
    "usenix security": "usenixsec",
    "usenix sec": "usenixsec",
    "acm ccs": "ccs",
    "sigmod": "sigmod",
    "siggraph asia": "siggraph-asia",
    "usenix atc": "usenixatc",
}


def resolve_venue_spec(
    specs: list[str] | None,
    areas: list[str] | None = None,
) -> set[str] | None:
    """Resolve user-provided venue specs into canonical venue slugs.

    Args:
        specs: List of venue slugs/aliases. None means use defaults for the
               given areas. Special value "all" includes next-tier venues.
        areas: If provided, restrict to venues belonging to these areas.

    Returns:
        Set of venue slugs to include, or None to use defaults.
    """
    if specs is None:
        return None

    result: set[str] = set()
    for spec in specs:
        key = spec.strip().lower()
        if key == "all":
            # Include all venues (including next-tier)
            if areas:
                result.update(v for v, a in VENUE_TO_AREA.items() if a in areas)
            else:
                result.update(VENUE_TO_AREA.keys())
        elif key == "default":
            if areas:
                result.update(
                    v for v in DEFAULT_VENUES if VENUE_TO_AREA.get(v) in areas
                )
            else:
                result.update(DEFAULT_VENUES)
        elif key == "next-tier":
            if areas:
                result.update(
                    v for v in NEXT_TIER_VENUES if VENUE_TO_AREA.get(v) in areas
                )
            else:
                result.update(NEXT_TIER_VENUES)
        elif key in VENUE_TO_AREA:
            result.add(key)
        elif key in _VENUE_ALIASES:
            result.add(_VENUE_ALIASES[key])
        else:
            raise ValueError(
                f"Unknown venue: '{spec}'. "
                f"Valid venues: {', '.join(sorted(VENUE_TO_AREA.keys()))}. "
                f"Special values: 'all', 'default', 'next-tier'."
            )
    return result


def get_area_venues(area: str, include_next_tier: bool = False) -> set[str]:
    """Get venue slugs for a given area.

    Args:
        area: Area slug (e.g. "mlmining", "sec").
        include_next_tier: If True, include next-tier venues.
    """
    all_venues = {v for v, a in VENUE_TO_AREA.items() if a == area}
    if include_next_tier:
        return all_venues
    return all_venues - NEXT_TIER_VENUES
