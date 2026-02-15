# FORMAL Documentation Guide

A complete guide to setting up, customizing, and maintaining your Fortran API documentation site.

## Table of contents

- [Site structure overview](#site-structure-overview)
- [Quick start walkthrough](#quick-start-walkthrough)
- [How VitePress turns Markdown into a site](#how-vitepress-turns-markdown-into-a-site)
- [Adding hand-written pages](#adding-hand-written-pages)
- [Adding a new documentation section](#adding-a-new-documentation-section)
- [Sidebar customization](#sidebar-customization)
- [How the API reference is generated](#how-the-api-reference-is-generated)
- [The FORD project file](#the-ford-project-file)
- [Customizing API output](#customizing-api-output)
- [Writing Fortran doc comments](#writing-fortran-doc-comments)
- [LaTeX math support](#latex-math-support)
- [Fortran syntax highlighting](#fortran-syntax-highlighting)
- [Common workflows](#common-workflows)
- [Deploying the site](#deploying-the-site)
- [Troubleshooting](#troubleshooting)

---

## Site structure overview

After running `formal init`, your project will have this layout:

```
your-project/
├── src/                        # Your Fortran source code
│   ├── lib/                    # Libraries
│   └── app/                    # Applications
├── doc/
│   └── formal.md               # FORD project file (tells FORD where sources are)
└── docs/                       # VitePress documentation site
    ├── index.md                # Landing page (hero + features)
    ├── package.json            # npm scripts and dependencies
    ├── .vitepress/
    │   └── config.mts          # Site config (nav, sidebar, markdown options)
    └── api/                    # AUTO-GENERATED (by formal generate)
        ├── index.md            # API index listing all modules
        ├── _sidebar.json       # Sidebar data imported by config
        └── *.md                # One page per Fortran module
```

You add hand-written pages as `.md` files anywhere under `docs/`. The `api/` directory is managed by FORMAL and regenerated on each run.

## Quick start walkthrough

```bash
# 1. Initialize (from your Fortran project root)
formal init --name "MyProject" --author "Jane Doe"

# 2. Install VitePress dependencies
cd docs && npm install

# 3. Generate API docs from Fortran sources
formal generate

# 4. Start development server (hot-reload on file changes)
npm run docs:dev
# Opens http://localhost:5173

# 5. When ready to publish, build the static site
npm run docs:build
# Output in docs/.vitepress/dist/
```

## How VitePress turns Markdown into a site

VitePress maps the file tree under `docs/` directly to URL paths:

| File | URL |
|------|-----|
| `docs/index.md` | `/` |
| `docs/guide/getting-started.md` | `/guide/getting-started` |
| `docs/api/index.md` | `/api/` |
| `docs/api/my_module.md` | `/api/my_module` |

Every `.md` file becomes an HTML page. VitePress handles Markdown parsing, syntax highlighting, navigation, and search indexing automatically.

### Frontmatter

Each page can have YAML frontmatter at the top:

```markdown
---
title: My Page Title
---

# My Page Title

Content here...
```

The `title` field sets the browser tab title. The landing page (`docs/index.md`) uses `layout: home` with hero/features -- see the [VitePress frontmatter docs](https://vitepress.dev/reference/frontmatter-config).

## Adding hand-written pages

### Step 1: Create the Markdown file

Place it in an appropriate directory under `docs/`:

```bash
# Create the file
docs/guide/installation.md
docs/tutorials/first-simulation.md
docs/reference/boundary-conditions.md
```

Write standard GitHub-flavored Markdown. VitePress extends it with:

- Syntax highlighting with language tags (use `` ```fortran `` for Fortran)
- LaTeX math with `$...$` (inline) and `$$...$$` (display)
- [Custom containers](https://vitepress.dev/guide/markdown#custom-containers):

```markdown
::: tip
This is a tip box.
:::

::: warning
This is a warning box.
:::

::: danger
Critical information here.
:::

::: details Click to expand
Hidden content revealed on click.
:::
```

### Step 2: Add it to the sidebar

Open `docs/.vitepress/config.mts` and add an entry to the appropriate sidebar section:

```typescript
sidebar: {
  '/guide/': [
    {
      text: 'Guide',
      items: [
        { text: 'Getting Started', link: '/guide/getting-started' },
        { text: 'Installation', link: '/guide/installation' },  // <-- new
      ],
    },
  ],
}
```

The `link` value must match the file path relative to `docs/`, without `.md`.

### Step 3 (optional): Add to the top nav bar

```typescript
nav: [
  { text: 'Home', link: '/' },
  { text: 'Guide', link: '/guide/getting-started' },   // <-- new
  { text: 'API', link: '/api/' },
],
```

## Adding a new documentation section

To create an entirely new section (e.g. `docs/tutorials/`):

1. **Create the directory and files**:
   ```
   docs/tutorials/
   ├── index.md          # Section landing page
   ├── beginner.md
   └── advanced.md
   ```

2. **Add a sidebar section** in `config.mts`:
   ```typescript
   sidebar: {
     // ... existing sections ...
     '/tutorials/': [
       {
         text: 'Tutorials',
         items: [
           { text: 'Overview', link: '/tutorials/' },
           { text: 'Beginner', link: '/tutorials/beginner' },
           { text: 'Advanced', link: '/tutorials/advanced' },
         ],
       },
     ],
   }
   ```

3. **Add a nav link**:
   ```typescript
   nav: [
     // ...
     { text: 'Tutorials', link: '/tutorials/' },
   ],
   ```

## Sidebar customization

### Single sidebar vs. multi-sidebar

**Multi-sidebar** (recommended, FORMAL's default): different URL prefixes show different sidebar trees. When a user is on `/guide/*` they see only guide pages; on `/api/*` only API pages.

```typescript
// Multi-sidebar (object)
sidebar: {
  '/guide/': [ /* guide items */ ],
  '/api/':   [ /* api items */ ],
}
```

**Single sidebar**: the same sidebar appears everywhere.

```typescript
// Single sidebar (array)
sidebar: [
  { text: 'Guide', items: [...] },
  { text: 'API', items: [...] },
]
```

### Collapsible groups

```typescript
{
  text: 'Section Name',
  collapsed: false,  // false = open by default, true = collapsed
  items: [
    { text: 'Page A', link: '/section/page-a' },
    { text: 'Page B', link: '/section/page-b' },
  ],
}
```

### Nested groups

```typescript
{
  text: 'Applications',
  items: [
    {
      text: 'Solver A',
      collapsed: true,
      items: [
        { text: 'Overview', link: '/apps/solver-a/' },
        { text: 'CPU Backend', link: '/apps/solver-a/cpu' },
        { text: 'GPU Backend', link: '/apps/solver-a/gpu' },
      ],
    },
    { text: 'Solver B', link: '/apps/solver-b' },
  ],
}
```

### How the API sidebar auto-updates

FORMAL writes `docs/api/_sidebar.json`, which `config.mts` imports:

```typescript
import apiSidebar from '../api/_sidebar.json'

sidebar: {
  '/api/': [
    {
      text: 'API Reference',
      items: [{ text: 'Overview', link: '/api/' }],
    },
    ...apiSidebar,  // spread auto-generated groups
  ],
}
```

When you re-run `formal generate`, the sidebar updates automatically with any new or removed modules. No manual editing of `config.mts` needed.

## How the API reference is generated

### Pipeline

```
Fortran .F90 sources
    │  FORD parser
    ▼
FORD Project (modules, types, procedures, variables)
    │  FORMAL generator
    ▼
docs/api/*.md + _sidebar.json
    │  VitePress build
    ▼
Static HTML site
```

### What FORD does

FORD (Fortran Documenter) reads `.F90` files and builds a structured object model:
- Each `module` becomes a `FortranModule` with lists of types, variables, subroutines, functions
- Each `type` has components (variables) and type-bound procedures
- Each subroutine/function has argument lists with types and intents
- Doc comments (`!<` by default) are attached as `doc_list` (raw Markdown strings)

FORMAL calls FORD's `Project()` + `correlate()` to build this model, then walks it to generate Markdown. It never calls FORD's HTML renderer.

### What FORMAL generates per module

```markdown
---
title: module_name
---
# module_name
> Module description from doc comments

**Source**: `src/lib/common/module_name.F90`

## Variables
| Name | Type | Attributes | Description |

## Derived Types
### type_name
> Type description
#### Components
| Name | Type | Attributes | Description |
#### Type-Bound Procedures
| Name | Attributes | Description |

## Interfaces

## Subroutines
### sub_name
> Subroutine description
```fortran
subroutine sub_name(arg1, arg2)
```
**Arguments**
| Name | Type | Intent | Attributes | Description |

## Functions
```

## The FORD project file

The FORD project file (`doc/formal.md` by default) tells FORD where to find your sources. It's a Markdown file with a metadata header:

```
project: MyProject
src_dir: ../src/lib
         ../src/app
exclude_dir: ../src/third_party/
docmark: <
display: public
         protected
         private
source: false
warn: true
graph: false
author: Jane Doe

This text after the metadata is the project description (unused by FORMAL).
```

### Key settings

| Setting | Description | FORMAL default |
|---------|-------------|----------------|
| `src_dir` | Directories to scan for `.F90` files | Auto-detected from `src/` |
| `exclude_dir` | Directories to skip | Auto-detected (`third_party/`, etc.) |
| `docmark` | Doc comment marker (`<` means `!<`) | `<` |
| `display` | Which visibility to include | `public protected private` |
| `source` | Include source code in output | `false` (not needed for VitePress) |
| `graph` | Generate dependency graphs | `false` (speeds up parsing) |
| `warn` | Print warnings for undocumented entities | `true` |

### Adding source directories

To cover more code, add paths to `src_dir` (relative to the FORD project file):

```
src_dir: ../src/lib
         ../src/app
         ../src/plugins        # <-- add new directories here
```

### Excluding directories

```
exclude_dir: ../src/third_party/
             ../src/generated/
             ../src/deprecated/
```

## Customizing API output

FORMAL's generator is in `src/formal/generator.py`. The formatting functions are modular and can be modified independently:

| Function | What it controls |
|----------|-----------------|
| `format_module()` | Overall page layout per module |
| `format_type()` | Derived type sections |
| `format_procedure()` | Subroutine/function sections |
| `format_variable_table()` | Variable/argument tables |
| `format_bound_proc_table()` | Type-bound procedure tables |
| `format_interface()` | Interface sections |
| `generate_sidebar()` | Sidebar grouping logic |
| `_classify_module()` | How modules map to sidebar groups |
| `inline_doc()` | How doc comments appear in table cells |
| `format_doc()` | How doc comments appear in block content |

### Programmatic usage

You can also use FORMAL as a library:

```python
from pathlib import Path
from formal.generator import generate

result = generate(
    project_file=Path("doc/formal.md"),
    output_dir=Path("docs/api"),
    verbose=True,
)
print(f"Generated {result['modules']} module pages")
print(f"Sidebar groups: {[g['text'] for g in result['sidebar']]}")
```

### Sidebar grouping

By default, `_classify_module()` groups modules by their source path:
- `src/app/<name>/...` -> `Applications / NAME`
- `src/lib/<name>/...` -> `Library / name`
- Other paths -> grouped by first two directory components

To change grouping, override `_classify_module()` or process the sidebar JSON after generation.

## Writing Fortran doc comments

### Where to place comments

```fortran
module my_module
!< Module description.            <-- after module statement

integer :: MY_CONST = 42 !< Constant description.  <-- same line as declaration

type :: my_type
   !< Type description.           <-- after type statement
   real :: x !< Component doc.    <-- same line as component
   contains
      procedure :: init !< Bound procedure doc.
endtype

contains

subroutine do_work(self, n)
!< Subroutine description.        <-- after subroutine statement
!< Can span multiple lines.
!< Supports **Markdown** and $\LaTeX$.
class(my_type), intent(inout) :: self !< The object.
integer,        intent(in)    :: n    !< Iteration count.
```

### Doc comment rules

1. Use `!<` (not `!!`) when `docmark: <` is set in the FORD project file
2. Module/type/procedure docs go on lines **immediately after** the statement
3. Variable/argument docs go on the **same line** as the declaration
4. Multi-line docs: continue with `!<` on subsequent lines
5. In table cells, only the **first line** is shown (full text in block descriptions)
6. Markdown and LaTeX are fully supported in doc comments

### Tips for good doc comments

- **First line matters**: for variables and type components, keep the first line short and descriptive -- it becomes the table cell content
- **Describe "what", not "how"**: `!< Conservative variables vector` not `!< A real array`
- **Units and ranges**: `!< CFL number (0 < cfl <= 1)` or `!< Temperature [K]`
- **Cross-references**: use module/type names in backticks for readability

## LaTeX math support

Math rendering is enabled via `markdown: { math: true }` in `config.mts` (uses `markdown-it-mathjax3`).

### In hand-written Markdown pages

```markdown
Inline: $E = mc^2$

Display:
$$
\frac{\partial u}{\partial t} + \nabla \cdot \mathbf{F}(u) = 0
$$
```

### In Fortran doc comments

Both LaTeX delimiter styles work:

```fortran
subroutine compute_flux(q, f)
!< Compute flux using: $F = \rho u \mathbf{e}_x$
!<
!< The Euler equations in conservation form:
!< $$
!< \frac{\partial U}{\partial t} + \frac{\partial F}{\partial x} = 0
!< $$
```

Or with `\(...\)` and `\[...\]` notation:

```fortran
!< Approximate \(\frac{dq}{ds}\) at \(x_i\) as:
!< \[
!< \frac{dq}{ds}\bigg|_i \approx \frac{1}{\Delta s} \sum_{m} c_m q_{i+m}
!< \]
```

## Fortran syntax highlighting

VitePress highlights Fortran code blocks. Use any of these language tags:

````markdown
```fortran
program hello
  implicit none
  print *, "Hello!"
end program
```
````

Tags `fortran`, `f90`, `f95`, `f03`, `f08` all map to free-form Fortran. Use `f77` for fixed-form.

## Common workflows

### "I added new Fortran modules"

Just re-run -- FORMAL picks up all modules in the configured source directories:

```bash
formal generate
```

### "I want to exclude a directory from API docs"

Edit `doc/formal.md` and add to `exclude_dir`:

```
exclude_dir: ../src/third_party/
             ../src/experimental/     # <-- add here
```

### "I want to add a hand-written page"

1. Create `docs/my-section/my-page.md`
2. Add to sidebar in `docs/.vitepress/config.mts`
3. Optionally add to nav bar

### "I want to change the landing page"

Edit `docs/index.md`. The hero section uses YAML frontmatter -- see [VitePress home layout](https://vitepress.dev/reference/default-theme-home-page).

### "I want to regenerate only when sources change"

Use file watching or a Makefile:

```makefile
docs/api/_sidebar.json: $(wildcard src/**/*.F90) doc/formal.md
	formal generate --quiet
```

Or integrate with your build system.

## Deploying the site

### Build

```bash
cd docs
npm run docs:build
# Static files in docs/.vitepress/dist/
```

### GitHub Pages

Add to `.github/workflows/docs.yml`:

```yaml
name: Deploy docs
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: pip install formal
      - run: formal generate
      - run: cd docs && npm ci && npm run docs:build
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/.vitepress/dist
```

### Other hosts

The output is plain static files. Upload `docs/.vitepress/dist/` to any host:
- **Netlify**: drag-and-drop or connect your repo
- **Vercel**: import the repo, set build command to `cd docs && npm run docs:build`
- **Self-hosted**: copy files to any web server

## Troubleshooting

### "No FORD project file found"

Run `formal init` to create one, or specify `--project path/to/file.md`.

### "markdown-it-mathjax3 not installed"

```bash
cd docs && npm install markdown-it-mathjax3
```

Or disable math: remove `math: true` from `config.mts`.

### "Include file 'X.H' not found" during generation

FORD's preprocessor can't find include files. These are warnings and the module will still be parsed (with preprocessor directives stripped). To suppress, add the include directories to your FORD project file or set `preprocess: false`.

### "Module has no types/procedures"

Check that:
1. The source file is in a directory listed in `src_dir`
2. The file has `.F90` or `.f90` extension
3. The module has `public` entities (or `display` includes `private`)

### Sidebar shows "Other" group

The module's source file path doesn't match the expected `src/app/` or `src/lib/` pattern. Customize `_classify_module()` in `generator.py` for your project layout.

## Reference links

- [VitePress documentation](https://vitepress.dev)
- [VitePress sidebar config](https://vitepress.dev/reference/default-theme-sidebar)
- [VitePress Markdown extensions](https://vitepress.dev/guide/markdown)
- [FORD documentation](https://forddocs.readthedocs.io)
- [FORD docmark syntax](https://forddocs.readthedocs.io/en/latest/user_guide/writing_documentation.html)
