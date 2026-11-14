import os, json, pathlib
R = str(pathlib.Path(__file__).resolve().parents[1])
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700&family=IBM+Plex+Mono:wght@400;500&family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">')
PAGES = []   # for search
URLS = []    # for sitemap

def rootof(path):
    d = path.count("/")
    return "../" * d if d else "./"

SITE = "https://tuhingm.github.io/biqep-policy/"
PERSON = {"@type": "Person", "@id": SITE + "people/#tuhin", "name": "Tuhin G. M. Al Mamun", "honorificPrefix": "Dr.",
          "jobTitle": "Founder and Executive Director, BIQEP", "url": SITE + "people/",
          "alumniOf": {"@type": "CollegeOrUniversity", "name": "Hannam University"},
          "nationality": {"@type": "Country", "name": "Bangladesh"},
          "knowsAbout": ["Monetary policy transmission", "Bayesian econometrics", "Time-series econometrics", "DSGE and heterogeneous-agent models", "Bangladesh economy"],
          "sameAs": ["https://tuhingm.github.io/almamun/", "https://github.com/tuhingm"]}
ORG = {"@type": "Organization", "@id": SITE + "#org", "name": "Bangladesh Institute of Quantitative Economics and Public Policy",
       "alternateName": ["BIQEP", "BIQEP Policy Briefs"], "url": SITE, "logo": SITE + "assets/og-image.png",
       "founder": {"@id": SITE + "people/#tuhin"}, "sameAs": ["https://tuhingm.github.io/almamun/oes/"]}
SITE_LD = {"@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": "BIQEP Policy Briefs", "inLanguage": "en",
           "publisher": {"@id": SITE + "#org"}, "author": {"@id": SITE + "people/#tuhin"}}

def page(path, title, desc, body, section="Site", search=True):
    root = rootof(path)
    canon = path.replace("index.html", "")
    url = SITE + canon
    full_title = ("BIQEP Policy Briefs: Bangladesh Economy | Tuhin G. M. Al Mamun" if path == "index.html"
                  else f"{title} | BIQEP Policy Briefs")
    graph = [ORG, SITE_LD, PERSON]
    parts = path.split("/")
    if len(parts) >= 2 and path != "404.html":
        crumbs_ld = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE}]
        if len(parts) >= 3:
            crumbs_ld.append({"@type": "ListItem", "position": 2, "name": section, "item": SITE + parts[0] + "/"})
        crumbs_ld.append({"@type": "ListItem", "position": len(crumbs_ld) + 1, "name": title, "item": url})
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs_ld})
    graph.append({"@type": "WebPage", "@id": url + "#page", "url": url, "name": full_title, "description": desc,
                  "isPartOf": {"@id": SITE + "#website"}, "author": {"@id": SITE + "people/#tuhin"}, "inLanguage": "en"})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    robots = "noindex,follow" if path in ("404.html", "search/index.html") else "index,follow,max-snippet:-1,max-image-preview:large"
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Tuhin G. M. Al Mamun">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#10283f">
<meta property="og:site_name" content="BIQEP Policy Briefs"><meta property="og:locale" content="en_US">
<meta property="og:title" content="{full_title}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}assets/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{full_title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="{SITE}assets/og-image.png">
<link rel="canonical" href="{url}">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<script type="application/ld+json">{ld}</script>
{FONTS}<link rel="stylesheet" href="{root}assets/style.css"></head>
<body><div id="hdr"></div>
<main id="main">
{body}
</main>
<div id="ftr"></div>
<script src="{root}assets/data.js"></script><script src="{root}assets/pages.js"></script><script src="{root}assets/site.js" data-root="{root}"></script></body></html>
'''
    full = os.path.join(R, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html)
    if search:
        PAGES.append({"u": canon, "t": title, "d": desc, "s": section})
    if 'noindex' not in robots:
        URLS.append(canon)

def crumbs(path, trail):
    root = rootof(path)
    out = f'<a href="{root}index.html">Home</a>'
    for label, href in trail:
        out += '<i>/</i>' + (f'<a href="{root}{href}">{label}</a>' if href else label)
    return f'<div class="crumbs">{out}</div>'

def head(path, trail, eyebrow, h1, lede, extra=""):
    return (f'<section class="pagehead"><div class="wrap">{crumbs(path, trail)}<div class="eyebrow">{eyebrow}</div>'
            f'<h1>{h1}</h1><p class="lede">{lede}</p>{extra}</div></section>')

def std(path, sec, sec_href, title, eyebrow, lede, content, desc, siblings=True, trail_extra=None):
    trail = [(sec, sec_href)] if sec else []
    if path.endswith("index.html") and path.count("/") == 1:
        trail = [(title, None)]
    else:
        trail = trail + [(title, None)]
    more = '<div class="more" data-render="siblings"></div>' if siblings else ""
    body = (head(path, trail, eyebrow, title, lede) +
            f'<section class="sec"><div class="wrap layout"><aside class="sidenav" data-render="sidebar" aria-label="Section navigation"></aside><div class="content">{content}{more}</div></div></section>')
    page(path, title, desc, body, sec or title)

def steps(items):
    out = '<div class="steps">'
    for i, (t, p) in enumerate(items, 1):
        out += f'<div class="step"><span class="n">{i:02d}</span><div><h3>{t}</h3><p>{p}</p></div></div>'
    return out + '</div>'

def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def note(t): return f'<div class="note" style="margin:22px 0">{t}</div>'

def kv(rows):
    return '<dl class="kv">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + "</dl>"

ABOUT=("About","about/"); RESEARCH=("Research","research/"); BRIEFS=("Policy briefs","briefs/index.html")
DATA=("Data hub","data/"); METH=("Methodology","methodology/"); POL=("Policies","policies/")

# =============================================================== HOME
home = '''
<section class="hero"><div class="wrap">
<div class="eyebrow">A quantitative economics institution · Policy briefs</div>
<h1>Evidence-based policy analysis for Bangladesh.</h1>
<p>BIQEP Policy Briefs turns official data into short, rigorous analysis of inflation, monetary policy, public finance, labor and trade. Every figure is validated against its source and every estimate can be replicated.</p>
<p class="byline">By <a href="people/index.html">Dr. Tuhin G. M. Al Mamun</a>, Founder and Executive Director</p>
<div class="btns"><a class="btn" href="briefs/index.html">Read the policy briefs</a><a class="btn ghost" href="data/index.html">Explore the data hub</a><a class="btn ghost" href="methodology/index.html">How we validate</a></div>
</div></section>
<div class="ribbon"><div class="wrap">
<a href="briefs/index.html"><b>Policy briefs</b><span>All records, searchable by topic</span></a>
<a href="data/index.html"><b>Data hub</b><span>Series, sources, validation log</span></a>
<a href="methodology/index.html"><b>Methodology</b><span>Models, standards, replication</span></a>
<a href="policies/index.html"><b>Policies</b><span>Publication, sources, corrections</span></a>
</div></div>

<section class="sec"><div class="wrap cols2">
<div><div class="eyebrow">The series</div><h2>Evidence begins with a better question.</h2>
<p class="lede">Economic questions rarely yield to one headline number. Each brief starts from a question people in Bangladesh are actually asking, brings in the official data, and is honest about what the evidence can and cannot show.</p>
<p><a class="link-arrow" href="about/index.html">About the series</a> &nbsp; <a class="link-arrow" href="about/mission-vision/index.html">Mission and vision</a></p></div>
<blockquote class="quote">A quantitative result is only as useful as the assumptions it makes visible.</blockquote>
</div></section>

<section class="sec mist"><div class="wrap">
<div class="row"><div><div class="eyebrow">Verified figures</div><h2>Where the data stand.</h2></div><a class="link-arrow" href="data/index.html">All series and sources</a></div>
<div class="indicators" data-render="indicators"></div>
<p class="small muted" style="margin:16px 0 0;max-width:720px">Figures are taken from official releases. The Data hub lists the source and retrieval date of each series.</p>
</div></section>

<section class="sec"><div class="wrap">
<div class="row"><div><div class="eyebrow">Latest</div><h2>Policy briefs.</h2></div><a class="link-arrow" href="briefs/index.html">All policy briefs</a></div>
<div data-render="latest"></div>
</div></section>

<section class="sec mist"><div class="wrap">
<div class="eyebrow">Research agenda</div><h2>Questions that matter in Bangladesh.</h2>
<p class="lede" style="margin-bottom:28px">Seven areas make up the research agenda.</p>
<div class="cards" data-render="topics"></div>
<p style="margin-top:20px"><a class="link-arrow" href="research/index.html">Read the research agenda</a></p>
</div></section>

<section class="sec"><div class="wrap">
<div class="eyebrow">Collections</div><h2>One record, in the right place.</h2>
<p class="lede" style="margin-bottom:24px">Records are kept apart by kind: briefs, data notes, outlook, statistical reports and replication materials.</p>
<div class="cards">
<a class="link-card" href="briefs/index.html"><h3>Policy briefs</h3><p>Short analysis built on official data.</p></a>
<a class="link-card" href="briefs/data-notes/index.html"><h3>Data notes</h3><p>Verified figures and open questions, with no model claims.</p></a>
<a class="link-card" href="briefs/outlook/index.html"><h3>Bangladesh Economic Outlook</h3><p>A periodic overview of the economy.</p></a>
<a class="link-card" href="briefs/statistical-reports/index.html"><h3>Statistical reports</h3><p>Documented datasets and statistical tables.</p></a>
<a class="link-card" href="briefs/replication/index.html"><h3>Replication materials</h3><p>Data, specifications and settings behind each brief.</p></a>
<a class="link-card" href="data/validation/index.html"><h3>Validation log</h3><p>How each series was checked against its official release.</p></a>
</div></div></section>

<section class="sec navy"><div class="wrap cols2">
<div><div class="eyebrow">The record</div><h2>Every figure findable — and verifiable.</h2>
<p class="lede">The Data hub lists each series with its official source and retrieval date, and the validation log records how each was checked.</p>
<p><a class="link-arrow" style="color:var(--teal-l)" href="data/index.html">Open the data hub</a> &nbsp; <a class="link-arrow" style="color:var(--teal-l)" href="data/validation/index.html">Validation log</a></p></div>
<div class="stats" data-render="stats"></div>
</div></section>

<section class="sec mist"><div class="wrap">
<div class="eyebrow">Our approach</div><h2>Built on official data.</h2>
<div class="cards" style="margin-top:26px">
<div class="link-card"><span class="num">01</span><h3>Official sources</h3><p>Numbers come from Bangladesh Bank, the Bangladesh Bureau of Statistics, the IMF and the World Bank.</p></div>
<div class="link-card"><span class="num">02</span><h3>Open methods</h3><p>Estimates run in the open-source Open Econometric Systems engine, so results can be replicated.</p></div>
<div class="link-card"><span class="num">03</span><h3>Clear limits</h3><p>Each brief states its data limits, its assumptions and what the results cannot show.</p></div>
<div class="link-card"><span class="num">04</span><h3>Public corrections</h3><p>Errors are corrected on the page, with the date and what changed.</p></div>
</div>
<div class="chips" style="margin-top:26px">
<a class="chip" href="policies/publication/index.html">Publication</a><a class="chip" href="policies/data-sources/index.html">Data and sources</a><a class="chip" href="policies/validation/index.html">Validation</a><a class="chip" href="policies/replication/index.html">Replication</a><a class="chip" href="policies/corrections/index.html">Corrections</a><a class="chip" href="policies/copyright/index.html">Copyright and reuse</a><a class="chip" href="policies/conflict-of-interest/index.html">Conflict of interest</a>
</div></div></section>

<section class="sec"><div class="wrap cols2">
<div><div class="eyebrow">People</div><h2>Research with a long view.</h2>
<p class="lede">Dr. Tuhin G. M. Al Mamun, Founder and Executive Director of BIQEP, researches monetary policy transmission, Bayesian and computational methods, and structural macroeconomic modeling.</p>
<p><a class="link-arrow" href="people/index.html">People</a> &nbsp; <a class="link-arrow" href="about/leadership/index.html">Leadership</a> &nbsp; <a class="link-arrow" href="about/governance/index.html">Governance</a></p></div>
<div class="note"><b>Independent initiative.</b> BIQEP is not a government body and is not affiliated with Bangladesh Bank, the Bangladesh Bureau of Statistics or the Government of Bangladesh.</div>
</div></section>

<section class="sec mist"><div class="wrap">
<div class="eyebrow">News and events</div><h2>Updates, when they are ready.</h2>
<div class="cards">
<a class="link-card" href="news/index.html"><h3>News</h3><p>Release notes and corrections.</p></a>
<a class="link-card" href="news/events/index.html"><h3>Events</h3><p>Seminars and talks.</p></a>
<a class="link-card" href="research/collaboration/index.html"><h3>Research collaboration</h3><p>How to work with the series on data and methods.</p></a>
</div></div></section>

<section class="sec navy"><div class="wrap">
<div class="eyebrow">Work with BIQEP</div><h2>Found a figure that does not match its source?</h2>
<p class="lede">Corrections, data questions and collaboration are welcome. We check every report against the original release.</p>
<div class="btns"><a class="btn" href="contact/index.html">Contact</a><a class="btn ghost" href="policies/corrections/index.html">Corrections policy</a></div>
</div></section>
'''
page("index.html", "Quantitative evidence for Bangladesh", "Evidence-based policy briefs on Bangladesh’s economy, built on official data and open, reproducible econometric methods.", home, "Home")

# =============================================================== ABOUT
std("about/index.html","About","about/index.html","The series","About","BIQEP Policy Briefs is the public-policy series of the Bangladesh Institute of Quantitative Economics and Public Policy.",
 '''<h2>What this series is</h2>
<p>The Bangladesh Institute of Quantitative Economics and Public Policy (BIQEP) advances economic research through mathematics, statistics and econometrics. BIQEP Policy Briefs is its public-policy series on Bangladesh.</p>
<p>The aim is plain: give readers short analysis they can check. Each brief names its data, its method and its limits, and the settings behind it are open.</p>
<blockquote class="quote" style="margin:26px 0">A quantitative result is only as useful as the assumptions it makes visible.</blockquote>
<h2>What it is not</h2>
<p>BIQEP is an independent research initiative. It is not a government body and is not affiliated with Bangladesh Bank, the Bangladesh Bureau of Statistics or the Government of Bangladesh. Views are the author’s own.</p>
<h2>How the series is organised</h2>
<div class="two">
<div><h3>Research areas</h3><p>Seven areas set the agenda: inflation, monetary policy, public finance, labor and wages, the external sector, finance and credit, and climate and energy.</p><a class="link-arrow" href="../research/index.html">Research agenda</a></div>
<div><h3>Records</h3><p>Policy briefs, data notes, the Bangladesh Economic Outlook, statistical reports and replication materials are kept in separate collections.</p><a class="link-arrow" href="../briefs/index.html">Policy briefs</a></div>
<div><h3>Data and methods</h3><p>The Data hub lists every series and its source. The methodology explains validation and the models used.</p><a class="link-arrow" href="../data/index.html">Data hub</a></div>
<div><h3>Standards</h3><p>Seven policies state the standards each brief is held to, from publication to corrections.</p><a class="link-arrow" href="../policies/index.html">Policies</a></div>
</div>''',
 "About the Bangladesh Institute of Quantitative Economics and Public Policy and its policy briefs series.")

std("about/mission-vision/index.html","About","about/index.html","Mission and vision","About","What the series is for, and the standard it holds itself to.",
 '''<h2>Mission</h2>
<p>To make quantitative evidence on Bangladesh’s economy easier to find, check and use. The series publishes short analysis built on official data, estimated with open methods, and stated with its limits.</p>
<h2>Vision</h2>
<p>A public conversation about economic policy in which every number has a visible source, every model can be rerun, and uncertainty is stated rather than hidden.</p>
<h2>Commitments</h2>''' + ul([
  "<b>Official sources.</b> Evidence comes from Bangladesh Bank, the Bangladesh Bureau of Statistics, the IMF and the World Bank.",
  "<b>Open methods.</b> The estimation engine is open source, and each brief states the settings needed to repeat its results.",
  "<b>Clear limits.</b> Each brief states its data limits and what its results cannot show.",
  "<b>Public corrections.</b> Errors are corrected on the page, with the date and what changed."]),
 "Mission, vision and commitments of the BIQEP Policy Briefs series.")

std("about/research-philosophy/index.html","About","about/index.html","Research philosophy","About","How we think about evidence, models and uncertainty.",
 '''<h2>Measurement first</h2>
<p>A model is only as good as its data. Before anything is estimated, each series is traced to its original release, its definition is read, and breaks in it are noted. In Bangladesh’s consumer price index, for example, the base year changed in April 2023, and any analysis across that date has to say how it handled the change.</p>
<h2>Methods fit the question</h2>
<p>Vector autoregressions and local projections suit questions about dynamics and timing. Structural and Bayesian models suit questions that need explicit assumptions. Panel and threshold methods suit questions about differences across groups or regimes. The method is chosen for the question, and the reason is stated.</p>
<h2>Say what the design cannot show</h2>
<p>Most macro-econometric evidence shows association and timing, not proof of cause. Each brief states which claims its design supports and which it does not.</p>
<h2>Robustness is part of the result</h2>
<p>A finding that disappears when the sample, lag length or specification changes is reported as fragile. Alternative specifications are published with the main one.</p>
<h2>Replicable by design</h2>
<p>The estimation engine is open, the data are versioned with a retrieval date, and the settings are listed, so a reader can repeat the work.</p>''',
 "The research philosophy behind BIQEP Policy Briefs: measurement, method choice, uncertainty and replication.")

std("about/leadership/index.html","About","about/index.html","Leadership","About","The person responsible for the series.",
 '''<div class="person"><div class="avatar">TA</div><div>
<h2 style="margin-bottom:.2em">Dr. Tuhin G. M. Al Mamun</h2><p class="muted" style="margin-bottom:.8em">Founder and Executive Director</p>
<p>Dr. Al Mamun holds a PhD in Economics from Hannam University. His research covers monetary policy transmission, heterogeneous-agent and structural macroeconomic models, Bayesian and time-series econometrics, and applied machine-learning methods.</p>
<p>He is responsible for the topics chosen, the data validated, the models run and every brief published in the series.</p>
<p><a class="link-arrow" href="https://tuhingm.github.io/almamun/" rel="noopener">Academic website</a></p></div></div>''',
 "Leadership of BIQEP Policy Briefs: Dr. Tuhin G. M. Al Mamun, Founder and Executive Director.")

std("about/governance/index.html","About","about/index.html","Governance","About","Responsibility for the series, and its independence.",
 '''<h2>Responsibility</h2>
<p>The Founder and Executive Director is responsible for the series, including the topics chosen, the data used and the briefs published. He is accountable for corrections.</p>
<h2>Independence</h2>
<p>BIQEP is an independent research initiative. It is not a government body and is not affiliated with Bangladesh Bank, the Bangladesh Bureau of Statistics or the Government of Bangladesh.</p>
<h2>Related policies</h2>''' + ul(['<a href="../../policies/publication/index.html">Publication policy</a>','<a href="../../policies/corrections/index.html">Corrections policy</a>','<a href="../../policies/conflict-of-interest/index.html">Conflict-of-interest policy</a>']),
 "Governance of BIQEP Policy Briefs: responsibility, independence and corrections.")

# =============================================================== RESEARCH
AREAS = [
 ("Inflation","inflation","Price dynamics, food and non-food inflation, and expectations.",
  "Inflation touches every household budget. Understanding what drives it, how fast shocks pass through, and why it can stay high is the starting point for most policy questions in Bangladesh.",
  ["How much of headline inflation comes from food prices, and how much from non-food prices?","How quickly and how fully do exchange-rate movements pass into consumer prices?","How do wage growth and inflation affect each other?","Does the 2023 change in the CPI base year change what we can say about trends?"],
  ["Bangladesh Bureau of Statistics: consumer price index, food and non-food","Bangladesh Bank: economic data pages"],
  ["Vector autoregressions and local projections","ARDL bounds tests","Markov-switching models for regimes"]),
 ("Monetary policy","monetary-policy","Policy rates, transmission to lending and the exchange rate.",
  "Bangladesh Bank’s policy decisions work through banks, credit and the exchange rate before they reach prices and output. The lags and strength of that chain are an empirical question.",
  ["How do policy-rate changes pass through to deposit and lending rates?","What are the lags from the policy rate to inflation and output?","How does the exchange rate respond to policy changes?","How has transmission changed across policy regimes?"],
  ["Bangladesh Bank: policy announcements and monetary policy statements","Bangladesh Bank: interest rate and monetary statistics"],
  ["Structural VARs","Bayesian VARs","Time-varying-parameter VARs","Local projections"]),
 ("Public finance","public-finance","Revenue, spending, deficits and debt sustainability.",
  "How the government raises and spends money shapes growth, inflation and the room for policy. Fiscal questions need careful sources, because definitions and coverage differ across documents.",
  ["How do revenue and spending respond to growth and prices?","What does the debt path look like under stated assumptions?","What are the size and timing of fiscal multipliers?","How do energy and food subsidies affect the budget?"],
  ["Finance Division, Ministry of Finance: budget documents","National Board of Revenue: revenue data","IMF country reports"],
  ["Structural VARs","Local projections","Threshold models","Bayesian VARs"]),
 ("Labor and wages","labor-wages","Employment, real wages and the informal economy.",
  "Whether wages keep pace with prices decides how inflation is felt. Labor data in Bangladesh come from surveys with their own definitions, which has to be handled with care.",
  ["Are nominal wages keeping pace with consumer prices?","How do real wages differ across sectors?","How large is informal employment, and how does it respond to shocks?","How does the labor market respond to monetary and fiscal changes?"],
  ["Bangladesh Bureau of Statistics: wage rate index","Bangladesh Bureau of Statistics: Labour Force Survey"],
  ["Panel methods","Quantile regression","ARDL models"]),
 ("External sector","external-sector","Exchange rate, remittances, reserves and trade.",
  "Bangladesh’s exchange rate, remittances and reserves link the domestic economy to the world. Changes there pass into prices, the budget and bank balance sheets.",
  ["How do remittances respond to the exchange rate and to policy?","What do reserves tell us about external resilience?","How do exchange-rate moves pass into import and consumer prices?","What happens to trade flows around large depreciations?"],
  ["Bangladesh Bank: exchange rate, balance of payments and remittance data","IMF: International Financial Statistics","World Bank: Bangladesh data"],
  ["Nonlinear ARDL","Vector autoregressions","Structural-break tests","Wavelet coherence"]),
 ("Finance and credit","finance-credit","Bank lending, interest rates and financial stability.",
  "Credit and bank health decide how much of a policy change reaches firms and households. Stability questions need bank-level and system-level data read together.",
  ["How does credit growth respond to interest rates and liquidity?","Where does bank risk concentrate, and how does it move over time?","How do deposit and lending rates move relative to the policy rate?","What threshold effects appear in credit and stability indicators?"],
  ["Bangladesh Bank: scheduled bank statistics and interest rate data","Bangladesh Bank: financial stability reports"],
  ["Panel methods","Threshold regression","Quantile regression"]),
 ("Climate and energy","climate-energy","Energy prices, green finance and climate risk.",
  "Energy prices feed into costs, inflation and the budget, and climate risk adds a longer-run channel. The questions here link macro data to energy and climate sources.",
  ["How do energy-price changes pass into consumer prices?","What are the fiscal costs of energy price policy?","How might climate-related shocks affect growth and prices?","How large is green finance relative to the credit system?"],
  ["Official energy price notifications","Bangladesh Bureau of Statistics","World Bank: climate and development data"],
  ["Structural VARs","Local projections","Panel threshold models"]),
]

std("research/index.html","Research","research/index.html","Research agenda","Research","Seven areas of work, from inflation and monetary policy to climate and energy.",
 '''<h2>The agenda</h2>
<p>Each area page lists the key questions, the official data sources and the methods that suit them.</p>
<div class="cards" data-render="topics"></div>
<h2>Across all areas</h2>''' + ul([
  "Data come from official releases, with source and retrieval date recorded.",
  "Models run in the open-source Open Econometric Systems engine, so results can be replicated.",
  "Each brief states what the design cannot show.",
  'See the <a href="../methodology/index.html">methodology</a> and the <a href="../policies/index.html">policies</a>.']),
 "The BIQEP Policy Briefs research agenda: seven areas covering inflation, monetary policy, public finance, labor, the external sector, credit and energy.")

for (name, slug, short, why, qs, srcs, meths) in AREAS:
    content = f'''<h2>Why it matters</h2><p>{why}</p>
<h2>Key questions</h2>{ul(qs)}
<h2>Data sources</h2>{ul(srcs)}
<p class="small muted">Series used in briefs are listed, with their sources, in the <a href="../../data/index.html">Data hub</a>.</p>
<h2>Methods that fit</h2>{ul(meths)}
<p class="small muted">Models run in <a href="../../methodology/models/index.html">Open Econometric Systems</a>. The method for each brief is chosen for its question and stated in the brief.</p>
<h2>Records in this area</h2>
<div data-render="collection" data-topic="{name}" data-empty-title="No records yet" data-empty="No publications in this area yet."></div>'''
    std(f"research/{slug}/index.html","Research","research/index.html",name,"Research area",short,content,
        f"BIQEP research area: {name}. Key questions, official sources and methods.")

std("research/collaboration/index.html","Research","research/index.html","Research collaboration","Research","How to work with the series on data, methods and questions.",
 '''<h2>What we welcome</h2>''' + ul([
  "Pointers to official data we may have missed, including the original release for a figure.",
  "Corrections to a figure or a method, with the brief and the release it conflicts with.",
  "Suggestions for topics, with the question you would like answered.",
  "Methodological comments on a published specification."]) +
 '''<h2>What we do not do</h2>''' + ul([
  "We do not publish figures supplied without an official source.",
  "We do not accept requests to change a finding.",
  "We do not take paid or sponsored briefs."]) + '<p>See the <a href="../../contact/index.html">contact page</a>.</p>',
 "How to collaborate with BIQEP Policy Briefs: data, corrections, topics and methods.")

# =============================================================== BRIEFS INDEX + COLLECTIONS
c = '''<div class="eyebrow">Repository</div><h2>Browse the records.</h2><p class="muted" style="max-width:660px">Search by title or summary, or filter by topic.</p><div data-render="briefs-page"></div>'''
body = head("briefs/index.html", [("Policy briefs", None)], "Policy briefs", "Policy briefs", "Short analysis of Bangladesh’s economy, built on official data and open methods.") + \
  f'<section class="sec"><div class="wrap layout"><aside class="sidenav" data-render="sidebar" aria-label="Section navigation"></aside><div class="content">{c}<div class="more" data-render="siblings"></div></div></div></section>'
page("briefs/index.html","Policy briefs","Policy briefs on Bangladesh’s economy: inflation, monetary policy, public finance, labor and trade.",body,"Policy briefs")

COLL = [
 ("data-notes","Data notes","Data note","A data note sets out verified figures and open questions for a topic. It makes no model claims.","Verified figures with their source and date, and the questions that follow from them.","No data notes published yet","No data notes have been published yet."),
 ("outlook","Bangladesh Economic Outlook","Economic outlook","A periodic overview of the economy, built from the series in the Data hub.","Each issue draws on the official series listed in the Data hub.","No outlook published yet","No outlook has been published yet."),
 ("statistical-reports","Statistical reports","Statistical report","Documented datasets and statistical tables derived from official releases.","Each report states its source tables, transformations and retrieval dates.","No statistical reports published yet","No statistical reports have been published yet."),
 ("replication","Replication materials","Replication package","Data files, specifications and settings that let a reader repeat a brief’s results.","A package holds the dataset with retrieval dates, the model specification and the engine version.","No replication packages published yet","No replication packages have been published yet."),
]
for slug, name, typ, lede, what, et, e in COLL:
    c = f'''<h2>About this collection</h2><p>{lede}</p><p class="muted">{what}</p>
<h2>Records</h2>
<div data-render="collection" data-type="{typ}" data-empty-title="{et}" data-empty="{e}"></div>
<p class="small muted" style="margin-top:20px">Collections keep different kinds of record apart. See <a href="../index.html">all records</a>.</p>'''
    std(f"briefs/{slug}/index.html","Policy briefs","briefs/index.html",name,"Collection",lede,c,f"BIQEP collection: {name}.")

# =============================================================== DATA HUB
std("data/index.html","Data hub","data/index.html","Series register","Data hub","Every series used in a brief, with its official source and retrieval date.",
 '''<div class="tbl" data-render="series-table"></div>
<h2>Break in the CPI series</h2>
<p>From April 2023 the BBS consumer price index uses base year 2021-22. Any estimate that spans that date must treat the change of base explicitly. Each brief says how it did so.</p>
<h2>Where the figures come from</h2>
<p>See <a href="sources/index.html">official sources</a> for each publisher, and the <a href="validation/index.html">validation log</a> for each check.</p>''',
 "Verified Bangladesh economic series with official sources and retrieval dates.")

std("data/sources/index.html","Data hub","data/index.html","Official sources","Data hub","The publishers whose releases we treat as evidence, and what we take from each.",
 '''<div class="cards">
<a class="link-card" href="https://www.bb.org.bd/en/index.php/econdata/index" rel="noopener"><h3>Bangladesh Bank</h3><p>Economic data, policy announcements, exchange rates, interest rates, monetary and bank statistics.</p></a>
<a class="link-card" href="https://bbs.gov.bd/" rel="noopener"><h3>Bangladesh Bureau of Statistics</h3><p>Consumer price index, wage rate index, national accounts and the Labour Force Survey.</p></a>
<a class="link-card" href="https://data.imf.org/" rel="noopener"><h3>International Monetary Fund</h3><p>International Financial Statistics, World Economic Outlook and country reports.</p></a>
<a class="link-card" href="https://data.worldbank.org/country/bangladesh" rel="noopener"><h3>World Bank</h3><p>World Development Indicators and Bangladesh country data.</p></a>
</div>
<h2>How a source is cited</h2>''' + ul([
  "The original publisher is named, not the site that relayed it.",
  "The address of the release page and the retrieval date are recorded.",
  "If Bangladesh Bank republishes a BBS figure, we say so, as in “BBS, published by Bangladesh Bank”.",
  "Where sources differ, the original release is followed."]),
 "Official sources used by BIQEP Policy Briefs and how they are cited.")

std("data/validation/index.html","Data hub","data/index.html","Validation log","Data hub","How each series was checked against its official release.",
 '''<p>Each row is a series in the register, checked against its official release on the date shown.</p>
<div class="tbl" data-render="validation"></div>
<h2>How a check is done</h2>''' + ul([
  "Find the original release on the publisher’s site.",
  "Read the value for the stated period and note the retrieval date.",
  "Compare it with the figure used. They must match exactly.",
  "Record the result. If they do not match, the figure is not used until the difference is explained."]),
 "Validation log for BIQEP series: how each was checked against its official release.")

# =============================================================== METHODOLOGY
std("methodology/index.html","Methodology","methodology/index.html","How a brief is made","Methodology","From official data to estimates: how series are sourced, checked and modelled.",
 '''<div class="steps">
<div class="step"><span class="n">01</span><div><h3>Official data</h3><p>Series come from Bangladesh Bank, the Bangladesh Bureau of Statistics, the IMF and the World Bank. The source, address and retrieval date of each series are recorded in the Data hub.</p></div></div>
<div class="step"><span class="n">02</span><div><h3>Validation</h3><p>Each figure is checked against its original release before it is used.</p></div></div>
<div class="step"><span class="n">03</span><div><h3>Estimation</h3><p>Models run in Open Econometric Systems (OES), an open-source engine. The specification, sample and settings are published with the brief.</p></div></div>
<div class="step"><span class="n">04</span><div><h3>Limits and corrections</h3><p>Each brief states its data limits and what its results cannot show. If a figure is found not to match its official source, it is corrected and the correction is noted on the page with its date.</p></div></div>
</div>
<h2>What every brief states</h2>''' + ul([
  "the data used, with source and retrieval date;",
  "the sample period and any break in the series, such as the 2023 change of CPI base;",
  "the model, the identifying assumptions and the main robustness checks;",
  "what the results cannot show, including causal claims the design does not support."]),
 "How BIQEP policy briefs are produced: official data, validation, open estimation and author review.")

std("methodology/models/index.html","Methodology","methodology/index.html","Models and tools","Methodology","The open-source engine behind the estimates, and the families of model it offers.",
 '''<h2>Open Econometric Systems</h2>
<p>Open Econometric Systems (OES) is a free, open-source econometric workspace. It currently offers 69 models and runs in the browser, so data stay on the user’s own computer. Its estimators are written in Python and can also be run from a laptop.</p>
<p><a class="link-arrow" href="https://tuhingm.github.io/almamun/oes/" rel="noopener">Open OES in your browser</a> &nbsp; <a class="link-arrow" href="https://github.com/tuhingm/open-econometric-systems" rel="noopener">Read the code on GitHub</a></p>
<h2>Model families</h2>
<dl class="kv">
<dt>Time series</dt><dd>OLS with diagnostics, ARDL bounds tests, nonlinear ARDL, VAR, VECM, instrumental variables and GMM, local projections, structural VARs, structural-break tests, threshold and smooth-transition regression, ARIMA, GARCH, quantile regression, cointegration tests and wavelet coherence.</dd>
<dt>Panel data</dt><dd>Pooled, fixed- and random-effects models, dynamic panel GMM, mean-group and common-correlated-effects estimators, panel local projections, panel threshold models and spatial panels.</dd>
<dt>Causal inference</dt><dd>Difference-in-differences, event studies, interrupted time series, regression discontinuity, synthetic control, matching and shift-share instruments.</dd>
<dt>Machine learning</dt><dd>LASSO, ridge, elastic net, random forest, XGBoost and double machine learning.</dd>
<dt>Bayesian</dt><dd>Bayesian regression and VARs with Minnesota and other priors, factor-augmented, time-varying and stochastic-volatility VARs, sign-restricted VARs and Bayesian local projections.</dd>
<dt>Markov switching</dt><dd>Markov-switching regression, autoregressions and VARs, including time-varying transition probabilities.</dd>
</dl>
<p class="small muted">Model groups as listed in the OES repository. DSGE models are not part of OES and are solved elsewhere.</p>
<h2>Which model for which question</h2>
<p>The method for each brief is chosen for its question and stated in the brief. See the <a href="../../research/index.html">research areas</a> for the methods that suit each topic.</p>''',
 "Open Econometric Systems (OES): the open-source engine and model families used by BIQEP Policy Briefs.")

std("methodology/data-standards/index.html","Methodology","methodology/index.html","Data standards","Methodology","How series are recorded, versioned and described.",
 '''<h2>Every series carries</h2>''' + ul([
  "its official name and publisher;",
  "the address of the release page it was read from;",
  "the period covered and the unit;",
  "the date it was retrieved."]) +
 '''<h2>Breaks and revisions</h2>''' + ul([
  "<b>CPI base.</b> From April 2023 the BBS consumer price index uses base year 2021-22. Analysis across that date states how the change was handled.",
  "<b>Revisions.</b> Official figures can be revised. A brief states the retrieval date of its data, and figures are re-checked before publication.",
  "<b>Seasonality.</b> A brief states whether series are seasonally adjusted. We do not adjust a series without saying so.",
  "<b>Transformations.</b> Logs, differences and growth rates are listed with the specification."]) +
 '''<h2>What is left out</h2><p>A series that cannot be traced to an official release, or whose definition cannot be established, is not used.</p>''',
 "Data standards for BIQEP Policy Briefs: source records, breaks, revisions and transformations.")

std("methodology/replication/index.html","Methodology","methodology/index.html","Replication","Methodology","What is published with a brief so that a reader can repeat it.",
 '''<h2>A replication package contains</h2>''' + ul([
  "the dataset, with source and retrieval date for each series;",
  "the model specification: variables, lags, sample, transformations and any break treatment;",
  "the engine and its version;",
  "the settings and random seeds for any simulation-based method;",
  "the tables and charts as produced."]) +
 '''<h2>How to repeat a result</h2>''' + steps([
  ("Open the engine","Use OES in a browser, or install it from the GitHub repository."),
  ("Load the data","Load the dataset from the package."),
  ("Apply the specification","Choose the model and enter the listed settings."),
  ("Compare","The output should match the tables in the brief.")]),
 "How BIQEP briefs are made replicable: packages, specification and how to repeat a result.")

# =============================================================== POLICIES
PCY = [
 ("publication","Publication policy","What a published record contains.",
  ["A brief is published with its date, its author and the retrieval date of its data.",
   "Each brief states its data, its method and its limits.",
   "Records are kept in separate collections by kind: briefs, data notes, outlook, statistical reports and replication materials."]),
 ("data-sources","Data and sources policy","What counts as evidence.",
  ["Figures come from Bangladesh Bank, the Bangladesh Bureau of Statistics, the IMF and the World Bank.",
   "Each series is listed in the Data hub with its source and retrieval date.",
   "A series is used only when it can be traced to an official release."]),
 ("validation","Validation policy","How figures are checked.",
  ["Every figure is checked against the original release before use.",
   "Where sources differ, the original release is followed.",
   "Checks are recorded in the validation log."]),
 ("replication","Replication policy","How results can be repeated.",
  ["Models are run in the open-source Open Econometric Systems engine.",
   "Each brief states the data, specification and settings needed to repeat its analysis.",
   "A replication package is released with each published brief.",
   "Where a method cannot be replicated in OES, the brief says so and explains why."]),
 ("corrections","Corrections policy","What happens when something is wrong.",
  ["A figure that does not match its official source is corrected on the page.",
   "The correction states the date and what changed. The earlier text is not silently removed.",
   "If a correction changes a conclusion, the brief says so at the top.",
   "Report an error through the contact page, naming the brief, the figure and the release."]),
 ("copyright","Copyright and reuse","Who owns what, and how to reuse it.",
  ["Official data belong to their publishers. Reuse of a figure follows the publisher’s terms.",
   "When you cite a brief, cite BIQEP and the original source of the data.",
   "Charts and tables made by BIQEP should be credited to BIQEP Policy Briefs."]),
 ("conflict-of-interest","Conflict-of-interest policy","Disclosure and independence.",
  ["The author discloses any interest that bears on a brief’s topic.",
   "BIQEP does not take paid or sponsored briefs.",
   "BIQEP is not affiliated with Bangladesh Bank, the Bangladesh Bureau of Statistics or the Government of Bangladesh.",
   "Views are the author’s own."]),
]
std("policies/index.html","Policies","policies/index.html","Series policies","Policies","The standards each brief is held to: publication, sources, validation, replication, corrections, reuse and independence.",
 '''<p>These policies describe how the series works.</p><div class="cards" style="margin-top:20px">''' +
 "".join(f'<a class="link-card" href="{s}/index.html"><h3>{t}</h3><p>{d}</p></a>' for s,t,d,_ in PCY) + "</div>",
 "Publication, source, validation, replication, corrections and other policies for BIQEP Policy Briefs.", siblings=False)
for s,t,d,items in PCY:
    std(f"policies/{s}/index.html","Policies","policies/index.html",t,"Policy",d,
        "<h2>The policy</h2>" + ul(items) + '<p class="small muted" style="margin-top:20px">Related: <a href="../../methodology/index.html">methodology</a>, <a href="../../about/governance/index.html">governance</a>.</p>',
        f"BIQEP policy: {t}.")

# =============================================================== PEOPLE / NEWS / EVENTS / CONTACT / SEARCH
std("people/index.html","People","people/index.html","People","People","Who is responsible for the series.",
 '''<div class="person"><div class="avatar">TA</div><div>
<h2 style="margin-bottom:.2em">Dr. Tuhin G. M. Al Mamun</h2><p class="muted" style="margin-bottom:.8em">Founder and Executive Director</p>
<p>PhD in Economics, Hannam University. Research on monetary policy transmission, structural and heterogeneous-agent macroeconomic models, Bayesian and time-series econometrics, and applied machine-learning methods.</p>
<p><a class="link-arrow" href="../about/leadership/index.html">Leadership</a> &nbsp; <a class="link-arrow" href="https://tuhingm.github.io/almamun/" rel="noopener">Academic website</a></p></div></div>''',
 "People behind BIQEP Policy Briefs.", siblings=False)

std("news/index.html","News","news/index.html","News","News","Release notes and corrections.",
 '''<div class="empty"><h3>No news published yet</h3><p>Release notes, new series and corrections are listed here with their dates.</p></div>
''',
 "News and release notes from BIQEP Policy Briefs.")

std("news/events/index.html","News","news/index.html","Events","News","Seminars and talks.",
 '''<div class="empty"><h3>No events listed</h3><p>No events are listed at present.</p></div>''',
 "Events of BIQEP Policy Briefs.")

std("contact/index.html","Contact","contact/index.html","Contact","Contact","Research collaboration, data corrections and policy questions.",
 '''<p>Contact details will be listed here.</p>
<h2>Corrections are welcome</h2>
<p>If a figure does not match its official source, tell us which brief, which figure and which release it conflicts with. We will check it against the original and publish a dated correction if you are right. See the <a href="../policies/corrections/index.html">corrections policy</a>.</p>
<h2>Collaboration and questions</h2>
<p>We welcome conversation on research collaboration, methods and the data used in the briefs. Please name the brief or series you are writing about. See <a href="../research/collaboration/index.html">research collaboration</a>.</p>
<h2>What to include</h2>''' + ul(["the brief or series you mean;","the figure or claim in question;","the official release you are comparing it with, if any."]),
 "How to reach BIQEP Policy Briefs about corrections, collaboration and questions.", siblings=False)

body = head("search/index.html", [("Search", None)], "Search", "Search the site", "Find pages, research areas, series and policies.") + \
  '<section class="sec"><div class="wrap narrow-w"><div data-render="site-search"></div></div></section>'
page("search/index.html","Search","Search BIQEP Policy Briefs.",body,"Search",search=False)

# =============================================================== 404
r = "/biqep-policy/"
nf = f'''<section class="pagehead"><div class="wrap"><div class="eyebrow">404</div><h1>Page not found</h1><p class="lede">That page does not exist. Try the briefs, the data hub or the home page.</p></div></section>
<section class="sec"><div class="wrap"><div class="btns" style="margin-top:0"><a class="btn" href="{r}index.html">Home</a><a class="btn line" href="{r}briefs/index.html">Policy briefs</a><a class="btn line" href="{r}data/index.html">Data hub</a><a class="btn line" href="{r}search/index.html">Search</a></div></div></section>'''
html404 = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | BIQEP Policy Briefs</title><meta name="robots" content="noindex">{FONTS}<link rel="stylesheet" href="{r}assets/style.css"></head>
<body><div id="hdr"></div><main id="main">{nf}</main><div id="ftr"></div><script src="{r}assets/data.js"></script><script src="{r}assets/pages.js"></script><script src="{r}assets/site.js" data-root="{r}"></script></body></html>
'''
open(R+"/404.html","w",encoding="utf-8").write(html404)

# =============================================================== existing brief page (kept)
# briefs/inflation-above-8.html is maintained by gen_brief.py (unchanged content); regenerate pages.js with it included
# removed: PAGES.append({"u":"briefs/inflation-above-8.html","t":"Why is inflation still above 8%?","d":"Data note on Bangladesh inflation: verified CPI figures, what is still to be checked, and the planned analysis.","s":"Policy briefs"})
# removed: URLS.append

# briefs produced by the pipeline are listed in search and the sitemap
for b in json.load(open(R+"/content/briefs.json", encoding="utf-8")):
    PAGES.append({"u": "briefs/%s.html" % b["slug"], "t": b["title"], "d": b["summary"], "s": "Policy briefs"})
    URLS.append("briefs/%s.html" % b["slug"])

open(R+"/assets/pages.js","w",encoding="utf-8").write("window.BIQEP_PAGES = " + json.dumps(PAGES, ensure_ascii=False, indent=0) + ";\n")
open(R+"/robots.txt","w").write("User-agent: *\nAllow: /\nSitemap: https://tuhingm.github.io/biqep-policy/sitemap.xml\n")
open(R+"/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>https://tuhingm.github.io/biqep-policy/{u}</loc><lastmod>2026-11-14</lastmod></url>\n" for u in sorted(set(URLS))) + "</urlset>\n")

print(len(PAGES), "pages")
