"""Official-data fetchers. Each returns {year: value} and the exact URL used."""
import json
from common import http_get

def worldbank(code, country="BGD", start=1995):
    url = "https://api.worldbank.org/v2/country/%s/indicator/%s?format=json&per_page=200&date=%d:2100" % (country, code, start)
    j = json.loads(http_get(url))
    if not isinstance(j, list) or len(j) < 2 or not j[1]:
        raise ValueError("empty World Bank response for " + code)
    return {int(r["date"]): float(r["value"]) for r in j[1] if r["value"] is not None}, url

def imf(code, country="BGD"):
    url = "https://www.imf.org/external/datamapper/api/v1/%s/%s" % (code, country)
    j = json.loads(http_get(url))
    d = j["values"][code][country]
    return {int(y): float(v) for y, v in d.items() if v is not None}, url

def get(source, code):
    if source == "worldbank": return worldbank(code)
    if source == "imf": return imf(code)
    raise NotImplementedError("no fetcher for source: " + source)
