> **NOTE (22 Oct 2026): deploy.sh currently FAILS silently (new pages 404). Deploy with wrangler from /tmp/wr instead: cd /tmp/wr && npx -y -p node@22 node /tmp/wr/node_modules/wrangler/bin/wrangler.js pages deploy dist --project-name tooldrop-hq --branch main**

# ToolDrop backup site (Cloudflare Pages)

`SITE_URL=https://tooldrop-hq.pages.dev python3 build.py` reads `data/tools.json` and writes `dist/`.

## Tool fields
`name, url, description, categories[], pricing (free|freemium|paid|unknown), pricingNote?, tags[], dateAdded, featured?, newRelease?, affiliateUrl?, sponsored?`

- `affiliateUrl` (optional, empty by default): if set, every Visit link for that tool uses it instead of `url`, gets
  `rel="sponsored nofollow noopener"` and a small "Affiliate link" note, and any page showing that link gets a one-line
  disclosure linked to `/disclosure/`. JSON-LD and llms files always keep the official `url`.
  To add one: set `"affiliateUrl": "https://vendor.com/?ref=tooldrop"` on the tool and rebuild.
- `sponsored` (optional): `true` renders a "Sponsored" label. `featured` is editorial only and is never shown as paid.

## Generated extras
llms.txt, llms-full.txt, sitemap.xml, robots.txt (AI crawlers allowed), _headers, JSON-LD (WebSite + SearchAction,
Organization, ItemList, SoftwareApplication, BreadcrumbList), /compare/* pages (selection rules in build.py), /disclosure/.
