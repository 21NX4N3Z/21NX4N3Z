"""Generate overview.svg + languages.svg (Obsidian Violet theme).
Runs in GitHub Actions with env METRICS_TOKEN, or locally with TOKEN file."""
import json, os, urllib.request

TOKEN = os.environ.get("METRICS_TOKEN") or open(os.path.join(os.path.dirname(__file__), "../../ghtoken.txt")).read().strip()
USER = "21NX4N3Z"

def gh(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

user = gh(f"https://api.github.com/users/{USER}")
repos = [r for r in gh(f"https://api.github.com/users/{USER}/repos?per_page=100") if not r["fork"]]
total_stars = sum(r["stargazers_count"] for r in repos)
followers, following = user["followers"], user["following"]

# per-repo language bytes (real code volume)
lang_bytes = {}
for r in repos:
    try:
        for lang, b in gh(f"https://api.github.com/repos/{USER}/{r['name']}/languages").items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + b
    except Exception:
        pass
top = sorted(lang_bytes.items(), key=lambda x: -x[1])[:6]
total_b = sum(v for _, v in top) or 1

BG="#07030f"; CARD="#120826"; STROKE="#2d1b4e"; P1="#c084fc"; P2="#a855f7"; TXT="#e9ddfb"; MUT="#7c6a99"
GLOW='<filter id="g"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
GRAD='<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07030f"/><stop offset="1" stop-color="#0d0620"/></linearGradient>'

# ── overview.svg ──
W,H=760,300
s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" font-family="Segoe UI,Arial,sans-serif"><defs>{GRAD}{GLOW}</defs><rect width="{W}" height="{H}" rx="14" fill="url(#bg)" stroke="{STROKE}"/>'
s+=f'<text x="36" y="52" fill="{P1}" font-size="20" font-weight="600" filter="url(#g)">overview</text><circle cx="128" cy="46" r="4" fill="{P2}"><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle>'
kpis=[("repos",str(len(repos))),("stars",str(total_stars)),("followers",str(followers))]
cw=(W-72-40)//3; x=36
for i,(lab,val) in enumerate(kpis):
    s+=f'<rect x="{x}" y="76" width="{cw}" height="86" rx="10" fill="{CARD}" stroke="{STROKE}"/>'
    s+=f'<text x="{x+cw/2}" y="126" fill="{P1 if i%2==0 else P2}" font-size="34" font-weight="700" text-anchor="middle" filter="url(#g)">{val}</text>'
    s+=f'<text x="{x+cw/2}" y="150" fill="{MUT}" font-size="12" text-anchor="middle" letter-spacing="2">{lab.upper()}</text>'
    x+=cw+20
s+=f'<text x="36" y="200" fill="{TXT}" font-size="13" letter-spacing="1">top languages</text>'
y=214; colors=["#c084fc","#a855f7","#7c5cff","#e879f9"]
maxv=max(v for _,v in top[:4]) or 1
for i,(lang,b) in enumerate(top[:4]):
    w=int(b/maxv*300)
    s+=f'<text x="36" y="{y+12}" fill="{TXT}" font-size="12">{lang}</text>'
    s+=f'<rect x="150" y="{y}" width="330" height="14" rx="7" fill="#150a26"/>'
    s+=f'<rect x="150" y="{y}" width="{w}" height="14" rx="7" fill="{colors[i%4]}" filter="url(#g)"/>'
    s+=f'<text x="495" y="{y+12}" fill="{MUT}" font-size="11">{b//1000}k</text>'
    y+=24
s+=f'<text x="{W-36}" y="{H-16}" fill="{MUT}" font-size="10" text-anchor="end">github.com/{USER} · obsidian violet</text></svg>'
open("overview.svg","w").write(s)

# ── languages.svg ──
W,H=480,300
t=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" font-family="Segoe UI,Arial,sans-serif"><defs>{GRAD}{GLOW}</defs><rect width="{W}" height="{H}" rx="14" fill="url(#bg)" stroke="{STROKE}"/>'
t+=f'<text x="28" y="44" fill="{P1}" font-size="17" font-weight="600" filter="url(#g)">languages</text><circle cx="112" cy="39" r="3.5" fill="#a855f7"><animate attributeName="opacity" values="1;.25;1" dur="2.2s" repeatCount="indefinite"/></circle>'
y=74; maxv=max(v for _,v in top) or 1
PALETTE=["#c084fc","#a855f7","#7c5cff","#e879f9","#d8b4fe","#9333ea"]
LANG_COLORS={"TypeScript":"#3178c6","JavaScript":"#f1e05a","HTML":"#e34c26","CSS":"#563d7c","Python":"#3572A5","Shell":"#89e051"}
for i,(lang,b) in enumerate(top):
    pct=b/total_b*100; w=int(b/maxv*280); col=LANG_COLORS.get(lang, PALETTE[i%len(PALETTE)])
    t+=f'<text x="28" y="{y+13}" fill="{TXT}" font-size="12">{lang}</text>'
    t+=f'<rect x="130" y="{y}" width="270" height="15" rx="7.5" fill="#150a26"/>'
    t+=f'<rect x="130" y="{y}" width="{w}" height="15" rx="7.5" fill="{col}" filter="url(#g)"/>'
    t+=f'<text x="410" y="{y+12}" fill="{MUT}" font-size="10.5">{pct:.0f}%</text>'
    y+=34
t+=f'<text x="28" y="{H-16}" fill="{MUT}" font-size="9.5">by bytes · {len(repos)} repositories</text></svg>'
open("languages.svg","w").write(t)
print("GEN_OK", len(s), len(t), "| langs:", top)
