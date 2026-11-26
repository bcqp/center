#!/usr/bin/env python3
"""Give every BIQEP page one clean set of link-preview tags and a 1200x630 card in the shared main-site style.
Usage: CHROME=/usr/bin/google-chrome [OG_FONT_CSS=fonts.css] python3 tools/og_pages.py   (idempotent)
Cards: assets/og/<page path>.jpg ; report pages keep briefs/<slug>/og.jpg."""
import asyncio, html, json, os, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://biqep.github.io/institute/"
SKIP = {"404.html", "google93d17a5aad1078de.html"}
def card_path(rel):
    if rel.startswith("briefs/") and re.search(r"-\d{4}-\d{2}-\d{2}\.html$", rel):
        return "briefs/" + rel[7:-5] + "/og.jpg"
    return "assets/og/" + ("index" if rel == "index.html" else rel[:-len("/index.html")] if rel.endswith("/index.html") else rel[:-5]) + ".jpg"
def kicker(rel):
    top = rel.split("/")[0]
    return {"briefs": "Statistical reports · Bangladesh", "research": "Research areas", "methodology": "Methodology", "policies": "Policies",
            "data": "Data and sources", "about": "About BIQEP", "news": "News and events", "journal": "Journal"}.get(top, "Bangladesh Institute of Quantitative Economics and Public Policy")
pages = []
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel in SKIP or rel.startswith(("tools/", "pipeline/", "content/", "oes/")): continue
    s = p.read_text(encoding="utf-8")
    t = re.search(r'<meta property="og:title" content="(.*?)">', s) or re.search(r"<title>(.*?)</title>", s)
    d = re.search(r'<meta name="description" content="(.*?)">', s)
    if not t or not d: continue
    title = html.unescape(t.group(1)); desc = html.unescape(d.group(1))
    short = re.sub(r"\s*\|\s*BIQEP.*$", "", title)
    if rel == "index.html": short = "Statistical reports on the Bangladesh economy"
    pages.append(dict(p=p, rel=rel, title=title, short=short, desc=desc, out=card_path(rel)))
def tags(c):
    u = SITE + (c["rel"][:-10] if c["rel"].endswith("index.html") else c["rel"]); img = SITE + c["out"]; e = lambda x: html.escape(x, quote=True)
    alt = e("BIQEP: " + c["short"])
    return ('<meta property="og:image" content="%s"><meta property="og:image:secure_url" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            '<meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="%s">'
            '<meta name="twitter:image" content="%s"><meta name="twitter:image:alt" content="%s">') % (img, img, alt, img, alt)
def patch():
    for c in pages:
        s = c["p"].read_text(encoding="utf-8"); o = s
        s = re.sub(r'\s*<meta (?:property="og:image(?::[a-z_]+)?"|name="twitter:image(?::alt)?")[^>]*>', "", s)
        if 'name="twitter:card"' not in s:
            s = s.replace("</title>", '</title>\n<meta name="twitter:card" content="summary_large_image">', 1)
        s = s.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary_large_image">\n' + tags(c), 1)
        s = s.replace('<meta name="theme-color" content="#00205b">', '<meta name="theme-color" content="#00205b">')
        if s != o: c["p"].write_text(s, encoding="utf-8")
HTMLT = """<html><head>{HEAD}<style>
body{margin:0;width:1200px;height:630px;overflow:hidden;font-family:'DM Sans',sans-serif;color:#fff;position:relative;
 background:radial-gradient(circle at 50% -10%,#6ec1e450,transparent 45%),linear-gradient(125deg,#0033A0,#00205B)}
.ring{position:absolute;border:1px solid #ffffff1c;border-radius:50%}.r1{width:560px;height:560px;left:-300px;top:-180px}.r2{width:560px;height:560px;right:-300px;bottom:-200px}
.col{position:absolute;left:260px;width:680px;top:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.brand{font:800 26px Manrope,sans-serif;letter-spacing:.1em;margin-bottom:24px}.brand span{color:#6EC1E4}
.eye{font-size:19px;font-weight:800;letter-spacing:.14em;color:#9fdaf2;text-transform:uppercase;line-height:1.35;max-width:620px}
h1{font:800 60px/1.08 Manrope,sans-serif;letter-spacing:-.035em;margin:16px 0;max-width:660px;overflow-wrap:anywhere}
p{font-size:24px;line-height:1.35;color:#d9e5f7;margin:0;max-width:620px}
.who{margin-top:24px;font-size:18px;font-weight:700;color:#c9d8ef;padding:8px 18px;border:1px solid #ffffff40;border-radius:40px;background:#ffffff12}
</style></head><body><div class="ring r1"></div><div class="ring r2"></div>
<div class="col"><div class="brand">BIQEP <span>POLICY BRIEFS</span></div><div class="eye" id="k"></div><h1 id="t"></h1><p id="s"></p><div class="who">Tuhin G. M. Al Mamun</div></div></body></html>"""
async def render():
    from playwright.async_api import async_playwright
    F = os.environ.get("OG_FONT_CSS")
    head = "<style>%s</style>" % pathlib.Path(F).read_text() if F and os.path.exists(F) else '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700;800&family=Manrope:wght@800&display=swap" rel="stylesheet">'
    only = os.environ.get("OG_MISSING")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROME"), args=["--no-sandbox"]); pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.set_content(HTMLT.replace("{HEAD}", head)); await pg.wait_for_timeout(800)
        for c in pages:
            out = ROOT / c["out"]
            if only and out.exists(): continue
            sub = c["desc"]
            if len(sub) > 130:
                m = re.match(r"(.{40,130}?[.])\s", sub + " "); sub = m.group(1) if m else sub[:127].rsplit(" ", 1)[0] + "…"
            await pg.evaluate("""c=>{k.textContent=c.k;t.textContent=c.t;s.textContent=c.s;t.style.fontSize='60px';s.style.display='';s.style.fontSize='24px';
              const col=document.querySelector('.col');let f=60;const used=()=>col.lastElementChild.getBoundingClientRect().bottom-col.firstElementChild.getBoundingClientRect().top;
              while((t.getBoundingClientRect().height>f*1.08*3.1||used()>540)&&f>34){f-=2;t.style.fontSize=f+'px'}
              if(used()>540)s.style.display='none'}""", dict(k=kicker(c["rel"]), t=c["short"], s=sub))
            out.parent.mkdir(parents=True, exist_ok=True); await pg.screenshot(path=str(out), type="jpeg", quality=82)
        await b.close()
if __name__ == "__main__":
    patch(); asyncio.run(render()); print(len(pages), "pages")
