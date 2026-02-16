---
title: Sidebar Customization
---

# Sidebar Customization

## Single Sidebar vs. Multi-Sidebar

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

## Collapsible Groups

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

## Nested Groups

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

## How the API Sidebar Auto-Updates

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
