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
  function fmtDate(iso) {
    if (!iso) return "";
    var m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var p = iso.split("-");
    return (p[2] ? p[2] + " " : "") + m[+p[1] - 1] + " " + p[0];
  }

  /* ---------- header, nav, footer ---------- */
  var items = [
    ["Home", "index.html", ""],
    ["Policy briefs", "briefs/index.html", "briefs"],
    ["Data hub", "data/index.html", "data"],
    ["Methodology", "methodology/index.html", "methodology"],
    ["About", "about/index.html", "about"],
    ["Contact", "contact/index.html", "contact"]
  ];
  var parts = location.pathname.split("/").filter(Boolean);
  var current = "";
  items.forEach(function (i) { if (i[2] && parts.indexOf(i[2]) > -1) current = i[2]; });

  var nav = items.map(function (i) {
    return '<a' + (i[2] === current ? ' class="on" aria-current="page"' : "") + ' href="' + root + i[1] + '">' + i[0] + "</a>";
  }).join("");

  var hdr = document.getElementById("hdr");
  if (hdr) {
    hdr.innerHTML =
      '<a class="skip" href="#main">Skip to content</a>' +
      '<div class="topbar">Quantitative evidence. Economic research. Better policy.</div>' +
      '<header class="site"><div class="wrap bar">' +
      '<a class="brand" href="' + root + 'index.html"><span class="logo">BIQEP</span><span><b>BIQEP Policy Briefs</b><small>Bangladesh Institute of Quantitative Economics and Public Policy</small></span></a>' +
      '<button class="navtoggle" aria-expanded="false" aria-controls="mainnav">Menu</button></div>' +
      '<nav class="main" id="mainnav" aria-label="Main"><div class="wrap">' + nav + "</div></nav></header>";
    var btn = hdr.querySelector(".navtoggle"), nv = hdr.querySelector("nav.main");
    btn.addEventListener("click", function () {
      var o = nv.classList.toggle("open");
      btn.setAttribute("aria-expanded", o ? "true" : "false");
    });
  }

  var ftr = document.getElementById("ftr");
  if (ftr) {
    ftr.innerHTML =
      '<footer class="site"><div class="wrap"><div class="cols">' +
      '<div><b>BIQEP Policy Briefs</b><p>Data-driven analysis of Bangladesh’s economy. Every figure is checked against an official source before publication.</p></div>' +
      '<div><b>Explore</b><a href="' + root + 'briefs/index.html">Policy briefs</a><a href="' + root + 'data/index.html">Data hub</a><a href="' + root + 'methodology/index.html">Methodology</a></div>' +
      '<div><b>Institute</b><a href="' + root + 'about/index.html">About</a><a href="' + root + 'contact/index.html">Contact</a></div>' +
      '<div><b>Open tools</b><a href="https://tuhingm.github.io/almamun/oes/" rel="noopener">Open Econometric Systems</a><a href="https://github.com/tuhingm/open-econometric-systems" rel="noopener">OES on GitHub</a></div>' +
      '</div><p class="legal">BIQEP is an independent research initiative. It is not a government body and is not affiliated with Bangladesh Bank, the Bangladesh Bureau of Statistics or the Government of Bangladesh. Views are the author’s own. Figures are for information, not investment or legal advice. Site data last updated ' +
      esc(fmtDate(D.updated)) + ".</p></div></footer>";
  }

  /* ---------- data-driven blocks ---------- */
  function statusTag(st) {
    var m = { verified: ["ok", "Verified"], pending: ["wip", "Pending"], published: ["ok", "Published"], "in-preparation": ["wip", "In preparation"], draft: ["wip", "Draft"] };
    var x = m[st] || ["", st];
    return '<span class="tag ' + x[0] + '">' + x[1] + "</span>";
  }

  function indicators(el) {
    var max = +el.getAttribute("data-max") || 99;
    var list = D.series.filter(function (x) { return x.status === "verified"; }).slice(0, max);
    var pend = D.series.filter(function (x) { return x.status !== "verified"; }).length;
    var html = list.map(function (x) {
      var prev = x.history && x.history[0];
      return '<div class="ind"><span class="k">' + esc(x.name) + '</span><span class="v">' + esc(x.latest.value.toFixed(2)) + esc(x.unit) +
        '</span><span class="delta">' + esc(x.latest.period) + (prev ? " · " + esc(prev.period) + " " + esc(prev.value.toFixed(2)) + esc(x.unit) : "") +
        '</span><br><span class="m">' + esc(x.source.split(",")[0]) + " · retrieved " + esc(fmtDate(x.retrieved)) + "</span></div>";
    }).join("");
    if (pend) {
      html += '<div class="ind"><span class="k">Other series</span><span class="v pending">' + pend + ' awaiting verification</span><span class="m">Shown once checked against the official release</span></div>';
    }
    el.innerHTML = html || '<div class="empty">No verified series yet.</div>';
  }

  function seriesTable(el) {
    var rows = D.series.map(function (x) {
      var v = x.status === "verified"
        ? esc(x.latest.value.toFixed(2)) + esc(x.unit) + '<br><span class="small muted">' + esc(x.latest.period) + "</span>"
        : '<span class="muted">Not yet verified</span>';
      var src = x.url ? '<a href="' + esc(x.url) + '" rel="noopener">' + esc(x.source) + "</a>" : esc(x.source);
      return "<tr><td><b>" + esc(x.name) + '</b><br><span class="small muted">' + esc(x.topic) + "</span></td><td>" + statusTag(x.status) +
        '</td><td class="n">' + v + "</td><td>" + src + "</td><td>" + (x.retrieved ? esc(fmtDate(x.retrieved)) : "—") +
        '</td><td class="small muted">' + esc(x.note || "") + "</td></tr>";
    }).join("");
    el.innerHTML = '<table><thead><tr><th>Series</th><th>Status</th><th class="n">Latest</th><th>Source</th><th>Retrieved</th><th>Notes</th></tr></thead><tbody>' + rows + "</tbody></table>";
  }

  function briefItem(b) {
    return '<a class="bitem" href="' + root + "briefs/" + esc(b.slug) + '.html" data-topic="' + esc(b.topic) + '">' +
      '<div class="when">' + esc(b.date) + "</div><div>" + statusTag(b.status) + '<span class="tag">' + esc(b.topic) + '</span><span class="tag">' + esc(b.type) +
      "</span><h3>" + esc(b.title) + "</h3><p>" + esc(b.summary) + "</p></div></a>";
  }

  function briefsList(el) {
    var all = D.briefs.slice();
    var topics = [];
    all.forEach(function (b) { if (topics.indexOf(b.topic) < 0) topics.push(b.topic); });
    var fl = document.getElementById("filters");
    function draw(t) {
      var sel = t ? all.filter(function (b) { return b.topic === t; }) : all;
      el.innerHTML = sel.length ? sel.map(briefItem).join("") : '<div class="empty">No briefs in this topic yet.</div>';
    }
    if (fl) {
      fl.innerHTML = '<button class="on" data-t="">All</button>' + topics.map(function (t) { return '<button data-t="' + esc(t) + '">' + esc(t) + "</button>"; }).join("");
      fl.addEventListener("click", function (e) {
        var b = e.target.closest("button"); if (!b) return;
        [].forEach.call(fl.children, function (c) { c.classList.remove("on"); });
        b.classList.add("on"); draw(b.getAttribute("data-t"));
      });
    }
    draw("");
  }

  function latest(el) {
    var b = D.briefs[0];
    el.innerHTML = b ? briefItem(b) : '<div class="empty">No briefs yet.</div>';
  }

  function topics(el) {
    el.innerHTML = D.topics.map(function (t) { return '<div class="card"><h3>' + esc(t.name) + "</h3><p>" + esc(t.text) + "</p></div>"; }).join("");
  }

  var map = { indicators: indicators, "series-table": seriesTable, "briefs-list": briefsList, latest: latest, topics: topics };
  [].forEach.call(document.querySelectorAll("[data-render]"), function (el) {
    var f = map[el.getAttribute("data-render")]; if (f) f(el);
  });
})();
