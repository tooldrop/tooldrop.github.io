#!/usr/bin/env python3
"""Submit sitemap URLs to IndexNow (Bing and other participating engines).

Finds the hex key file in static/, reads URLs from dist/sitemap.xml if present
or from the live sitemap, then POSTs to https://api.indexnow.org/indexnow.
Usage: SITE_URL=https://trytooldrop.com python3 submit_indexnow.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = os.environ.get("SITE_URL", "https://trytooldrop.com").rstrip("/")
HOST = SITE.split("://", 1)[-1]


def find_key() -> tuple[str, Path]:
    keys = [
        p
        for p in (ROOT / "static").glob("*.txt")
        if re.fullmatch(r"[0-9a-fA-F]{8,128}", p.stem)
    ]
    if not keys:
        sys.exit("No IndexNow key file found in static/ (expected an 8–128 hex .txt file)")
    if len(keys) > 1:
        sys.exit(f"Multiple IndexNow key files in static/: {', '.join(p.name for p in keys)}")
    return keys[0].stem, keys[0]


def sitemap_urls() -> list[str]:
    local = ROOT / "dist" / "sitemap.xml"
    if local.is_file():
        raw = local.read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(f"{SITE}/sitemap.xml", timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    root = ET.fromstring(raw)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [el.text.strip() for el in root.findall("sm:url/sm:loc", ns) if el.text]
    if not locs:
        locs = [el.text.strip() for el in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if el.text]
    if not locs:
        sys.exit("No <loc> entries found in sitemap")
    return locs


def main() -> None:
    key, key_path = find_key()
    urls = sitemap_urls()
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"{SITE}/{key}.txt",
        "urlList": urls,
    }
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"IndexNow {resp.status}: submitted {len(urls)} URLs ({key_path.name})")
            if body:
                print(body)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        sys.exit(f"IndexNow HTTP {exc.code}: {detail or exc.reason}")


if __name__ == "__main__":
    main()
