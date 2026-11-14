"""Append a version query to asset URLs in every HTML page so browsers fetch fresh data after each publish."""
import pathlib, re, sys
R = pathlib.Path(__file__).resolve().parents[1]; v = sys.argv[1]
for p in R.rglob("*.html"):
    if ".git" in p.parts: continue
    s = p.read_text(encoding="utf-8")
    n = re.sub(r'(assets/(?:data|pages|site)\.js|assets/style\.css)(\?v=\w+)?"', r'\1?v=%s"' % v, s)
    if n != s: p.write_text(n, encoding="utf-8")
