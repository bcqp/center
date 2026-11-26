import json, pathlib, urllib.request, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = pathlib.Path(__file__).resolve().parent / "config"
UA = "BIQEP-pipeline/1.0 (+https://biqep.github.io/institute/)"

def cfg(name): return json.loads((CFG / name).read_text(encoding="utf-8"))

def allowed_host(url):
    host = urllib.parse.urlparse(url).hostname or ""
    return host in {v["host"] for v in cfg("sources.json")["allow"].values()}

def http_get(url, timeout=30, check_allow=True):
    if check_allow and not allowed_host(url):
        raise PermissionError("host not on the source allowlist: " + url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()
