"""Build another person's card as a subfolder, using the main card (index.html) as the template.

Usage: python3 tools/build_card.py tools/cards/<slug>.json
The folder <slug>/ gets its own page, contact files, manifest and service worker; logo, icons and fonts are shared from the root.
"""
import io, json, re, sys, pathlib, segno

ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
slug = cfg['slug']; out = ROOT / slug; out.mkdir(exist_ok=True)
file_ar, file_en = f"{cfg['file']}-ar.vcf", f"{cfg['file']}-en.vcf"

def vcard(last, first, full, org, title):
    return ("BEGIN:VCARD\r\nVERSION:3.0\r\n"
            f"N:{last};{first};;;\r\nFN:{full}\r\nORG:{org}\r\nTITLE:{title}\r\n"
            f"TEL;TYPE=CELL:{cfg['phone']}\r\nEMAIL;TYPE=WORK:{cfg['email']}\r\nURL:https://hailthy.net/\r\nEND:VCARD\r\n")

vc_ar = vcard(cfg['ar']['last'], cfg['ar']['first'], cfg['ar']['name'], 'تجمع حائل الصحي', cfg['ar']['title'])
vc_en = vcard(cfg['en']['last'], cfg['en']['first'], cfg['en']['name'], 'Hail Health Cluster', cfg['en']['title'])
(out / file_ar).write_text(vc_ar, encoding='utf-8', newline='')
(out / file_en).write_text(vc_en, encoding='utf-8', newline='')

def qr(text):
    b = io.BytesIO()
    segno.make(text.replace('\r\n', '\n'), error='l', encoding='utf-8').save(
        b, kind='svg', xmldecl=False, svgns=True, dark='#0E3A66', light=None, border=0, scale=1, omitsize=True)
    return b.getvalue().decode().replace('class="segno"', 'shape-rendering="crispEdges"')

t = (ROOT / 'index.html').read_text(encoding='utf-8')
svgs = re.findall(r'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 \d+ \d+" shape-rendering="crispEdges">.*?</svg>', t, re.S)
assert len(svgs) == 2
t = t.replace(svgs[0], qr(vc_ar)).replace(svgs[1], qr(vc_en))

phone_disp = cfg['phone_display']
reps = [
    ('<title>فيصل مذود الشمري | Faisal M. Alshammari</title>', f"<title>{cfg['ar']['name']} | {cfg['en']['name']}</title>"),
    ('<meta name="apple-mobile-web-app-title" content="بطاقتي">', f'<meta name="apple-mobile-web-app-title" content="{cfg["short_name"]}">'),
    ('href="icons/', 'href="../icons/'),
    ('href="assets/', 'href="../assets/'),
    ('url(assets/', 'url(../assets/'),
    ('src="logo.png"', 'src="../logo.png"'),
    ('<p class="name">فيصل مذود الشمري</p>', f"<p class=\"name\">{cfg['ar'].get('display', cfg['ar']['name'])}</p>"),
    ('<p class="title">مدير الإدارة العامة لسلاسل الإمداد</p>', f"<p class=\"title\">{cfg['ar']['title_html']}</p>"),
    ('<p class="name">Faisal M. Alshammari</p>', f"<p class=\"name\">{cfg['en']['name']}</p>"),
    ('<p class="title">Director, General Administration<br>of Supply Chain</p>', f"<p class=\"title\">{cfg['en']['title_html']}</p>"),
    ('+966 54 369 8888', phone_disp),
    ('<meta property="og:title" content="فيصل مذود الشمري | Faisal M. Alshammari">', f'<meta property="og:title" content="{cfg["ar"]["name"]} | {cfg["en"]["name"]}">'),
    ('<meta property="og:description" content="مدير الإدارة العامة لسلاسل الإمداد - تجمع حائل الصحي">', f'<meta property="og:description" content="{cfg["ar"]["title"]} - تجمع حائل الصحي">'),
    ('content="https://faisalms468.github.io/faisal-card/"', f'content="https://faisalms468.github.io/faisal-card/{slug}/"'),
    ('content="https://faisalms468.github.io/faisal-card/images/og.jpg"', f'content="https://faisalms468.github.io/faisal-card/{slug}/images/og.jpg"'),
    ('fal-shammry@moh.gov.sa', cfg['email']),
    ('Faisal-Alshammari-ar.vcf', file_ar),
    ('Faisal-Alshammari-en.vcf', file_en),
]
for a, b in reps:
    assert a in t, a
    t = t.replace(a, b)
(out / 'index.html').write_text(t, encoding='utf-8')

json.dump({"name": f"{cfg['ar']['name']} | {cfg['en']['name']}", "short_name": cfg['short_name'], "lang": "ar", "dir": "rtl",
           "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#EEF4F9", "theme_color": "#1C8FCF",
           "icons": [{"src": "../icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                     {"src": "../icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                     {"src": "../icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
          (out / 'manifest.webmanifest').open('w', encoding='utf-8'), ensure_ascii=False, indent=2)

sw = (ROOT / 'sw.js').read_text(encoding='utf-8')
sw = sw.replace("const CACHE='faisal-card-", f"const CACHE='{slug}-card-")
sw = sw.replace("'logo.png'", "'../logo.png'").replace("'icons/", "'../icons/").replace("'assets/", "'../assets/")
sw = sw.replace('Faisal-Alshammari-ar.vcf', file_ar).replace('Faisal-Alshammari-en.vcf', file_en)
(out / 'sw.js').write_text(sw, encoding='utf-8')
print('built', out)
