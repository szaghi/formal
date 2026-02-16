import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: 'FORMAL',
  description: 'Fortran API documentation with FORD + VitePress',

  // Set base path for GitHub Pages (repo name)
  // base: '/formal/',

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/' },
      { text: 'Development', link: '/development/' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Guide',
          items: [
            { text: 'Introduction', link: '/guide/' },
            { text: 'Site Structure', link: '/guide/site-structure' },
            { text: 'Writing Pages', link: '/guide/writing-pages' },
            { text: 'Sidebar Customization', link: '/guide/sidebar' },
            { text: 'API Reference Generation', link: '/guide/api-reference' },
            { text: 'Doc Comments', link: '/guide/doc-comments' },
            { text: 'Common Workflows', link: '/guide/workflows' },
            { text: 'Deployment', link: '/guide/deployment' },
          ],
        },
      ],

      '/development/': [
        {
          text: 'Development',
          items: [
            { text: 'Setup & Testing', link: '/development/' },
            { text: 'Releasing', link: '/development/releasing' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/szaghi/formal' },
    ],

    search: {
      provider: 'local',
    },
  },

  markdown: {
    math: true,
    languageAlias: {
      fortran: 'fortran-free-form',
      f90: 'fortran-free-form',
      f95: 'fortran-free-form',
      f03: 'fortran-free-form',
      f08: 'fortran-free-form',
      f77: 'fortran-fixed-form',
    },
  },
})
