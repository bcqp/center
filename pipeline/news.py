"""Rank topics from news headlines. News is a hint only: it never supplies a number."""
import re, urllib.request, xml.etree.ElementTree as ET
from common import cfg, UA

def fetch_feed(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        root = ET.fromstring(r.read())
    out = []
    for it in root.iter("item"):
        out.append({"title": (it.findtext("title") or "").strip(), "desc": re.sub("<[^>]+>", " ", it.findtext("description") or "")[:300]})
    for en in root.iter("{http://www.w3.org/2005/Atom}entry"):
        out.append({"title": (en.findtext("{http://www.w3.org/2005/Atom}title") or "").strip(), "desc": ""})
    return out

def score(items, topics):
    res = {}
    for t in topics:
        n, hits = 0, []
        for it in items:
            text = (it["title"] + " " + it["desc"]).lower()
            m = sum(1 for k in t["keywords"] if re.search(r"\b" + re.escape(k) + r"\b", text))
            if m:
                n += m; hits.append(it["title"])
        res[t["slug"]] = {"score": n, "headlines": hits[:5]}
    return res

def run(log):
    items = []
    for f in cfg("feeds.json")["feeds"]:
        try:
            got = fetch_feed(f["url"]); items += got
            log.append("feed ok: %s (%d items)" % (f["name"], len(got)))
        except Exception as e:
            log.append("feed skipped: %s (%s)" % (f["name"], type(e).__name__))
    return score(items, cfg("topics.json")["topics"]), len(items)
