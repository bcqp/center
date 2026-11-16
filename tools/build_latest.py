"""Write latest.json: the newest published reports, for display on other sites (e.g. the author's homepage)."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; B = "https://biqep.github.io/institute/"
brf = json.load(open(R / "content/briefs.json")); out = []
for b in reversed(brf):
    if not (R / "briefs" / b["slug"] / "thumb.jpg").exists(): continue
    out.append({"title": b["title"], "summary": b["summary"], "date": b["date"], "url": B + "briefs/%s.html" % b["slug"], "thumb": B + "briefs/%s/thumb.jpg" % b["slug"]})
(R / "latest.json").write_text(json.dumps({"updated": brf[-1]["date"] if brf else None, "reports": out[:3], "all": B + "briefs/index.html"}, indent=1, ensure_ascii=False), encoding="utf-8")
