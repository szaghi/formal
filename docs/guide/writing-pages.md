---
title: Writing Pages
---

# Adding Hand-Written Pages

## Step 1: Create the Markdown File

Place it in an appropriate directory under `docs/`:

```bash
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

## Step 2: Add It to the Sidebar

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

## Step 3 (optional): Add to the Top Nav Bar

```typescript
nav: [
  { text: 'Home', link: '/' },
  { text: 'Guide', link: '/guide/getting-started' },   // <-- new
  { text: 'API', link: '/api/' },
],
```

## Adding a New Documentation Section

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
