---
title: Deployment
---

# Deploying the Site

## Build

```bash
cd docs
npm run docs:build
# Static files in docs/.vitepress/dist/
```

## GitHub Pages

Add a workflow at `.github/workflows/docs.yml`:

```yaml
name: Deploy docs

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: docs/package-lock.json
      - run: pip install formal-ford2vitepress
      - run: formal generate
      - run: cd docs && npm ci && npm run docs:build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

::: tip
Remember to enable GitHub Pages in your repository settings under **Settings > Pages > Source > GitHub Actions**.
:::

::: tip
If your site is deployed to a subpath (e.g. `https://user.github.io/formal/`), uncomment and set the `base` option in `docs/.vitepress/config.mts`:
```typescript
base: '/formal/',
```
:::

## Other Hosts

The output is plain static files. Upload `docs/.vitepress/dist/` to any host:

- **Netlify**: drag-and-drop or connect your repo
- **Vercel**: import the repo, set build command to `cd docs && npm run docs:build`
- **Self-hosted**: copy files to any web server
