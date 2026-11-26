"""Add a 'Cite this' line with the Zenodo archive DOI to every report page (idempotent)."""
import re, pathlib, json, html
R = pathlib.Path(__file__).resolve().parents[1]; DOI = "10.5281/zenodo.24215521"
for b in json.load(open(R / "content/briefs.json")):
    p = R / "briefs" / (b["slug"] + ".html"); s = p.read_text(encoding="utf-8")
    if "cite-this" in s: continue
    year = b["date"][:4]
    box = ('<p class="small cite-this"><b>Cite as:</b> Al Mamun, Tuhin G. M., and Dr Rahim Md Abdur (%s). %s. BCQP Policy Briefs. Archived at <a href="https://doi.org/%s">https://doi.org/%s</a>.</p>' % (year, html.escape(b["title"]), DOI, DOI))
    n = re.sub(r'(<p class="small muted">Tuhin G\. M\. Al Mamun[^<]*</p>)', lambda m: m.group(1) + box, s, count=1)
    if n != s: p.write_text(n, encoding="utf-8")
