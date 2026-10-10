"""Generate the obsidian-violet profile cards: stats.svg, status.svg, languages.svg.

Runs inside GitHub Actions (env METRICS_TOKEN) or locally.
Stdlib only. Live data: public non-fork repos + language bytes + star count.
"""
import json, os, urllib.request

TOKEN = os.environ.get("METRICS_TOKEN") or ""
USER = "21NX4N3Z"

BG0, BG1 = "#07030f", "#0d0620"
CARD, CARD2 = "#120826", "#150a26"
STROKE, HAIR = "#2d1b4e", "#1e0f38"
P1, P2, P3, P4 = "#c084fc", "#a855f7", "#7c5cff", "#f0abfc"
TXT, MUT, GRN = "#e9ddfb", "#7c6a99", "#39ff14"
RAMP = ["#f0abfc", "#c084fc", "#a855f7", "#7c5cff", "#6d28d9", "#4c1d95"]
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Courier New',monospace"

DEFS = (
    '<defs>'
    f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
    f'<stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>'
    f'<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">'
    f'<path d="M30 0 L0 0 0 30" fill="none" stroke="{HAIR}" stroke-width="0.6" opacity="0.55"/></pattern>'
    '<filter id="g" x="-30%" y="-30%" width="160%" height="160%">'
    '<feGaussianBlur stdDeviation="2.2" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    '</defs>'
)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def head(w, h, rx=14, font=SANS, grid=True):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
         f'font-family="{font}">{DEFS}')
    s += f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#bg)"/>'
    if grid:
        s += f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#grid)"/>'
    s += f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="none" stroke="{STROKE}"/>'
    return s


def title(x, y, label, dot_x=None, size=20):
    s = f'<text x="{x}" y="{y}" fill="{P1}" font-size="{size}" font-weight="600" filter="url(#g)">{esc(label)}</text>'
    if dot_x:
        s += (f'<circle cx="{dot_x}" cy="{y - 6}" r="4" fill="{P2}">'
              f'<animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle>')
    return s


# ── live data ──────────────────────────────────────────────────────────────
def gh(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


user = gh(f"https://api.github.com/users/{USER}")
repos = [r for r in gh(f"https://api.github.com/users/{USER}/repos?per_page=100") if not r["fork"]]
stars = sum(r["stargazers_count"] for r in repos)
lang_bytes = {}
for r in repos:
    try:
        for lang, b in gh(f"https://api.github.com/repos/{USER}/{r['name']}/languages").items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + b
    except Exception:
        pass
top = sorted(lang_bytes.items(), key=lambda x: -x[1])[:6]
total_b = sum(v for _, v in top) or 1
since = user["created_at"][:4]

# ── stats.svg ──────────────────────────────────────────────────────────────
W, H = 880, 200
s = head(W, H)
s += title(36, 54, "overview", dot_x=138)
tiles = [("repos", str(len(repos)), P1), ("stars", str(stars), P2),
         ("languages", str(len(lang_bytes)), P1), ("since", since, P2)]
tw, gap, tx = 190, 16, 36
for lab, val, col in tiles:
    s += f'<rect x="{tx}" y="80" width="{tw}" height="78" rx="10" fill="{CARD}" stroke="{STROKE}"/>'
    s += f'<text x="{tx + tw / 2}" y="126" fill="{col}" font-size="34" font-weight="700" text-anchor="middle" filter="url(#g)">{esc(val)}</text>'
    s += f'<text x="{tx + tw / 2}" y="152" fill="{MUT}" font-size="11" text-anchor="middle" letter-spacing="2">{esc(lab.upper())}</text>'
    tx += tw + gap
s += f'<text x="{W - 36}" y="182" fill="{MUT}" font-size="10" text-anchor="end">github.com/{USER} · obsidian violet</text>'
s += '</svg>'
open("stats.svg", "w", encoding="utf-8").write(s)

# ── status.svg ─────────────────────────────────────────────────────────────
W, H = 880, 140
s = head(W, H, rx=12, font=MONO)
s += (f'<circle cx="36" cy="40" r="5" fill="{GRN}">'
      f'<animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>')
s += f'<text x="52" y="45" fill="{TXT}" font-size="13">online · shipping side projects</text>'
s += f'<text x="{W - 36}" y="45" fill="{MUT}" font-size="10" text-anchor="end">now</text>'
cycle = [("fsae-cost-web", P1), ("bp18-dashboard", P2), ("eco-forge", P3)]
anim = [("1;1;0;0;1", "0;0.33;0.34;0.99;1"),
        ("0;0;1;1;0;0", "0;0.33;0.34;0.65;0.66;1"),
        ("0;0;0;0;1;1", "0;0.33;0.34;0.65;0.66;1")]
for i, (name, col) in enumerate(cycle):
    vals, kt = anim[i]
    s += (f'<g opacity="{"1" if i == 0 else "0"}"><text x="36" y="82" fill="{col}" font-size="15" filter="url(#g)">'
          f'&gt; {esc(name)} ▮</text>'
          f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" '
          f'dur="9s" repeatCount="indefinite"/></g>')
s += f'<line x1="36" y1="104" x2="{W - 36}" y2="104" stroke="{HAIR}" stroke-width="1"/>'
s += f'<text x="36" y="126" fill="{MUT}" font-size="12">stack  ts · react · next · vite · node · mongodb</text>'
s += '</svg>'
open("status.svg", "w", encoding="utf-8").write(s)

# ── languages.svg ──────────────────────────────────────────────────────────
R = 6
W = 880
H = 118 + R * 30 + 24
s = head(W, H)
s += title(36, 52, "languages", dot_x=150)
s += (f'<text x="{W - 36}" y="48" fill="{MUT}" font-size="11" text-anchor="end">'
      f'by bytes · {len(repos)} public repositories</text>')
# stacked share bar
bx, bw, by, bh = 36, W - 72, 76, 18
s += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="9" fill="{CARD2}"/>'
cursor = float(bx)
for i, (lang, b) in enumerate(top):
    seg = bw * b / total_b
    col = RAMP[i % len(RAMP)]
    rx = bw * (b / total_b)
    s += (f'<rect x="{cursor + 1:.1f}" y="{by}" width="{max(seg - 2, 1):.1f}" height="{bh}" '
          f'rx="4" fill="{col}" filter="url(#g)"/>')
    cursor += seg
# rows
y = 118
for i, (lang, b) in enumerate(top):
    pct = b / total_b * 100
    w = max(500 * b / total_b, 4)
    col = RAMP[i % len(RAMP)]
    s += f'<text x="36" y="{y + 10}" fill="{TXT}" font-size="12" font-family="{MONO}">{esc(lang)}</text>'
    s += f'<rect x="170" y="{y}" width="500" height="12" rx="6" fill="{CARD2}"/>'
    s += f'<rect x="170" y="{y}" width="{w:.1f}" height="12" rx="6" fill="{col}" filter="url(#g)"/>'
    s += f'<text x="{W - 36}" y="{y + 11}" fill="{MUT}" font-size="11" text-anchor="end">{pct:.0f}% · {b / 1000:.0f}k</text>'
    y += 30
s += '</svg>'
open("languages.svg", "w", encoding="utf-8").write(s)

print("GEN_OK", [l for l, _ in top], "stars", stars, "repos", len(repos))
