# FORMAL

**F**(ortran) **(f)O**(rd) **(vitep)R**(ess) **M**(arkdown) **(document)A**(tion) **(htm)L**

Generate beautiful API documentation websites for Fortran projects. FORMAL bridges [FORD](https://github.com/Fortran-FOSS-Programmers/ford) (Fortran Documenter) and [VitePress](https://vitepress.dev) (Vue-powered static site generator) -- it parses your Fortran `!<` doc comments and produces a complete, searchable, themed documentation site.

## Features

- Parses Fortran sources using FORD's battle-tested parser
- Generates clean Markdown that VitePress renders natively
- One page per module with: type components, bound procedures, subroutine/function signatures, argument tables
- Auto-generated sidebar grouped by source directory structure
- LaTeX math support in doc comments (rendered by MathJax)
- Fortran syntax highlighting in code blocks
- Scaffolds a ready-to-use VitePress site in seconds
- Works with any FORD-compatible Fortran project

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
- [FORD](https://github.com/Fortran-FOSS-Programmers/ford) >= 7.0 (installed automatically as dependency)
- [Node.js](https://nodejs.org/) >= 18 (for VitePress, needed at docs build time only)

## Quick start

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

Scaffolds a VitePress documentation site and creates a FORD project file for your Fortran sources.

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

**What it creates** (never overwrites existing files):

```
your-project/
├── doc/
│   └── formal.md              # FORD project file
└── docs/
    ├── index.md               # Landing page
    ├── package.json           # npm config with scripts
    └── .vitepress/
        └── config.mts         # VitePress config with API sidebar
```

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

**What it generates**:

```
docs/api/
├── index.md                   # Index page listing all modules
├── _sidebar.json              # Sidebar groups (imported by config.mts)
├── adam_grid_object.md        # One page per Fortran module
├── adam_field_object.md
└── ...
```

**Auto-detection**: if `--project` is not given, FORMAL looks for these files in order:
1. `doc/formal.md`
2. `doc/vitepress.md`
3. `doc/main_page.md`

## Writing Fortran doc comments

FORMAL reads FORD-style `!<` doc comments (configurable via `docmark`):

```fortran
module physics_solver
!< Compressible Navier-Stokes solver.
!< Supports 1D, 2D, and 3D configurations.

real(R8P), parameter :: GAMMA = 1.4_R8P !< Ratio of specific heats.

type :: solver_config
   !< Solver configuration.
   integer(I4P) :: order = 5 !< WENO reconstruction order.
   real(R8P)    :: cfl = 0.8 !< CFL number.
   contains
      procedure :: init !< Initialize the solver.
endtype solver_config

contains

subroutine compute_flux(self, q, flux)
!< Compute numerical flux.
!<
!< Uses the Rusanov approximate Riemann solver:
!< $$ F_{i+1/2} = \frac{1}{2}(F_L + F_R) - \frac{\lambda}{2}(U_R - U_L) $$
class(solver_config), intent(in)  :: self    !< Solver config.
real(R8P),            intent(in)  :: q(:)    !< Conservative variables.
real(R8P),            intent(out) :: flux(:) !< Numerical flux.
```

**What gets extracted**:
- Module-level comments become the module description
- Variable comments (same-line `!<`) become table cell descriptions
- Type comments become type section descriptions
- Procedure comments become procedure section descriptions with full argument tables
- LaTeX math (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`) renders via MathJax

## Generated page structure

Each module page contains (when applicable):

```
# module_name
> Module description

**Source**: `src/lib/common/module_name.F90`

## Variables
| Name | Type | Attributes | Description |

## Derived Types
### type_name
#### Components
| Name | Type | Attributes | Description |
#### Type-Bound Procedures
| Name | Attributes | Description |

## Interfaces
### interface_name

## Subroutines
### subroutine_name
```fortran
subroutine name(arg1, arg2)
```
**Arguments**
| Name | Type | Intent | Attributes | Description |

## Functions
(same as subroutines, plus return type)
```

## Integrating with an existing VitePress site

If you already have a VitePress site, add FORMAL's API sidebar to your config:

```typescript
// docs/.vitepress/config.mts
import apiSidebar from '../api/_sidebar.json'

export default defineConfig({
  markdown: {
    math: true,  // if you want LaTeX support
  },
  themeConfig: {
    sidebar: {
      // ... your existing sidebars ...
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'Overview', link: '/api/' },
          ],
        },
        ...apiSidebar,
      ],
    },
  },
})
```

Then generate and build:

```bash
formal generate --project doc/my_ford_file.md --output docs/api
cd docs && npm run docs:build
```

## Customization

See the [Documentation Guide](docs/guide/) for:

- Adding hand-written pages alongside API docs
- Customizing sidebar structure and grouping
- Modifying the generated Markdown layout
- Writing effective Fortran doc comments
- LaTeX math and Fortran syntax highlighting
- Deployment to GitHub Pages, Netlify, etc.

## How it works

```
Fortran .F90 sources
    │
    │  FORD parser (load_settings + Project + correlate)
    │  extracts modules, types, procedures, doc_list
    ▼
FORD Project object model
    │
    │  FORMAL generator (format_module, format_type, ...)
    │  walks the object tree, generates Markdown
    ▼
docs/api/*.md + _sidebar.json
    │
    │  VitePress (npm run docs:build)
    ▼
Static HTML documentation site
```

Key insight: FORD's pipeline goes `parse → correlate → markdown → HTML`. FORMAL hooks in after `correlate()` and reads the raw `doc_list` (Markdown strings) from every entity, skipping FORD's own HTML generation entirely. VitePress handles the Markdown-to-HTML conversion with its own theme.

## Development

### Setup

```bash
git clone https://github.com/szaghi/formal.git
cd formal
pip install -e ".[dev]"
```

This installs FORMAL in editable mode along with `pytest` and `ruff`.

### Running tests

```bash
# Run all tests (unit + integration)
pytest -v

# Run unit tests only (no FORD dependency needed)
pytest -v -m "not integration"

# Run integration tests only (requires FORD)
pytest -v -m "integration"

# Quick summary
pytest --tb=short
```

### Test structure

```
tests/
├── mocks.py                     # Lightweight mock FORD objects for unit tests
├── conftest.py                  # Shared fixtures
├── fixtures/
│   └── sample_module.F90        # Fortran fixture for integration tests
├── test_formatting.py           # strip_html, escape_pipe, format_doc, inline_doc, ...
├── test_classify.py             # _classify_module sidebar grouping
├── test_entity_formatters.py    # format_variable_table, format_procedure, format_type, ...
├── test_scaffold.py             # create_ford_project_file, init_vitepress_site, ...
├── test_cli.py                  # CLI argument parsing and command dispatch
└── test_integration.py          # Full pipeline: Fortran fixture -> FORD parse -> Markdown
```

**Unit tests** use mock objects that mimic FORD entities by duck-typing, so they run without FORD parsing overhead. **Integration tests** exercise the full pipeline (FORD parse + Markdown generation) and are marked with `@pytest.mark.integration`.

### Linting

```bash
ruff check src/ tests/
ruff format --check src/ tests/
```

## Releasing a new version

A release script at `scripts/build_publish.sh` automates the full release pipeline.

### One-command release

```bash
./scripts/build_publish.sh release 1.0.0
```

This runs through every step with a confirmation prompt upfront:

| Step | Action | Aborts if... |
|------|--------|-------------|
| Pre-flight | Checks clean working tree, tag doesn't exist | Uncommitted changes or tag collision |
| 1. Bump | Updates version in `pyproject.toml` and `src/formal/__init__.py` | Invalid format or already at that version |
| 2. Commit | `git commit -m "release: v1.0.0"` | |
| 3. Build | Clean build of sdist + wheel, validates with twine | Build or validation failure |
| 4. Test | Installs wheel via pipx, checks `--version` and `--help` | Version mismatch or broken CLI |
| 5. Tag | `git tag -a v1.0.0 -m "Release v1.0.0"` | |
| 6. Publish | `twine upload dist/*` to PyPI | Upload failure |
| 7. Push | Pushes commit and tag to origin | |

### Individual steps

Each step is also available standalone for more control:

```bash
# Bump version without committing (useful for pre-release tweaks)
./scripts/build_publish.sh bump 0.2.0

# Build and validate only
./scripts/build_publish.sh build

# Smoke-test the built wheel
./scripts/build_publish.sh test

# Publish to TestPyPI first (dry run)
./scripts/build_publish.sh testpublish

# Publish to PyPI (assumes dist/ already built)
./scripts/build_publish.sh publish

# Build + publish in one go (no version bump)
./scripts/build_publish.sh all
```

### Where the version lives

The version is stored in two files that the `bump` / `release` commands update together:

| File | Line | Used by |
|------|------|---------|
| `pyproject.toml` | `version = "X.Y.Z"` | PyPI, build tools |
| `src/formal/__init__.py` | `__version__ = "X.Y.Z"` | `formal --version`, runtime |

### Requirements for publishing

- A [PyPI account](https://pypi.org/account/register/) with an [API token](https://pypi.org/manage/account/token/)
- `build` and `twine` available via pip or pipx (the script auto-detects both)

## Author

**Stefano Zaghi** -- [szaghi](https://github.com/szaghi)

## License

[MIT License](LICENSE)

## Acknowledgments

- [FORD](https://github.com/Fortran-FOSS-Programmers/ford) by Chris MacMackin -- the Fortran parser that makes this possible
- [VitePress](https://vitepress.dev) -- the static site generator
- The ADAM development team for the original use case
