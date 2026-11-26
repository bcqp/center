#!/usr/bin/env python3
"""Static internal links and breadcrumb schema: 'More reports' on each report, 'Reports on this topic' on research pages,
BreadcrumbList JSON-LD on reports. Reads assets/data.js. Idempotent (marker comments)."""
import json, re, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; B = "https://bcqp.github.io/center/"
d = json.loads(re.search(r"window\.BCQP = (\{.*\});?\s*$", (ROOT / "assets/data.js").read_text(encoding="utf-8"), re.S).group(1))
briefs = sorted([b for b in d["briefs"] if b["status"] == "published"], key=lambda b: b["date"], reverse=True)
topics = {t["name"]: t["slug"] for t in d["topics"]}
e = html.escape
def card(b, pre):
    return '<li><a href="%sbriefs/%s.html">%s</a> <span class="small muted">· %s · %s</span></li>' % (pre, b["slug"], e(b["title"]), e(b["topic"]), b["date"])
def put(p, block, tag):
    s = p.read_text(encoding="utf-8"); s = re.sub(r"<!--%s-->.*?<!--/%s-->\s*" % (tag, tag), "", s, flags=re.S)
    s = s.replace("</main>", "<!--%s-->%s<!--/%s-->\n</main>" % (tag, block, tag), 1); p.write_text(s, encoding="utf-8")
for b in briefs:
    p = ROOT / "briefs" / (b["slug"] + ".html")
    if not p.exists(): continue
    others = [x for x in briefs if x["slug"] != b["slug"]]
    same = [x for x in others if x["topic"] == b["topic"]]; rest = [x for x in others if x not in same]
    pick = (same + rest)[:3]
    if not pick: continue
    put(p, '<section class="sec tight"><div class="wrap"><div class="content" style="max-width:900px"><h2>More reports on the Bangladesh economy</h2><ul>%s</ul>'
        '<p><a href="../briefs/index.html">All policy briefs</a> · <a href="../research/%s/index.html">Research area: %s</a> · <a href="../data/index.html">Verified data series</a></p></div></div></section>'
        % ("".join(card(x, "../") for x in pick), topics.get(b["topic"], ""), e(b["topic"])), "more-reports")
    s = p.read_text(encoding="utf-8")
    if '"BreadcrumbList"' not in s:
        ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": B}, {"@type": "ListItem", "position": 2, "name": "Policy briefs", "item": B + "briefs/"},
            {"@type": "ListItem", "position": 3, "name": b["title"], "item": B + "briefs/%s.html" % b["slug"]}]}
        s = s.replace("</head>", '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(ld, ensure_ascii=False), 1); p.write_text(s, encoding="utf-8")
for name, slug in topics.items():
    p = ROOT / "research" / slug / "index.html"
    if not p.exists(): continue
    mine = [x for x in briefs if x["topic"] == name]
    items = "".join(card(x, "../../") for x in (mine or briefs[:3]))
    h = "Reports on this topic" if mine else "Latest reports"
    put(p, '<section class="sec tight"><div class="wrap"><div class="content" style="max-width:900px"><h2>%s</h2><ul>%s</ul></div></div></section>' % (h, items), "topic-reports")
print("ok")
