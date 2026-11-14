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
  function topicHref(t) { return root + "briefs/index.html#" + encodeURIComponent(t); }

  /* ---------- masthead, navigation, footer ---------- */
  var parts = location.pathname.split("/").filter(Boolean);
  var sections = [
    ["Policy briefs", "briefs/index.html", "briefs"],
    ["Data hub", "data/index.html", "data"],
    ["Methodology", "methodology/index.html", "methodology"],
    ["Policies", "policies/index.html", "policies"],
    ["About", "about/index.html", "about"],
    ["Contact", "contact/index.html", "contact"]
  ];
  var current = "";
  sections.forEach(function (i) { if (parts.indexOf(i[2]) > -1) current = i[2]; });

  var briefDrop = '<div class="drop"><div class="dh">Browse</div><a href="' + root + 'briefs/index.html">All policy briefs</a>' +
    '<div class="dh">By topic</div>' + D.topics.map(function (t) { return '<a href="' + topicHref(t.name) + '">' + esc(t.name) + "</a>"; }).join("") + "</div>";

  var navHtml = '<div class="item"><a' + (current === "" && parts.join("/").indexOf("404") < 0 ? ' class="on" aria-current="page"' : "") + ' href="' + root + 'index.html">Home</a></div>' +
    sections.map(function (i) {
      var on = i[2] === current ? ' class="on" aria-current="page"' : "";
      var has = i[2] === "briefs";
      return '<div class="item' + (has ? " has" : "") + '"><a' + on + ' href="' + root + i[1] + '">' + i[0] + "</a>" + (has ? briefDrop : "") + "</div>";
    }).join("");
  // Home is "on" only on the home page
  if (current !== "") navHtml = navHtml.replace(' class="on" aria-current="page" href="' + root + 'index.html"', ' href="' + root + 'index.html"');

  var hdr = document.getElementById("hdr");
  if (hdr) {
    hdr.innerHTML =
      '<a class="skip" href="#main">Skip to main content</a>' +
      '<div class="topbar">Quantitative evidence. Economic research. Better policy.</div>' +
      '<header class="masthead"><div class="wrap">' +
      '<a class="brand" href="' + root + 'index.html"><span class="logo">BIQEP</span><span><b>Bangladesh Institute of Quantitative Economics and Public Policy</b><small>BIQEP · Policy briefs</small></span></a>' +
      '<button class="menubtn" aria-expanded="false" aria-controls="primary">Menu</button></div></header>' +
      '<nav class="primary" id="primary" aria-label="Main"><div class="wrap">' + navHtml + "</div></nav>";
    var btn = hdr.querySelector(".menubtn"), nv = hdr.querySelector("nav.primary");
    btn.addEventListener("click", function () {
      var o = nv.classList.toggle("open");
      btn.setAttribute("aria-expanded", o ? "true" : "false");
    });
  }

  var ftr = document.getElementById("ftr");
  if (ftr) {
    ftr.innerHTML =
      '<footer class="site"><div class="wrap"><div class="cols">' +
      '<div class="about"><b>Bangladesh Institute of Quantitative Economics and Public Policy</b><p>BIQEP Policy Briefs is the institute’s public-policy series on Bangladesh. Every figure is checked against an official source before publication.</p></div>' +
      '<div><h4>Briefs</h4><a href="' + root + 'briefs/index.html">All policy briefs</a><a href="' + root + 'data/index.html">Data hub</a><a href="' + root + 'methodology/index.html">Methodology</a></div>' +
      '<div><h4>Institute</h4><a href="' + root + 'about/index.html">About</a><a href="' + root + 'policies/index.html">Policies</a><a href="' + root + 'contact/index.html">Contact</a></div>' +
      '<div><h4>Open tools</h4><a href="https://tuhingm.github.io/almamun/oes/" rel="noopener">Open Econometric Systems</a><a href="https://github.com/tuhingm/open-econometric-systems" rel="noopener">OES on GitHub</a></div>' +
      '</div><p class="legal">BIQEP is an independent research initiative. It is not a government body and is not affiliated with Bangladesh Bank, the Bangladesh Bureau of Statistics or the Government of Bangladesh. Views are the author’s own. Briefs describe evidence and are not investment, legal or policy-implementation advice. Site data last updated ' +
      esc(fmtDate(D.updated)) + ".</p></div></footer>";
  }

  /* ---------- helpers ---------- */
  function statusTag(st) {
    var m = { verified: ["ok", "Verified"], pending: ["wip", "Pending"], published: ["ok", "Published"], "in-preparation": ["wip", "In preparation"], draft: ["wip", "Draft"] };
    var x = m[st] || ["", st];
    return '<span class="tag ' + x[0] + '">' + x[1] + "</span>";
  }
  function count(list, f) { return list.filter(f).length; }
  var verified = D.series.filter(function (x) { return x.status === "verified"; });
  var pending = D.series.filter(function (x) { return x.status !== "verified"; });
  var published = D.briefs.filter(function (b) { return b.status === "published"; });

  function recItem(b) {
    return '<a class="rec" href="' + root + "briefs/" + esc(b.slug) + '.html">' +
      '<div class="when">' + esc(b.date) + "</div><div>" + statusTag(b.status) + '<span class="tag">' + esc(b.topic) + '</span><span class="tag">' + esc(b.type) + "</span>" +
      "<h3>" + esc(b.title) + "</h3><p>" + esc(b.summary) + "</p></div></a>";
  }
  function noPublished() {
    return '<div class="empty"><h3>No published briefs yet</h3><p>Briefs appear in this list as published only after the data are validated and the author has approved the text. Items marked “in preparation” are not findings.</p></div>';
  }

  /* ---------- renderers ---------- */
  var R = {};

  R.indicators = function (el) {
    var html = verified.map(function (x) {
      var prev = x.history && x.history[0];
      return '<div class="ind"><span class="k">' + esc(x.name) + '</span><span class="v">' + esc(x.latest.value.toFixed(2)) + esc(x.unit) +
        '</span><span class="m">' + esc(x.latest.period) + (prev ? " · " + esc(prev.period) + " " + esc(prev.value.toFixed(2)) + esc(x.unit) : "") +
        '</span><span class="s">' + esc(x.source.split(",")[0].replace(/ \(BBS\)/, "")) + " · " + esc(fmtDate(x.retrieved)) + "</span></div>";
    }).join("");
    if (pending.length) {
      html += '<div class="ind pend"><span class="k">Other series</span><span class="v t">' + pending.length + ' awaiting verification</span><span class="m">Shown here only after each is checked against its official release.</span><span class="s">See the Data hub</span></div>';
    }
    el.innerHTML = html || '<div class="empty"><h3>No verified series yet</h3></div>';
  };

  R.stats = function (el) {
    var st = [
      [verified.length, "series verified against an official release"],
      [pending.length, "series awaiting verification"],
      [count(D.briefs, function (b) { return b.status === "in-preparation"; }), "brief in preparation"],
      [published.length, "briefs published"]
    ];
    el.innerHTML = st.map(function (x) { return '<div class="stat"><b>' + String(x[0]).padStart(2, "0") + "</b><span>" + x[1] + "</span></div>"; }).join("");
  };

  R["series-table"] = function (el) {
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
  };

  R.latest = function (el) {
    el.innerHTML = D.briefs.length ? D.briefs.slice(0, 1).map(recItem).join("") + (published.length ? "" : noPublished()) : noPublished();
  };

  R.topics = function (el) {
    el.innerHTML = D.topics.map(function (t, i) {
      return '<a class="link-card" href="' + topicHref(t.name) + '"><span class="num">' + String(i + 1).padStart(2, "0") + "</span><h3>" + esc(t.name) + "</h3><p>" + esc(t.text) + "</p></a>";
    }).join("");
  };

  R["topic-chips"] = function (el) {
    el.innerHTML = D.topics.map(function (t) { return '<a class="chip" href="' + topicHref(t.name) + '">' + esc(t.name) + "</a>"; }).join("");
  };

  R.sidebar = function (el) {
    var mode = el.getAttribute("data-mode") || "site";
    function draw() {
      var h = decodeURIComponent((location.hash || "").slice(1));
      var html;
      if (mode === "topics") {
        html = "<h4>Briefs by topic</h4><a" + (h ? "" : ' class="on"') + ' href="' + root + 'briefs/index.html#">All policy briefs</a>' +
          D.topics.map(function (t) { return "<a" + (h === t.name ? ' class="on"' : "") + ' href="' + topicHref(t.name) + '">' + esc(t.name) + "</a>"; }).join("") +
          '<a href="' + root + 'data/index.html">Data hub</a><a href="' + root + 'methodology/index.html">Methodology</a>';
      } else {
        html = "<h4>Site sections</h4>" + sections.map(function (i) {
          return "<a" + (i[2] === current ? ' class="on"' : "") + ' href="' + root + i[1] + '">' + i[0] + "</a>";
        }).join("");
      }
      el.innerHTML = html;
    }
    draw();
    if (mode === "topics") window.addEventListener("hashchange", draw);
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
      list.innerHTML = sel.length ? sel.map(recItem).join("") :
        '<div class="empty"><h3>No briefs match</h3><p>' + (t ? "There are no briefs under “" + esc(t) + "” yet." : "No brief matches that search.") + "</p></div>";
      after.innerHTML = published.length ? "" : noPublished();
    }
    fc.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      var t = b.getAttribute("data-t");
      if (t) location.hash = encodeURIComponent(t); else history.replaceState(null, "", location.pathname), draw(), window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
    q.addEventListener("input", draw);
    window.addEventListener("hashchange", draw);
    draw();
  };

  [].forEach.call(document.querySelectorAll("[data-render]"), function (el) {
    var f = R[el.getAttribute("data-render")]; if (f) f(el);
  });
})();
