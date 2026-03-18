# CSRankings MCP Server

An [MCP](https://modelcontextprotocol.io/) server that brings [CSRankings.org](https://csrankings.org/) data to AI assistants like Claude. Rank CS departments, look up faculty, and explore researcher profiles — all through natural language.

## Features

The server exposes four tools:

| Tool | Description |
|------|-------------|
| `csrankings_rank` | Rank institutions by research area using geometric-mean scoring (same method as csrankings.org) |
| `csrankings_institution` | List faculty at an institution with per-area publication counts and homepage URLs |
| `csrankings_researcher` | Get a researcher's profile: affiliation, homepage, Google Scholar link, and yearly publications |
| `csrankings_search` | Fuzzy search for institutions or researchers by name |

### Supported Research Areas

Areas can be specified as slugs, human-readable names, or broad categories:

- **AI** — Artificial Intelligence, Computer Vision, Machine Learning, NLP, Web & IR
- **Systems** — Architecture, Networks, Security, Databases, OS, PL, Software Engineering, HPC, and more
- **Theory** — Algorithms & Complexity, Cryptography, Logic & Verification
- **Interdisciplinary** — Graphics, HCI, Robotics, Computational Biology, Visualization, CS Education, Economics & Computation

Use `"all"` to include every area.

### Filtering Options

- **Region** — `us`, `europe`, `asia`, `canada`, `australasia`, `southamerica`, `africa`, or worldwide (default)
- **Year range** — configurable start/end year (default: 2015–2025)
- **Top N** — number of results to return (default: 25)

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Install

```bash
git clone https://github.com/xiawubing/csrankings-mcp.git
cd csrankings-mcp
uv sync
```

### Configure for Claude Code

Add the server to your Claude Code MCP settings (`~/.claude/settings.json` or project-level `.mcp.json`):

```json
{
  "mcpServers": {
    "csrankings": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/csrankings-mcp", "csrankings-mcp"]
    }
  }
}
```

Replace `/path/to/csrankings-mcp` with the actual path to the cloned repository.

### Configure for Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "csrankings": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/csrankings-mcp", "csrankings-mcp"]
    }
  }
}
```

## Usage Examples

Once configured, you can ask Claude questions like:

- *"Rank the top 10 US institutions in machine learning"*
- *"Who are the security researchers at Carnegie Mellon?"*
- *"Show me the profile of Geoffrey Hinton"*
- *"Search for universities with 'Illinois' in the name"*
- *"Compare the top systems schools in Europe vs Asia"*

## Development

```bash
# Run the MCP server locally
uv run csrankings-mcp

# Run tests
uv run pytest tests/
```

## How It Works

The server downloads CSV data from the [CSRankings GitHub repository](https://github.com/emeryberger/CSrankings) and caches it locally for 24 hours. Rankings are computed using the same geometric-mean formula as csrankings.org:

```
score = ((sum_area₁ + 1) × (sum_area₂ + 1) × … × (sum_areaₙ + 1)) ^ (1/n)
```

## Data Source

All publication and affiliation data comes from [CSRankings](https://csrankings.org/) by [Emery Berger](https://emeryberger.com/). CSRankings is a metrics-based ranking of top CS departments based on publications in selective venues.
