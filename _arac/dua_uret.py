"""Dua sayfalari (/dua/<slug>/, /dua/index.html, sitemap-dua.xml) uretir ve dogrular.
Kullanim: python -I -X utf8 dua_uret.py <items.json> <elmalili.json> <site_koku>
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

BASE = "https://kilinccan.github.io/hal"
STORE = "https://apps.apple.com/tr/app/id6837715909"
TARIH = "2026-11-26"
CSS = (Path(__file__).parent / "stil.css").read_text(encoding="utf-8").rstrip()

NEEDS = {
    "calm": ("huzur", "Huzur"), "patience": ("sabir", "Sabır"), "hope": ("umut", "Umut"),
    "strength": ("guc", "Güç"), "gratitude": ("sukur", "Şükür"),
    "forgiveness": ("bagislanma", "Bağışlanma"), "guidance": ("rehberlik", "Rehberlik"),
    "trust": ("tevekkul", "Tevekkül"), "comfort": ("teselli", "Teselli"),
    "closeness": ("yakinlik", "Yakınlık"), "wish": ("dilek-duasi", "Bir dilek duası"),
}

# sure:ayet -> yaygin ad (okunusun dua cumlesinden elle). None: ad yerine "<Sure> <ayet>. ayetteki dua".
AD = {
    "2:286": "Rabbenâ lâ tüâhıznâ duası",
    "20:25": "Rabbişrah lî sadrî duası",
    "21:87": "Lâ ilâhe illâ ente duası",
    "3:8": "Rabbenâ lâ tüziğ kulûbenâ duası",
    "18:10": "Rabbenâ âtinâ min ledünke rahmeten duası",
    "20:114": "Rabbi zidnî ilmâ duası",
    "2:250": "Rabbenâ efrığ aleynâ sabran duası",
    "2:201": "Rabbenâ âtinâ duası",
    "14:40": "Rabbic'alnî mukîmas salâti duası",
    "14:41": "Rabbenağfir lî ve li vâlideyye duası",
    "17:24": "Rabbirhamhümâ duası",
    "7:23": "Rabbenâ zalemnâ enfüsenâ duası",
    "25:74": "Rabbenâ heb lenâ min ezvâcinâ duası",
    "3:147": "Rabbenağfir lenâ zünûbenâ duası",
    "59:10": "Rabbenağfir lenâ ve li ihvâninellezîne duası",
    "28:24": "Rabbi innî limâ enzelte ileyye duası",
    "3:193": "Rabbenâ innenâ semi'nâ münâdiyen duası",
    "3:16": "Rabbenâ innenâ âmennâ duası",
    "7:126": "Rabbenâ efriğ aleynâ sabran duası",
    "12:101": "Rabbi kad âteytenî minel mülk duası",
    "17:80": "Rabbi edhılnî müdhale sıdkın duası",
    "23:97": "Rabbi eûzü bike min hemezâtiş şeyâtîn duası",
    "26:83": "Rabbi heb lî hükmen duası",
    "27:19": "Rabbi evzı'nî en eşkure ni'meteke duası",
    "66:8": None,
    "2:128": "Rabbenâ vec'alnâ müslimeyni leke duası",
    "3:194": "Rabbenâ ve âtinâ mâ ve'adtenâ duası",
    "11:47": "Rabbi innî eûzü bike en es'eleke duası",
    "14:38": "Rabbenâ inneke ta'lemü mâ nuhfî duası",
    "7:151": "Rabbiğfir lî ve li ehî duası",
    "3:53": "Rabbenâ âmennâ bimâ enzelte duası",
}
# Yaygin adi birbirine yakin olup ayri ayetlere ait olanlar: slug'a sure-ayet eklenir
AYIR = {"2:250", "7:126"}

TR = str.maketrans({"â": "a", "Â": "a", "î": "i", "û": "u", "ı": "i", "İ": "i", "ö": "o",
                    "ü": "u", "ş": "s", "ç": "c", "ğ": "g", "Ş": "s", "Ç": "c", "Ö": "o", "Ü": "u"})


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.translate(TR).lower()).strip("-")


def esc(s):
    return html.escape(s, quote=True)


def yukle(items_p, meal_p):
    items = json.loads(Path(items_p).read_text(encoding="utf-8"))
    meals = json.loads(Path(meal_p).read_text(encoding="utf-8"))["texts"]
    duas = []
    for x in items:
        if x["kind"] != "dua" or not x.get("verified"):
            continue
        key = x["translation_key"]
        ref = f"{x['surah']}:{x['ayah']}"
        aralik = f"{x['ayah']}-{x['ayah_end']}" if x.get("ayah_end") else str(x["ayah"])
        etiket = f"{x['surah_name']} {aralik}"
        ad = AD[ref] or f"{x['surah_name']} {aralik}. ayetteki dua"
        sl = slug(ad)
        if ref in AYIR:
            sl += f"-{x['surah']}-{x['ayah']}"
        ayet = f"{x['surah']}-{x['ayah']}" + (f"-{x['ayah_end']}" if x.get("ayah_end") else "")
        duas.append({"ad": ad, "slug": sl, "ref": f"{x['surah']}:{aralik}", "etiket": etiket, "ayet": ayet, "x": x, "meal": meals[key]})
    assert len({d["slug"] for d in duas}) == len(duas), "slug cakismasi"
    return duas


def sayfa(d, up):
    x = d["x"]
    title = f"{d['ad']} Arapça Okunuşu ve Anlamı ({d['etiket']})"
    desc = f"{d['ad']} ({d['etiket']}): Arapçası, okunuşu ve Elmalılı meali."
    canon = f"{BASE}/dua/{d['slug']}/"
    og = f"{BASE}/ayet/{d['ayet']}/og.png"
    wa = f"https://wa.me/?text={quote(d['ad'] + chr(10) + canon, safe='')}"
    konular = "".join(
        f'<li><a href="{up}ayetler/{NEEDS[n][0]}/">{NEEDS[n][1]}</a></li>' for n in x["needs"])
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="max-image-preview:large">
<meta name="apple-itunes-app" content="app-id=6837715909">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="HÂL">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og}">
<style>
{CSS}
</style>
</head>
<body>
<main>
<p class="marka"><a href="{up}">HÂL</a></p>
<h1>{esc(title)}</h1>
<p class="muted">Dua · {esc(d['etiket'])}. ayet ({d['ref']})</p>
<h2>Arapçası</h2>
<p class="arapca" dir="rtl" lang="ar">{esc(x['arabic'])}</p>
<h2>Okunuşu</h2>
<p>{esc(x['transliteration'])}</p>
<h2>Meali (Elmalılı Hamdi Yazır)</h2>
<p>{esc(d['meal'])}</p>
<h2>Konular</h2>
<ul class="konular">{konular}</ul>
<p><a href="{up}ayet/{d['ayet']}/">Ayetin sayfası: {esc(d['etiket'])}</a> · <a href="../">Tüm dualar</a></p>
<p><a class="gonder" href="{wa}" rel="noopener">WhatsApp'ta gönder</a></p>
<p><a class="indir" href="{STORE}">HÂL'i App Store'dan indir</a></p>
<p class="muted">Hâline uygun ayet ve dualar, HÂL uygulamasında Arapçası, okunuşu, meali ve kaynağıyla bir arada.</p>
<p class="kaynak">{esc(x['source_note'])}<br>Arapça metin lisansı: Tanzil, CC BY 3.0 (tanzil.net). HÂL bir tefsir ya da fetva kaynağı değildir; dini hüküm vermez. Amacı, günün içinde kısa bir an durup okumana eşlik etmektir.
<footer><a href="{up}gizlilik/">Gizlilik</a> · <a href="{up}destek/">Destek</a> · <a href="{up}">HÂL</a></footer>
</main>
</body>
</html>
"""


def index(duas):
    title = "Kur'an'daki dualar: Arapçası, okunuşu ve anlamı"
    desc = "Kur'an'daki dualar: Arapçası, okunuşu ve Elmalılı meali ile her dua için ayrı sayfa."
    canon = f"{BASE}/dua/"
    lis = "".join(
        f'<li><a href="{d["slug"]}/">{esc(d["ad"])}</a> <span class="muted">({esc(d["etiket"])})</span></li>\n'
        for d in sorted(duas, key=lambda d: (d["x"]["surah"], d["x"]["ayah"])))
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="max-image-preview:large">
<meta name="apple-itunes-app" content="app-id=6837715909">
<title>{esc(title)} | HÂL</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="HÂL">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary">
<style>
{CSS}
</style>
</head>
<body>
<main>
<p class="marka"><a href="../">HÂL</a></p>
<h1>{esc(title)}</h1>
<p class="muted">Sure sırasına göre {len(duas)} dua. Her sayfada Arapçası, okunuşu, Elmalılı meali ve kaynağı var.</p>
<ul class="liste">
{lis}</ul>
<p><a class="indir" href="{STORE}">HÂL'i App Store'dan indir</a></p>
<footer><a href="../gizlilik/">Gizlilik</a> · <a href="../destek/">Destek</a> · <a href="../">HÂL</a></footer>
</main>
</body>
</html>
"""


def kontrol(root, duas):
    hatalar = []
    for d in duas:
        p = root / "dua" / d["slug"] / "index.html"
        t = p.read_text(encoding="utf-8")
        ar = html.unescape(re.search(r'lang="ar">(.*?)</p>', t, re.S).group(1))
        ml = html.unescape(re.search(r"Meali \(Elmalılı Hamdi Yazır\)</h2>\n<p>(.*?)</p>", t, re.S).group(1))
        ok = html.unescape(re.search(r"Okunuşu</h2>\n<p>(.*?)</p>", t, re.S).group(1))
        if ar != d["x"]["arabic"] or ml != d["meal"] or ok != d["x"]["transliteration"]:
            hatalar.append(f"icerik uyusmuyor: {d['slug']}")
        if re.search(r"etkili|kesin kabul|şifa", t, re.I):
            hatalar.append(f"vaat kelimesi: {d['slug']}")
        if not (root / "ayet" / d["ayet"] / "og.png").exists():
            hatalar.append(f"og.png yok: {d['ayet']}")
    tum = [root / "dua" / "index.html"] + [root / "dua" / d["slug"] / "index.html" for d in duas]
    n = 0
    for p in tum:
        for h in re.findall(r'href="([^"#]+)"', p.read_text(encoding="utf-8")):
            if re.match(r"(https?:|mailto:)", h):
                continue
            n += 1
            hedef = (p.parent / h)
            if not (hedef / "index.html" if h.endswith("/") else hedef).exists():
                hatalar.append(f"kirik link {p.relative_to(root)} -> {h}")
    return hatalar, n


def main():
    items_p, meal_p, root = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    duas = yukle(items_p, meal_p)
    for d in duas:
        out = root / "dua" / d["slug"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(sayfa(d, "../../"), encoding="utf-8", newline="\n")
    (root / "dua" / "index.html").write_text(index(duas), encoding="utf-8", newline="\n")
    urls = [f"{BASE}/dua/"] + [f"{BASE}/dua/{d['slug']}/" for d in duas]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{u}</loc><lastmod>{TARIH}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    (root / "sitemap-dua.xml").write_text(sm, encoding="utf-8", newline="\n")
    hatalar, n = kontrol(root, duas)
    print(f"{len(duas)} dua sayfasi + index, {n} ic link kontrol edildi")
    for h in hatalar:
        print("HATA:", h)
    for d in duas:
        print(d["slug"], "|", d["ad"], "|", d["etiket"])
    sys.exit(1 if hatalar else 0)


main()
