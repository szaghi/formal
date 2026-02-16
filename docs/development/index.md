---
title: Development
---

# Development

## Setting Up a Development Environment

```bash
git clone https://github.com/szaghi/formal.git
cd formal
pip install -e ".[dev]"
```

This installs FORMAL in editable mode with `pytest` and `ruff` as dev dependencies.

## Running the Test Suite

```bash
# All tests (unit + integration)
pytest -v

# Unit tests only -- fast, no FORD dependency
pytest -v -m "not integration"

# Integration tests only -- requires FORD installed
pytest -v -m "integration"

# Quick summary output
pytest --tb=short
```

## Test Organization

| Module | What it tests |
|--------|---------------|
| `test_formatting.py` | Pure text helpers: `strip_html`, `escape_pipe`, `format_doc`, `inline_doc`, `format_type_str`, `format_attribs` |
| `test_classify.py` | Sidebar classification: `_classify_module` path-to-group mapping |
| `test_entity_formatters.py` | Entity formatters: `format_variable_table`, `format_procedure`, `format_type`, `format_interface`, `format_module` |
| `test_scaffold.py` | Scaffolding: `create_ford_project_file`, `init_vitepress_site`, `inject_api_sidebar`, `_generate_config` |
| `test_cli.py` | CLI dispatch: `--version`, help output, `init` and `generate` subcommands |
| `test_integration.py` | Full pipeline: parses `tests/fixtures/sample_module.F90` with FORD and verifies generated Markdown |

Unit tests use lightweight mock objects (defined in `tests/mocks.py`) that replicate FORD entity attributes by duck-typing, keeping them fast and independent of FORD internals.

Integration tests are marked with `@pytest.mark.integration` and exercise the complete pipeline: FORD parsing, Markdown generation, sidebar JSON, and index page creation.

## Linting

```bash
ruff check src/ tests/
ruff format --check src/ tests/
```

## Adding Tests for New Features

When adding a new formatting function or CLI option:

1. Add mock objects to `tests/mocks.py` if the feature uses new FORD entity attributes
2. Write unit tests using mocks -- cover edge cases (empty input, HTML in strings, pipe characters)
3. If the feature affects the full pipeline, extend `test_integration.py` with assertions on the generated output
4. Run `pytest -v` to verify everything passes before committing
