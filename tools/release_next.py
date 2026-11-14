"""Publish the next reports from the queue branch. Usage: release_next.py <queue_dir> [--force]
Runs weekly; releases `per_release` reports if at least `interval_days` have passed since the last release."""
import json, re, shutil, sys, datetime, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; Q = pathlib.Path(sys.argv[1]); force = "--force" in sys.argv
log = json.load(open(R / "content/release_log.json")); today = datetime.date.today(); last = datetime.date.fromisoformat(log["last_release"])
if not force and (today - last).days < log["interval_days"]: print("not due"); sys.exit(0)
brf = json.load(open(R / "content/briefs.json")); have = {b["slug"] for b in brf}
queue = json.load(open(Q / "queue.json")); recs = {r["slug"]: r for r in queue["records"]}
todo = [s for s in queue["order"] if s not in have][: log["per_release"]]
if not todo: print("queue empty"); sys.exit(0)
d = today.isoformat()
for s in todo:
    h = (Q / (s + ".html")).read_text(encoding="utf-8")
    h = h.replace("· Statistical report · 2026-11-14", "· Statistical report · " + d).replace('"datePublished": "2026-11-14"', '"datePublished": "%s"' % d)
    h = re.sub(r"(Al Mamun, Tuhin G\. M\., and Rahim Md Abdur \()\d{4}\)", r"\g<1>%d)" % today.year, h)
    (R / "briefs" / (s + ".html")).write_text(h, encoding="utf-8"); shutil.copytree(Q / s, R / "briefs" / s, dirs_exist_ok=True)
    r = dict(recs[s]); r["date"] = d; brf.append(r)
json.dump(brf, open(R / "content/briefs.json", "w"), indent=1, ensure_ascii=False)
log["last_release"] = d; json.dump(log, open(R / "content/release_log.json", "w"))
print("released:", todo)
