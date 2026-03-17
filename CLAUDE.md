# CSRankings MCP Server

## What this is
A FastMCP server that provides CSRankings.org data via MCP tools.
It downloads CSV data from the CSRankings GitHub repo, computes geometric-mean rankings, and exposes 4 tools: `csrankings_rank`, `csrankings_institution`, `csrankings_researcher`, `csrankings_search`.

## How to run
```bash
uv run csrankings-mcp          # run the MCP server
uv run pytest tests/           # run tests
```

## Project layout
- `src/csrankings_mcp/config.py` — area slug mappings and category groups
- `src/csrankings_mcp/data.py` — CSV download, caching, pandas loading
- `src/csrankings_mcp/ranking.py` — ranking computation (geometric mean)
- `src/csrankings_mcp/server.py` — FastMCP tool definitions
