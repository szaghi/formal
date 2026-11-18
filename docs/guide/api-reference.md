---
title: API Reference Generation
---

# API Reference Generation

## Pipeline

```
Fortran .F90 sources
    |  FORD parser
    v
FORD Project (modules, types, procedures, variables)
    |  FORMAL generator
    v
docs/api/*.md + _sidebar.json
    |  VitePress build
    v
Static HTML site
```

## What FORD Does

FORD (Fortran Documenter) reads `.F90` files and builds a structured object model:
- Each `module` becomes a `FortranModule` with lists of types, variables, subroutines, functions
- Each `type` has components (variables) and type-bound procedures
- Each subroutine/function has argument lists with types and intents
- Doc comments (`!<` by default) are attached as `doc_list` (raw Markdown strings)

FORMAL calls FORD's `Project()` + `correlate()` to build this model, then walks it to generate Markdown. It never calls FORD's HTML renderer.

## What FORMAL Generates Per Module

````markdown
---
title: module_name
outline: [2, 4]
---
# module_name
> Module description

**Source**: `src/lib/common/module_name.F90`

**Dependencies**                  (with --diagrams: the used modules, each a link)

## Re-exports                     (a facade: what it takes from other modules)
| Name | Kind | Module | Description |

## Variables
| Name | Type | Attributes | Description |

## Derived Types
### type_name
**Components**
| Name | Type | Attributes | Description |
**Type-Bound Procedures**
| Name | Attributes | Description |
#### type_name%binding            (each binding's implementation, even a private one)
```fortran
subroutine impl(self, arg)
```
**Arguments**
| Name | Type | Intent | Attributes | Description |

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
````

The front matter's `outline: [2, 4]` makes VitePress's right-hand outline list the sections, the entities and the
types' bound procedures. A bound procedure is documented under its type, as `type_name%binding`, with its
implementation's signature, arguments and doc: also when the implementation is private, which `display: public`
otherwise drops from the module's own sections. A binding without a doc comment takes its implementation's in the
table; a generic binding lists its specific bindings, linked.

A module that makes public what it takes from other modules (a facade: `use x, only: ...` plus `public :: ...`) lists
those names under Re-exports, in the order of its public list, each linked to its definition. A name from a module
outside the project is traced to the `use ..., only:` it comes from.

## The FORD Project File

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

This text after the metadata is the API overview: FORMAL makes it the introduction of api/index.md.
```

The Markdown after the metadata header is the introduction of the generated API index page (`api/index.md`), above
the list of modules; FORD `[[name]]` links in it are resolved like those of the doc comments. Write there what a
reader needs before opening a module: the layers of the library, the module to start from, the conventions every
module follows. Leave it empty for a bare list of modules.

### Key Settings

| Setting | Description | FORMAL default |
|---------|-------------|----------------|
| `src_dir` | Directories to scan for `.F90` files | Auto-detected from `src/` |
| `exclude_dir` | Directories to skip | Auto-detected (`third_party/`, etc.) |
| `docmark` | Doc comment marker (`<` means `!<`) | `<` |
| `display` | Which visibility to include | `public protected private` |
| `source` | Include source code in output | `false` (not needed for VitePress) |
| `graph` | Generate dependency graphs | `false` (speeds up parsing) |
| `warn` | Print warnings for undocumented entities | `true` |

### Adding Source Directories

To cover more code, add paths to `src_dir` (relative to the FORD project file):

```
src_dir: ../src/lib
         ../src/app
         ../src/plugins        # <-- add new directories here
```

### Excluding Directories

```
exclude_dir: ../src/third_party/
             ../src/generated/
             ../src/deprecated/
```

## Mirrored Source Layout

By default all generated pages land flat inside `docs/api/`. Passing `--mirror-sources` reproduces the Fortran source directory tree inside the output directory:

```bash
formal generate --mirror-sources
```

| Without `--mirror-sources` | With `--mirror-sources` |
|----------------------------|-------------------------|
| `api/my_module.md` | `api/src/lib/my_module.md` |
| `api/other_module.md` | `api/src/app/other_module.md` |

Sidebar links and cross-reference URLs are updated automatically to match. The sidebar groups also switch from human-readable labels to real directory paths (see [Sidebar → Mirroring Source Directory Structure](./sidebar#mirroring-source-directory-structure)).

## Regenerating

Each run writes `.formal-manifest.json` in the output directory: the files it wrote. The next run removes the files
of that list it did not write again (the page of a module deleted, renamed or newly excluded), and the directories
left empty; a file FORMAL did not write (a page added by hand) is never touched, nor anything outside the output
directory. The first run in a directory without a manifest removes nothing.

## Mermaid Diagrams

Passing `--diagrams` embeds Mermaid diagram blocks in every generated page:

```bash
formal generate --diagrams
# or combine both flags:
formal generate --mirror-sources --diagrams
```

Three diagram types are generated from data already present in FORD's correlated object model:

| Diagram | Where it appears | Source data |
|---------|-----------------|-------------|
| **Dependency graph** | Module page, below the source path | `module.uses` |
| **Inheritance diagram** | Each derived type section | `type.extends` + child types |
| **Call graph** | Each subroutine/function section | `proc.calls` + inverse lookup |

Example dependency diagram in Markdown:

````markdown
**Dependencies**

```mermaid
graph LR
  penf["penf"] --> penf_global_parameters_variables["penf_global_parameters_variables"]
  penf["penf"] --> penf_b_size["penf_b_size"]
```
````

Example call graph showing callers (inbound) and callees (outbound), with the current procedure highlighted:

````markdown
**Call graph**

```mermaid
flowchart LR
  strf_r8p["strf_r8p"] --> str_r8p["str_r8p"]
  classDef focus stroke-width:3px,font-weight:bold
  class str_r8p focus
```
````

The call graph runs left to right, so it is at most three columns wide (callers, the procedure, callees) however many
procedures call it: a procedure with many callers grows down the page instead of being shrunk to its width.

The current procedure carries the class `focus`: a thicker border and a bold label, with no colours, so it keeps the
text contrast of the Mermaid theme that renders it, light or dark. To colour it with your site's palette, style the
class in your VitePress theme CSS (`!important` is needed to win over the rules Mermaid writes into each SVG):

```css
.vp-doc .mermaid .node.focus rect { fill: var(--vp-c-brand-soft) !important; stroke: var(--vp-c-brand-1) !important; }
```

### Diagram nodes are links

Every node that has a page or a section is a link to it: a used module to its page, a caller or callee to its section,
a parent or child type to its section. FORMAL writes one Mermaid `click` line per node:

```
  click penf_b_size href "penf_b_size.html" "penf_b_size"
  click str_r8p href "#str-r8p" "str_r8p"
```

The URLs are relative to the page the diagram is on. VitePress rewrites the links of the Markdown with the site's
`base`, but not the links inside an SVG drawn in the browser, so an absolute `/api/...` path would miss the base of a
site served from a subdirectory (`/<repo>/` on GitHub Pages). A node without a page (an external module, an unresolved
call) stays plain text. The links work with Mermaid's default `securityLevel: 'strict'`.

::: warning VitePress 1.x: turn off link prefetching
VitePress 1.6 prefetches the page of every link in view, and reads `link.pathname`, which an SVG link does not have: a
production build logs `TypeError: Cannot read properties of undefined (reading 'replace')` when a diagram with
cross-page links scrolls into view. Navigation is unaffected, only some prefetches are skipped. VitePress 2 fixes it
([vuejs/vitepress#5442](https://github.com/vuejs/vitepress/pull/5442)); on 1.x, turn prefetching off:

```typescript
// .vitepress/config.mts
export default withMermaid({
  router: { prefetchLinks: false },
  // ...
})
```
:::

### Enabling Mermaid in VitePress

Diagrams require `vitepress-plugin-mermaid`. For **new projects**, pass `--mermaid` to `formal init` and it is wired up automatically:

```bash
formal init --mermaid
cd docs && npm install
formal generate --diagrams
```

For an **existing site**, install manually and wrap the config:

```bash
npm i vitepress-plugin-mermaid mermaid -D
```

```typescript
// .vitepress/config.mts
import { withMermaid } from 'vitepress-plugin-mermaid'  // replace defineConfig import
import apiSidebar from '../api/_sidebar.json'

export default withMermaid({           // replace defineConfig(
  // ... your existing config unchanged ...
  mermaid: {},
})
```

## Customizing API Output

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
| `_classify_module()` | How modules map to sidebar groups (default mode) |
| `format_dependency_diagram()` | Module dependency graph block |
| `format_inheritance_diagram()` | Type inheritance diagram block |
| `format_call_diagram()` | Procedure call graph block |
| `build_called_by_index()` | Project-wide callee→callers mapping |
| `build_type_children_index()` | Project-wide parent→children type mapping |
| `inline_doc()` | How doc comments appear in table cells |
| `format_doc()` | How doc comments appear in block content |

### Sidebar Grouping

By default, `_classify_module()` groups modules by their source path:
- `src/app/<name>/...` → `Applications / NAME`
- `src/lib/<name>/...` → `Library / name`
- Other paths → grouped by first two directory components

With `--mirror-sources`, the group name is the raw source directory path (e.g. `src/lib`, `src/tests`). To change grouping in default mode, override `_classify_module()` or post-process the sidebar JSON after generation.

## Programmatic Usage

You can also use FORMAL as a library:

```python
from pathlib import Path
from formal.generator import generate

result = generate(
    project_file=Path("doc/formal.md"),
    output_dir=Path("docs/api"),
    mirror_sources=True,   # mirror source tree in output
    diagrams=True,         # embed Mermaid diagrams
    verbose=True,
)
print(f"Generated {result['modules']} module pages")
print(f"Sidebar groups: {[g['text'] for g in result['sidebar']]}")
```
