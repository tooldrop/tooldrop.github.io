# 🛠️ ToolDrop

**AI tools directory for vibe coders and indie game devs**

[Visit the live site →](https://tooldrop-hq.pages.dev)

## About

ToolDrop is a curated directory of AI tools for indie game developers and vibe coders. Find the best AI tools for:

- 💻 Coding agents & IDEs
- 🚀 App builders (vibe coding)
- 🔍 Code review & testing
- 🎨 Game art & sprites
- 📦 3D models & textures
- 🎵 Music & sound effects
- 🎙️ Voice synthesis
- 📖 Game design & narrative
- 🎬 Video & trailers
- 📝 Marketing copy
- 🤖 Agent frameworks

## Tech Stack

- **[Eleventy](https://www.11ty.dev/)** - Static site generator
- **GitHub Pages** - Hosting
- **GitHub Actions** - Automated deployment

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run serve

# Build for production
npm run build
```

## Adding Tools

Tools are stored in `src/_data/tools.json`. See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to add new tools.

## Structure

```
src/
├── _data/
│   ├── tools.json    # All tool data
│   └── site.json     # Site configuration
├── _includes/
│   ├── base.njk      # Base layout
│   └── tool-card.njk # Tool card component
├── category/         # Category page template
├── tool/             # Tool page template
├── css/              # Styles
├── js/               # Client-side JavaScript
├── index.njk         # Home page
├── new-releases.njk  # New releases page
├── about.njk         # About page
├── sitemap.njk       # Sitemap generator
└── robots.txt        # Robots file
```

## Live Site (Cloudflare Pages)

The live site is hosted on Cloudflare Pages at https://tooldrop-hq.pages.dev. Its source is in the `cloudflare-site/` directory.

To build the Cloudflare site locally:

```bash
cd cloudflare-site
SITE_URL=https://tooldrop-hq.pages.dev python3 build.py
# Output is in cloudflare-site/dist/
```

The legacy Eleventy site in the root `src/` directory is no longer actively deployed. GitHub Pages (tooldrop.github.io) now redirects all visitors to the Cloudflare-hosted site.

## License

MIT
