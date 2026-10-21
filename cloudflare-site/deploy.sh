#!/usr/bin/env bash
# NOTE (22 Oct 2026): deploy.sh currently FAILS silently (new pages 404). Deploy with wrangler from /tmp/wr instead: cd /tmp/wr && npx -y -p node@22 node /tmp/wr/node_modules/wrangler/bin/wrangler.js pages deploy dist --project-name tooldrop-hq --branch main
# Usage: CLOUDFLARE_ACCOUNT_ID=<32-hex id> ./deploy.sh   (CLOUDFLARE_API_TOKEN must already be set)
set -euo pipefail
cd "$(dirname "$0")"
: "${CLOUDFLARE_API_TOKEN:?missing}"; : "${CLOUDFLARE_ACCOUNT_ID:?missing}"
WR="npx -y -p node@22 node /tmp/wr/node_modules/wrangler/bin/wrangler.js"   # wrangler 4 needs Node 22; box has Node 20
NAME=tooldrop
if ! $WR pages project create tooldrop --production-branch main; then NAME=tooldrop-hq; $WR pages project create tooldrop-hq --production-branch main; fi
SITE_URL="https://$NAME.pages.dev" python3 build.py
$WR pages deploy dist --project-name "$NAME" --branch main --commit-dirty=true
echo "Deployed to https://$NAME.pages.dev"
