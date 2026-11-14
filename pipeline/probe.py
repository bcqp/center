"""One-off reachability probe, run from a GitHub runner. Reports status and size only; saves nothing."""
import urllib.request, json
from common import UA, cfg
URLS = [f["url"] for f in cfg("feeds.json")["feeds"]] + [
    "https://api.worldbank.org/v2/country/BGD/indicator/FP.CPI.TOTL.ZG?format=json&per_page=3",
    "https://www.imf.org/external/datamapper/api/v1/PCPIPCH/BGD",
    "https://www.bb.org.bd/en/index.php/econdata/inflation",
    "https://www.bb.org.bd/en/index.php/econdata/index",
    "https://bbs.gov.bd/",
]
for u in URLS:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30)
        b = r.read()
        print("OK  ", r.status, len(b), r.headers.get("content-type"), u)
    except Exception as e:
        print("FAIL", type(e).__name__, str(e)[:80], u)
