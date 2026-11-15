(function () {
  "use strict";
  var s = document.currentScript;
  var root = s.getAttribute("data-root") || "./";
  var D = window.BIQEP || { series: [], briefs: [], topics: [] };

  function esc(t) {
    return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function fmtDate(iso) {
    if (!iso) return "";
    var p = iso.split("-");
    return (p[2] ? +p[2] + " " : "") + MONTHS[+p[1] - 1] + " " + p[0];
  }

  /* ---------- site map (single source for nav, sidebars, footer) ---------- */
  var topicKids = D.topics.map(function (t) { return [t.name, "research/" + t.slug + "/"]; });
  var NAV = [
    { label: "About", key: "about", href: "about/", kids: [
      ["The series", "about/"], ["Mission and vision", "about/mission-vision/"], ["Research philosophy", "about/research-philosophy/"],
      ["Leadership", "about/leadership/"], ["Governance", "about/governance/"]] },
    { label: "Research", key: "research", href: "research/", kids: [["Research agenda", "research/"]].concat(topicKids, [["Research collaboration", "research/collaboration/"]]) },
    { label: "Policy briefs", key: "briefs", href: "briefs/", kids: [
      ["All records", "briefs/"], ["Data notes", "briefs/data-notes/"], ["Bangladesh Economic Outlook", "briefs/outlook/"],
      ["Statistical reports", "briefs/statistical-reports/"], ["Replication materials", "briefs/replication/"]] },
    { label: "Data hub", key: "data", href: "data/", kids: [
      ["Series register", "data/"], ["Official sources", "data/sources/"], ["Validation log", "data/validation/"]] },
    { label: "Methodology", key: "methodology", href: "methodology/", kids: [
      ["How a brief is made", "methodology/"], ["Models and tools", "methodology/models/"], ["Data standards", "methodology/data-standards/"], ["Replication", "methodology/replication/"]] },
    { label: "Policies", key: "policies", href: "policies/", kids: [
      ["Series policies", "policies/"], ["Publication policy", "policies/publication/"], ["Data and sources policy", "policies/data-sources/"],
      ["Validation policy", "policies/validation/"], ["Replication policy", "policies/replication/"], ["Corrections policy", "policies/corrections/"],
      ["Copyright and reuse", "policies/copyright/"], ["Conflict-of-interest policy", "policies/conflict-of-interest/"]] },
    { label: "News", key: "news", href: "news/", kids: [["News", "news/"], ["Events", "news/events/"]] },
    { label: "Journal", key: "journal", href: "journal/" },
    { label: "Contact", key: "contact", href: "contact/" }
  ];

  /* ---------- where are we? ---------- */
  var depth = (root.match(/\.\.\//g) || []).length;
  var segs = location.pathname.split("/").filter(Boolean);
  var isFile = segs.length && /\.html$/.test(segs[segs.length - 1]) && segs[segs.length - 1] !== "index.html";
  if (segs.length && segs[segs.length - 1] === "index.html") segs.pop();
  var relSegs = depth ? segs.slice(-(depth + (isFile ? 1 : 0))) : [];
  if (root.charAt(0) === "/") relSegs = []; // 404 page
  var rel = relSegs.join("/");
  function norm(h) { return h.replace(/index\.html$/, "").replace(/\/+$/, ""); }
  var curKey = relSegs[0] || "";
  var section = NAV.filter(function (n) { return n.key === curKey; })[0] || null;

  /* ---------- masthead, nav ---------- */
  function navItem(n) {
    var on = n.key === curKey;
    var has = n.kids && n.kids.length > 1;
    var drop = has ? '<div class="drop">' + n.kids.map(function (k) { return '<a href="' + root + k[1] + '">' + esc(k[0]) + "</a>"; }).join("") + "</div>" : "";
    return '<div class="item' + (has ? " has" : "") + '"><a' + (on ? ' class="on" aria-current="page"' : "") + ' href="' + root + n.href + '">' + esc(n.label) + "</a>" + drop + "</div>";
  }
  var navHtml = '<div class="item"><a' + (curKey === "" && root.charAt(0) !== "/" ? ' class="on" aria-current="page"' : "") + ' href="' + root + 'index.html">Home</a></div>' + NAV.map(navItem).join("");

  var hdr = document.getElementById("hdr");
  if (hdr) {
    hdr.innerHTML =
      '<a class="skip" href="#main">Skip to main content</a>' +
      '<div class="topbar">Quantitative evidence. Economic research. Better policy.</div>' +
      '<header class="masthead"><div class="wrap">' +
      '<a class="brand" href="' + root + 'index.html"><span class="logo">BIQEP</span><span><b>Bangladesh Institute of Quantitative Economics and Public Policy</b><small>BIQEP · Policy briefs</small></span></a>' +
      '<div class="tools"><a class="iconbtn" href="' + root + 'search/index.html" aria-label="Search the site"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><span>Search</span></a>' +
      '<button class="menubtn" aria-expanded="false" aria-controls="primary">Menu</button></div></div></header>' +
      '<nav class="primary" id="primary" aria-label="Main"><div class="wrap">' + navHtml + "</div></nav>";
    var btn = hdr.querySelector(".menubtn"), nv = hdr.querySelector("nav.primary");
    btn.addEventListener("click", function () {
      var o = nv.classList.toggle("open");
      btn.setAttribute("aria-expanded", o ? "true" : "false");
    });
  }

  /* ---------- footer ---------- */
  var ftr = document.getElementById("ftr");
  if (ftr) {
    function fcol(n) {
      return "<div><h4>" + esc(n.label) + "</h4>" + (n.kids || [[n.label, n.href]]).map(function (k) { return '<a href="' + root + k[1] + '">' + esc(k[0]) + "</a>"; }).join("") + "</div>";
    }
    var byKey = {}; NAV.forEach(function (n) { byKey[n.key] = n; });
    var misc = { label: "More", kids: [["News and events", "news/"], ["Contact", "contact/"], ["Search", "search/index.html"],
      ["Open Econometric Systems", "https://tuhingm.github.io/almamun/oes/"]] };
    var miscHtml = "<div><h4>More</h4>" + misc.kids.map(function (k) {
      var ext = /^https?:/.test(k[1]);
      return '<a href="' + (ext ? "" : root) + k[1] + '"' + (ext ? ' rel="noopener"' : "") + ">" + esc(k[0]) + "</a>";
    }).join("") + "</div>";
    ftr.innerHTML =
      '<footer class="site"><div class="wrap"><div class="fgrid">' +
      '<div class="about"><b>Bangladesh Institute of Quantitative Economics and Public Policy</b><p>BIQEP Policy Briefs is the institute’s public-policy series on Bangladesh. Every figure is checked against an official source before publication, and every estimate is run in an open, reproducible engine.</p>' +
      '<p class="mono tiny">Quantitative evidence. Economic research. Better policy.</p></div>' +
      fcol(byKey.about) + fcol(byKey.briefs) + fcol(byKey.data) + fcol(byKey.methodology) + fcol(byKey.policies) + miscHtml +
      '</div><p class="legal">BIQEP is an independent research initiative. It is not a government body and is not affiliated with Bangladesh Bank, the Bangladesh Bureau of Statistics or the Government of Bangladesh. Founded and written by <a href="' + root + 'tuhin-al-mamun/">Dr. Tuhin G. M. Al Mamun</a>; views are the author’s own. Archived at <a href="https://doi.org/10.5281/zenodo.24215521">doi.org/10.5281/zenodo.24215521</a>. Site data last updated ' +
      esc(fmtDate(D.updated)) + ".</p></div></footer>";
  }

  /* ---------- helpers ---------- */
  function statusTag(st) {
    var m = { verified: ["ok", "Verified"], published: ["ok", "Published"] };
    var x = m[st] || ["", st];
    return '<span class="tag ' + x[0] + '">' + x[1] + "</span>";
  }
  var verified = D.series.filter(function (x) { return x.status === "verified"; });
  var published = D.briefs.filter(function (b) { return b.status === "published"; });

  function recItem(b) {
    return '<a class="rec" href="' + root + "briefs/" + esc(b.slug) + '.html">' +
      '<div class="when">' + esc(b.date) + "</div><div>" + statusTag(b.status) + '<span class="tag">' + esc(b.topic) + '</span><span class="tag">' + esc(b.type) + "</span>" +
      "<h3>" + esc(b.title) + "</h3><p>" + esc(b.summary) + "</p></div></a>";
  }
  function emptyBox(title, text) {
    return '<div class="empty"><h3>' + esc(title) + "</h3><p>" + esc(text) + "</p></div>";
  }
  function topicHref(t) { return root + "briefs/index.html#" + encodeURIComponent(t); }

  /* ---------- renderers ---------- */
  var R = {};

  R.indicators = function (el) {
    var html = verified.map(function (x) {
      var prev = x.history && x.history[0];
      return '<div class="ind"><span class="k">' + esc(x.name) + '</span><span class="v">' + esc(x.latest.value.toFixed(2)) + esc(x.unit) +
        '</span><span class="m">' + esc(x.latest.period) + (prev ? " · " + esc(prev.period) + " " + esc(prev.value.toFixed(2)) + esc(x.unit) : "") +
        '</span><span class="s">' + esc(x.source.split(",")[0].replace(/ \(BBS\)/, "")) + " · " + esc(fmtDate(x.retrieved)) + "</span></div>";
    }).join("");
    el.innerHTML = html || emptyBox("No verified series yet", "");
  };

  R.stats = function (el) {
    var st = [
      [verified.length, "series with official sources"],
      [D.topics.length, "research areas"],
      [5, "record collections"],
      [published.length, "briefs published"]
    ];
    el.innerHTML = st.map(function (x) { return '<div class="stat"><b>' + String(x[0]).padStart(2, "0") + "</b><span>" + x[1] + "</span></div>"; }).join("");
  };

  R["series-table"] = function (el) {
    var rows = D.series.map(function (x) {
      var v = x.status === "verified"
        ? esc(x.latest.value.toFixed(2)) + esc(x.unit) + '<br><span class="small muted">' + esc(x.latest.period) + "</span>"
        : "";
      var src = x.url ? '<a href="' + esc(x.url) + '" rel="noopener">' + esc(x.source) + "</a>" : esc(x.source);
      return "<tr><td><b>" + esc(x.name) + '</b><br><span class="small muted">' + esc(x.topic) + "</span></td><td>" + statusTag(x.status) +
        '</td><td class="n">' + v + "</td><td>" + src + "</td><td>" + (x.retrieved ? esc(fmtDate(x.retrieved)) : "—") +
        '</td><td class="small muted">' + esc(x.note || "") + "</td></tr>";
    }).join("");
    el.innerHTML = '<table><thead><tr><th>Series</th><th>Status</th><th class="n">Latest</th><th>Source</th><th>Retrieved</th><th>Notes</th></tr></thead><tbody>' + rows + "</tbody></table>";
  };

  R.validation = function (el) {
    var rows = D.series.map(function (x) {
      var res = "Value read from the official release and matched to the figure used.";
      return "<tr><td><b>" + esc(x.name) + "</b></td><td>" + (x.retrieved ? esc(fmtDate(x.retrieved)) : "—") + "</td><td>" + statusTag(x.status) +
        "</td><td>" + esc(res) + '</td><td class="small muted">' + esc(x.note || "") + "</td></tr>";
    }).join("");
    el.innerHTML = '<table><thead><tr><th>Series</th><th>Checked</th><th>Status</th><th>Result</th><th>Note</th></tr></thead><tbody>' + rows + "</tbody></table>";
  };

  R.latest = function (el) {
    el.innerHTML = D.briefs.length ? recItem(D.briefs[0]) + (published.length ? "" : emptyBox("No published briefs yet", "")) : emptyBox("No published briefs yet", "Policy briefs will appear here.");
  };

  R.collection = function (el) {
    var type = el.getAttribute("data-type"), topic = el.getAttribute("data-topic");
    var sel = D.briefs.filter(function (b) { return (!type || b.type === type) && (!topic || b.topic === topic); });
    var title = el.getAttribute("data-empty-title") || "No records yet";
    var text = el.getAttribute("data-empty") || "No records yet.";
    el.innerHTML = sel.length ? sel.map(recItem).join("") + (published.length ? "" : "") : emptyBox(title, text);
  };

  R.topics = function (el) {
    el.innerHTML = D.topics.map(function (t, i) {
      return '<a class="link-card" href="' + root + "research/" + t.slug + '/"><span class="num">' + String(i + 1).padStart(2, "0") + "</span><h3>" + esc(t.name) + "</h3><p>" + esc(t.text) + "</p></a>";
    }).join("");
  };

  R["topic-chips"] = function (el) {
    el.innerHTML = D.topics.map(function (t) { return '<a class="chip" href="' + root + "research/" + t.slug + '/">' + esc(t.name) + "</a>"; }).join("");
  };

  R.sidebar = function (el) {
    var n = section;
    var list = n && n.kids && n.kids.length > 1 ? n.kids : null;
    var title = n ? n.label : "Site sections";
    if (!list) {
      list = NAV.map(function (x) { return [x.label, x.href]; });
      title = "Site sections";
    }
    el.innerHTML = "<h4>" + esc(title) + "</h4>" + list.map(function (k) {
      return "<a" + (norm(k[1]) === rel ? ' class="on" aria-current="page"' : "") + ' href="' + root + k[1] + '">' + esc(k[0]) + "</a>";
    }).join("");
  };

  R.siblings = function (el) {
    var n = section;
    if (!n || !n.kids || n.kids.length < 2) return;
    var others = n.kids.filter(function (k) { return norm(k[1]) !== rel; });
    el.innerHTML = '<h2>More in ' + esc(n.label.toLowerCase()) + '</h2><div class="cards">' +
      others.map(function (k) { return '<a class="link-card" href="' + root + k[1] + '"><h3>' + esc(k[0]) + '</h3><p class="link-arrow">Open</p></a>'; }).join("") + "</div>";
  };

  R["briefs-page"] = function (el) {
    el.innerHTML =
      '<div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
      '<input id="q" type="search" placeholder="Search title, summary or topic" aria-label="Search policy briefs"></div>' +
      '<div class="fchips" id="fc"></div><div id="list"></div><div id="after"></div>';
    var q = el.querySelector("#q"), fc = el.querySelector("#fc"), list = el.querySelector("#list"), after = el.querySelector("#after");
    function topicNow() { return decodeURIComponent((location.hash || "").slice(1)); }
    function draw() {
      var t = topicNow(), term = q.value.trim().toLowerCase();
      fc.innerHTML = '<button data-t=""' + (t ? "" : ' class="on"') + ">All topics</button>" +
        D.topics.map(function (x) { return '<button data-t="' + esc(x.name) + '"' + (x.name === t ? ' class="on"' : "") + ">" + esc(x.name) + "</button>"; }).join("");
      var sel = D.briefs.filter(function (b) {
        return (!t || b.topic === t) && (!term || (b.title + " " + b.summary + " " + b.topic + " " + b.type).toLowerCase().indexOf(term) > -1);
      });
      list.innerHTML = sel.length ? sel.map(recItem).join("") : emptyBox("No briefs match", t ? "There are no briefs under “" + t + "” yet." : "No brief matches that search.");
      after.innerHTML = published.length ? "" : emptyBox("No published briefs yet", "Policy briefs will appear here.");
    }
    fc.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      var t = b.getAttribute("data-t");
      if (t) { location.hash = encodeURIComponent(t); }
      else { history.replaceState(null, "", location.pathname); draw(); }
    });
    q.addEventListener("input", draw);
    window.addEventListener("hashchange", draw);
    draw();
  };

  R["site-search"] = function (el) {
    var pages = window.BIQEP_PAGES || [];
    el.innerHTML =
      '<div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
      '<input id="sq" type="search" placeholder="Search pages, topics and series" aria-label="Search the site" autofocus></div><div id="sres" style="margin-top:18px"></div>';
    var inp = el.querySelector("#sq"), out = el.querySelector("#sres");
    var params = new URLSearchParams(location.search); inp.value = params.get("q") || "";
    function run() {
      var term = inp.value.trim().toLowerCase();
      if (!term) { out.innerHTML = '<p class="muted">Type to search ' + pages.length + " pages.</p>"; return; }
      var words = term.split(/\s+/);
      var hits = pages.map(function (p) {
        var hay = (p.t + " " + p.d + " " + p.s).toLowerCase(), score = 0;
        words.forEach(function (w) {
          var re = new RegExp("(^|[^a-z0-9])" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
          if (re.test(p.t.toLowerCase())) score += 3;
          if (re.test(hay)) score += 1; else score -= 100;
        });
        return { p: p, score: score };
      }).filter(function (x) { return x.score > 0; }).sort(function (a, b) { return b.score - a.score; });
      out.innerHTML = hits.length ? hits.map(function (h) {
        return '<a class="rec" href="' + root + h.p.u + '"><div class="when">' + esc(h.p.s) + "</div><div><h3>" + esc(h.p.t) + "</h3><p>" + esc(h.p.d) + "</p></div></a>";
      }).join("") : emptyBox("No pages match", "Try a shorter or different word.");
    }
    inp.addEventListener("input", run); run();
  };

  [].forEach.call(document.querySelectorAll("[data-render]"), function (el) {
    var f = R[el.getAttribute("data-render")]; if (f) f(el);
  });
})();
