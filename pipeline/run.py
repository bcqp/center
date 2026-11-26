"""Weekly run: rank topics from news, fetch and validate official data, run OES, write a report. Fails closed."""
import sys, json, datetime, pathlib, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, cfg
import news, validate, run_oes, report

def main(force_topic=None, offline_news=None):
    log = []; today = datetime.date.today().isoformat()
    topics = {t["slug"]: t for t in cfg("topics.json")["topics"]}
    if force_topic:
        order = [force_topic]
    else:
        sc, n = news.run(log) if offline_news is None else offline_news
        log.append("headlines read: %d" % n)
        order = [s for s, v in sorted(sc.items(), key=lambda kv: -kv[1]["score"]) if v["score"] > 0]
        for s in order: log.append("topic %s score %d" % (s, sc[s]["score"]))
    done = {b["slug"] for b in json.loads((ROOT / "content/briefs.json").read_text())}
    for slug in order:
        t = topics[slug]
        if "%s-%s" % (slug, today) in done: log.append("skip %s: already produced today" % slug); continue
        try:
            data, meta = {}, {}
            for v in t["variables"]:
                s, url = validate.fetch_validated(v)
                data[v["id"]] = s
                meta[v["id"]] = {"source": cfg("sources.json")["allow"][v["source"]]["name"], "url": url}
            if t.get("cross_check"): validate.cross_check(data[t["cross_check"]["var"]], t["cross_check"], log)
            res, csv_text, years = run_oes.run(t, data)
            rec = report.build(t, meta, data, res, years, csv_text, today)
            review = report.review_body(t, meta, data, res, years, rec)
        except Exception as e:
            log.append("REJECTED %s: %s" % (slug, e)); continue
        bp = ROOT / "content/briefs.json"
        b = json.loads(bp.read_text()); b.append(rec); bp.write_text(json.dumps(b, indent=2, ensure_ascii=False))
        log.append("produced %s" % rec["slug"])
        (ROOT / "pipeline" / "review.md").write_text(review, encoding="utf-8")
        subprocess.check_call([sys.executable, str(ROOT / "tools/build_data.py")])
        break
    else:
        log.append("no brief produced")
    (ROOT / "pipeline" / "last_run.log").write_text("\n".join(log) + "\n")
    print("\n".join(log))

if __name__ == "__main__":
    main(force_topic=sys.argv[1] if len(sys.argv) > 1 else None)
