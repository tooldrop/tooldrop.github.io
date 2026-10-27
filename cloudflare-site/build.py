#!/usr/bin/env python3
"""Static rebuild of ToolDrop (backup for Cloudflare Pages). Usage: SITE_URL=https://x.pages.dev python3 build.py

Tool fields (data/tools.json): name, url, description, categories[], pricing (free|freemium|paid|unknown),
pricingNote?, tags[], dateAdded, featured?, newRelease?, affiliateUrl? (optional, empty = not used),
sponsored? (optional, renders a "Sponsored" label). See README.md.
"""
import json, os, re, shutil, html
from datetime import date
SITE = os.environ.get("SITE_URL", "https://tooldrop.pages.dev").rstrip("/")
SUB = "https://tooldrophq.substack.com"
XURL = "https://x.com/trytooldrop"
OUT = "dist"
TODAY = date.today().isoformat()
tools = json.load(open(os.environ.get("TOOLS_JSON", "data/tools.json")))
CATS = [("AI Coding Agents & IDEs","💻"),("App Builders","🚀"),("Code Review & Testing","🔍"),("Game Art & Sprites","🎨"),
        ("3D & Models","📦"),("Audio, Music & SFX","🎵"),("Voice","🎙️"),("Game Design & Narrative","📖"),
        ("Video & Trailers","🎬"),("Marketing & Store Page Copy","📝"),("Agent Frameworks","🤖"),("Deploy & Hosting","☁️")]
ICON = dict(CATS)
APPCAT = {"AI Coding Agents & IDEs":"DeveloperApplication","App Builders":"DeveloperApplication","Code Review & Testing":"DeveloperApplication",
          "Agent Frameworks":"DeveloperApplication","Deploy & Hosting":"DeveloperApplication","Game Art & Sprites":"DesignApplication","3D & Models":"DesignApplication",
          "Audio, Music & SFX":"MultimediaApplication","Voice":"MultimediaApplication","Video & Trailers":"MultimediaApplication"}
PRICE_LABEL = {"free":"Free","freemium":"Freemium","paid":"Paid","unknown":"Pricing not published"}
DISCLOSURE_LINE = 'Some links on this page are affiliate links. If you sign up through them we may earn a commission at no extra cost to you. <a href="/disclosure/">Read our disclosure</a>.'
e = lambda s: html.escape(str(s), quote=True)
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
for t in tools:
    t["slug"] = slug(t["name"])
    t.setdefault("affiliateUrl", "")
assert len({t["slug"] for t in tools}) == len(tools)
BY_NAME = {t["name"]: t for t in tools}
def nicedate(s):
    y,m,d = map(int, s.split("-")); return date(y,m,d).strftime("%-d %b %Y")
def in_cat(c): return [t for t in tools if c in t["categories"]]
def newest(): return sorted([t for t in tools if t.get("newRelease")], key=lambda t: t["dateAdded"], reverse=True)
def tags_lc(t): return {g.lower() for g in t.get("tags", [])}
def price_text(t):
    lab = PRICE_LABEL.get(t["pricing"], t["pricing"])
    note = t.get("pricingNote", "")
    return f"{lab} ({note})" if note and note != lab else lab
SPEND_CAVEAT = "Rough estimates from vendors' public pricing, checked 28 Oct 2026. Not exact — always check the vendor."
def money(v): return "Free" if v == 0 else f"${v:g}"
def spend_text(t):
    sp = t.get("spend")
    if not sp: return "Unknown"
    vals = [v for v in (sp["light"], sp["medium"], sp["heavy"]) if v is not None]
    lo, hi = min(vals), max(vals)
    if hi == 0: return "Free · est."
    r = money(lo) if lo == hi else f"{money(lo)}–{money(hi)}"
    return f"{r}/mo" + ("+" if sp["heavy"] is None else "") + " · est."
def spend_attr(t, k):
    sp = t.get("spend")
    return "" if not sp or sp.get(k) is None else f"{sp[k]:g}"
def spend_dd(t):
    sp = t.get("spend")
    if not sp: return "Unknown. Check the vendor's site for current pricing."
    f = lambda v: "not listed" if v is None else (money(v) if v == 0 else f"{money(v)}/mo")
    return (f'Light {f(sp["light"])} · Medium {f(sp["medium"])} · Heavy {f(sp["heavy"])} (est.)<br><small>{e(sp["basis"])}. {e(SPEND_CAVEAT)}</small>')
def clip(s, n=155):
    s = " ".join(s.split())
    if len(s) <= n: return s
    return s[:n-1].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
def tool_path(t): return f"/tool/{t['slug']}/"

# ---- outbound links (affiliate-aware) ----
def visit_link(t, label, where, cls="btn btn-primary"):
    """Visit link uses affiliateUrl || url. Affiliate links get rel=sponsored nofollow noopener and a visible note."""
    aff = (t.get("affiliateUrl") or "").strip()
    href, rel = (aff, "sponsored nofollow noopener") if aff else (t["url"], "noopener")
    c = f' class="{cls}"' if cls else ""
    a = (f'<a href="{e(href)}" target="_blank" rel="{rel}"{c} data-tool="{e(t["name"])}" data-goatcounter-click="out-{t["slug"]}" '
         f'data-goatcounter-title="Visit {e(t["name"])} ({where})" data-goatcounter-referrer="__GC_PAGE__">{label}</a>')
    if aff: a += ' <small class="affiliate-note" data-affiliate="1">Affiliate link</small>'
    return a

def card(t, show_date=False):
    cats = "|".join(c.lower() for c in t["categories"])
    pc = "paid" if t["pricing"]=="paid" else ("free" if t["pricing"]=="free" else "")
    badge = '\n    <span class="new-badge">New</span>' if t.get("newRelease") else ""
    if t.get("sponsored"): badge += '\n    <span class="sponsored-badge">Sponsored</span>'
    dt = f'\n  <p class="date-added">Added {nicedate(t["dateAdded"])}</p>' if show_date else ""
    tags = "".join(f'\n    <span class="tag category">{e(c)}</span>' for c in t["categories"])
    return f'''<div class="tool-card" data-tool="{t["slug"]}" data-name="{e(t["name"])}" data-description="{e(t["description"])}" data-categories="{e(cats)}" data-pricing="{e(t["pricing"])}" data-tags="{e(",".join(t.get("tags",[])))}" data-spend-light="{spend_attr(t,"light")}" data-spend-medium="{spend_attr(t,"medium")}" data-spend-heavy="{spend_attr(t,"heavy")}">
  <div class="tool-card-header">
    <h3><a href="{tool_path(t)}">{e(t["name"])}</a></h3>{badge}
  </div>
  <p class="description">{e(t["description"])}</p>{dt}
  <div class="meta">{tags}
    <span class="tag pricing {pc}">{e(t["pricing"])}</span>
  </div>
  <p class="spend-est" title="{e(SPEND_CAVEAT)}">Est. monthly spend: {e(spend_text(t))}</p>
  <div class="actions">
    {visit_link(t, "Visit →", "card")}
    <a href="{tool_path(t)}" class="btn btn-secondary">Details</a>
  </div>
</div>'''
def grid(ts, id_="", show_date=False):
    i = f' id="{id_}"' if id_ else ""
    return f'<div class="tools-grid"{i}>\n' + "\n".join(card(t, show_date) for t in ts) + "\n</div>"
SUBSCRIBE = f'''<section class="section"><div class="container"><div class="newsletter-section">
  <h2>📬 Stay Updated</h2><p>Get weekly updates on the latest AI tools for game devs and vibe coders</p>
  <div class="substack-embed-container"><iframe src="{SUB}/embed" width="100%" height="150" style="border:none; background:transparent;" frameborder="0" scrolling="no" title="Subscribe to the ToolDrop newsletter"></iframe></div>
  <p class="subscribe-fallback"><a href="{SUB}/subscribe" target="_blank" rel="noopener" class="btn btn-primary" data-goatcounter-click="subscribe-click" data-goatcounter-title="Subscribe on Substack" data-goatcounter-referrer="__GC_PAGE__">Subscribe on Substack →</a></p>
</div></div></section>'''

# ---- JSON-LD helpers ----
def ld(obj):
    obj = dict({"@context": "https://schema.org"}, **obj)
    s = json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{s}\n</script>'
def crumbs(trail):
    """trail: list of (name, path); first is Home. Returns (visible html, JSON-LD)."""
    vis = " › ".join((f'<a href="{p}">{e(n)}</a>' if i < len(trail)-1 else f'<span aria-current="page">{e(n)}</span>') for i,(n,p) in enumerate(trail))
    j = ld({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i+1, "name": n, "item": SITE + p} for i,(n,p) in enumerate(trail)]})
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb">{vis}</nav>', j
def itemlist(name, items):
    """items: list of (name, path)"""
    return ld({"@type": "ItemList", "name": name, "numberOfItems": len(items),
               "itemListElement": [{"@type": "ListItem", "position": i+1, "url": SITE + p, "name": n} for i,(n,p) in enumerate(items)]})
def tl(ts): return [(t["name"], tool_path(t)) for t in ts]

titles, descs, pages, lastmods = {}, {}, [], {}
def page(path, title, desc, body, jsonld="", lastmod=None, noindex=False):
    url = SITE + path
    assert len(desc) <= 160, (path, len(desc))
    if not noindex:
        assert title not in titles.values(), ("duplicate title", path, title)
        assert desc not in descs.values(), ("duplicate description", path, desc)
        titles[path], descs[path] = title, desc
    footer_cats = "".join(f'<li><a href="/category/{slug(c)}/">{e(c)}</a></li>' for c,_ in sorted(CATS))
    disc = f'<div class="disclosure-bar"><div class="container">{DISCLOSURE_LINE}</div></div>\n' if 'data-affiliate="1"' in body else ""
    robots = '\n  <meta name="robots" content="noindex">' if noindex else ""
    doc = f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">{robots}
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="ToolDrop">
  <meta property="og:locale" content="en_AU">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:site" content="@trytooldrop">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" type="text/plain" title="llms.txt" href="/llms.txt">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🛠️</text></svg>">
  <link rel="stylesheet" href="/css/style.css">
  <script data-goatcounter="https://tooldrop.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
{jsonld}
</head>
<body>
  <nav class="navbar"><div class="container">
    <a href="/" class="logo">🛠️ ToolDrop</a>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/new-releases/">New Releases</a>
      <a href="/compare/">Compare</a>
      <a href="{SUB}" target="_blank" rel="noopener" data-goatcounter-click="newsletter-click" data-goatcounter-title="Newsletter link" data-goatcounter-referrer="__GC_PAGE__">Newsletter</a>
      <a href="/about/">About</a>
    </div>
    <button class="mobile-menu-btn" aria-label="Toggle menu">☰</button>
  </div></nav>
  {disc}<main>
{body}
  </main>
  <footer class="footer"><div class="container">
    <div class="footer-content">
      <div class="footer-brand"><span class="logo">🛠️ ToolDrop</span><p>AI tools for vibe coders and indie game devs</p></div>
      <div class="footer-links"><h4>Categories</h4><ul>{footer_cats}</ul></div>
      <div class="footer-links"><h4>Pages</h4><ul><li><a href="/">Home</a></li><li><a href="/new-releases/">New Releases</a></li><li><a href="/compare/">Comparisons</a></li><li><a href="{SUB}" target="_blank" rel="noopener" data-goatcounter-click="newsletter-click" data-goatcounter-title="Newsletter link" data-goatcounter-referrer="__GC_PAGE__">Newsletter</a></li><li><a href="/about/">About</a></li><li><a href="/disclosure/">Disclosure</a></li><li><a href="{XURL}" target="_blank" rel="noopener">X / Twitter</a></li></ul></div>
      <div class="footer-newsletter"><h4>Newsletter</h4><p>Get weekly AI tool updates</p><a href="{SUB}/subscribe" target="_blank" rel="noopener" class="btn btn-primary" data-goatcounter-click="subscribe-click" data-goatcounter-title="Subscribe on Substack" data-goatcounter-referrer="__GC_PAGE__">Subscribe on Substack →</a></div>
    </div>
    <div class="footer-bottom"><p>&copy; 2026 ToolDrop. Built for the indie dev community. <a href="/disclosure/">Affiliate disclosure</a></p></div>
  </div></footer>
  <script src="/js/main.js"></script>
</body>
</html>
'''
    doc = doc.replace("__GC_PAGE__", url)
    f = os.path.join(OUT, path.lstrip("/")) if path.endswith(".html") else os.path.join(OUT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w").write(doc)
    if not noindex:
        pages.append(path); lastmods[path] = lastmod or TODAY

# ---- comparison pages (selection rules from the brief; facts come from tools.json) ----
def tagged(t, *names): return bool(tags_lc(t) & {n.lower() for n in names})
def has_free_way_in(t):
    return t["pricing"] == "free" or (t["pricing"] == "freemium" and re.search(r"\bfree\b|^open source", t.get("pricingNote",""), re.I))
def sel_pixel():
    ts = [t for t in tools if tagged(t, "pixel art", "sprites") or "Game Art & Sprites" in t["categories"]]
    return sorted(ts, key=lambda t: (not tagged(t, "pixel art"), not tagged(t, "sprites")))  # pixel art first; stable otherwise
def sel_audio():
    ts = [t for t in tools if "Audio, Music & SFX" in t["categories"] or tagged(t, "music", "SFX", "sound effects")]
    return sorted(ts, key=lambda t: "Audio, Music & SFX" not in t["categories"])
def sel_coding():
    return [t for t in tools if {"AI Coding Agents & IDEs", "App Builders"} & set(t["categories"])]
def sel_free():
    ts = [t for t in tools if has_free_way_in(t)]
    order = [c for c,_ in CATS]
    return sorted(ts, key=lambda t: (t["pricing"] != "free", order.index(t["categories"][0])))

def sel_3d():
    return [t for t in tools if "3D & Models" in t["categories"]]
def sel_voice():
    return [t for t in tools if "Voice" in t["categories"]]
def sel_video():
    return [t for t in tools if "Video & Trailers" in t["categories"]]

COMPARISONS = [
 dict(path="/compare/ai-pixel-art-tools/", h1="Best AI pixel art and sprite tools for indie game devs",
      title="Best AI Pixel Art & Sprite Tools for Game Devs | ToolDrop",
      desc="Compare AI pixel art, sprite and game art tools for indie devs: what each does, pricing and free tiers, side by side.",
      cats=["Game Art & Sprites"], select=sel_pixel,
      intro="""Need sprites, tiles or animation frames without spending weeks in an editor? These are the AI tools in the ToolDrop directory for game art, with pixel art first. Pixel Lab is built specifically for pixel art sprites, animations and game assets, and it has a free tier. Ludo.ai is a game asset suite that covers sprites and 2D assets alongside 3D, audio and video, with free credits to start and an Indie plan from $15/mo (billed annually). For broader game art, Leonardo AI (free tier, from $12/mo) and Scenario (free tier, with custom models for style consistency) target game assets directly. Stable Diffusion is open source and runs locally, so you can use pixel art fine-tunes at no cost. Midjourney (from $10/mo) and OpenAI's GPT Image 2.5 (pay as you go via the API) are general image generators that are good for concept art. Prices are as listed by each vendor, in USD, and can change, so check before you commit."""),
 dict(path="/compare/ai-game-music-sfx-tools/", h1="AI music and sound effects tools for games",
      title="AI Music & Sound Effects Tools for Games | ToolDrop",
      desc="Compare AI music, soundtrack and sound effects (SFX) generators for indie games: what each does, pricing and free tiers.",
      cats=["Audio, Music & SFX", "Voice"], select=sel_audio,
      intro="""A good soundtrack makes a small game feel finished. These tools from the ToolDrop directory generate music and audio you can use in your projects. Suno (free tier, Pro from $10/mo) and Udio (free tier) both create full tracks with vocals from a text prompt. Soundraw (from $16.99/mo) focuses on royalty-free background music trained only on in-house productions, which is handy if licensing worries you. For sound effects, Mirelo (free plan, Creator from €20/mo) generates footsteps, impacts, foley and ambience synced to your video, and Ludo.ai (free credits to start, Indie from $15/mo billed annually) includes audio in its game asset suite. ElevenLabs (free tier, from $5/mo) is best known for voice, but now does music generation too. Always check each tool's licence terms for commercial game releases."""),
 dict(path="/compare/ai-coding-agents-for-vibe-coding/", h1="AI coding agents and app builders for vibe coding",
      title="AI Coding Agents & App Builders for Vibe Coding | ToolDrop",
      desc="Compare AI coding agents, AI code editors and app builders for vibe coding: Cursor, Copilot, OpenCode, Replit, Bolt, v0, Lovable and more.",
      cats=["AI Coding Agents & IDEs", "App Builders"], select=sel_coding,
      intro="""Vibe coding means describing what you want and letting AI write the code. These are the coding agents, AI editors and app builders in the ToolDrop directory, side by side. If you want to stay in an editor, Cursor (free tier, Pro from $20/mo) and Zed (free, with Pro features) build AI into the IDE, and GitHub Copilot (from $10/mo) plugs into the editor you already use. OpenCode is an open-source coding agent that works in your terminal, desktop app or IDE, with free models included or your own provider's models. If you'd rather not touch a local setup, Replit and Bolt write, run and deploy code in the browser, Lovable builds full-stack web apps from plain-English descriptions, and v0 generates React components from text prompts. All four have a free tier. Claude and ChatGPT (both free tiers, $20/mo paid plans) are strong general coding assistants. Devin ($500/mo) is the autonomous end of the scale."""),
 dict(path="/compare/best-free-ai-tools-for-indie-devs/", h1="Best free AI tools for indie devs",
      title="Best Free AI Tools for Indie Devs | ToolDrop",
      desc="Free and free-tier AI tools for indie game devs and vibe coders, grouped by category: code, art, music, voice, 3D and more.",
      cats=[c for c,_ in CATS], select=sel_free, grouped=True,
      intro="""Shipping on a shoestring? Every tool on this page is either completely free or has a free tier, according to the ToolDrop directory. Most of the fully free picks are open source: OpenCode for coding in your terminal, Stable Diffusion for images run locally, plus LangChain, Haystack, Semantic Kernel and the Vercel AI SDK for building AI features into your own game or app. Epherem is free during early access and scans AI-built apps for security problems. After those come the freemium favourites, so you can try before you pay. They include Cursor and Replit for code, Pixel Lab and Leonardo AI for art, Suno and Udio for music, and ElevenLabs for voice. Free tiers change often, so check the limits on each tool's site."""),
 dict(path="/compare/ai-3d-model-generators-for-games/", h1="Best AI 3D model generators for indie game devs",
      title="Best AI 3D Model Generators for Indie Game Devs | ToolDrop",
      desc="Compare AI 3D model generators for games: text-to-3D and image-to-3D tools, what each does, pricing and free tiers, side by side.",
      cats=["3D & Models"], select=sel_3d,
      intro="""Need props, characters or environments for your game without modelling every one by hand? These are the AI 3D tools in the ToolDrop directory. Meshy (free tier, Pro from $20/mo) and Tripo AI (free tier) turn text prompts or images into 3D models. Meshy outputs textured, print-ready models, and Tripo AI offers an API. Kaedim (from $15/mo) converts 2D images into production-ready 3D models for games. Thrixel generates structured assets with labelled parts and works from coding agents like Claude Code, Codex and Cursor as well as the browser, though its pricing isn't published. Ludo.ai (free credits to start, Indie from $15/mo billed annually) covers 3D models alongside sprites, audio and video. Spline AI (free tier, Pro from $7/mo) is a 3D design tool aimed at interactive web experiences, and Luma AI (free tier) does photorealistic video, image and 3D generation. Prices are as listed by each vendor, in USD, and can change, so check before you commit."""),
 dict(path="/compare/ai-voice-generators-for-games/", h1="Best AI voice generators for game characters and voiceover",
      title="Best AI Voice Generators for Games & Voiceover | ToolDrop",
      desc="Compare AI voice generators for game characters, narration and trailers: text-to-speech, voice cloning, pricing and free tiers.",
      cats=["Voice"], select=sel_voice,
      intro="""Need voices for characters, narration or a trailer? These are the AI voice tools in the ToolDrop directory. ElevenLabs (free tier, from $5/mo) is the best-known option for realistic speech and voice cloning, and it does music too. Fish Audio (free tier, Plus from $11/mo billed annually) focuses on expressive text-to-speech with emotion tags. Murf AI (free tier, from $19/mo) is built for studio-quality voiceovers in multiple languages and has a text-to-speech API. Inworld AI (pay-as-you-go) offers realtime text-to-speech, speech-to-text and speech-to-speech models for apps that need live voice. Resemble AI (contact for pricing) is aimed at enterprises, with voice cloning plus deepfake detection and voice watermarking. Mistral Voxtral 3 (usage-based API, $13 per 1M characters for Voxtral TTS 3) adds voice cloning with emotion and pace tags plus a real-time voice agent SDK. Phonon is Gradium's open-weight text-to-speech, small enough to run offline on phones, laptops and browsers; its 31m English model is Apache-2.0, while the larger and multilingual models are non-commercial unless licensed. Check each tool's licence and voice-cloning consent rules before you ship voices in a commercial release."""),
 dict(path="/compare/ai-video-trailer-tools-for-games/", h1="Best AI video and trailer tools for indie game devs",
      title="Best AI Video & Trailer Tools for Indie Game Devs | ToolDrop",
      desc="Compare AI video generators and editors for game trailers, devlogs and store page videos: what each does, pricing and free tiers.",
      cats=["Video & Trailers"], select=sel_video,
      intro="""A short trailer or devlog clip does a lot of work on a Steam page or social feed. These are the AI video tools in the ToolDrop directory. Runway (free tier, from $15/mo), Pika (free tier) and Kling AI (free Basic plan with watermarked exports, paid credit plans) generate video clips from text and images, and Kling 4.0 makes native 30-second clips with keyframes, sound effects and lip sync. Luma AI (free tier) does photorealistic video alongside image and 3D generation. Descript (free tier, from $15/mo) edits video by editing the transcript, which is handy for devlogs. Framefields is open source (Apache-2.0) and lets coding agents write motion graphics in TypeScript and render MP4s. HeyGen (free tier, from $29/mo) and Synthesia (from $30/mo) make AI avatar presenter videos, which suit explainers more than gameplay trailers. Prices are as listed by each vendor, in USD, and can change, so check before you commit."""),
]

def names_list(ts):
    links = [f'<a href="{tool_path(t)}">{e(t["name"])}</a>' for t in ts]
    return links[0] if len(links) == 1 else ", ".join(links[:-1]) + " and " + links[-1]
def how_to_choose(ts):
    rules = [
        ("Completely free", lambda t: t["pricing"] == "free", "Listed as free in our data (pricing note: open source, self-hosted or early access)."),
        ("Free tier or free credits, paid upgrades", lambda t: t["pricing"] == "freemium" and has_free_way_in(t), "Try before you pay; check each tool's limits."),
        ("Paid only", lambda t: t["pricing"] == "paid", "No free tier listed in our data."),
        ("Pricing not published", lambda t: t["pricing"] == "unknown" or "not published" in t.get("pricingNote","").lower(), "Check the vendor's site for current pricing."),
        ("Open source", lambda t: tagged(t, "open source") or t.get("pricingNote","").lower().startswith("open source"), "Tagged or listed as open source."),
        ("Runs locally", lambda t: tagged(t, "local", "self-hosted") or "self-hosted" in t.get("pricingNote","").lower(), "Tagged as local or self-hosted."),
        ("In the browser", lambda t: any("browser" in g for g in tags_lc(t)), "Tagged as browser-based."),
        ("In the terminal", lambda t: tagged(t, "terminal"), "Tagged as a terminal tool."),
        ("API or MCP access", lambda t: tagged(t, "API", "MCP"), "Tagged with API or MCP, handy if you want to drive it from code or a coding agent."),
    ]
    items = []
    for label, fn, note in rules:
        m = [t for t in ts if fn(t)]
        if m and len(m) < len(ts) or (m and label.startswith("Completely")):
            items.append(f"<li><strong>{label}:</strong> {names_list(m)}. <span class=\"muted\">{note}</span></li>")
    return "<ul class=\"choose-list\">" + "\n".join(items) + "</ul>"
def compare_table(ts):
    rows = "".join(f'''<tr><td><a href="{tool_path(t)}">{e(t["name"])}</a></td><td>{e(t["description"])}</td><td>{e(price_text(t))}</td><td>{" · ".join(f'<a href="/category/{slug(c)}/">{e(c)}</a>' for c in t["categories"])}</td><td>{visit_link(t, "Visit →", "compare table", cls="")}</td></tr>\n''' for t in ts)
    return f'''<div class="table-wrap"><table class="compare-table"><thead><tr><th scope="col">Tool</th><th scope="col">What it does</th><th scope="col">Pricing</th><th scope="col">Categories</th><th scope="col">Link</th></tr></thead>
<tbody>
{rows}</tbody></table></div>'''
def comparisons_for_cat(c): return [cp for cp in COMPARISONS if c in cp["cats"] and not cp.get("grouped")]
def compare_links(cps):
    if not cps: return ""
    return '<p class="compare-links">Compare: ' + " · ".join(f'<a href="{cp["path"]}">{e(cp["h1"])}</a>' for cp in cps) + "</p>"

# ================= build =================
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree("static", OUT)
# Home
pills = "".join(f'<button class="filter-pill" data-filter-type="category" data-filter-value="{e(c.lower())}">{i} {e(c)}</button>' for c,i in CATS)
catcards = "".join(f'<div class="category-card"><div class="icon">{i}</div><h3><a href="/category/{slug(c)}/">{e(c)}</a></h3><p class="count">{len(in_cat(c))} tools</p></div>' for c,i in CATS)
cmpcards = "".join(f'<div class="category-card"><div class="icon">⚖️</div><h3><a href="{cp["path"]}">{e(cp["h1"])}</a></h3><p class="count">{len(cp["select"]())} tools compared</p></div>' for cp in COMPARISONS)
home = f'''<section class="hero"><div class="container">
  <h1>AI Tools for Creators</h1>
  <p class="subtitle">Discover the best AI tools for vibe coders and indie game devs. From coding agents to art generators, find everything you need to build.</p>
  <form class="search-container" role="search" action="/" method="get" onsubmit="return false"><span class="search-icon">🔍</span><input type="search" name="q" id="tool-search" class="search-box" placeholder="Search tools by name, category, or feature..." aria-label="Search tools"></form>
</div></section>
<section class="section"><div class="container"><div class="filter-section">
  <div class="filter-group"><span class="filter-label">Filter by category:</span><div class="filter-pills"><button class="filter-pill active" data-filter-type="category" data-filter-value="all">All</button>{pills}</div></div>
  <div class="filter-group"><span class="filter-label">Filter by pricing:</span><div class="filter-pills"><button class="filter-pill active" data-filter-type="pricing" data-filter-value="all">All</button><button class="filter-pill" data-filter-type="pricing" data-filter-value="free">Free</button><button class="filter-pill" data-filter-type="pricing" data-filter-value="freemium">Freemium</button><button class="filter-pill" data-filter-type="pricing" data-filter-value="paid">Paid</button></div></div>
  <div class="filter-group"><span class="filter-label">Est. monthly spend — my usage:</span><div class="filter-pills"><button class="filter-pill" data-filter-type="usage" data-filter-value="light">Light</button><button class="filter-pill active" data-filter-type="usage" data-filter-value="medium">Medium</button><button class="filter-pill" data-filter-type="usage" data-filter-value="heavy">Heavy</button></div></div>
  <div class="filter-group"><span class="filter-label">Budget:</span><div class="filter-pills"><button class="filter-pill active" data-filter-type="budget" data-filter-value="any">Any</button><button class="filter-pill" data-filter-type="budget" data-filter-value="0">Free</button><button class="filter-pill" data-filter-type="budget" data-filter-value="10">Under $10</button><button class="filter-pill" data-filter-type="budget" data-filter-value="25">Under $25</button><button class="filter-pill" data-filter-type="budget" data-filter-value="50">Under $50</button></div></div>
  <p class="spend-caveat">Light = hobby or occasional use, Medium = a regular solo dev, Heavy = daily heavy use. {e(SPEND_CAVEAT)} Tools with unknown pricing are hidden when a budget is picked.</p>
</div></div></section>
<section class="section browse"><div class="container"><div class="section-header"><h2 class="section-title">🔥 Latest Releases</h2><a href="/new-releases/" class="section-link">View all →</a></div>
{grid(newest()[:6])}
</div></section>
<section class="section browse"><div class="container"><div class="section-header"><h2 class="section-title">📂 Browse by Category</h2></div><div class="categories-grid">{catcards}</div></div></section>
<section class="section browse"><div class="container"><div class="section-header"><h2 class="section-title">⚖️ Compare Tools</h2><a href="/compare/" class="section-link">All comparisons →</a></div><div class="categories-grid">{cmpcards}</div></div></section>
<section class="section browse"><div class="container"><div class="section-header"><h2 class="section-title">⭐ Featured Tools</h2></div>
{grid([t for t in tools if t.get("featured")])}
</div></section>
<section class="section"><div class="container"><div class="section-header"><h2 class="section-title">🛠️ All Tools <span class="count-pill">{len(tools)}</span></h2></div>
{grid(tools, "filtered-tools")}
<div id="no-results" class="no-results" style="display: none;"><h3>No tools found</h3><p>Try adjusting your search or filters</p></div>
</div></section>
{SUBSCRIBE}'''
home_ld = ld({"@type": "WebSite", "name": "ToolDrop", "url": SITE + "/", "inLanguage": "en-AU",
              "description": "A directory of AI tools for vibe coders and indie game devs, organised by use case, with a weekly newsletter.",
              "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": SITE + "/?q={search_term_string}"},
                                  "query-input": "required name=search_term_string"}}) + "\n" + \
          ld({"@type": "Organization", "name": "ToolDrop", "url": SITE + "/", "sameAs": [XURL, SUB]})
page("/", "AI Tools for Vibe Coders & Indie Game Devs | ToolDrop", "Discover the best AI tools for indie game development and vibe coding. Find AI coding agents, art generators, music tools, voice synthesis, and more.", home, home_ld)

# Categories
SPEND_FILTER = home[home.index('  <div class="filter-group"><span class="filter-label">Est. monthly'):home.index('</p>\n</div>', home.index('spend-caveat'))+4]
SPEND_FILTER = f'<div class="filter-section">{SPEND_FILTER}</div>'
for c,i in CATS:
    ts = in_cat(c)
    path = f"/category/{slug(c)}/"
    bc, bcld = crumbs([("Home", "/"), (c, path)])
    body = f'''<section class="hero hero-small"><div class="container">{bc}<h1>{i} {e(c)}</h1><p class="subtitle">{len(ts)} AI tools for {e(c.lower())}, picked for vibe coders and indie game devs.</p>{compare_links(comparisons_for_cat(c))}</div></section>
<section class="section"><div class="container">{SPEND_FILTER}{grid(ts, "filtered-tools")}<div id="no-results" class="no-results" style="display: none;"><h3>No tools found</h3><p>Try a bigger budget or a lighter usage level</p></div></div></section>{SUBSCRIBE}'''
    title = f"Best AI Tools for {c} | ToolDrop"
    if len(title) > 60: title = f"AI Tools for {c} | ToolDrop"
    names = ", ".join(t["name"] for t in ts[:4])
    page(path, title, clip(f"{len(ts)} AI tools for {c.lower()} for indie game devs and vibe coders, incl. {names}. Compare pricing and free tiers."),
         body, bcld + "\n" + itemlist(f"AI tools for {c}", tl(ts)), max(t["dateAdded"] for t in ts))

# New releases
nr = newest()
bc, bcld = crumbs([("Home", "/"), ("New Releases", "/new-releases/")])
page("/new-releases/", "New AI Tool Releases | ToolDrop", "The latest AI tools added to ToolDrop for vibe coders and indie game devs, newest first.",
     f'''<section class="hero hero-small"><div class="container">{bc}<h1>🔥 New Releases</h1><p class="subtitle">The newest AI tools for vibe coders and indie game devs, most recent first.</p></div></section>
<section class="section"><div class="container">{grid(nr, show_date=True)}</div></section>{SUBSCRIBE}''',
     bcld + "\n" + itemlist("New AI tool releases", tl(nr)), max(t["dateAdded"] for t in nr))

# Tool pages
def similar(t):
    scored = []
    for x in tools:
        if x is t: continue
        sc, st = len(set(x["categories"]) & set(t["categories"])), len(tags_lc(x) & tags_lc(t))
        if sc or st: scored.append((-sc, -st, x["name"].lower(), x))
    return [s[-1] for s in sorted(scored, key=lambda s: s[:3])][:4]   # never ranked by affiliate status
for t in tools:
    path = tool_path(t)
    c0 = t["categories"][0]
    cats = " · ".join(f'<a href="/category/{slug(c)}/">{e(c)}</a>' for c in t["categories"])
    sim = similar(t)
    assert 1 <= len(sim) <= 4, t["name"]
    tags = "".join(f'<span class="tag">{e(g)}</span>' for g in t.get("tags", []))
    bc, bcld = crumbs([("Home", "/"), (c0, f"/category/{slug(c0)}/"), (t["name"], path)])
    in_cmp = [cp for cp in COMPARISONS if t in cp["select"]()]
    sw = {"@type": "SoftwareApplication", "name": t["name"], "url": t["url"], "description": t["description"],
          "applicationCategory": APPCAT.get(c0, "BusinessApplication")}
    if any("browser" in g for g in tags_lc(t)): sw["operatingSystem"] = "Web"
    if t["pricing"] == "free": sw["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
    if t.get("spend"):
        sw["additionalProperty"] = {"@type": "PropertyValue", "name": "Estimated monthly spend (USD, rough estimate)", "value": spend_text(t),
                                    "description": f'Light {t["spend"]["light"]}, medium {t["spend"]["medium"]}, heavy {t["spend"]["heavy"] if t["spend"]["heavy"] is not None else "not listed"} USD/mo. {t["spend"]["basis"]}. {SPEND_CAVEAT}'}
    if t.get("tags"): sw["keywords"] = ", ".join(t["tags"])
    sponsored = ' <span class="sponsored-badge">Sponsored</span>' if t.get("sponsored") else ""
    body = f'''<section class="hero hero-small"><div class="container">{bc}
<h1>{e(t["name"])}{' <span class="new-badge">New</span>' if t.get("newRelease") else ""}{sponsored}</h1><p class="subtitle">{e(t["description"])}</p>
<p>{visit_link(t, f"Visit {e(t['name'])} →", "tool page button")}</p></div></section>
<section class="section"><div class="container"><div class="tool-details">
<dl><dt>Categories</dt><dd>{cats}</dd><dt>Pricing</dt><dd><span class="tag pricing">{e(PRICE_LABEL.get(t["pricing"], t["pricing"]))}</span> {e(t.get("pricingNote",""))}</dd><dt>Est. monthly spend</dt><dd>{spend_dd(t)}</dd><dt>Website</dt><dd>{visit_link(t, e(t["url"]), "tool page link", cls="")}</dd><dt>Added</dt><dd>{nicedate(t["dateAdded"])}</dd></dl>
<div class="tags">{tags}</div>{compare_links(in_cmp)}</div></div></section>
<section class="section"><div class="container"><div class="section-header"><h2 class="section-title">Similar tools</h2></div>{grid(sim)}</div></section>{SUBSCRIBE}'''
    title = f"{t['name']}: {c0} AI Tool | ToolDrop"
    if len(title) > 60: title = f"{t['name']}: AI Tool for {c0.split(' & ')[0].split(',')[0]} | ToolDrop"
    if len(title) > 60: title = f"{t['name']} | AI Tool | ToolDrop"
    page(path, title, clip(f"{t['name']}: {t['description']}"), body, ld(sw) + "\n" + bcld, t["dateAdded"])

# Comparison pages
for cp in COMPARISONS:
    ts = cp["select"]()
    assert ts, cp["path"]
    bc, bcld = crumbs([("Home", "/"), ("Compare", "/compare/"), (cp["h1"], cp["path"])])
    if cp.get("grouped"):
        sections = []
        for kind, lab in (("free", "Completely free"), ("freemium", "Free tier or free credits")):
            sub = [t for t in ts if t["pricing"] == kind]
            for c,i in CATS:
                g = [t for t in sub if t["categories"][0] == c]
                if g: sections.append(f'<h3>{lab}: {i} {e(c)}</h3>\n{compare_table(g)}')
        tables = "\n".join(sections)
    else:
        tables = compare_table(ts)
    rel_cats = " · ".join(f'<a href="/category/{slug(c)}/">{e(c)}</a>' for c in cp["cats"])
    body = f'''<section class="hero hero-small"><div class="container">{bc}<h1>{e(cp["h1"])}</h1></div></section>
<section class="section"><div class="container prose prose-wide"><p>{e(cp["intro"])}</p>
<p class="muted">Prices and details come from the ToolDrop directory and are as listed by each vendor. They can change, so check each tool's site.</p></div></section>
<section class="section"><div class="container"><h2 class="section-title">Side by side <span class="count-pill">{len(ts)} tools</span></h2>
{tables}</div></section>
<section class="section"><div class="container prose prose-wide"><h2 class="section-title">How to choose</h2>
{how_to_choose(ts)}
<p>Related categories: {rel_cats}</p></div></section>{SUBSCRIBE}'''
    page(cp["path"], cp["title"], cp["desc"], body, itemlist(cp["h1"], tl(ts)) + "\n" + bcld, max(t["dateAdded"] for t in ts))

# Compare hub
bc, bcld = crumbs([("Home", "/"), ("Compare", "/compare/")])
page("/compare/", "Compare AI Tools for Game Devs & Vibe Coders | ToolDrop", "Side-by-side comparisons of AI tools for indie game devs and vibe coders: pixel art, music and SFX, coding agents and free tools.",
     f'''<section class="hero hero-small"><div class="container">{bc}<h1>⚖️ Compare AI tools</h1><p class="subtitle">Side-by-side tables built from the ToolDrop directory, with pricing and what each tool does.</p></div></section>
<section class="section"><div class="container"><div class="categories-grid">{cmpcards}</div></div></section>{SUBSCRIBE}''',
     bcld + "\n" + itemlist("ToolDrop comparisons", [(cp["h1"], cp["path"]) for cp in COMPARISONS]))

# Disclosure
bc, bcld = crumbs([("Home", "/"), ("Disclosure", "/disclosure/")])
page("/disclosure/", "Affiliate Disclosure | ToolDrop", "How ToolDrop handles affiliate links, paid placements and sponsored newsletter issues.",
     f'''<section class="hero hero-small"><div class="container">{bc}<h1>Affiliate disclosure</h1></div></section>
<section class="section"><div class="container prose">
<p><strong>Affiliate disclosure</strong><br>Some links on ToolDrop are affiliate links. If you sign up through them we may earn a commission at no extra cost to you. It never affects which tools we list or how we rank them.</p>
<p><strong>Paid placements:</strong> any paid listing is clearly labelled "Featured (paid)" or "Sponsored" on the card.</p>
<p><strong>Newsletter:</strong> sponsored issues say "This issue is sponsored by …" at the top of the slot.</p>
<p>Questions? Reach us on X at <a href="{XURL}" target="_blank" rel="noopener">@trytooldrop</a>.</p>
</div></section>''', bcld)

# About
bc, bcld = crumbs([("Home", "/"), ("About", "/about/")])
page("/about/", "About ToolDrop", "ToolDrop is a directory and weekly newsletter of AI tools for vibe coders and indie game devs.",
     f'''<section class="hero hero-small"><div class="container">{bc}<h1>About ToolDrop</h1><p class="subtitle">A directory of AI tools for vibe coders and indie game devs, sorted by the job you need done.</p></div></section>
<section class="section"><div class="container prose"><p>A new AI tool seems to launch every hour. ToolDrop cuts through the noise with a curated list of {len(tools)} tools across coding agents, app builders, code review, game art, 3D, audio, voice, narrative, trailers, store-page copy and agent frameworks.</p>
<p>Every week the <a href="{SUB}" target="_blank" rel="noopener" data-goatcounter-click="newsletter-click" data-goatcounter-title="Newsletter link" data-goatcounter-referrer="__GC_PAGE__">ToolDrop newsletter</a> brings you the short version: the best new releases and practical tips. You can also follow <a href="{XURL}" target="_blank" rel="noopener">@trytooldrop on X</a>.</p>
<p>Some links may be affiliate links; see our <a href="/disclosure/">disclosure</a>.</p></div></section>{SUBSCRIBE}''', bcld)

# 404
page("/404.html", "Page not found | ToolDrop", "Page not found.", '<section class="hero"><div class="container"><h1>Page not found</h1><p class="subtitle">That page doesn\'t exist. <a href="/">Browse all tools →</a> or <a href="/compare/">see our comparisons</a>.</p></div></section>', noindex=True)

# llms.txt / llms-full.txt
L = ["# ToolDrop", "", "> ToolDrop is an AI tools directory for vibe coders and indie game devs, organised by use case (coding agents, app builders, game art, 3D, audio, voice, video and more), with a weekly newsletter.", "",
     f"The directory lists {len(tools)} tools. Pricing is as published by each vendor and can change. Tool pages link to each tool's official site.", "", f"Est. monthly spend figures are {SPEND_CAVEAT[0].lower()+SPEND_CAVEAT[1:]}", ""]
for c,_ in CATS:
    L += [f"## {c}", ""] + [f"- [{t['name']}]({SITE}{tool_path(t)}): {t['description']} Pricing: {price_text(t)}. Est. monthly spend: {spend_text(t).replace(" · est.", " (est.)")}" for t in in_cat(c)] + [""]
L += ["## Comparisons", ""] + [f"- [{cp['h1']}]({SITE}{cp['path']}): {cp['desc']}" for cp in COMPARISONS] + [""]
L += ["## More", "", f"- [New releases]({SITE}/new-releases/): the newest tools added to the directory.",
      f"- [Newsletter]({SUB}): weekly ToolDrop newsletter on Substack.", f"- [Affiliate disclosure]({SITE}/disclosure/): how affiliate links and sponsorships are handled.",
      f"- [Full tool data]({SITE}/llms-full.txt): every tool with all fields.", ""]
open(f"{OUT}/llms.txt", "w").write("\n".join(L))
F = ["# ToolDrop: full tool list", "", f"> Every tool in the ToolDrop directory ({len(tools)} tools), with all fields, grouped by category. Generated {TODAY} from tools.json. Tools in more than one category appear under each.", "",
     f"Site: {SITE}/  ", f"Newsletter: {SUB}  ", f"Disclosure: {SITE}/disclosure/", ""]
for c,_ in CATS:
    F += [f"## {c}", ""]
    for t in in_cat(c):
        F += [f"### {t['name']}", "", f"- Official URL: {t['url']}", f"- ToolDrop page: {SITE}{tool_path(t)}", f"- Description: {t['description']}",
              f"- Categories: {', '.join(t['categories'])}", f"- Pricing: {PRICE_LABEL.get(t['pricing'], t['pricing'])}" + (f" ({t['pricingNote']})" if t.get('pricingNote') else ""),
              f"- Est. monthly spend (USD, rough estimate): " + (f"light {t['spend']['light']}, medium {t['spend']['medium']}, heavy {t['spend']['heavy'] if t['spend']['heavy'] is not None else 'not listed'} ({t['spend']['basis']}; checked {t['spend']['checked']})" if t.get('spend') else "unknown"),
              f"- Tags: {', '.join(t.get('tags', []))}", f"- Date added: {t['dateAdded']}"]
        if t.get("newRelease"): F.append("- New release: yes")
        F.append("")
open(f"{OUT}/llms-full.txt", "w").write("\n".join(F))

# sitemap, robots, headers
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
     "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{lastmods[p]}</lastmod></url>\n" for p in pages) + "</urlset>\n")
bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot"]
open(f"{OUT}/robots.txt","w").write("# AI crawlers are welcome\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
open(f"{OUT}/_headers","w").write("/llms.txt\n  Content-Type: text/plain; charset=utf-8\n/llms-full.txt\n  Content-Type: text/plain; charset=utf-8\n")
print(f"Built {len(pages)} pages, {len(tools)} tools -> {OUT}/ (SITE_URL={SITE})")
