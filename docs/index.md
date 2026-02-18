---
layout: home

hero:
  name: FORMAL
  text: Fortran API Documentation
  tagline: Generate beautiful documentation websites for Fortran projects using FORD + VitePress.
  actions:
    - theme: brand
      text: Guide
      link: /guide/
    - theme: alt
      text: View on GitHub
      link: https://github.com/szaghi/formal

features:
  - title: FORD-Powered Parsing
    details: Parses Fortran sources using FORD's battle-tested parser. Works with any FORD-compatible project.
  - title: VitePress Rendering
    details: Generates clean Markdown that VitePress renders natively into a modern, searchable, themed site.
  - title: One Page Per Module
    details: "Type components, bound procedures, subroutine/function signatures, and argument tables -- all auto-generated."
  - title: Auto-Generated Sidebar
    details: Sidebar groups are derived from your source directory structure and update automatically on each run.
  - title: LaTeX Math Support
    details: "Write equations in doc comments using $...$ or $$...$$ -- rendered by MathJax."
  - title: Scaffold in Seconds
    details: "Run `formal init` to scaffold a ready-to-use VitePress site with FORD project file."
---

## Showcases

Projects using FORMAL for their API documentation:

- **[BeFoR64](https://szaghi.github.io/BeFoR64/)** — Base64 encoding/decoding library for Fortran &nbsp;|&nbsp; [GitHub](https://github.com/szaghi/BeFoR64)
- **[FACE](https://szaghi.github.io/FACE/)** — Fortran ANSI Colors and Escape sequences &nbsp;|&nbsp; [GitHub](https://github.com/szaghi/FACE)
- **[FLAP](https://szaghi.github.io/FLAP/)** — Fortran command Line Arguments Parser for poor people &nbsp;|&nbsp; [GitHub](https://github.com/szaghi/FLAP)
- **[PENF](https://szaghi.github.io/PENF/)** — Portability Environment for Fortran poor people &nbsp;|&nbsp; [GitHub](https://github.com/szaghi/PENF)

## Author

**Stefano Zaghi** -- [szaghi](https://github.com/szaghi)

## License

[MIT License](LICENSE)

## Installation

### From PyPI (recommended)

```bash
pipx install formal-ford2vitepress
```

Or with pip:

```bash
pip install formal-ford2vitepress
```

### From source

```bash
git clone https://github.com/szaghi/formal.git
cd formal
pipx install -e .
```

### Requirements

- Python >= 3.9
- [FORD](https://github.com/Fortran-FOSS-Programmers/ford) >= 7.0 (installed automatically)
- [Node.js](https://nodejs.org/) >= 18 (for VitePress, needed at build time only)

## Quick Start

### New project -- scaffold everything

```bash
cd /path/to/your/fortran/project
formal init --name "MyProject" --author "Your Name"
cd docs && npm install
formal generate
npm run docs:dev    # opens http://localhost:5173
```

### Existing project -- just generate API docs

```bash
# If you already have a FORD project file:
formal generate --project doc/main_page.md --output docs/api

# Or let FORMAL auto-detect:
formal generate
```

## Usage

### `formal init`

Scaffolds a VitePress documentation site and creates a FORD project file.

```
formal init [project_root] [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `project_root` | `.` | Root of the Fortran project |
| `--name NAME` | Directory name | Project name |
| `--src-dir DIR [DIR...]` | Auto-detect `src/` | Source directories |
| `--exclude-dir DIR [DIR...]` | Auto-detect | Directories to exclude |
| `--docs-dir DIR` | `docs` | Where to create VitePress site |
| `--ford-file PATH` | `doc/formal.md` | FORD project file location |
| `--docmark MARK` | `<` | FORD doc comment marker (`<` = `!<`) |
| `--author NAME` | | Author name |
| `--no-math` | | Disable LaTeX math support |
| `--no-fortran-highlight` | | Disable Fortran syntax aliases |

### `formal generate`

Parses Fortran sources and generates VitePress Markdown API documentation.

```
formal generate [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--project FILE` | Auto-detect | FORD project file path |
| `--output DIR` | `docs/api` | Output directory for generated files |
| `--src-root PATH` | Auto-detect | Root path to strip from source paths |
| `--quiet` | | Suppress progress output |

## How It Works

```
Fortran .F90 sources
    |
    |  FORD parser (load_settings + Project + correlate)
    |  extracts modules, types, procedures, doc_list
    v
FORD Project object model
    |
    |  FORMAL generator (format_module, format_type, ...)
    |  walks the object tree, generates Markdown
    v
docs/api/*.md + _sidebar.json
    |
    |  VitePress (npm run docs:build)
    v
Static HTML documentation site
```

FORD's pipeline goes `parse -> correlate -> markdown -> HTML`. FORMAL hooks in after `correlate()` and reads the raw `doc_list` (Markdown strings) from every entity, skipping FORD's own HTML generation entirely. VitePress handles the Markdown-to-HTML conversion with its own theme.
