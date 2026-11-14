"""Generic topic report: OES models (BVAR 10+ variables, VAR, LP), peer benchmarking, 300-dpi figures, HTML."""
import json, io, csv, sys, pathlib, html, datetime, statistics, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import oes_engine, topics20 as TP
ROOT = pathlib.Path(__file__).resolve().parents[1]; D = ROOT / "pipeline" / "data"; esc = html.escape
NAVY, BLUE, TEAL, GOLD, RED, GREY = "#10283f", "#0033a0", "#168b88", "#c6a15b", "#b5372c", "#6b7885"
plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
  "axes.edgecolor": "#444", "axes.linewidth": .8, "axes.titlesize": 9, "axes.titleweight": "bold", "legend.frameon": False, "savefig.dpi": 300,
  "figure.dpi": 150, "axes.grid": True, "grid.color": "#e3e7ea", "grid.linewidth": .6})
PEERS = ["IND", "PAK", "LKA", "VNM", "IDN", "NPL"]
NAMES = {"BGD": "Bangladesh", "IND": "India", "PAK": "Pakistan", "LKA": "Sri Lanka", "VNM": "Viet Nam", "IDN": "Indonesia", "NPL": "Nepal"}
f = lambda v, d=1: ("%." + str(d) + "f") % v

def store():
    a = json.loads((D / "wb_bgd.json").read_text())["series"]; m = json.loads((D / "wb_multi.json").read_text())
    S = {k: {int(y): v for y, v in s.items()} for k, s in {**a, **m["series"]}.items()}
    return S, m["peers"], m["bgd_latest"]
def tr(s, how):
    ys = sorted(s)
    if how == "lvl": return dict(s)
    if how == "diff": return {y: s[y] - s[p] for p, y in zip(ys, ys[1:]) if y - p == 1}
    return {y: 100 * (s[y] / s[p] - 1) for p, y in zip(ys, ys[1:]) if y - p == 1 and s[p]}
def irf(res, resp, shock):
    for c in res.get("charts", []):
        if c["title"].startswith("Response of %s to a shock in %s" % (resp, shock)):
            b = c.get("band"); return {"x": c["x"], "y": c["series"][0]["y"], "lo": b["lo"] if b else None, "hi": b["hi"] if b else None}
def save(fig, out, name):
    fig.savefig(out / (name + ".png"), dpi=300, bbox_inches="tight", facecolor="white"); fig.savefig(out / (name + ".svg"), bbox_inches="tight", facecolor="white"); plt.close(fig)

def dataset(t, S):
    keys = [t["shock"]] + [r for r in t["resp"]] + [k for k in t["extra"]]
    for k in TP.CORE:
        if len(keys) >= 12: break
        if k not in keys: keys.append(k)
    keys = list(dict.fromkeys(keys))
    cols = {k: tr(S[TP.POOL[k][0]], TP.POOL[k][1]) for k in keys}
    years = sorted(set.intersection(*[set(c) for c in cols.values()]))
    while len(years) > 1 and years[-1] - years[0] != len(years) - 1: years = years[1:]
    return keys, cols, years

def run_models(t, keys, cols, years):
    b = io.StringIO(); w = csv.writer(b); w.writerow(["year"] + keys)
    for y in years: w.writerow([y] + [round(cols[k][y], 6) for k in keys])
    T = b.getvalue(); sh, r1 = t["shock"], t["resp"][0]
    bv = {"time": "year", "horizon": 6, "draws": 2500, "burn": 500, "seed": 7, "delta": 0, "lambda1": 0.1, "vars": keys}
    ctrl = [k for k in keys if k not in (sh, r1)][:3]; v4 = [sh, r1] + ctrl[:2]
    specs = [("BVAR, %d variables" % len(keys), "bvar1", "bvar", dict(bv, lags=1), "68%"), ("BVAR, 2 lags", "bvar2", "bvar", dict(bv, lags=2), "68%"),
             ("BVAR, looser prior", "bvar3", "bvar", dict(bv, lags=1, lambda1=0.2), "68%"),
             ("VAR, 4 variables", "var4", "var", {"vars": v4, "time": "year", "transform": "levels", "max_lags": 2, "horizon": 6}, "95%"),
             ("Local projections", "lp", "lp", {"y": r1, "shock": sh, "controls": ctrl, "time": "year", "lags": 1, "horizon": 6, "scale": "sd", "cov": "hac"}, "95%")]
    out = {"n": len(years), "years": [years[0], years[-1]], "vars": keys, "runs": [], "csv": T}
    for lab, key, mid, spec, lev in specs:
        rec = {"label": lab, "key": key, "model": mid, "level": lev, "error": None, "irf": {}}
        try:
            r = oes_engine.run(mid, T, spec)
            if r.get("error"): rec["error"] = str(r["error"])[:200]
            else:
                for rs in t["resp"]:
                    if mid == "lp":
                        if rs == r1: c = r["charts"][0]; bb = c.get("band"); rec["irf"][rs] = {"x": c["x"], "y": c["series"][0]["y"], "lo": bb["lo"] if bb else None, "hi": bb["hi"] if bb else None}
                    else:
                        v = irf(r, rs, sh)
                        if v: rec["irf"][rs] = v
        except Exception as e: rec["error"] = "%s: %s" % (type(e).__name__, e)
        rec["spec"] = {k: v for k, v in spec.items() if k != "vars"} | {"vars": spec.get("vars")}
        out["runs"].append(rec)
    return out

def peer_table(t, S, P, L):
    rows = []
    for code, lab, good in t["peers"]:
        if code in P: pe = P[code]; bl = L[code]
        else: continue
        ps = {c: pe[c] for c in PEERS if c in pe and pe[c] and pe[c][1] is not None}
        if not ps or bl[1] is None: continue
        latest = {"BGD": bl[1]} | {c: v[1] for c, v in ps.items()}; yrs = {"BGD": bl[0]} | {c: v[0] for c, v in ps.items()}
        med = statistics.median([v[1] for v in ps.values()])
        old = bl[2]; chg = None if old is None else bl[1] - old
        pchg = [v[1] - v[2] for v in ps.values() if v[2] is not None]; pmed = statistics.median(pchg) if pchg else None
        rank = None
        if good: order = sorted(latest, key=lambda c: -good * latest[c]); rank = order.index("BGD") + 1
        lvl = None if not good else good * (bl[1] - med)
        if lvl is not None and abs(lvl) < 0.05 * abs(med): lvl = 0.0
        trd = None if (not good or chg is None) else good * (chg - (pmed if pmed is not None else 0))
        rows.append(dict(code=code, label=lab, good=good, latest=latest, years=yrs, med=med, chg=chg, pmed=pmed, rank=rank, n=len(latest), lvl=lvl, trd=trd, y0=bl[0]))
    return rows

def sig(v):
    if not v or not v.get("lo"): return None
    i = max(range(1, len(v["y"])), key=lambda j: abs(v["y"][j])); return i, v["y"][i], (v["lo"][i] > 0 or v["hi"][i] < 0)

def build(t, today):
    S, P, L = store(); keys, cols, years = dataset(t, S)
    if len(years) < 26: return None, "sample too short (%d)" % len(years)
    slug = t["id"] + "-" + today; out = ROOT / "briefs" / slug; out.mkdir(parents=True, exist_ok=True)
    M = run_models(t, keys, cols, years); PT = peer_table(t, S, P, L); sh, r1 = t["shock"], t["resp"][0]
    lab = lambda k: TP.POOL[k][2]
    def sn(k):
        x = lab(k).split(" (")[0]; x = x[len("Change in "):] if x.startswith("Change in ") else x
        return x[0].lower() + x[1:] if not x[:2].isupper() else x
    # fig1: stylised facts
    fig, ax = plt.subplots(2, 2, figsize=(6.8, 5.0)); ax = ax.ravel()
    for a, code in zip(ax, t["facts"]):
        s = S[code]; ys = sorted(y for y in s if y >= 1990); a.plot(ys, [s[y] for y in ys], color=[BLUE, NAVY, TEAL, GOLD][list(ax).index(a)], lw=1.6)
        nm = next((l for c, l, g in t["peers"] if c == code), code); a.set_title(nm, fontsize=8); a.set_xlim(1990, 2026)
    fig.text(0.5, -0.01, "Source: World Bank, World Development Indicators (retrieved 14 Nov 2026).", ha="center", fontsize=7.5, color="#444"); fig.tight_layout(); save(fig, out, "fig1_stylised_facts")
    # fig2: peers
    n = len(PT); nc = 3; nr = (n + nc - 1) // nc; fig, axs = plt.subplots(nr, nc, figsize=(6.9, 2.2 * nr), squeeze=False); axs = axs.ravel()
    for a, r in zip(axs, PT):
        cs = sorted(r["latest"], key=lambda c: r["latest"][c]); vals = [r["latest"][c] for c in cs]
        a.barh(range(len(cs)), vals, color=[RED if c == "BGD" else "#aab4bd" for c in cs]); a.set_yticks(range(len(cs))); a.set_yticklabels([c for c in cs], fontsize=7); a.set_title(r["label"], fontsize=7.2); a.grid(axis="y", visible=False); a.tick_params(axis="x", labelsize=7)
    for a in axs[n:]: a.axis("off")
    fig.text(0.5, -0.01, "Latest available year per country (see Table 2). Source: World Bank, World Development Indicators.", ha="center", fontsize=7.5, color="#444"); fig.tight_layout(); save(fig, out, "fig2_peer_comparison")
    # fig3: IRFs
    pl = [r for r in M["runs"] if not r["error"] and r1 in r["irf"]]
    if pl:
        nc = 3; nr = (len(pl) + 2) // 3; fig, axs = plt.subplots(nr, nc, figsize=(6.9, 2.3 * nr), squeeze=False); axs = axs.ravel()
        for a, r in zip(axs, pl):
            v = r["irf"][r1]; a.axhline(0, color="#222", lw=.8)
            if v.get("lo"): a.fill_between(v["x"], v["lo"], v["hi"], color=BLUE, alpha=.18, lw=0)
            a.plot(v["x"], v["y"], color=BLUE, lw=1.8); a.set_title("%s (%s band)" % (r["label"], r["level"]), fontsize=7.5); a.set_xticks(range(0, 7)); a.set_xlabel("Years after the shock", fontsize=7.5)
        for a in axs[len(pl):]: a.axis("off")
        fig.suptitle("Response of %s to a one-standard-deviation shock in %s" % (sn(r1), sn(sh)), fontsize=9, fontweight="bold", y=1.0)
        fig.text(0.5, -0.01, "Source: authors' estimates in Open Econometric Systems; annual data %d–%d." % tuple(M["years"]), ha="center", fontsize=7.5, color="#444"); fig.tight_layout(); save(fig, out, "fig3_impulse_responses")
    # ---- derived statements
    rows = []; nsig = 0; npos = 0; nok = 0
    for r in M["runs"]:
        if r["error"]: continue
        v = r["irf"].get(r1)
        if not v: continue
        nok += 1; g = sig(v)
        if g is None: continue
        i, pv, s_ = g; nsig += bool(s_); npos += (v["y"][1] > 0)
        rows.append((r["label"], f(v["y"][1], 2), "year %d: %s" % (i, f(pv, 2)), r["level"], "yes" if s_ else "no"))
    sign_agree = len({np.sign(float(r[1])) for r in rows if float(r[1]) != 0}) == 1
    worse = [p for p in PT if p["good"] and p["lvl"] is not None and p["lvl"] < 0 and p["trd"] is not None and p["trd"] < 0]
    mixed = [p for p in PT if p["good"] and p["lvl"] is not None and p["lvl"] < 0 and (p["trd"] is None or p["trd"] >= 0)]
    strong = [p for p in PT if p["good"] and p["lvl"] is not None and p["lvl"] >= 0]  # within 5% of, or above, the median
    failed = [r["label"] for r in M["runs"] if r["error"]]
    fmt = lambda p, v: (f(v / 1e9, 1) + " bn") if abs(v) >= 1e9 else ((f(v / 1e6, 1) + " m") if abs(v) >= 1e6 else (f(v, 2) if abs(v) < 100 else f(v, 0)))
    sd = {k: statistics.pstdev(cols[k].values()) for k in (sh, r1)}
    title = t["title"]
    def sent(p):
        tr_ = "" if p["chg"] is None else (", %s from %s %d" % ("up" if p["chg"] > 0 else "down", fmt(p, p["latest"]["BGD"] - p["chg"]), p["y0"] - 10) if False else "")
        return "<li><b>%s</b>: Bangladesh %s (%d), peer median %s; rank %d of %d%s.</li>" % (esc(p["label"]), fmt(p, p["latest"]["BGD"]), p["y0"], fmt(p, p["med"]), p["rank"], p["n"],
            "" if p["chg"] is None else "; change over ten years %s%s (peer median %s)" % ("+" if p["chg"] >= 0 else "", fmt(p, p["chg"]), "n/a" if p["pmed"] is None else ("+" if p["pmed"] >= 0 else "") + fmt(p, p["pmed"])))
    summary = ("Peer benchmarks and %d model specifications on %d variables (%d–%d) for %s. %s" % (
        nok, len(keys), M["years"][0], M["years"][1], t["sdesc"],
        ("Bangladesh is below the peer median and worsening on %d of %d indicators judged." % (len(worse), len([p for p in PT if p["good"]]))) if worse else
        ("Bangladesh is above the peer median on %d of %d indicators judged." % (len(strong), len([p for p in PT if p["good"]])))))
    A = lambda s_: "<p>%s</p>" % s_
    body = ['<p class="small muted">Tuhin G. M. Al Mamun and Dr Rahim Md Abdur · Statistical report · %s</p>' % today]
    body.append('<div class="note"><b>Abstract.</b> %s We benchmark Bangladesh against India, Pakistan, Sri Lanka, Viet Nam, Indonesia and Nepal using World Bank data, and estimate a %d-variable Bayesian VAR with vector autoregression and local-projection checks on annual data for %d–%d. %s Where the models cannot separate the effect from zero, we say so.</div>' % (
        esc(t["question"]), len(keys), M["years"][0], M["years"][1],
        ("Of %d estimated impulse responses, %d have a band that excludes zero at the peak." % (len(rows), nsig)) if rows else "No impulse response could be estimated."))
    kf = []
    for p in worse[:3] + mixed[:2] + strong[:2]: kf.append(sent(p))
    mod = ("<li><b>Models</b>: the response of %s to a shock in %s is %s across specifications; %d of %d bands exclude zero at the peak (Table 1).</li>" % (
        esc(sn(r1)), esc(sn(sh)), "of the same sign" if sign_agree else "of mixed sign", nsig, len(rows)) if rows else "")
    body.append("<h2>Key findings</h2><ul>%s%s</ul>" % ("".join(kf), mod))
    body.append("<h2>1. Question</h2>" + A(esc(t["question"]) + " We answer with official data, benchmarking against six regional peers and several estimators that make different assumptions; the results are reported whatever they show."))
    body.append("<h2>2. Data</h2>" + A("Annual series from the World Bank World Development Indicators for Bangladesh, retrieved on %s, years %d–%d (%d observations after transformation). The %d variables are: %s. Transformations: growth rates and percentage changes where the series is a level, first differences where it is a ratio." % (
        today, M["years"][0], M["years"][1], M["n"], len(keys), "; ".join(esc(lab(k)) for k in keys)))
        + A("Validation. Single compiled source for most series. " + ("Real GDP growth and CPI inflation were compared with the IMF DataMapper series for 2015–2025 (IMF: NGDP_RPCH, PCPIPCH); see the data-validation note in the Statistical report on inflation, the Taka and policy stance for the gaps found (up to 0.05 percentage points for GDP growth and 1.6 for inflation). " if ("gdp" in keys or "infl" in keys) else "The IMF DataMapper series cover only a few macro aggregates (GDP growth, inflation, current account) and do not overlap with the main series here, so these indicators rest on the World Bank compilation alone. ") + "Gaps in peer data are shown with the year used."))
    body.append("<h2>3. What the data show</h2>" + A("Figure 1 plots four headline series. Figure 2 and Table 2 compare Bangladesh with six peers on the latest available year; rank 1 is best on the direction indicated.")
        + '<figure><img src="%s/fig1_stylised_facts.png" alt="Headline series" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 1.</b> Headline series, 1990–latest.</figcaption></figure>' % slug
        + '<figure><img src="%s/fig2_peer_comparison.png" alt="Peer comparison" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 2.</b> Bangladesh (red) and six peers, latest year.</figcaption></figure>' % slug
        + '<div class="tbl"><table><thead><tr><th>Indicator</th><th>Bangladesh (year)</th><th>Peer median</th><th>Rank (1 = best)</th><th>Ten-year change, Bangladesh</th><th>Ten-year change, peer median</th></tr></thead><tbody>'
        + "".join("<tr><td>%s</td><td>%s (%d)</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (esc(p["label"]), fmt(p, p["latest"]["BGD"]), p["y0"], fmt(p, p["med"]), ("%d of %d" % (p["rank"], p["n"])) if p["rank"] else "n/a",
              "n/a" if p["chg"] is None else ("+" if p["chg"] >= 0 else "") + fmt(p, p["chg"]), "n/a" if p["pmed"] is None else ("+" if p["pmed"] >= 0 else "") + fmt(p, p["pmed"])) for p in PT)
        + '</tbody></table></div><p class="small muted"><b>Table 2.</b> Peer benchmarks. Peers: India, Pakistan, Sri Lanka, Viet Nam, Indonesia, Nepal.</p>')
    body.append("<h2>4. Empirical strategy</h2>" + A("We trace the response of %s to a shock in %s. Models, all run in Open Econometric Systems: (i) a Bayesian VAR with a Minnesota prior on %d variables (shock ordered first), with a variation in lag length and prior tightness; (ii) a four-variable VAR with a recursive ordering; (iii) local projections with Newey–West standard errors. The large system is possible only in the Bayesian model: an unrestricted VAR on %d variables with two lags has %d coefficients per equation for about %d usable observations, leaving too few degrees of freedom for reliable estimates. Recursive identification is an assumption; the responses are dynamic correlations conditional on the ordering, not causal effects." % (
        esc(sn(r1)), esc(sn(sh)), len(keys), len(keys), 2 * len(keys) + 1, M["n"])))
    if rows:
        body.append("<h2>5. Results</h2>" + A("Figure 3 shows the response to a one-standard-deviation shock (sd = %s, in the units of the shock series). The response one year after the shock is %s across specifications. %d of %d bands exclude zero at the largest response (Table 1). The BVAR bands are 68%% credible bands and the VAR and local-projection bands are 95%%, so they should not be compared directly." % (
            f(sd[sh], 2), "of the same sign" if sign_agree else "of mixed sign", nsig, len(rows)))
            + '<figure><img src="%s/fig3_impulse_responses.png" alt="Impulse responses" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 3.</b> Impulse responses. Bands: 68%% credible for BVAR, 95%% for VAR and local projections.</figcaption></figure>' % slug
            + '<div class="tbl"><table><thead><tr><th>Specification</th><th>Response after 1 year</th><th>Largest response</th><th>Band</th><th>Band excludes zero</th></tr></thead><tbody>' + "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r) for r in rows)
            + '</tbody></table></div><p class="small muted"><b>Table 1.</b> Response of %s to a shock in %s.</p>' % (esc(sn(r1)), esc(sn(sh))))
    else: body.append("<h2>5. Results</h2>" + A("No specification produced a usable impulse response on this sample, so the report rests on the descriptive and benchmark evidence."))
    body.append("<h2>6. Policy assessment</h2>")
    if worse: body.append("<h3>Where the record supports criticism</h3><p class=\"small muted\">Bangladesh is more than 5% below the peer median, and its ten-year change is worse than the peer median change.</p><ol>" + "".join(sent(p) for p in worse) + "</ol>")
    if mixed: body.append("<h3>Behind peers, but improving</h3><ul>" + "".join(sent(p) for p in mixed) + "</ul>")
    if strong: body.append("<h3>Where Bangladesh does well</h3><ul>" + "".join(sent(p) for p in strong) + "</ul>")
    if not worse: body.append("<p>On these indicators the record does not support a general criticism: there is no indicator on which Bangladesh is both below the peer median and deteriorating.</p>")
    body.append("<h3>Where the evidence is not strong enough</h3><ul><li>Dynamic effects: %s</li></ul>" % (
        "%d of %d impulse-response bands exclude zero, so the estimated effect of %s on %s cannot be stated precisely with annual data." % (nsig, len(rows), esc(sn(sh)), esc(sn(r1))) if nsig < len(rows) else "the estimated effect is distinguishable from zero in all specifications, but remains conditional on the ordering."))
    body.append("<h3>Implications for discussion</h3><p class=\"small muted\">Judgements drawn from the record, not estimates.</p><ul>%s</ul>" % "".join("<li>%s</li>" % esc(d) for d in t["disc"]))
    body.append("<h2>7. Limitations</h2><ul><li>Annual data give about %d observations; responses at one to six years are fragile.</li><li>Recursive identification is an assumption, not a result.</li><li>Peer comparisons use each country's latest year, which differs for some indicators; ten-year changes use the year ten years before the latest.</li><li>Peer groups reflect economies of comparable region or size and are a choice; other groups could change ranks.</li>%s</ul>" % (
        M["n"], "<li>Models that did not run on this sample (%s) are not reported.</li>" % esc(", ".join(failed)) if failed else ""))
    body.append("<h2>Data and replication</h2><ul><li><a href=\"%s/data.csv\">data.csv</a> (%d variables)</li><li><a href=\"%s/results.json\">results.json</a></li><li>Figures at 300 dpi (PNG) and vector (SVG) in the same folder: fig1_stylised_facts, fig2_peer_comparison%s.</li></ul><h3>Sources</h3><ul><li>World Bank, World Development Indicators: <a href=\"https://api.worldbank.org/v2/country/BGD\">api.worldbank.org</a>, retrieved %s.</li><li>Models: Open Econometric Systems, <a href=\"https://github.com/tuhingm/open-econometric-systems\">github.com/tuhingm/open-econometric-systems</a>.</li></ul>" % (
        slug, len(keys), slug, ", fig3_impulse_responses" if pl else "", today))
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%s | BIQEP Policy Briefs</title><meta name="description" content="%s"><meta name="author" content="Tuhin G. M. Al Mamun">'
        '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><meta name="theme-color" content="#10283f"><meta property="og:title" content="%s"><meta property="og:type" content="article"><meta property="og:image" content="https://tuhingm.github.io/biqep-policy/briefs/%s/fig2_peer_comparison.png"><meta name="twitter:card" content="summary_large_image">'
        '<link rel="canonical" href="https://tuhingm.github.io/biqep-policy/briefs/%s.html"><script type="application/ld+json">%s</script><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="../assets/style.css"></head>\n'
        '<body><div id="hdr"></div>\n<main id="main">\n<section class="pagehead"><div class="wrap"><div class="crumbs"><a href="../index.html">Home</a><i>/</i><a href="index.html">Policy briefs</a><i>/</i>Statistical report</div><div class="eyebrow">Statistical report</div><h1>%s</h1><p class="lede">%s</p></div></section>\n'
        '<section class="sec"><div class="wrap"><div class="content" style="max-width:900px">%s</div></div></section>\n</main>\n<div id="ftr"></div>\n<script src="../assets/data.js"></script><script src="../assets/pages.js"></script><script src="../assets/site.js" data-root="../"></script></body></html>\n') % (
        esc(title), esc(summary), esc(title), slug, slug, json.dumps({"@context": "https://schema.org", "@type": "ScholarlyArticle", "headline": title, "description": summary, "datePublished": today,
        "author": [{"@type": "Person", "name": "Tuhin G. M. Al Mamun", "url": "https://tuhingm.github.io/biqep-policy/tuhin-al-mamun/"}, {"@type": "Person", "name": "Dr Rahim Md Abdur"}], "publisher": {"@type": "Organization", "name": "BIQEP Policy Briefs"}}, ensure_ascii=False),
        esc(title), esc(summary), "\n".join(body))
    (ROOT / "briefs" / (slug + ".html")).write_text(page, encoding="utf-8"); (out / "data.csv").write_text(M["csv"]); M2 = {k: v for k, v in M.items() if k != "csv"}
    (out / "results.json").write_text(json.dumps({"retrieved": today, **M2, "peers": PT}, indent=1, default=str))
    return {"slug": slug, "title": title, "date": today, "topic": t["area"], "type": t["type"], "status": "published", "summary": summary}, "ok n=%d vars=%d sig=%d/%d worse=%d fails=%s" % (M["n"], len(keys), nsig, len(rows), len(worse), failed)

if __name__ == "__main__":
    today = datetime.date.today().isoformat(); only = sys.argv[1] if len(sys.argv) > 1 else None
    for t in TP.TOPICS:
        if only and t["id"] != only: continue
        rec, msg = build(t, today); print(t["id"], msg)
        if rec: print(json.dumps(rec))
