#!/usr/bin/env python3
"""Build redirect-only GitHub Pages site that sends visitors to Cloudflare.

This script:
1. Runs cloudflare-site/build.py to get valid Cloudflare paths
2. Builds Eleventy to get old GitHub Pages paths
3. Creates redirect HTML pages for each old URL

Usage: python3 scripts/build_redirects.py
Output: _site/ directory with redirect pages
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CLOUDFLARE_BASE = "https://tooldrop-hq.pages.dev"
OUT_DIR = Path("_site")

def slugify(s):
    """Match the slugify filter from .eleventy.js"""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def get_eleventy_paths():
    """Get all paths the old Eleventy site would generate."""
    tools_file = Path("src/_data/tools.json")
    site_file = Path("src/_data/site.json")
    
    tools = json.loads(tools_file.read_text())
    site = json.loads(site_file.read_text())
    
    paths = set()
    
    paths.add("/")
    paths.add("/about/")
    paths.add("/new-releases/")
    
    categories = set()
    for tool in tools:
        for cat in tool.get("categories", []):
            categories.add(cat)
    
    for cat in categories:
        paths.add(f"/category/{slugify(cat)}/")
    
    for tool in tools:
        slug = slugify(tool["name"])
        paths.add(f"/tool/{slug}/")
    
    return paths

def get_cloudflare_paths():
    """Get all paths the Cloudflare site generates by running build.py."""
    cf_dir = Path("cloudflare-site")
    dist_dir = cf_dir / "dist"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    env = os.environ.copy()
    env["SITE_URL"] = CLOUDFLARE_BASE
    
    result = subprocess.run(
        [sys.executable, "build.py"],
        cwd=cf_dir,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running cloudflare build.py: {result.stderr}")
        sys.exit(1)
    
    paths = set()
    for f in dist_dir.rglob("index.html"):
        rel = f.parent.relative_to(dist_dir)
        path = "/" if str(rel) == "." else f"/{rel}/"
        paths.add(path)
    
    paths.add("/")
    
    for f in dist_dir.rglob("*.html"):
        if f.name != "index.html":
            rel = f.relative_to(dist_dir)
            paths.add(f"/{rel}")
    
    return paths

KNOWN_REDIRECTS = {
    "/tool/play-ht/": "/category/voice/",
}

def map_path(old_path, cf_paths):
    """Map an old Eleventy path to a Cloudflare path."""
    if old_path in KNOWN_REDIRECTS:
        return KNOWN_REDIRECTS[old_path]
    
    if old_path in cf_paths:
        return old_path
    
    if old_path.startswith("/tool/"):
        tool_slug = old_path.replace("/tool/", "").rstrip("/")
        cf_tool_path = f"/tool/{tool_slug}/"
        if cf_tool_path in cf_paths:
            return cf_tool_path
        
        for cf_path in cf_paths:
            if cf_path.startswith("/tool/") and cf_path.rstrip("/").endswith(tool_slug):
                return cf_path
    
    if old_path.startswith("/category/"):
        cat_slug = old_path.replace("/category/", "").rstrip("/")
        cf_cat_path = f"/category/{cat_slug}/"
        if cf_cat_path in cf_paths:
            return cf_cat_path
    
    return "/"

def create_redirect_html(target_url, title="ToolDrop"):
    """Create an HTML page that redirects to target_url with all required elements."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={target_url}">
  <link rel="canonical" href="{target_url}">
  <title>Redirecting to {title}</title>
  <script>window.location.replace("{target_url}");</script>
</head>
<body>
  <p>This page has moved. If you are not redirected automatically, <a href="{target_url}">click here to go to {title}</a>.</p>
</body>
</html>
'''

def main():
    print("Getting Eleventy (old) paths...")
    eleventy_paths = get_eleventy_paths()
    print(f"  Found {len(eleventy_paths)} old paths")
    
    print("Getting Cloudflare (new) paths...")
    cf_paths = get_cloudflare_paths()
    print(f"  Found {len(cf_paths)} Cloudflare paths")
    
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    
    mappings = {}
    non_1to1_mappings = []
    
    for old_path in sorted(eleventy_paths):
        new_path = map_path(old_path, cf_paths)
        mappings[old_path] = new_path
        
        if old_path != new_path:
            non_1to1_mappings.append((old_path, new_path))
        
        target_url = CLOUDFLARE_BASE + new_path
        
        if old_path == "/":
            out_file = OUT_DIR / "index.html"
        else:
            out_file = OUT_DIR / old_path.strip("/") / "index.html"
        
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(create_redirect_html(target_url, f"ToolDrop - {old_path}"))
    
    (OUT_DIR / "404.html").write_text(create_redirect_html(CLOUDFLARE_BASE, "ToolDrop"))
    
    (OUT_DIR / "robots.txt").write_text(f"""User-agent: *
Disallow: /

Sitemap: {CLOUDFLARE_BASE}/sitemap.xml
""")
    
    (OUT_DIR / ".nojekyll").write_text("")
    
    print(f"\nBuilt {len(mappings)} redirect pages to {OUT_DIR}/")
    
    if non_1to1_mappings:
        print(f"\nPath mappings that are NOT 1:1 ({len(non_1to1_mappings)}):")
        for old, new in non_1to1_mappings:
            print(f"  {old} -> {new}")
    else:
        print("\nAll paths map 1:1")
    
    print(f"\nAlso created: 404.html, robots.txt, .nojekyll")
    
    return non_1to1_mappings

if __name__ == "__main__":
    main()
