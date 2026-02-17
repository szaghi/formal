---
title: Site Structure
---

# Site Structure

## Overview

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

With `--mirror-sources`, the `api/` directory reproduces the Fortran source tree instead of placing all pages at the top level:

```
    └── api/
        ├── index.md
        ├── _sidebar.json
        └── src/
            ├── lib/
            │   ├── my_module.md
            │   └── another_module.md
            └── app/
                └── main_module.md
```

You add hand-written pages as `.md` files anywhere under `docs/`. The `api/` directory is managed by FORMAL and regenerated on each run.

## How VitePress Turns Markdown into a Site

VitePress maps the file tree under `docs/` directly to URL paths:

| File | URL |
|------|-----|
| `docs/index.md` | `/` |
| `docs/guide/getting-started.md` | `/guide/getting-started` |
| `docs/api/index.md` | `/api/` |
| `docs/api/my_module.md` | `/api/my_module` |

Every `.md` file becomes an HTML page. VitePress handles Markdown parsing, syntax highlighting, navigation, and search indexing automatically.

## Frontmatter

Each page can have YAML frontmatter at the top:

```markdown
---
title: My Page Title
---

# My Page Title

Content here...
```

The `title` field sets the browser tab title. The landing page (`docs/index.md`) uses `layout: home` with hero/features -- see the [VitePress frontmatter docs](https://vitepress.dev/reference/frontmatter-config).
