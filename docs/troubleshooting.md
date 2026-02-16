---
title: Troubleshooting
---

# Troubleshooting

## "No FORD project file found"

Run `formal init` to create one, or specify `--project path/to/file.md`.

## "markdown-it-mathjax3 not installed"

```bash
cd docs && npm install markdown-it-mathjax3
```

Or disable math: remove `math: true` from `config.mts`.

## "Include file 'X.H' not found" during generation

FORD's preprocessor can't find include files. These are warnings and the module will still be parsed (with preprocessor directives stripped). To suppress, add the include directories to your FORD project file or set `preprocess: false`.

## "Module has no types/procedures"

Check that:
1. The source file is in a directory listed in `src_dir`
2. The file has `.F90` or `.f90` extension
3. The module has `public` entities (or `display` includes `private`)

## Sidebar shows "Other" group

The module's source file path doesn't match the expected `src/app/` or `src/lib/` pattern. Customize `_classify_module()` in `generator.py` for your project layout.

## Reference Links

- [VitePress documentation](https://vitepress.dev)
- [VitePress sidebar config](https://vitepress.dev/reference/default-theme-sidebar)
- [VitePress Markdown extensions](https://vitepress.dev/guide/markdown)
- [FORD documentation](https://forddocs.readthedocs.io)
- [FORD docmark syntax](https://forddocs.readthedocs.io/en/latest/user_guide/writing_documentation.html)
