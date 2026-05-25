# -*- coding: utf-8 -*-
"""
build_web.py — Generates a fully self-contained, offline, dark-premium web
version of the "12 Déclencheurs de Contenu Viral" lead magnet by Loïc Bourget.

Each reel is rendered as an inline HTML5 <video> player (poster + controls).
Zero external CDN, zero analytics, zero tracking. Self-hosted fonts.

Usage:
    python build_web.py content.json index-expert.html
    python build_web.py content_createur.json index-createur.html
    python build_web.py content_accessible.json index-accessible.html

Or with no args, builds all three at once:
    python build_web.py
"""

import json
import sys
import os
import re
import html


# --------------------------------------------------------------------------
# Path normalization
# --------------------------------------------------------------------------
# The JSON authoring paths point at "assets/reels/reelN.mp4" / "assets/thumbs/reelN.jpg"
# but the real bundle layout is "videos/reelN.mp4" / "thumbs/reelN.jpg".
# We normalize by extracting the basename and prefixing the real directory.

def norm_video(path):
    base = os.path.basename(path)
    return "videos/" + base


def norm_thumb(path):
    base = os.path.basename(path)
    return "thumbs/" + base


def esc(text):
    """HTML-escape a plain string."""
    return html.escape(str(text), quote=True)


def esc_attr(text):
    """HTML-escape for attribute context."""
    return html.escape(str(text), quote=True)


# --------------------------------------------------------------------------
# CSS (inlined, self-contained, mobile-first)
# --------------------------------------------------------------------------

CSS = r"""
@font-face {
  font-family: 'Space Grotesk';
  src: url('fonts/SpaceGrotesk-500.woff2') format('woff2');
  font-weight: 500; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Space Grotesk';
  src: url('fonts/SpaceGrotesk-700.woff2') format('woff2');
  font-weight: 700; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Manrope';
  src: url('fonts/Manrope-400.woff2') format('woff2');
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Manrope';
  src: url('fonts/Manrope-500.woff2') format('woff2');
  font-weight: 500; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Manrope';
  src: url('fonts/Manrope-600.woff2') format('woff2');
  font-weight: 600; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Manrope';
  src: url('fonts/Manrope-700.woff2') format('woff2');
  font-weight: 700; font-style: normal; font-display: swap;
}

:root {
  --bg: #0A0A0A;
  --bg-soft: #111111;
  --surface: rgba(255, 255, 255, 0.035);
  --surface-2: rgba(255, 255, 255, 0.05);
  --ring: rgba(255, 255, 255, 0.08);
  --ring-soft: rgba(255, 255, 255, 0.06);
  --amber: #F59E0B;
  --amber-soft: rgba(245, 158, 11, 0.12);
  --amber-ring: rgba(245, 158, 11, 0.22);
  --text: #F4F4F5;
  --text-dim: #A1A1AA;
  --text-faint: #71717A;
  --heading: 'Space Grotesk', system-ui, -apple-system, sans-serif;
  --body: 'Manrope', system-ui, -apple-system, sans-serif;
  --radius: 14px;
  --radius-sm: 10px;
  --maxw: 1080px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--body);
  font-weight: 400;
  font-size: 16px;
  line-height: 1.7;
  letter-spacing: -0.003em;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  overflow-x: hidden;
}

/* Subtle amber glow at top — not a gradient bg, a single soft radial halo */
body::before {
  content: '';
  position: fixed;
  top: -30vh; left: 50%;
  transform: translateX(-50%);
  width: 140vw; height: 90vh;
  background: radial-gradient(ellipse 50% 50% at 50% 50%, rgba(245,158,11,0.10), transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.wrap {
  position: relative;
  z-index: 1;
  max-width: var(--maxw);
  margin: 0 auto;
  padding: 0 22px;
}

/* ---- Eyebrow (mono uppercase) ---- */
.eyebrow {
  font-family: var(--heading);
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--amber);
  display: inline-flex;
  align-items: center;
  gap: 9px;
}
.eyebrow::before {
  content: '';
  width: 22px; height: 1px;
  background: var(--amber);
  opacity: 0.7;
}

/* ---- HERO ---- */
.hero {
  padding: 92px 0 60px;
  border-bottom: 1px solid var(--ring-soft);
}
.hero .eyebrow { margin-bottom: 26px; }
.hero h1 {
  font-family: var(--heading);
  font-weight: 700;
  font-size: clamp(2.3rem, 8vw, 4.4rem);
  line-height: 1.02;
  letter-spacing: -0.035em;
  max-width: 14ch;
}
.hero h1 .accent { color: var(--amber); }
.hero .byline {
  margin-top: 28px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-family: var(--heading);
  font-weight: 500;
  font-size: 15px;
  color: var(--text-dim);
  padding: 9px 16px;
  background: var(--surface);
  border: 1px solid var(--ring);
  border-radius: 100px;
}
.hero .byline .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 12px rgba(245,158,11,0.7);
}

/* ---- INTRO ---- */
.intro { padding: 60px 0; }
.intro .lead {
  font-size: clamp(1.05rem, 2.4vw, 1.3rem);
  line-height: 1.65;
  color: var(--text);
  font-weight: 500;
  max-width: 62ch;
}
.intro .lead strong { color: var(--amber); font-weight: 700; }
.howto {
  margin-top: 34px;
  background: var(--surface);
  border: 1px solid var(--ring);
  border-radius: var(--radius);
  padding: 26px 28px;
  max-width: 64ch;
}
.howto .eyebrow { margin-bottom: 14px; }
.howto p { color: var(--text-dim); font-size: 15.5px; line-height: 1.7; }

/* ---- TRIGGERS ---- */
.triggers-head {
  padding: 50px 0 8px;
}
.triggers-head .eyebrow { margin-bottom: 14px; }
.triggers-head h2 {
  font-family: var(--heading);
  font-weight: 700;
  font-size: clamp(1.7rem, 5vw, 2.6rem);
  letter-spacing: -0.03em;
  line-height: 1.08;
}

.trigger {
  padding: 48px 0;
  border-top: 1px solid var(--ring-soft);
}

.trigger-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
  align-items: start;
}

/* The video column */
.reel {
  position: relative;
  width: 100%;
  max-width: 340px;
  margin: 0 auto;
}
.reel-frame {
  position: relative;
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-soft);
  border: 1px solid var(--ring);
  box-shadow: 0 24px 60px -28px rgba(0,0,0,0.9), 0 0 0 1px rgba(245,158,11,0.04);
}
.reel-frame video {
  display: block;
  width: 100%;
  aspect-ratio: 9 / 16;
  max-height: 72vh;
  object-fit: cover;
  background: #000;
  border-radius: var(--radius);
}
.reel-meta {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-family: var(--heading);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--text-faint);
  text-transform: uppercase;
}
.reel-meta .reel-link {
  color: var(--text-dim);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: color 0.18s ease;
}
.reel-meta .reel-link:hover { color: var(--amber); }
.reel-meta .reel-link svg { width: 13px; height: 13px; }
.reel-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 100px;
  background: var(--amber-soft);
  border: 1px solid var(--amber-ring);
  color: var(--amber);
}

/* The text column */
.trigger-body { min-width: 0; }
.trigger-num {
  font-family: var(--heading);
  font-weight: 700;
  font-size: clamp(2.4rem, 7vw, 3.4rem);
  line-height: 1;
  letter-spacing: -0.04em;
  color: var(--amber);
  display: block;
  margin-bottom: 6px;
}
.trigger-num .of { color: var(--text-faint); font-size: 0.45em; letter-spacing: 0.05em; }
.trigger-name {
  font-family: var(--heading);
  font-weight: 700;
  font-size: clamp(1.4rem, 4vw, 2rem);
  line-height: 1.12;
  letter-spacing: -0.025em;
  margin-bottom: 18px;
}
.trigger-principe {
  font-size: 16.5px;
  line-height: 1.7;
  color: var(--text);
  font-weight: 500;
  margin-bottom: 26px;
}
.block-label {
  font-family: var(--heading);
  font-weight: 500;
  font-size: 11.5px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-faint);
  margin-bottom: 10px;
  display: block;
}
.trigger-pourquoi {
  font-size: 15px;
  line-height: 1.74;
  color: var(--text-dim);
  margin-bottom: 26px;
}

/* The "loi" amber pull-quote */
.loi {
  position: relative;
  margin: 0 0 26px;
  padding: 20px 24px;
  background: var(--amber-soft);
  border-radius: var(--radius-sm);
  border: 1px solid var(--amber-ring);
}
.loi::before {
  content: '';
  position: absolute;
  left: 0; top: 14px; bottom: 14px;
  width: 3px;
  background: var(--amber);
  border-radius: 3px;
}
.loi .loi-label {
  font-family: var(--heading);
  font-weight: 500;
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--amber);
  display: block;
  margin-bottom: 7px;
  padding-left: 12px;
}
.loi p {
  font-family: var(--heading);
  font-weight: 500;
  font-size: 17px;
  line-height: 1.4;
  color: var(--text);
  letter-spacing: -0.01em;
  padding-left: 12px;
}

/* Appliquer list */
.appliquer { list-style: none; display: grid; gap: 12px; }
.appliquer li {
  position: relative;
  padding: 14px 16px 14px 46px;
  background: var(--surface);
  border: 1px solid var(--ring-soft);
  border-radius: var(--radius-sm);
  font-size: 14.5px;
  line-height: 1.62;
  color: var(--text-dim);
}
.appliquer li .idx {
  position: absolute;
  left: 14px; top: 13px;
  width: 22px; height: 22px;
  border-radius: 7px;
  background: var(--amber-soft);
  border: 1px solid var(--amber-ring);
  color: var(--amber);
  font-family: var(--heading);
  font-weight: 700;
  font-size: 12px;
  display: flex; align-items: center; justify-content: center;
}

/* ---- CHEATSHEET ---- */
.cheatsheet {
  margin: 60px 0;
  padding: 44px 0 8px;
  border-top: 1px solid var(--ring-soft);
}
.cheatsheet .eyebrow { margin-bottom: 14px; }
.cheatsheet h2 {
  font-family: var(--heading);
  font-weight: 700;
  font-size: clamp(1.6rem, 5vw, 2.4rem);
  letter-spacing: -0.03em;
  margin-bottom: 28px;
}
.cheat-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.cheat-item {
  background: var(--surface);
  border: 1px solid var(--ring-soft);
  border-radius: var(--radius-sm);
  padding: 15px 18px;
  font-size: 14.5px;
  line-height: 1.55;
  color: var(--text-dim);
}
.cheat-item strong {
  color: var(--text);
  font-weight: 700;
  font-family: var(--heading);
}

/* ---- BRIDGE ---- */
.bridge {
  margin: 0 0 0;
  padding: 56px 0;
  border-top: 1px solid var(--ring-soft);
}
.bridge .eyebrow { margin-bottom: 18px; }
.bridge p {
  font-size: clamp(1.05rem, 2.6vw, 1.35rem);
  line-height: 1.62;
  color: var(--text);
  font-weight: 500;
  max-width: 60ch;
}
.bridge p strong { color: var(--amber); font-weight: 700; }

/* ---- CTA ---- */
.cta {
  margin: 36px 0 90px;
  padding: 48px 36px;
  background:
    radial-gradient(ellipse 80% 120% at 50% -20%, rgba(245,158,11,0.13), transparent 60%),
    var(--surface-2);
  border: 1px solid var(--amber-ring);
  border-radius: 22px;
  text-align: center;
}
.cta h2 {
  font-family: var(--heading);
  font-weight: 700;
  font-size: clamp(1.5rem, 4.5vw, 2.3rem);
  line-height: 1.15;
  letter-spacing: -0.03em;
  max-width: 22ch;
  margin: 0 auto 18px;
}
.cta p {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-dim);
  max-width: 52ch;
  margin: 0 auto 30px;
}
.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: var(--heading);
  font-weight: 700;
  font-size: 16px;
  letter-spacing: -0.01em;
  color: #0A0A0A;
  background: var(--amber);
  padding: 16px 30px;
  border-radius: 12px;
  text-decoration: none;
  transition: transform 0.18s cubic-bezier(0.16,1,0.3,1), box-shadow 0.18s ease;
  box-shadow: 0 10px 34px -10px rgba(245,158,11,0.55);
}
.cta-btn:hover { transform: translateY(-2px); box-shadow: 0 16px 44px -10px rgba(245,158,11,0.7); }
.cta-btn:active { transform: translateY(0); }
.cta-btn svg { width: 17px; height: 17px; }

/* ---- FOOTER ---- */
.footer {
  padding: 30px 0 50px;
  border-top: 1px solid var(--ring-soft);
  font-size: 13px;
  color: var(--text-faint);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.footer .brand { font-family: var(--heading); font-weight: 500; color: var(--text-dim); }

/* ============ RESPONSIVE: desktop split layout ============ */
@media (min-width: 860px) {
  .wrap { padding: 0 40px; }
  .hero { padding: 120px 0 76px; }
  .trigger-grid {
    grid-template-columns: 340px 1fr;
    gap: 52px;
  }
  /* Video sticks while text scrolls */
  .reel {
    position: sticky;
    top: 40px;
    margin: 0;
  }
  .cheat-grid { grid-template-columns: 1fr 1fr; gap: 14px; }
  .cta { padding: 64px 56px; }
}

@media (min-width: 1024px) {
  .trigger { padding: 64px 0; }
}

/* Accessibility: visible focus rings */
a:focus-visible, video:focus-visible, .cta-btn:focus-visible {
  outline: 2px solid var(--amber);
  outline-offset: 3px;
  border-radius: 6px;
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  * { transition: none !important; }
}
"""


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------

ICON_PLAY = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>'
ICON_EXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8"/></svg>'
ICON_ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def render_trigger(t):
    n = t["n"]
    nn = f"{n:02d}"
    video = norm_video(t["video"])
    thumb = norm_thumb(t["thumb"])
    duration = t.get("duration")
    dur_str = f"{duration}s" if duration else ""
    reel_url = t.get("reel_url", "")

    appliquer_items = "\n".join(
        f'        <li><span class="idx">{i+1}</span>{esc(step)}</li>'
        for i, step in enumerate(t["appliquer"])
    )

    # Only allow http/https in the reel link href (anti-XSS hygiene)
    safe_link = ""
    if reel_url.startswith("http://") or reel_url.startswith("https://"):
        safe_link = (
            f'<a class="reel-link" href="{esc_attr(reel_url)}" target="_blank" '
            f'rel="noopener noreferrer">Voir sur Instagram {ICON_EXT}</a>'
        )

    return f"""
    <section class="trigger" id="trigger-{n}">
      <div class="wrap">
        <div class="trigger-grid">
          <div class="reel">
            <div class="reel-frame">
              <video controls playsinline preload="none" poster="{esc_attr(thumb)}"
                     aria-label="Reel exemple — {esc_attr(t['name'])}">
                <source src="{esc_attr(video)}" type="video/mp4">
                Votre navigateur ne supporte pas la lecture vidéo.
              </video>
            </div>
            <div class="reel-meta">
              <span class="reel-badge">{ICON_PLAY} Exemple{(' · ' + dur_str) if dur_str else ''}</span>
              {safe_link}
            </div>
          </div>

          <div class="trigger-body">
            <span class="trigger-num">{nn}<span class="of"> / 12</span></span>
            <h3 class="trigger-name">{esc(t['name'])}</h3>
            <p class="trigger-principe">{esc(t['principe'])}</p>

            <span class="block-label">Pourquoi ça marche</span>
            <p class="trigger-pourquoi">{esc(t['pourquoi'])}</p>

            <div class="loi">
              <span class="loi-label">La loi</span>
              <p>{esc(t['punchline'])}</p>
            </div>

            <span class="block-label">Comment l'appliquer</span>
            <ul class="appliquer">
{appliquer_items}
            </ul>
          </div>
        </div>
      </div>
    </section>"""


def render_cheatsheet(items):
    cells = []
    for raw in items:
        # Split "1. Name — rest" into bold lead + body
        m = re.match(r"^\s*(\d+\.\s*[^—–-]+[—–-])\s*(.*)$", raw)
        if m:
            lead, body = m.group(1).strip(), m.group(2).strip()
            cells.append(
                f'        <div class="cheat-item"><strong>{esc(lead)}</strong> {esc(body)}</div>'
            )
        else:
            cells.append(f'        <div class="cheat-item">{esc(raw)}</div>')
    grid = "\n".join(cells)
    return f"""
    <section class="cheatsheet" id="cheatsheet">
      <div class="wrap">
        <span class="eyebrow">Mémo</span>
        <h2>Les 12 déclencheurs en une page</h2>
        <div class="cheat-grid">
{grid}
        </div>
      </div>
    </section>"""


def split_hero_title(title):
    """Render the last word of the title in amber for emphasis."""
    words = title.rsplit(" ", 1)
    if len(words) == 2:
        return f'{esc(words[0])} <span class="accent">{esc(words[1])}</span>'
    return esc(title)


def render_page(data):
    title = data["title"]
    author = data["author"]
    intro = data["intro"]
    bridge = data["bridge"]
    cta = data["cta"]

    # CTA href — only allow http/https
    cta_href = cta.get("form_url", "#")
    if not (cta_href.startswith("http://") or cta_href.startswith("https://")):
        cta_href = "#"

    triggers_html = "\n".join(render_trigger(t) for t in data["triggers"])
    cheat_html = render_cheatsheet(data["cheatsheet"])
    hero_title = split_hero_title(title)

    meta_desc = esc_attr(intro["promise"][:155])

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} — {esc(author)}</title>
  <meta name="description" content="{meta_desc}">
  <meta name="robots" content="noindex">
  <meta name="theme-color" content="#0A0A0A">
  <meta property="og:title" content="{esc_attr(title)}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="article">
  <style>{CSS}</style>
</head>
<body>

  <header class="hero">
    <div class="wrap">
      <span class="eyebrow">Guide · Mécanismes de viralité</span>
      <h1>{hero_title}</h1>
      <span class="byline"><span class="dot"></span>par {esc(author)}</span>
    </div>
  </header>

  <section class="intro">
    <div class="wrap">
      <p class="lead">{esc(intro['promise'])}</p>
      <div class="howto">
        <span class="eyebrow">Comment utiliser ce guide</span>
        <p>{esc(intro['how_to_use'])}</p>
      </div>
    </div>
  </section>

  <div class="triggers-head">
    <div class="wrap">
      <span class="eyebrow">Les déclencheurs</span>
      <h2>12 leviers que le cerveau ne peut pas ignorer</h2>
    </div>
  </div>

{triggers_html}

{cheat_html}

  <section class="bridge">
    <div class="wrap">
      <span class="eyebrow">{esc(bridge['eyebrow'])}</span>
      <p>{esc(bridge['text'])}</p>
    </div>
  </section>

  <section class="cta-section">
    <div class="wrap">
      <div class="cta">
        <h2>{esc(cta['headline'])}</h2>
        <p>{esc(cta['body'])}</p>
        <a class="cta-btn" href="{esc_attr(cta_href)}" target="_blank" rel="noopener noreferrer">
          {esc(cta['button'])} {ICON_ARROW}
        </a>
      </div>
    </div>
  </section>

  <footer class="footer">
    <div class="wrap" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;width:100%;">
      <span class="brand">{esc(title)}</span>
      <span>© {esc(author)}</span>
    </div>
  </footer>

</body>
</html>"""


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def build(src_json, out_html):
    with open(src_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    page = render_page(data)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  built {out_html}  ({len(page):,} bytes)  from {src_json}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    if len(sys.argv) == 3:
        build(sys.argv[1], sys.argv[2])
        return

    # Default: build all three variants
    jobs = [
        ("content.json", "index-expert.html"),
        ("content_createur.json", "index-createur.html"),
        ("content_accessible.json", "index-accessible.html"),
    ]
    print("Building all 3 tone variants...")
    for src, out in jobs:
        if os.path.exists(src):
            build(src, out)
        else:
            print(f"  SKIP {src} (not found)")
    print("Done.")


if __name__ == "__main__":
    main()
