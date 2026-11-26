"""Build the full policy report (text, tables, 300-dpi figures) from validated data and OES results."""
import json, pathlib, html, datetime, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import study
ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / "pipeline" / "data"
esc = html.escape
NAVY, BLUE, TEAL, GOLD, RED, GREY = "#10283f", "#0033a0", "#168b88", "#c6a15b", "#b5372c", "#6b7885"
plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#444", "axes.linewidth": .8, "axes.titlesize": 9.5, "axes.titleweight": "bold", "legend.frameon": False,
                     "savefig.dpi": 300, "figure.dpi": 150, "axes.grid": True, "grid.color": "#e3e7ea", "grid.linewidth": .6})

def save(fig, outdir, name):
    fig.savefig(outdir / (name + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(outdir / (name + ".svg"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

def build(today=None):
    today = today or datetime.date.today().isoformat()
    slug = "inflation-taka-and-policy-stance-" + today
    out = ROOT / "briefs" / slug; out.mkdir(parents=True, exist_ok=True)
    w = study.load(); R = json.loads((D / "study_results.json").read_text()); I = R["irf"]; runs = R["runs"]
    cpi, fx, lend, dep = w["FP.CPI.TOTL.ZG"], w["PA.NUS.FCRF"], w["FR.INR.LEND"], w["FR.INR.DPST"]
    res = {y: v / 1e9 for y, v in w["FI.RES.TOTL.CD"].items()}
    gdp, credit, inv = w["NY.GDP.MKTP.KD.ZG"], w["FS.AST.PRVT.GD.ZS"], w["NE.GDI.TOTL.ZS"]
    rev = w["GC.REV.XGRT.GD.ZS"]
    rl = {y: lend[y] - cpi[y] for y in lend}; rd = {y: dep[y] - cpi[y] for y in dep}
    y0, y1 = 1992, 2025

    # ---- Figure 1: stylised facts
    fig, ax = plt.subplots(2, 2, figsize=(6.8, 5.2)); ax = ax.ravel()
    ys = sorted(cpi); ax[0].plot(ys, [cpi[y] for y in ys], color=BLUE, lw=1.6); ax[0].set_title("A. CPI inflation (% per year)")
    ys = sorted(fx); ax[1].plot(ys, [fx[y] for y in ys], color=NAVY, lw=1.6); ax[1].set_title("B. Official exchange rate (Taka per US$)")
    ys = sorted(res); ax[2].plot(ys, [res[y] for y in ys], color=TEAL, lw=1.6); ax[2].set_title("C. Total reserves (US$ billion)")
    ys = sorted(lend); ax[3].plot(ys, [lend[y] for y in ys], color=GOLD, lw=1.6, label="Lending rate"); ax[3].plot(ys, [dep[y] for y in ys], color=GREY, lw=1.6, label="Deposit rate")
    ax[3].plot(ys, [cpi[y] for y in ys], color=BLUE, lw=1.1, ls="--", label="CPI inflation"); ax[3].legend(fontsize=7.5); ax[3].set_title("D. Interest rates and inflation (%)")
    for a in ax: a.axvspan(2021.5, 2025.5, color="#f3e7d0", alpha=.55, lw=0); a.set_xlim(1990, 2025.5)
    fig.text(0.5, -0.01, "Source: World Bank, World Development Indicators (retrieved 14 Nov 2026). Shaded: 2022–2025.", ha="center", fontsize=7.5, color="#444")
    fig.tight_layout(); save(fig, out, "fig1_stylised_facts")

    # ---- Figure 2: real rates
    fig, ax = plt.subplots(figsize=(6.8, 3.2)); yrs = list(range(2012, 2026)); import numpy as np
    x = np.arange(len(yrs)); ax.bar(x - .2, [rl[y] for y in yrs], .4, color=GOLD, label="Real lending rate"); ax.bar(x + .2, [rd[y] for y in yrs], .4, color=BLUE, label="Real deposit rate")
    ax.axhline(0, color="#222", lw=.8); ax.set_xticks(x); ax.set_xticklabels(yrs, rotation=45); ax.set_ylabel("Percentage points"); ax.legend(ncol=2, fontsize=8)
    ax.set_title("Real interest rates: nominal rate minus CPI inflation")
    fig.text(0.5, -0.04, "Source: World Bank, World Development Indicators; authors' calculation.", ha="center", fontsize=7.5, color="#444")
    fig.tight_layout(); save(fig, out, "fig2_real_rates")

    # ---- Figure 3: IRF inflation to depreciation shock
    panels = [("A. VAR, 3 variables", "var3|infl<-fx_dep", "95%"), ("B. VAR, 5 variables", "var5_fx|infl<-fx_dep", "95%"), ("C. Local projections", "lp|infl", "95%"),
              ("D. BVAR, 13 variables", "bvar13_fx|infl<-fx_dep", "68%"), ("E. BVAR, 2 lags", "bvar13_fx_l2|infl<-fx_dep", "68%"), ("F. BVAR, looser prior", "bvar13_fx_tight|infl<-fx_dep", "68%")]
    fig, axs = plt.subplots(2, 3, figsize=(6.9, 4.6), sharex=True); axs = axs.ravel()
    for a, (t, key, lev) in zip(axs, panels):
        v = I[key]; h = v["x"]; a.axhline(0, color="#222", lw=.8)
        if v.get("lo"): a.fill_between(h, v["lo"], v["hi"], color=BLUE, alpha=.18, lw=0)
        a.plot(h, v["y"], color=BLUE, lw=1.8); a.set_title(t + " (" + lev + " band)", fontsize=8); a.set_xticks(range(0, 7))
    for a in axs[3:]: a.set_xlabel("Years after the shock")
    for a in (axs[0], axs[3]): a.set_ylabel("Inflation, pp")
    fig.suptitle("Response of inflation to a one-standard-deviation depreciation of the Taka", fontsize=10, fontweight="bold", y=1.0)
    fig.text(0.5, -0.02, "Source: authors' estimates in Open Econometric Systems; annual data 1992–2025.", ha="center", fontsize=7.5, color="#444")
    fig.tight_layout(); save(fig, out, "fig3_irf_depreciation")

    # ---- Figure 4: policy rate shock
    pan = [("A. VAR, 5 variables", "var5_mp|infl<-lend", "95%"), ("B. Local projections", "lp_mp|infl", "95%"), ("C. BVAR, 13 variables", "bvar13_mp|infl<-lend", "68%")]
    fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.7), sharex=True)
    for a, (t, key, lev) in zip(axs, pan):
        v = I[key]; h = v["x"]; a.axhline(0, color="#222", lw=.8)
        if v.get("lo"): a.fill_between(h, v["lo"], v["hi"], color=GOLD, alpha=.3, lw=0)
        a.plot(h, v["y"], color=NAVY, lw=1.8); a.set_title(t + " (" + lev + ")", fontsize=8); a.set_xlabel("Years after the shock"); a.set_xticks(range(0, 7))
    axs[0].set_ylabel("Inflation, pp")
    fig.suptitle("Response of inflation to a one-standard-deviation rise in the lending rate", fontsize=10, fontweight="bold", y=1.04)
    fig.tight_layout(); save(fig, out, "fig4_irf_lending_rate")

    # ---- Figure 5: variance decomposition (VAR5)
    fe = next(t for t in runs["var5_fx"]["tables"] if "variance" in t["title"].lower())
    names = ["fx_dep", "infl", "money", "gdp", "lend"]; lab = {"fx_dep": "Depreciation", "infl": "Inflation", "money": "Broad money", "gdp": "GDP growth", "lend": "Lending rate"}
    row = next(r for r in fe["rows"] if r[0] == "infl"); vals = row[1:6]
    fig, ax = plt.subplots(figsize=(6.0, 2.2)); left = 0
    for n, v, c in zip(names, vals, [GOLD, BLUE, TEAL, NAVY, GREY]):
        ax.barh([0], [v], left=left, color=c, label=lab[n] + " (%.1f%%)" % v); left += v
    ax.set_yticks([]); ax.set_xlim(0, 100); ax.set_xlabel("Share of the six-year forecast-error variance of inflation (%)"); ax.legend(ncol=3, fontsize=7.5, loc="upper center", bbox_to_anchor=(.5, 1.5))
    ax.grid(False); fig.tight_layout(); save(fig, out, "fig5_variance_decomposition")

    # ---- numbers used in the text
    f = lambda v, d=1: ("%." + str(d) + "f") % v
    neg_lend = [y for y in range(2022, 2026) if rl[y] < 0]; neg_dep = [y for y in range(2022, 2026) if rd[y] < 0]
    res_pk_y = max(res, key=lambda y: res[y] if y <= 2025 else -1)
    fx_chg = 100 * (fx[2025] / fx[2021] - 1); res_fall = 100 * (1 - res[2024] / res[2021])
    def peak(k):
        v = I[k]; i = max(range(1, len(v["y"])), key=lambda j: abs(v["y"][j])); sig = (v["lo"][i] > 0 or v["hi"][i] < 0) if v.get("lo") else None
        return i, v["y"][i], sig
    rows = []
    for lbl, key, lev in [("VAR, 3 variables", "var3|infl<-fx_dep", "95%"), ("VAR, 5 variables", "var5_fx|infl<-fx_dep", "95%"), ("Local projections", "lp|infl", "95%"),
                          ("BVAR, 13 variables", "bvar13_fx|infl<-fx_dep", "68%"), ("BVAR, 2 lags", "bvar13_fx_l2|infl<-fx_dep", "68%"), ("BVAR, looser prior", "bvar13_fx_tight|infl<-fx_dep", "68%")]:
        i, pv, sg = peak(key); v = I[key]
        rows.append((lbl, f(v["y"][1], 2), "year %d: %s" % (i, f(pv, 2)), lev, "yes" if sg else "no"))
    n_sig = sum(1 for r in rows if r[4] == "yes")
    fevd_own = vals[1]; fevd_fx = vals[0]
    lp_sig_h = [h for h in range(1, 7) if I["lp|infl"]["lo"][h] > 0 or I["lp|infl"]["hi"][h] < 0]

    title = "Inflation, the Taka and the stance of policy in Bangladesh, 1992–2025"
    summary = ("Inflation rose to %s%% in %d while lending rates stayed below it in each of the four years from 2022 to 2025. Nine econometric estimates, "
               "using 13 official macro variables, find a positive but imprecisely estimated pass-through from Taka depreciation to inflation." % (f(cpi[2024]), 2024))
    A = lambda s: "<p>%s</p>" % s
    body = []
    body.append('<p class="small muted">Tuhin G. M. Al Mamun and Dr Rahim Md Abdur · Statistical report · %s</p>' % today)
    body.append('<div class="note"><b>Abstract.</b> Consumer-price inflation in Bangladesh reached %s%% in 2023 and %s%% in 2024, up from %s%% in 2021, while the Taka lost %s%% of its value against the US dollar between 2021 and 2025 and reserves fell by %s%% from 2021 to 2024. '
                'Using 13 annual macroeconomic series from 1992 to 2025, we estimate vector autoregressions, local projections and Bayesian VARs. A depreciation shock of one standard deviation raises inflation in every specification at the one-year horizon, but only %d of the six impulse responses exclude zero at their stated confidence level, and inflation is overwhelmingly driven by its own past (%s%% of its forecast-error variance). '
                'The descriptive record is clearer than the estimates: lending rates were below inflation in %s, and deposit rates in %s. Annual data are too short to settle the size of pass-through; monthly series are needed.</div>' % (
                f(cpi[2023]), f(cpi[2024]), f(cpi[2021]), f(fx_chg, 0), f(res_fall, 0), n_sig, f(fevd_own, 0), ", ".join(map(str, neg_lend)), ", ".join(map(str, neg_dep))))
    body.append("<h2>Key findings</h2><ul>"
                "<li>Real lending rates were negative in %s, and real deposit rates in %s (Figure 2).</li>"
                "<li>The Taka depreciated %s%% between 2021 and 2025 (from %s to %s per US$), and reserves fell from US$%s billion in 2021 to US$%s billion in 2024 before recovering to US$%s billion in 2025.</li>"
                "<li>In the econometric models, pass-through from depreciation to inflation is positive but imprecise; %d of 6 specifications show a response whose band excludes zero (Table 1).</li>"
                "<li>Private credit fell from %s%% of GDP in 2015 to %s%% in 2025, and real GDP growth slowed from %s%% in 2019 to %s%% in 2025.</li></ul>" % (
                ", ".join(map(str, neg_lend)), ", ".join(map(str, neg_dep)), f(fx_chg, 0), f(fx[2021]), f(fx[2025]), f(res[2021]), f(res[2024]), f(res[2025]), n_sig, f(credit[2015]), f(credit[2025]), f(gdp[2019]), f(gdp[2025])))
    body.append("<h2>1. Introduction</h2>" + A("Bangladesh entered the 2020s with stable, moderate inflation. Between 2021 and 2024 inflation nearly doubled, the exchange rate adjusted sharply and reserves declined. This report asks two questions that bear directly on policy. First, how much of the rise in prices can be traced to the depreciation of the Taka? Second, did the stance of interest-rate policy lean against inflation, or follow it? We answer both with official data, several estimators that make different assumptions, and a fixed rule: the estimates are reported whatever they show.")
                + A("The contribution is a transparent assessment on a common dataset. We use 13 series from a single compiled source, check overlapping series against a second source, and run the same question through nine specifications in the open Open Econometric Systems engine, so that every number can be reproduced."))
    body.append("<h2>2. Data</h2>" + A("All series are annual, 1992–2025 (34 annual observations, 33 usable after one lag), from the World Bank World Development Indicators for Bangladesh, retrieved on %s. The variables are: CPI inflation; the official exchange rate (Taka per US$), transformed to annual percentage depreciation; total reserves, in annual growth; real GDP growth; private consumption growth; and the annual change in the investment, export and import ratios to GDP, the deposit rate, the lending rate, broad money to GDP, private credit to GDP and the unemployment rate." % today)
                + "<h3>Validation</h3>" + A("Real GDP growth was compared with the IMF DataMapper series for 2015–2025: the largest difference is 0.05 percentage points. CPI inflation differs between the two sources by up to 1.6 percentage points (largest in 2022, when the World Bank series is 1.6 points above the IMF series); the series are compiled on different annual bases, and we use the World Bank series throughout, noting that the level of 2022–2025 inflation depends on the source. The current-account balance differs by up to 2.7 percentage points of GDP, so it is <b>not used</b>. Remittances were not retrievable and are not used.")
                + '<div class="tbl"><table><thead><tr><th>Check</th><th>Sources</th><th>Largest gap</th><th>Status</th></tr></thead><tbody>'
                  '<tr><td>Real GDP growth, 2015–2025</td><td>World Bank vs IMF</td><td>0.05 pp</td><td>Agrees</td></tr>'
                  '<tr><td>CPI inflation, 2015–2025</td><td>World Bank vs IMF</td><td>1.6 pp</td><td>Differs; World Bank used, disclosed</td></tr>'
                  '<tr><td>Current account, 2015–2025</td><td>World Bank vs IMF</td><td>2.7 pp</td><td>Differs; not used</td></tr>'
                  '<tr><td>All other series</td><td>World Bank only</td><td>n/a</td><td>Single compiled source</td></tr></tbody></table></div>')
    body.append("<h2>3. What the data show</h2>" + A("Figure 1 shows the record. Inflation stayed between %s%% and %s%% from 2012 to 2021, then rose to %s%% in 2023 and %s%% in 2024, easing to %s%% in 2025. The Taka stood at %s per dollar in 2021 and %s in 2025. Reserves peaked at US$%s billion in %d and had fallen to US$%s billion by 2024." % (
                f(min(cpi[y] for y in range(2012, 2022))), f(max(cpi[y] for y in range(2012, 2022))), f(cpi[2023]), f(cpi[2024]), f(cpi[2025]), f(fx[2021]), f(fx[2025]), f(res[res_pk_y]), res_pk_y, f(res[2024])))
                + '<figure><img src="%s/fig1_stylised_facts.png" alt="Four panels: inflation, exchange rate, reserves, interest rates" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 1.</b> Inflation, the exchange rate, reserves and interest rates. High-resolution PNG and SVG are available in the replication files.</figcaption></figure>' % slug
                + A("Figure 2 turns the interest-rate panel into real rates. The real lending rate was %s percentage points in 2022, %s in 2023, %s in 2024 and %s in 2025. The real deposit rate was %s, %s, %s and %s over the same years. Savers therefore earned less than inflation for three consecutive years, and borrowers faced lending rates below inflation in each of the four years." % (
                f(rl[2022], 2), f(rl[2023], 2), f(rl[2024], 2), f(rl[2025], 2), f(rd[2022], 2), f(rd[2023], 2), f(rd[2024], 2), f(rd[2025], 2)))
                + '<figure><img src="%s/fig2_real_rates.png" alt="Real lending and deposit rates, 2012 to 2025" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 2.</b> Real interest rates, 2012–2025.</figcaption></figure>' % slug)
    body.append("<h2>4. Empirical strategy</h2>" + A("We estimate the response of inflation to two shocks: a depreciation of the Taka and a rise in the lending rate. Each is traced through three families of models, all run in Open Econometric Systems. (i) Reduced-form vector autoregressions with a recursive (Cholesky) ordering, in a three-variable and a five-variable version. (ii) Local projections with Newey–West standard errors, controlling for GDP growth, the lending rate and broad money. (iii) Bayesian VARs with a Minnesota prior on all 13 variables, which shrink the large system toward a stationary benchmark, with variations in lag length and prior tightness. The use of 13 variables is possible only in the Bayesian system: an unrestricted VAR on 13 variables with two lags has 27 coefficients per equation for 33 observations, leaving too few degrees of freedom, so adding variables there would make the estimates less, not more, reliable.")
                + A("<b>Identification.</b> Recursive identification assumes that the shocked variable is not affected within the year by the variables ordered after it. For the depreciation shock this places the exchange rate first; for the lending-rate shock the rate is placed first. These are strong assumptions. The estimates describe dynamic correlations conditional on the ordering and should not be read as causal effects."))
    body.append("<h2>5. Results</h2><h3>5.1 Pass-through from depreciation to inflation</h3>" + A("Figure 3 shows the response of inflation to a one-standard-deviation depreciation shock (about 4 percentage points). In all six specifications the response one year after the shock is positive, between %s and %s percentage points. The effect is imprecise: %d of the six responses have a band that excludes zero at the peak (Table 1). In the local projections, the response is individually significant at only %s of six horizons." % (
                f(min(float(r[1]) for r in rows), 2), f(max(float(r[1]) for r in rows), 2), n_sig, "one" if len(lp_sig_h) == 1 else str(len(lp_sig_h)))
                + (" (year %d)" % lp_sig_h[0] if len(lp_sig_h) == 1 else ""))
                + '<figure><img src="%s/fig3_irf_depreciation.png" alt="Impulse responses of inflation to a depreciation shock in six specifications" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 3.</b> Response of inflation to a one-standard-deviation depreciation. Bands: 95%% for VAR and local projections, 68%% credible for BVAR.</figcaption></figure>' % slug
                + '<div class="tbl"><table><thead><tr><th>Specification</th><th>Response after 1 year (pp)</th><th>Largest response</th><th>Band</th><th>Band excludes zero at peak</th></tr></thead><tbody>'
                + "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r) for r in rows) + "</tbody></table></div><p class=\"small muted\"><b>Table 1.</b> Inflation response to a depreciation shock across specifications.</p>"
                + A("The Bayesian systems give smaller responses than the unrestricted VARs. This follows from shrinkage: the Minnesota prior pulls cross-variable effects toward zero, and loosening the prior from λ₁ = 0.1 to 0.2 roughly doubles the peak response. The BVAR bands are 68% credible bands, which are narrower than 95% bands and should be compared with that in mind."))
    body.append("<h3>5.2 Interest rates and inflation</h3>" + A("Figure 4 shows the response of inflation to a rise in the lending rate. The sign is not stable across specifications and the bands include zero throughout. With annual data and a policy rate that moves in few discrete steps, the data do not support a precise estimate of how interest-rate changes feed into inflation in Bangladesh.")
                + '<figure><img src="%s/fig4_irf_lending_rate.png" alt="Impulse responses of inflation to a lending-rate shock" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 4.</b> Response of inflation to a one-standard-deviation rise in the lending rate.</figcaption></figure>' % slug)
    body.append("<h3>5.3 What drives inflation</h3>" + A("Figure 5 decomposes the six-year forecast-error variance of inflation in the five-variable VAR. Inflation's own past accounts for %s%%, depreciation for %s%%, and the other three variables for the remaining %s%%. High persistence is the dominant feature of the series." % (f(fevd_own, 1), f(fevd_fx, 1), f(100 - fevd_own - fevd_fx, 1)))
                + '<figure><img src="%s/fig5_variance_decomposition.png" alt="Variance decomposition of inflation" style="width:100%%;height:auto"><figcaption class="small muted"><b>Figure 5.</b> Forecast-error variance decomposition of inflation.</figcaption></figure>' % slug)
    body.append("<h2>6. Policy assessment</h2>" + A("The assessment below separates what the data show from what the models can support.")
                + "<h3>Areas for policy attention</h3><ol>"
                "<li><b>Interest rates trailed inflation.</b> Lending rates were below inflation in %s and deposit rates in %s. Whatever the reason, the effect was to leave real borrowing costs near or below zero while prices were rising fastest.</li>"
                "<li><b>External buffers were run down.</b> A %s%% depreciation and a %s%% fall in reserves between 2021 and 2024 show that the external adjustment was large and concentrated in a short period.</li>"
                "<li><b>Credit and investment weakened.</b> Private credit fell from %s%% of GDP (2015) to %s%% (2025) and investment from %s%% of GDP (2019) to %s%% (2025). These are correlations with the tightening and the external stress, not estimated effects.</li>"
                "<li><b>Public revenue stays low.</b> Central-government revenue was %s%% of GDP in 2021, the latest year available, and never exceeded %s%% in 2001–2021, leaving limited room for fiscal support.</li></ol>" % (
                ", ".join(map(str, neg_lend)), ", ".join(map(str, neg_dep)), f(fx_chg, 0), f(res_fall, 0), f(credit[2015]), f(credit[2025]), f(inv[2019]), f(inv[2025]), f(rev[2021]), f(max(rev.values()))) 
                + "<h3>Where the evidence is not strong enough</h3>" + "<ul><li>The precise size of exchange-rate pass-through. The estimates are positive but imprecise, and a critic or defender of the exchange-rate policy cannot rely on them.</li><li>The effect of interest-rate changes on inflation. The responses are statistically indistinguishable from zero in every specification.</li></ul>"
                + "<h3>Implications for discussion</h3><p class=\"small muted\">These are judgements drawn from the record above, not estimates.</p><ul>"
                "<li>Publishing a real-rate benchmark alongside each rate decision would make the stance of policy easy to judge.</li>"
                "<li>Gradual exchange-rate adjustment, announced in advance, would avoid concentrating the price effects in a short period.</li>"
                "<li>Reserve adequacy and the pace of adjustment should be reported together so that depreciation is not read in isolation.</li>"
                "<li>Monthly price, wage and exchange-rate series from the Bangladesh Bureau of Statistics and Bangladesh Bank should be used to estimate pass-through, because annual data cannot do it.</li></ul>")
    body.append("<h2>7. Limitations</h2><ul><li>Annual data give 33 observations. Responses at one to six years are fragile, and the unrestricted VARs are small systems for that reason.</li>"
                "<li>Recursive identification is an assumption, not a result. The results are conditional on the ordering.</li>"
                "<li>Inflation differs by source (up to 1.6 percentage points). The level of 2022–2025 inflation depends on the choice of source.</li>"
                "<li>Reserves and the exchange rate are year averages or year-end values as published; intra-year movements are not captured.</li>"
                "<li>The ARDL bounds test and the structural VAR with bootstrap bands could not be run on this sample (an engine error for the first, too few observations for the second), and are not reported.</li></ul>")
    body.append("<h2>Data and replication</h2><ul>"
                "<li>Dataset (13 variables): <a href=\"%s/data.csv\">data.csv</a></li><li>Model specifications and full results: <a href=\"%s/results.json\">results.json</a></li>"
                "<li>Figures at 300 dpi: <a href=\"%s/fig1_stylised_facts.png\">1</a>, <a href=\"%s/fig2_real_rates.png\">2</a>, <a href=\"%s/fig3_irf_depreciation.png\">3</a>, <a href=\"%s/fig4_irf_lending_rate.png\">4</a>, <a href=\"%s/fig5_variance_decomposition.png\">5</a>; vector versions (SVG) in the same folder.</li></ul>" % ((slug,) * 7)
                + "<h3>Sources</h3><ul><li>World Bank, World Development Indicators, Bangladesh: <a href=\"https://api.worldbank.org/v2/country/BGD\">api.worldbank.org</a>, retrieved %s.</li><li>International Monetary Fund, DataMapper: <a href=\"https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/BGD\">imf.org</a>, retrieved %s.</li><li>Models: Open Econometric Systems, <a href=\"https://github.com/tuhingm/open-econometric-systems\">github.com/tuhingm/open-econometric-systems</a>.</li></ul>" % (today, today))
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s | BIQEP Policy Briefs</title><meta name="description" content="%s"><meta name="author" content="Tuhin G. M. Al Mamun">'
            '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><meta name="theme-color" content="#10283f">'
            '<meta property="og:title" content="%s"><meta property="og:type" content="article"><meta property="og:image" content="https://biqep.github.io/institute/briefs/%s/fig3_irf_depreciation.png"><meta name="twitter:card" content="summary_large_image">'
            '<link rel="canonical" href="https://biqep.github.io/institute/briefs/%s.html"><script type="application/ld+json">%s</script>%s<link rel="stylesheet" href="../assets/style.css"></head>\n'
            '<body><div id="hdr"></div>\n<main id="main">\n<section class="pagehead"><div class="wrap"><div class="crumbs"><a href="../index.html">Home</a><i>/</i><a href="index.html">Policy briefs</a><i>/</i>Statistical report</div><div class="eyebrow">Statistical report</div><h1>%s</h1><p class="lede">%s</p></div></section>\n'
            '<section class="sec"><div class="wrap"><div class="content" style="max-width:900px">%s</div></div></section>\n</main>\n<div id="ftr"></div>\n'
            '<script src="../assets/data.js"></script><script src="../assets/pages.js"></script><script src="../assets/site.js" data-root="../"></script></body></html>\n') % (
            esc(title), esc(summary), esc(title), slug, slug,
            json.dumps({"@context": "https://schema.org", "@type": "ScholarlyArticle", "headline": title, "description": summary, "datePublished": today,
                        "author": [{"@type": "Person", "name": "Tuhin G. M. Al Mamun", "url": "https://biqep.github.io/institute/tuhin-al-mamun/"}, {"@type": "Person", "name": "Dr Rahim Md Abdur"}],
                        "publisher": {"@type": "Organization", "name": "BIQEP Policy Briefs"}}, ensure_ascii=False),
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">',
            esc(title), esc(summary), "\n".join(body))
    (ROOT / "briefs" / (slug + ".html")).write_text(page, encoding="utf-8")
    (out / "data.csv").write_text(R["csv"], encoding="utf-8")
    (out / "results.json").write_text(json.dumps({"retrieved": today, "runs": runs, "irf": I}, indent=1, default=str), encoding="utf-8")
    return {"slug": slug, "title": title, "date": today, "topic": "Monetary policy", "type": "Statistical report", "status": "published", "summary": summary}

if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
