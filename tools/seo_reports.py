"""Give every report page full link-preview and scholar metadata, and draw its 1200x630 preview image.
Usage: seo_reports.py <dir containing <slug>.html and <slug>/ folders>   (idempotent)"""
import re, sys, json, html, pathlib, textwrap
from PIL import Image, ImageDraw, ImageFont
B = "https://tuhingm.github.io/biqep-policy/"; D = pathlib.Path(sys.argv[1])
F = lambda n, z: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf" % ("-Bold" if n else ""), z)
def card(title, thumb, out):
    im = Image.new("RGB", (1200, 630), "#10283f"); d = ImageDraw.Draw(im)
    d.rectangle([0, 598, 1200, 630], fill="#c6a15b"); d.text((60, 56), "BIQEP POLICY BRIEFS", font=F(1, 26), fill="#c6a15b")
    y = 120
    for ln in textwrap.wrap(title, 19)[:6]: d.text((60, y), ln, font=F(1, 42), fill="#ffffff"); y += 58
    d.text((60, 520), "Tuhin G. M. Al Mamun and Dr Rahim Md Abdur", font=F(0, 24), fill="#d8e0ea")
    if thumb.exists():
        t = Image.open(thumb).convert("RGB"); t.thumbnail((470, 440)); px, py = 1140 - t.width, 130
        d.rectangle([px - 8, py - 8, px + t.width + 8, py + t.height + 8], fill="#ffffff"); im.paste(t, (px, py))
    im.save(out, quality=88, optimize=True)
for p in sorted(D.glob("*-2026-*.html")):
    slug = p.stem; s = p.read_text(encoding="utf-8")
    title = html.unescape(re.search(r"<h1>(.*?)</h1>", s).group(1))
    card(title, D / slug / "thumb.jpg", D / slug / "og.jpg")
    if 'name="citation_title"' in s: continue
    desc = html.unescape(re.search(r'<meta name="description" content="(.*?)">', s).group(1))
    date = re.search(r"Statistical report · (\d{4}-\d{2}-\d{2})", s).group(1)
    url = B + "briefs/%s.html" % slug; img = B + "briefs/%s/og.jpg" % slug; e = lambda t: html.escape(t, quote=True)
    block = ('<meta property="og:site_name" content="BIQEP Policy Briefs"><meta property="og:locale" content="en_US"><meta property="og:url" content="%s"><meta property="og:description" content="%s">'
             '<meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="%s">'
             '<meta property="article:published_time" content="%s"><meta property="article:author" content="Tuhin G. M. Al Mamun"><meta property="article:author" content="Dr Rahim Md Abdur">'
             '<meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s"><meta name="twitter:image:alt" content="%s">'
             '<meta name="citation_title" content="%s"><meta name="citation_author" content="Al Mamun, Tuhin G. M."><meta name="citation_author" content="Rahim, Md Abdur">'
             '<meta name="citation_publication_date" content="%s"><meta name="citation_publisher" content="BIQEP Policy Briefs"><meta name="citation_abstract_html_url" content="%s"><meta name="citation_language" content="en">') % (
             url, e(desc), img, e("Preview card: " + title), date, e(title), e(desc), img, e("Preview card: " + title), e(title), date.replace("-", "/"), url)
    s = re.sub(r'<meta property="og:image" content="[^"]*">', "", s, count=1)
    s = s.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary_large_image">' + block, 1)
    s = s.replace('<link rel="stylesheet" href="../assets/style.css', '<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="../assets/favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="../assets/apple-touch-icon.png"><link rel="stylesheet" href="../assets/style.css', 1)
    p.write_text(s, encoding="utf-8"); print("seo", slug)
