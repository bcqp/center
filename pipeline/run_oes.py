"""Build the dataset, run the OES model, enforce the diagnostics gate."""
import io, csv
import oes_engine

def to_csv(cols, years):
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["year"] + list(cols))
    for y in years: w.writerow([y] + [cols[c][y] for c in cols])
    return buf.getvalue()

def prepare(topic, data):
    cols = {}
    for v in topic["variables"]:
        s = data[v["id"]]
        if v.get("transform") == "pct":
            ys = sorted(s); s = {y: 100 * (s[y] / s[p] - 1) for p, y in zip(ys, ys[1:])}
        cols[v["id"]] = s
    years = sorted(set.intersection(*[set(s) for s in cols.values()]))
    return cols, years

def run(topic, data):
    cols, years = prepare(topic, data)
    if len(years) < 15: raise ValueError("only %d common years" % len(years))
    csv_text = to_csv(cols, years)
    res = oes_engine.run(topic["model"]["id"], csv_text, topic["model"]["spec"])
    g = topic["gate"]
    got = {s["label"]: s["value"] for s in res["summary"]}.get(g["summary_label"])
    if str(got).lower() != g["equals"]:
        raise ValueError("diagnostics gate failed: %s = %r" % (g["summary_label"], got))
    return res, csv_text, years
