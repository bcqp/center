#!/usr/bin/env python3
"""Apply hand-written search titles (<=62 chars) and descriptions (110-155 chars) to every page. Idempotent.
Old title/description strings are replaced wherever they appear as a whole (title tag, og, twitter, JSON-LD)."""
import re, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
S = " | BCQP"
M = {
"index.html": ("BCQP: Bangladesh Economy Statistical Reports & Policy", "Replicable statistical reports on the Bangladesh economy: inflation, money, credit and growth, built on official data and open econometric methods."),
"about/index.html": ("About BCQP, Bangladesh Center for Quantitative Policy", "BCQP is an independent research center publishing source-checked, replicable policy analysis on the Bangladesh economy. Who we are and how we work."),
"about/governance/index.html": ("Governance and Editorial Independence" + S, "How BCQP is governed: who is responsible for each report, how independence is protected and how errors are corrected in published work."),
"about/leadership/index.html": ("Leadership and Co-Founders" + S, "BCQP was co-founded by economists Dr. Tuhin G. M. Al Mamun and Dr. Abdur Rahim. Roles, expertise and responsibilities of the founding team."),
"about/mission-vision/index.html": ("Mission and Vision" + S, "BCQP's mission is better policy through better evidence: transparent, replicable quantitative analysis of the Bangladesh economy for decision-makers."),
"about/research-philosophy/index.html": ("Research Philosophy: Measurement, Method, Uncertainty" + S, "How BCQP chooses methods, measures indicators, reports uncertainty and makes every estimate replicable before it informs policy discussion."),
"briefs/index.html": ("Policy Briefs on the Bangladesh Economy" + S, "All BCQP policy briefs and statistical reports on Bangladesh: inflation, monetary policy, credit, growth and public finance, with data and code."),
"briefs/data-notes/index.html": ("Data Notes on Bangladesh Statistics" + S, "Short data notes on Bangladesh economic statistics: what the official series show, how they were checked and where they are revised or break."),
"briefs/outlook/index.html": ("Bangladesh Economic Outlook" + S, "BCQP's Bangladesh Economic Outlook series: periodic, evidence-based reading of inflation, growth, credit and the external position."),
"briefs/replication/index.html": ("Replication Materials: Data and Code" + S, "Download the data, specifications and results behind every BCQP report so that you can check, repeat and extend the analysis yourself."),
"briefs/statistical-reports/index.html": ("Statistical Reports on Bangladesh" + S, "BCQP statistical reports: peer benchmarks and econometric models for Bangladesh, from official data, with every figure traceable to its source."),
"contact/index.html": ("Contact BCQP" + S, "Contact BCQP about corrections, data questions, research collaboration or press. How to reach the team and what to include in your message."),
"data/index.html": ("Bangladesh Economic Data: Verified Series Register" + S, "Verified Bangladesh economic series, such as CPI inflation, each linked to its official source, reference period and retrieval date."),
"data/sources/index.html": ("Official Data Sources for Bangladesh Statistics" + S, "The official sources BCQP uses for Bangladesh data, including Bangladesh Bank, BBS and international databases, and how each is cited in reports."),
"data/validation/index.html": ("Data Validation Log" + S, "How each BCQP series is checked against its official release before publication, with dates, results and notes on revisions or breaks."),
"journal/index.html": ("Proposed Journal of Quantitative Economics" + S, "Plans for the Journal of Quantitative Economics and Public Policy, a BCQP initiative. Submissions are not yet open and details are provisional."),
"methodology/index.html": ("How a BCQP Brief Is Made: Method and Replication" + S, "From official data and validation to open estimation and author review: the full workflow behind every BCQP policy brief and statistical report."),
"methodology/data-standards/index.html": ("Data Standards: Sources, Breaks, Revisions" + S, "BCQP data standards: source records, definitions, structural breaks, revisions and transformations that every published series must document."),
"methodology/models/index.html": ("Econometric Models and Tools (OES)" + S, "The open-source Open Econometric Systems engine and the VAR, Bayesian VAR and local-projection models BCQP uses, with links to run them yourself."),
"methodology/quantitative-policy-analysis/index.html": ("Quantitative Policy Analysis: Methods and Evidence" + S, "How BCQP applies econometrics, statistics, causal inference and structural modelling to analyse economic policy questions in Bangladesh."),
"methodology/replication/index.html": ("Replication: How to Repeat a BCQP Result" + S, "How BCQP reports are made replicable: data packages, model specifications and step-by-step guidance to repeat any published result."),
"news/index.html": ("News and Release Notes" + S, "News, new report releases and methodology updates from BCQP, the Bangladesh Center for Quantitative Policy."),
"news/events/index.html": ("Events and Seminars" + S, "BCQP seminars, workshops and research exchange events. Only confirmed events are listed, with dates and how to take part."),
"people/index.html": ("People Behind BCQP" + S, "The people behind BCQP: founders, authors and contributors, with their roles and links to their academic profiles."),
"policies/index.html": ("Policies: Publication, Sources, Validation, Corrections" + S, "BCQP policies for publication, data sources, validation, replication, corrections, copyright and conflicts of interest."),
"policies/conflict-of-interest/index.html": ("Conflict-of-Interest Policy" + S, "How BCQP identifies, discloses and manages conflicts of interest so that its Bangladesh policy analysis stays independent and trustworthy."),
"policies/copyright/index.html": ("Copyright and Reuse Policy" + S, "How you can reuse BCQP reports, figures and data, how to cite them correctly, and what attribution is required."),
"policies/corrections/index.html": ("Corrections Policy" + S, "How BCQP handles errors: how to report one, how fast we respond and how corrections are dated and shown on the affected report."),
"policies/data-sources/index.html": ("Data and Sources Policy" + S, "BCQP's rules for choosing, citing and documenting data sources, with preference for official producers and full retrieval records."),
"policies/publication/index.html": ("Publication Policy" + S, "How BCQP decides what to publish, how reports are reviewed and dated, and what readers can expect from each release."),
"policies/replication/index.html": ("Replication Policy" + S, "What BCQP releases so that readers can repeat its analysis: data, specifications, results and code, and any limits due to licensing."),
"policies/validation/index.html": ("Validation Policy" + S, "How BCQP validates each figure against the official release before publication and what happens when a source cannot be verified."),
"research/index.html": ("Research Agenda: Nine Bangladesh Policy Areas" + S, "BCQP's research agenda covers inflation, monetary policy, public finance, labor, trade, credit, energy, growth and human development in Bangladesh."),
"research/climate-energy/index.html": ("Climate and Energy Policy in Bangladesh" + S, "BCQP research on climate and energy in Bangladesh: key policy questions, official data sources and the econometric methods used."),
"research/collaboration/index.html": ("Research Collaboration" + S, "Collaborate with BCQP on data, corrections, topics and methods. How academics and institutions can propose joint work."),
"research/external-sector/index.html": ("External Sector and Trade in Bangladesh" + S, "BCQP research on Bangladesh's external sector: exchange rate, reserves, trade and remittances, with official sources and methods."),
"research/finance-credit/index.html": ("Finance, Credit and Banking in Bangladesh" + S, "BCQP research on private credit, banking and interest rates in Bangladesh: key questions, official data sources and methods."),
"research/growth-structure/index.html": ("Growth and Structural Change in Bangladesh" + S, "BCQP research on Bangladesh's growth, investment and structural change: key questions, official data sources and methods."),
"research/human-development/index.html": ("Human Development in Bangladesh" + S, "BCQP research on human development in Bangladesh: health, education and living standards, with official sources and methods."),
"research/inflation/index.html": ("Inflation in Bangladesh: Data and Research" + S, "BCQP research on Bangladesh inflation: CPI measurement, drivers and pass-through, with official data sources and econometric methods."),
"research/labor-wages/index.html": ("Labor Market and Wages in Bangladesh" + S, "BCQP research on Bangladesh's labor market and wages: key questions, official labor force data and the methods used."),
"research/monetary-policy/index.html": ("Monetary Policy in Bangladesh" + S, "BCQP research on Bangladesh monetary policy: policy rates, money growth, the taka and transmission, with data and methods."),
"research/public-finance/index.html": ("Public Finance and Fiscal Policy in Bangladesh" + S, "BCQP research on Bangladesh public finance: revenue, spending, deficits and debt, with official sources and econometric methods."),
"tuhin-al-mamun/index.html": ("Dr. Tuhin G. M. Al Mamun, Economist and BCQP Co-Founder", "Dr. Tuhin G. M. Al Mamun is an economist and BCQP co-founder working on monetary policy, econometrics and macroeconomic research on Bangladesh."),
"briefs/growth-and-investment-2026-11-14.html": ("Growth and Investment in Bangladesh, 1991–2025" + S, "How far does capital formation carry output in Bangladesh? Peer benchmarks and five models on investment, savings, FDI and growth, with data."),
"briefs/private-credit-and-banking-2026-11-14.html": ("Private Credit and Banking in Bangladesh, 1992–2025" + S, "Private credit, broad money, interest rates and growth in Bangladesh: peer benchmarks and five model specifications, with replication data."),
"briefs/inflation-taka-and-policy-stance-2026-11-14.html": ("Inflation, the Taka and Monetary Policy in Bangladesh" + S, "Inflation hit 10.5% in 2024 while lending rates stayed below it. Nine estimates on taka pass-through, from 13 official macro series."),
"briefs/money-and-prices-2026-11-14.html": ("Money Growth and Inflation in Bangladesh, 1992–2025" + S, "Does money growth move inflation in Bangladesh? Peer benchmarks and five model specifications on 12 official variables, with replication data."),
}
E1 = lambda x: html.escape(x, quote=True)
for rel, (t, d) in M.items():
    p = ROOT / rel; s = p.read_text(encoding="utf-8")
    ot = re.search(r"<title>(.*?)</title>", s)[1]; od = re.search(r'<meta name="description" content="(.*?)">', s)[1]
    s = s.replace("<title>%s</title>" % ot, "<title>%s</title>" % E1(t))
    for a, b in ((od, E1(d)),):
        s = s.replace('content="%s"' % a, 'content="%s"' % b)
    for k in ('og:title', 'twitter:title'):
        s = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % k, lambda m: m.group(1) + E1(t) + m.group(2), s)
    s = s.replace(json_old := '"description": "%s"' % html.unescape(od).replace('"', '\\"'), '"description": "%s"' % d.replace('"', '\\"'))
    s = s.replace('"name": "%s"' % html.unescape(ot), '"name": "%s"' % t)
    p.write_text(s, encoding="utf-8")
print(len(M), "pages")
