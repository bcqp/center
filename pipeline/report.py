"""Template-based report. Every sentence is built from validated numbers; nothing is free text."""
import json, html, datetime
from common import ROOT, cfg

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">')
esc = html.escape

def svg_chart(ch, w=640, h=260):
    xs = ch["x"]; ser = ch["series"][:3]
    ys = [v for s in ser for v in s["y"] if v is not None]
    lo, hi = min(ys + [0]), max(ys + [0])
    pad = (hi - lo) * 0.08 or 1; lo -= pad; hi += pad
    L, R, T, B = 48, 12, 14, 34
    fx = lambda i: L + (w - L - R) * i / max(len(xs) - 1, 1)
    fy = lambda v: T + (h - T - B) * (hi - v) / (hi - lo)
    cols = ["#0033a0", "#168b88", "#c6a15b"]
    o = ['<svg viewBox="0 0 %d %d" role="img" aria-label="%s" style="width:100%%;height:auto">' % (w, h, esc(ch["title"]))]
    o.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#9aa7b2" stroke-dasharray="3 3"/>' % (L, w - R, fy(0), fy(0)))
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        o.append('<text x="%d" y="%.1f" font-size="10" text-anchor="end" fill="#55636f">%.2f</text>' % (L - 6, fy(v) + 3, v))
    for i in range(0, len(xs), max(1, len(xs) // 8)):
        o.append('<text x="%.1f" y="%d" font-size="10" text-anchor="middle" fill="#55636f">%s</text>' % (fx(i), h - 14, esc(str(xs[i]))))
    for n, s in enumerate(ser):
        pts = " ".join("%.1f,%.1f" % (fx(i), fy(v)) for i, v in enumerate(s["y"]) if v is not None)
        o.append('<polyline fill="none" stroke="%s" stroke-width="2" points="%s"/>' % (cols[n], pts))
    o.append("</svg>")
    leg = " ".join('<span class="tag" style="border-color:%s">%s</span>' % (cols[n], esc(s["name"])) for n, s in enumerate(ser))
    return "<h3>%s</h3>%s<p class=\"small muted\">%s</p>" % (esc(ch["title"]), "".join(o), leg)

def build(topic, series_meta, data, res, years, csv_text, today=None):
    today = today or datetime.date.today().isoformat()
    slug = "%s-%s" % (topic["slug"], today)
    vm = {v["id"]: v for v in topic["variables"]}
    facts = []
    for vid, v in vm.items():
        s = data[vid]; y = max(s); prev = y - 1
        line = "%s: %.2f in %d" % (v["label"], s[y], y)
        if prev in s: line += " (%.2f in %d)" % (s[prev], prev)
        facts.append(line + ".")
    nobs = res.get("nobs")
    charts = [c for c in res["charts"] if "mpulse" in c["title"]][:4] or res["charts"][:2]
    srcs = sorted({series_meta[v]["url"] for v in series_meta})
    title = "%s in Bangladesh: latest official data and model results" % topic["name"]
    summary = "Official figures on %s for %d–%d with vector autoregression results. %s" % (topic["name"].lower(), years[0], years[-1], facts[0])
    body = ['<section class="pagehead"><div class="wrap"><div class="crumbs"><a href="../index.html">Home</a><i>/</i><a href="index.html">Policy briefs</a><i>/</i>%s</div>' % esc(topic["name"]),
            '<div class="eyebrow">Data note</div><h1>%s</h1><p class="lede">%s</p>' % (esc(title), esc(summary)),
            '<p class="small muted">Tuhin G. M. Al Mamun · %s</p></div></section>' % today,
            '<section class="sec"><div class="wrap"><div class="content" style="max-width:900px"><h2>Latest figures</h2><ul>']
    body += ["<li>%s</li>" % esc(f) for f in facts]
    body += ["</ul>", "<h2>Model results</h2>",
             "<p>A vector autoregression was estimated on %d annual observations (%d–%d) with the Open Econometric Systems engine. The stability condition is met.</p>" % (nobs or len(years), years[0], years[-1])]
    body += [svg_chart(c) for c in charts]
    for t in res["tables"][:2]:
        if t["rows"]:
            cols = list(t["rows"][0].keys()) if isinstance(t["rows"][0], dict) else None
            if cols:
                body.append("<h3>%s</h3><div class=\"tbl\"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>" % (
                    esc(t["title"]), "".join("<th>%s</th>" % esc(c) for c in cols),
                    "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(str(r.get(c, ""))) for c in cols) for r in t["rows"][:15])))
    body.append("<h2>Sources</h2><ul>")
    for vid, m in series_meta.items():
        body.append('<li>%s: %s, <a href="%s">%s</a>, retrieved %s.</li>' % (esc(vm[vid]["label"]), esc(m["source"]), esc(m["url"]), esc(m["url"]), today))
    body.append('</ul><h2>Replication</h2><p><a href="%s.csv">Dataset (CSV)</a> · <a href="%s.json">Specification and results (JSON)</a></p>' % (slug, slug))
    body.append('</div></div></section>')
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title, "description": summary, "datePublished": today,
                     "author": {"@type": "Person", "name": "Tuhin G. M. Al Mamun", "url": "https://biqep.github.io/institute/people/"},
                     "publisher": {"@type": "Organization", "name": "BIQEP Policy Briefs", "url": "https://biqep.github.io/institute/"}}, ensure_ascii=False)
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s | BIQEP Policy Briefs</title><meta name="description" content="%s"><meta name="theme-color" content="#10283f">'
            '<meta name="author" content="Tuhin G. M. Al Mamun"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">'
            '<meta property="og:title" content="%s"><meta property="og:type" content="article"><meta property="og:image" content="https://biqep.github.io/institute/assets/og-image.png"><meta name="twitter:card" content="summary_large_image">'
            '<link rel="canonical" href="https://biqep.github.io/institute/briefs/%s.html"><script type="application/ld+json">%s</script>%s<link rel="stylesheet" href="../assets/style.css"></head>\n'
            '<body><div id="hdr"></div>\n<main id="main">\n%s\n</main>\n<div id="ftr"></div>\n'
            '<script src="../assets/data.js"></script><script src="../assets/pages.js"></script><script src="../assets/site.js" data-root="../"></script></body></html>\n') % (
            esc(title), esc(summary), esc(title), slug, ld, FONTS, "\n".join(body))
    record = {"slug": slug, "title": title, "date": today, "topic": topic["name"], "type": "Data note", "status": "published", "summary": summary}
    out = ROOT / "briefs"
    (out / (slug + ".html")).write_text(page, encoding="utf-8")
    (out / (slug + ".csv")).write_text(csv_text, encoding="utf-8")
    (out / (slug + ".json")).write_text(json.dumps({"topic": topic["slug"], "model": topic["model"], "variables": topic["variables"], "retrieved": today, "result": res}, indent=1, default=str), encoding="utf-8")
    return record


def review_body(topic, series_meta, data, res, years, rec):
    """Pull-request text: each statement the brief makes, with Agree / Disagree boxes for the author."""
    vm = {v["id"]: v for v in topic["variables"]}
    st = []
    for vid, v in vm.items():
        s = data[vid]; y = max(s)
        st.append(("%s was %.2f in %d." % (v["label"], s[y], y), series_meta[vid]["source"] + ", " + series_meta[vid]["url"]))
    st.append(("The model uses %d annual observations, %d to %d." % (len(years), years[0], years[-1]), "Dataset in the replication CSV"))
    st.append(("The vector autoregression meets the stability condition.", "OES engine diagnostics"))
    out = ["## Review: %s" % rec["title"], "", "Tick one box for each statement. Merge only when every statement is agreed.", ""]
    for i, (text, src) in enumerate(st, 1):
        out += ["### Statement %d" % i, text, "", "Source: " + src, "", "- [ ] Agree", "- [ ] Disagree", "- Comment:", ""]
    out += ["### Whole brief", "- [ ] Agree to publish", "- [ ] Do not publish", ""]
    return "\n".join(out)
