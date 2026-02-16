---
title: Common Workflows
---

# Common Workflows

## "I added new Fortran modules"

Just re-run -- FORMAL picks up all modules in the configured source directories:

```bash
formal generate
```

## "I want to exclude a directory from API docs"

Edit `doc/formal.md` and add to `exclude_dir`:

```
exclude_dir: ../src/third_party/
             ../src/experimental/     # <-- add here
```

## "I want to add a hand-written page"

1. Create `docs/my-section/my-page.md`
2. Add to sidebar in `docs/.vitepress/config.mts`
3. Optionally add to nav bar

See [Writing Pages](./writing-pages) for details.

## "I want to change the landing page"

Edit `docs/index.md`. The hero section uses YAML frontmatter -- see [VitePress home layout](https://vitepress.dev/reference/default-theme-home-page).

## "I want to regenerate only when sources change"

Use file watching or a Makefile:

```makefile
docs/api/_sidebar.json: $(wildcard src/**/*.F90) doc/formal.md
	formal generate --quiet
```

Or integrate with your build system.
