---
title: Guide
---

# Documentation Guide

A complete guide to setting up, customizing, and maintaining your Fortran API documentation site with FORMAL.

## Quick Start Walkthrough

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

## What's in this guide

| Page | What you'll learn |
|------|-------------------|
| [Site Structure](./site-structure) | How the docs directory maps to URLs, frontmatter basics |
| [Writing Pages](./writing-pages) | Adding hand-written pages and new sections |
| [Sidebar](./sidebar) | Single vs. multi-sidebar, collapsible groups, auto-updating API sidebar |
| [API Reference](./api-reference) | How the API reference pipeline works, FORD project file, customization |
| [Doc Comments](./doc-comments) | Writing Fortran doc comments, LaTeX math, syntax highlighting |
| [Workflows](./workflows) | Common recipes for day-to-day use |
| [Deployment](./deployment) | Deploying to GitHub Pages, Netlify, and other hosts |
