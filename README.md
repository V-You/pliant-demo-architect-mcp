# Pliant demo architect MCP

Mock-first FastMCP server for preparing Pliant demo scenarios, configuring spend controls, testing policies, generating transactions, and diagnosing callback issues.

The current implementation is intentionally mock-first. It preserves the response shapes and terminology of the Pliant API wherever practical, while keeping state in memory so a sales or solutions workflow can be demonstrated end to end.

## What is implemented

- FastMCP server entry point with five tools
- In-memory `MockPliantClient` with deterministic IDs and seeded data
- HTML MCP app resources for controls and callback diagnostics
- Initial test suite for the mock layer and prompt-chain state propagation
- Copilot skill files for demo prep and policy checking

## Tools

- `setup_demo_scenario` creates or reuses a deterministic scenario with org, card account, cardholder, and virtual card
- `set_card_controls` applies category, merchant, time, and amount controls to a card
- `test_spend_policy` returns structured controls data for LLM reasoning and MCP app rendering
- `generate_demo_data` creates realistic transactions, including optional declined attempts
- `diagnose_callbacks` returns callback health, recent events, retry strategy, and security guidance

## Quick start

Create a local virtual environment and install the project with dev dependencies:

```bash
/usr/bin/python3 -m venv .venv
.venv/bin/python -m pip install -e .[dev]
```

List the registered tools:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/fastmcp list server.py
```

Run the server over stdio:

```bash
.venv/bin/python server.py
```

Call a single tool through the FastMCP CLI:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/fastmcp call server.py setup_demo_scenario \
	scenario_name='Smoke Demo' \
	cardholder_name='Alex Example' \
	--json
```

Run the test suite:

```bash
.venv/bin/python -m pytest -q tests
```

## Smoke run

The mock state lives inside one Python process, so an end-to-end smoke run should execute all five tools in the same process. Use the helper script below:

```bash
.venv/bin/python scripts/smoke_run.py
```

The script runs this flow:

1. `setup_demo_scenario`
2. `set_card_controls`
3. `generate_demo_data`
4. `test_spend_policy`
5. `diagnose_callbacks`

It prints a compact summary and exits non-zero if any tool returns an error payload.

## Repository layout

```text
pliant-demo-architect-mcp/
|- README.md
|- pyproject.toml
|- server.py
|- client.py
|- mock.py
|- models.py
|- fixtures.py
|- apps/
|- scripts/
|- tests/
|- .github/skills/
`- md/
```

## Notes

- The authoritative product spec is in `md/PRD_initial_20260306.md`.
- The system Python on this machine is PEP 668-managed. Use `.venv` for installs, tests, and smoke runs.
- The server currently targets FastMCP 3.x and uses the `@modelcontextprotocol/ext-apps` JS SDK for app rendering.
- In this environment, keep `.venv/bin` on `PATH` when using the `fastmcp` CLI against a local file target.
