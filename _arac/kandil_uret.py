"""Regaip Kandili mesajları: sayfa, 8 kare, OG görseli ve site haritası üretir.

Kullanım: python -X utf8 -I _arac/kandil_uret.py
Yalnız verified öğeler ve Elmalılı meali kullanılır. Görseller için Chrome gerekir (CHROME ortam değişkeni
ya da bilinen yollar). Bağımlılık yok.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

KOK = Path(__file__).resolve().parent.parent
DOC = Path("C:/Users/lastp/Documents")
ITEMS = DOC / "ckapp-wt/app/assets/content/items.json"
MEAL = DOC / "ckapp-wt/app/assets/content/meal/elmalili.json"
FRAUNCES = DOC / "hal-sosyal-v2/uret/sinema/fonts/Fraunces.ttf"
AMIRI = DOC / "ckapp-wt/app/assets/fonts/AmiriQuran-Regular.ttf"

BASE = "https://kilinccan.github.io/hal/"
STORE = "https://apps.apple.com/tr/app/id6837715909"
SAYFA_URL = BASE + "kandil-mesajlari/"
CSS = (KOK / "_arac" / "stil.css").read_text(encoding="utf8")

AYETLER = ["2:152", "3:8", "4:110", "7:23", "7:151", "14:41", "42:25", "42:28"]

DISCLAIMER = (
    "HÂL bir tefsir ya da fetva kaynağı değildir; dini hüküm vermez. "
    "Amacı, günün içinde kısa bir an durup okumana eşlik etmektir."
)

BASE_CSS = """*{margin:0;box-sizing:border-box}
body{background:radial-gradient(ellipse at 50% 40%,#FBF9F4 0%,#F8F6F0 55%,#F2EFE6 100%);color:#1F1B16;
font-family:'HalFraunces',Georgia,serif;font-weight:400;position:relative;overflow:hidden}
.ar{font-family:'HalAmiri';direction:rtl;text-align:center;line-height:2}
.altin{color:#7A6226;letter-spacing:.06em}
"""


def find_chrome():
    for c in (os.environ.get("CHROME", ""), shutil.which("chrome"), shutil.which("google-chrome"),
              "C:/Program Files/Google/Chrome/Application/chrome.exe",
              "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"):
        if c and Path(c).is_file():
            return c
    sys.exit("Chrome bulunamadı: CHROME ortam değişkenine chrome yolunu ver")


def doc(css, body):
    fonts = (
        f"@font-face{{font-family:'HalFraunces';font-weight:100 900;src:url('{FRAUNCES.as_uri()}')}}"
        f"@font-face{{font-family:'HalAmiri';src:url('{AMIRI.as_uri()}')}}"
    )
    return f"<!doctype html><html lang='tr'><meta charset='utf-8'><style>{fonts}{BASE_CSS}{css}</style><body>{body}</body></html>"


def kare_html(item, label, meal):
    n = len(item["arabic"])
    px = 66 if n <= 60 else 56 if n <= 110 else 48
    css = """body{width:1080px;height:1080px}
.top{position:absolute;top:70px;left:0;right:0;text-align:center;font-size:38px;line-height:1.2}
.c{position:absolute;left:100px;right:100px;top:150px;bottom:170px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.ml{font-size:36px;line-height:1.5;margin-top:40px}.src{margin-top:34px;font-size:30px}
.hal{position:absolute;bottom:96px;left:0;right:0;text-align:center;font-size:44px;letter-spacing:.14em}
.ara{position:absolute;bottom:48px;left:0;right:0;text-align:center;font-size:28px;letter-spacing:.06em;color:#7A6226}"""
    body = (
        "<div class='top altin' lang='tr'>Regaip Kandiliniz mübarek olsun</div>"
        f"<div class='c'><div class='ar' lang='ar' style='font-size:{px}px'>{escape(item['arabic'])}</div>"
        f"<div class='ml'>{escape(meal)}</div><div class='src altin'>{escape(label)}</div></div>"
        "<div class='hal' lang='tr'>HÂL</div><div class='ara' lang='tr'>App Store'da HÂL ara</div>"
    )
    return doc(css, body)


def og_html():
    css = """body{width:1200px;height:630px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.h{font-size:78px;line-height:1.15}.k{width:80px;height:2px;background:#7A6226;margin:40px 0}
.hal{font-size:52px;letter-spacing:.14em}"""
    body = "<div class='h'>Ayetli Regaip Kandili mesajları</div><div class='k'></div><div class='hal' lang='tr'>HÂL</div>"
    return doc(css, body)


def render_all(jobs, chrome):
    with tempfile.TemporaryDirectory() as tmp:
        def run(k):
            html, png, w, h = jobs[k]
            f = Path(tmp) / f"{k}.html"
            f.write_text(html, encoding="utf-8")
            png.parent.mkdir(parents=True, exist_ok=True)
            r = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                 f"--user-data-dir={Path(tmp) / f'p{k}'}", f"--screenshot={png}", f"--window-size={w},{h}",
                 "--virtual-time-budget=3000", f.as_uri()],
                capture_output=True, timeout=120,
            )
            if r.returncode != 0 or not png.is_file():
                sys.exit(f"render başarısız: {png}\n{r.stderr.decode(errors='replace')[-300:]}")

        with ThreadPoolExecutor(4) as ex:
            list(ex.map(run, range(len(jobs))))


def kisalt(text, n):
    return text if len(text) <= n else text[: n - 3].rsplit(" ", 1)[0] + "..."


def wa(text, url):
    href = "https://wa.me/?text=" + quote(f"{text}\n{url}", safe="")
    return f'<a class="gonder" href="{escape(href, quote=True)}" rel="noopener">WhatsApp\'ta gönder</a>'


def sayfa(body, title, desc):
    t, d = escape(title), escape(desc, quote=True)
    img = BASE + "kandil-mesajlari/og.png"
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="max-image-preview:large">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{SAYFA_URL}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="HÂL">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{SAYFA_URL}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img}">
<style>{CSS}</style>
</head>
<body>
<main>
<p class="marka"><a href="../">HÂL</a></p>
{body}
<footer><a href="../gizlilik/">Gizlilik</a> · <a href="../destek/">Destek</a> · <a href="../">HÂL</a></footer>
</main>
</body>
</html>
"""


def main():
    items = {i["translation_key"]: i for i in json.loads(ITEMS.read_text(encoding="utf-8")) if i["verified"]}
    meals = json.loads(MEAL.read_text(encoding="utf-8"))["texts"]
    eksik = [k for k in AYETLER if k not in items or not meals.get(k)]
    assert not eksik, f"doğrulanmış/mealli öğe değil: {eksik}"
    out = KOK / "kandil-mesajlari"
    jobs, kareler = [], []
    for n, k in enumerate(AYETLER, 1):
        i = items[k]
        label = f"{i['surah_name']} Suresi {i['ayah']}"
        meal = meals[k]
        jobs.append((kare_html(i, label, meal), out / f"k{n}.png", 1080, 1080))
        alt = f"Regaip Kandiliniz mübarek olsun. {label}: {meal}"
        kareler.append(
            f'<figure class="kare" id="k{n}"><img src="k{n}.png" width="1080" height="1080" '
            f'alt="{escape(alt, quote=True)}" loading="lazy">'
            f'<div class="islem"><a class="gonder" href="k{n}.png" download="hal-regaip-{n}.png">İndir</a> '
            f'{wa(f"Regaip Kandiliniz mübarek olsun. {label}: {kisalt(meal, 100)}", SAYFA_URL + f"#k{n}")}</div></figure>'
        )
    jobs.append((og_html(), out / "og.png", 1200, 630))
    title = "Ayetli Regaip Kandili Mesajları 2026 | HÂL"
    desc = "Regaip Kandili için ayet ve dua içeren görsel mesajlar. İndir ya da WhatsApp'ta gönder. Reklamsız, ücretsiz."
    body = f"""<h1>Ayetli Regaip Kandili mesajları</h1>
<p>Regaip Kandili: 10 Aralık 2026 Perşembe akşamı (Diyanet takvimi). Rahmet, bağışlanma, dua ve yakınlık üzerine ayetleri Arapçası ve Elmalılı mealiyle sevdiklerine gönder. Görseli indir ya da doğrudan WhatsApp'ta paylaş.</p>
{"".join(kareler)}
<p><a class="indir" href="{STORE}">HÂL'i App Store'dan indir</a></p>
<p class="muted">Hâline uygun ayet ve dualar, HÂL uygulamasında Arapçası, okunuşu, meali ve kaynağıyla bir arada.</p>
<p class="kaynak">Arapça: Tanzil Uthmani (tanzil.net, CC BY 3.0, değiştirilmeden). Meal: Elmalılı Hamdi Yazır, Hak Dini Kur'an Dili, Eser Neşriyat 1979. Kandil tarihi: Diyanet takvimi. {DISCLAIMER}</p>"""
    (out).mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(sayfa(body, title, desc), encoding="utf-8", newline="\n")
    render_all(jobs, find_chrome())
    sm = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"<url><loc>{SAYFA_URL}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n</urlset>\n"
    )
    (KOK / "sitemap-kandil.xml").write_text(sm, encoding="utf-8", newline="\n")


main()
