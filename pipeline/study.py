"""Run several OES models on the validated annual dataset and collect impulse responses."""
import json, io, csv, math, pathlib, warnings
warnings.filterwarnings("ignore")
import oes_engine
D = pathlib.Path(__file__).resolve().parent / "data"

def load():
    wb = json.loads((D / "wb_bgd.json").read_text())["series"]
    return {k: {int(y): v for y, v in s.items()} for k, s in wb.items()}

def diff(s): ys = sorted(s); return {y: s[y] - s[p] for p, y in zip(ys, ys[1:])}
def pct(s): ys = sorted(s); return {y: 100 * (s[y] / s[p] - 1) for p, y in zip(ys, ys[1:])}

def dataset():
    w = load()
    cols = {
     "fx_dep":  pct(w["PA.NUS.FCRF"]),                      # exchange-rate depreciation, % per year
     "reserves": pct(w["FI.RES.TOTL.CD"]),                  # reserves growth, % per year
     "gdp":     w["NY.GDP.MKTP.KD.ZG"],                     # real GDP growth
     "cons":    w["NE.CON.PRVT.KD.ZG"],                     # private consumption growth
     "inv":     diff(w["NE.GDI.TOTL.ZS"]),                  # change in investment/GDP
     "exp":     diff(w["NE.EXP.GNFS.ZS"]),                  # change in exports/GDP
     "imp":     diff(w["NE.IMP.GNFS.ZS"]),                  # change in imports/GDP
     "dep":     diff(w["FR.INR.DPST"]),                     # change in deposit rate
     "lend":    diff(w["FR.INR.LEND"]),                     # change in lending rate
     "money":   diff(w["FM.LBL.BMNY.GD.ZS"]),               # change in broad money/GDP
     "credit":  diff(w["FS.AST.PRVT.GD.ZS"]),               # change in private credit/GDP
     "unemp":   diff(w["SL.UEM.TOTL.ZS"]),                  # change in unemployment rate
     "infl":    w["FP.CPI.TOTL.ZG"],                        # CPI inflation
    }
    years = sorted(set.intersection(*[set(s) for s in cols.values()]))
    return cols, years

def to_csv(cols, years):
    b = io.StringIO(); w = csv.writer(b); w.writerow(["year"] + list(cols))
    for y in years: w.writerow([y] + [round(cols[c][y], 6) for c in cols])
    return b.getvalue()

def irf(res, resp, shock):
    for c in res.get("charts", []):
        if c["title"].startswith("Response of %s to a shock in %s" % (resp, shock)):
            s = c["series"][0]["y"]; b = c.get("band")
            return {"x": c["x"], "y": s, "lo": b["lo"] if b else None, "hi": b["hi"] if b else None}
    return None

def run_all(log=print):
    cols, years = dataset(); T = to_csv(cols, years)
    out = {"years": [years[0], years[-1]], "n": len(years), "csv": T, "runs": {}, "irf": {}}
    rest = ["reserves", "gdp", "cons", "inv", "exp", "imp", "dep", "money", "credit", "unemp"]
    fxo = ["fx_dep", "infl", "lend"] + rest                      # exchange-rate shock ordered first
    mo = ["lend", "infl", "gdp", "credit", "money", "fx_dep"] + [v for v in rest if v not in ("gdp", "credit", "money")]  # policy-rate shock ordered first
    bv = {"time": "year", "horizon": 6, "draws": 3000, "burn": 500, "seed": 7, "delta": 0, "lambda1": 0.1}
    specs = [
     ("bvar13_fx", "bvar", dict(bv, vars=fxo, lags=1), [("infl", "fx_dep"), ("gdp", "fx_dep"), ("lend", "fx_dep")]),
     ("bvar13_fx_l2", "bvar", dict(bv, vars=fxo, lags=2), [("infl", "fx_dep")]),
     ("bvar13_fx_tight", "bvar", dict(bv, vars=fxo, lags=1, lambda1=0.2), [("infl", "fx_dep")]),
     ("bvar13_mp", "bvar", dict(bv, vars=mo, lags=1), [("infl", "lend"), ("gdp", "lend"), ("credit", "lend")]),
     ("var3", "var", {"vars": ["fx_dep", "infl", "gdp"], "time": "year", "transform": "levels", "max_lags": 2, "horizon": 6}, [("infl", "fx_dep")]),
     ("var5_fx", "var", {"vars": ["fx_dep", "infl", "money", "gdp", "lend"], "time": "year", "transform": "levels", "max_lags": 2, "horizon": 6}, [("infl", "fx_dep")]),
     ("var5_mp", "var", {"vars": ["lend", "infl", "money", "gdp", "fx_dep"], "time": "year", "transform": "levels", "max_lags": 2, "horizon": 6}, [("infl", "lend")]),
     ("svar3", "svar", {"vars": ["fx_dep", "infl", "gdp"], "shock": "fx_dep", "time": "year", "lags": 1, "horizon": 6, "boot": 500, "level": "90"}, []),
     ("lp", "lp", {"y": "infl", "shock": "fx_dep", "controls": ["gdp", "lend", "money"], "time": "year", "lags": 1, "horizon": 6, "scale": "sd", "cov": "hac"}, []),
     ("lp_mp", "lp", {"y": "infl", "shock": "lend", "controls": ["gdp", "fx_dep", "money"], "time": "year", "lags": 1, "horizon": 6, "scale": "sd", "cov": "hac"}, []),
    ]
    for name, mid, spec, pairs in specs:
        try:
            r = oes_engine.run(mid, T, spec)
        except Exception as e:
            r = {"error": "%s: %s" % (type(e).__name__, e)}
        out["runs"][name] = {"model": mid, "spec": spec, "error": r.get("error"),
                             "summary": r.get("summary"), "nobs": r.get("nobs"),
                             "tables": [{"title": t["title"], "rows": t["rows"][:25]} for t in r.get("tables", [])[:9]] if not r.get("error") else None}
        log("%s: %s" % (name, r.get("error") or ("ok nobs=%s %s" % (r.get("nobs"), [(s["label"], s["value"]) for s in (r.get("summary") or [])][:7]))))
        if not r.get("error"):
            for resp, shk in pairs:
                out["irf"]["%s|%s<-%s" % (name, resp, shk)] = irf(r, resp, shk)
            if name in ("svar3", "lp", "lp_mp"):
                out["irf"][name + "|infl"] = next(({"x": c["x"], "y": c["series"][0]["y"], "lo": (c.get("band") or {}).get("lo"), "hi": (c.get("band") or {}).get("hi"), "title": c["title"]} for c in r["charts"] if "infl" in c["title"] or name.startswith("lp")), None)
    return out

if __name__ == "__main__":
    o = run_all(); (D / "study_results.json").write_text(json.dumps(o, indent=1, default=str))
    print({k: (v is not None) for k, v in o["irf"].items()}, o["n"], o["years"])
