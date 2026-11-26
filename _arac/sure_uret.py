"""114 sure sayfasi uretir. Kullanim:
python -I sure_uret.py <tanzil_klasoru> <items.json> <elmalili.json> <site_koku>
tanzil_klasoru: q.txt (Tanzil uthmani txt-2, marks=true) ve meta.xml icerir.
"""
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "https://kilinccan.github.io/hal"
STORE = "https://apps.apple.com/tr/app/id6837715909"
TARIH = "2026-11-26"

# Diyanet yazimi. Tek tirnak/’/‘ ayrimi items.json'daki yazimla ayni.
# 0: items.json'da olan, 1: elle yazilan (kontrol edilmeli)
NAMES = {
    1: "Fâtiha", 2: "Bakara", 3: "Âl-i İmrân", 4: "Nisâ", 5: "Mâide", 6: "En‘âm",
    7: "A'râf", 8: "Enfâl", 9: "Tevbe", 10: "Yûnus", 11: "Hûd", 12: "Yûsuf",
    13: "Ra'd", 14: "İbrahim", 15: "Hicr", 16: "Nahl", 17: "İsrâ", 18: "Kehf",
    19: "Meryem", 20: "Tâhâ", 21: "Enbiyâ", 22: "Hac", 23: "Mü’minûn", 24: "Nûr",
    25: "Furkân", 26: "Şuarâ", 27: "Neml", 28: "Kasas", 29: "Ankebût", 30: "Rûm",
    31: "Lokmân", 32: "Secde", 33: "Ahzâb", 34: "Sebe'", 35: "Fâtır", 36: "Yâsîn",
    37: "Sâffât", 38: "Sâd", 39: "Zümer", 40: "Mü’min", 41: "Fussilet", 42: "Şûrâ",
    43: "Zuhruf", 44: "Duhân", 45: "Câsiye", 46: "Ahkâf", 47: "Muhammed", 48: "Fetih",
    49: "Hucurât", 50: "Kâf", 51: "Zâriyât", 52: "Tûr", 53: "Necm", 54: "Kamer",
    55: "Rahmân", 56: "Vâkıa", 57: "Hadîd", 58: "Mücâdele", 59: "Haşr", 60: "Mümtehine",
    61: "Saff", 62: "Cuma", 63: "Münâfikûn", 64: "Teğâbün", 65: "Talâk", 66: "Tahrîm",
    67: "Mülk", 68: "Kalem", 69: "Hâkka", 70: "Meâric", 71: "Nûh", 72: "Cin",
    73: "Müzzemmil", 74: "Müddessir", 75: "Kıyâme", 76: "İnsan", 77: "Mürselât", 78: "Nebe'",
    79: "Nâziât", 80: "Abese", 81: "Tekvîr", 82: "İnfitâr", 83: "Mutaffifîn", 84: "İnşikak",
    85: "Bürûc", 86: "Târık", 87: "A'lâ", 88: "Gâşiye", 89: "Fecr", 90: "Beled",
    91: "Şems", 92: "Leyl", 93: "Duhâ", 94: "İnşirah", 95: "Tîn", 96: "Alak",
    97: "Kadir", 98: "Beyyine", 99: "Zilzâl", 100: "Âdiyât", 101: "Kâria", 102: "Tekâsür",
    103: "Asr", 104: "Hümeze", 105: "Fîl", 106: "Kureyş", 107: "Mâûn", 108: "Kevser",
    109: "Kâfirûn", 110: "Nasr", 111: "Tebbet", 112: "İhlâs", 113: "Felak", 114: "Nâs",
}
TR = str.maketrans({"â": "a", "Â": "a", "î": "i", "û": "u", "ı": "i", "İ": "i", "ö": "o",
                    "ü": "u", "ş": "s", "ç": "c", "ğ": "g", "Ş": "s", "Ç": "c", "Ö": "o", "Ü": "u",
                    "Ğ": "g", "’": "", "‘": "", "'": ""})

CSS = """  :root { --bg: #F8F6F0; --fg: #1F2A25; --muted: #5B6660; --accent: #23483B; --on-accent: #F8F6F0; --line: #E0DCCF; }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #151C19; --fg: #ECE9E1; --muted: #A3ACA7; --accent: #A9C7B8; --on-accent: #151C19; --line: #2B3530; }
  }
  body { margin: 0; background: var(--bg); color: var(--fg);
         font: 17px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  main { max-width: 680px; margin: 0 auto; padding: 28px 16px 48px; }
  .marka { color: var(--accent); font-weight: 600; letter-spacing: .2em; margin: 0 0 1.2em; }
  .marka a { color: inherit; text-decoration: none; }
  h1 { color: var(--accent); font-size: 1.6rem; line-height: 1.25; margin: 0 0 .6em; }
  h2 { color: var(--accent); font-size: 1.1rem; margin: 1.8em 0 .4em; }
  p { margin: 0 0 1em; }
  .muted { color: var(--muted); }
  a { color: var(--accent); }
  .arapca { font-family: "Geeza Pro", "Noto Naskh Arabic", "Traditional Arabic", "Segoe UI", serif;
            font-size: 2rem; line-height: 2.5; margin: 0 0 .3em; }
  .no { display: inline-block; min-width: 1.6em; padding: 0 .3em; margin: 0 .4em; border: 1px solid var(--line);
        border-radius: 999px; font: 600 .8rem/1.6 -apple-system, "Segoe UI", sans-serif; color: var(--muted);
        text-align: center; vertical-align: middle; }
  .ayet { border-bottom: 1px solid var(--line); padding: .8em 0; }
  .meal { font-size: .95rem; color: var(--muted); }
  .bilgi { display: grid; grid-template-columns: auto 1fr; gap: .3em 1.2em; margin: 0 0 1.4em; padding: 14px 16px;
           border: 1px solid var(--line); border-radius: 12px; }
  .bilgi dt { color: var(--muted); }
  .bilgi dd { margin: 0; font-weight: 600; }
  .indir { display: inline-block; background: var(--accent); color: var(--on-accent); text-decoration: none;
           font-weight: 600; padding: 14px 26px; border-radius: 14px; margin: 1.2em 0; }
  .indir:focus-visible, a:focus-visible { outline: 3px solid var(--fg); outline-offset: 3px; }
  ul.liste { list-style: none; padding: 0; margin: 0; }
  ul.liste li { padding: 10px 0; border-bottom: 1px solid var(--line); }
  .gez { display: flex; justify-content: space-between; gap: 12px; margin: 1.4em 0; }
  .kaynak { font-size: .85rem; color: var(--muted); margin-top: 2.2em; border-top: 1px solid var(--line); padding-top: 1em; }
  footer { font-size: .85rem; color: var(--muted); margin-top: 1.2em; }
  footer a { color: var(--muted); }"""


def slug(name):
    s = name.translate(TR).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def yer(tip):
    return "Mekkî" if tip == "Meccan" else "Medenî"


def head(title, desc, canon):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="max-image-preview:large">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="HÂL">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary">
<style>
{CSS}
</style>
</head>
<body>
<main>
"""


def foot(up):
    return f"""<footer><a href="{up}gizlilik/">Gizlilik</a> · <a href="{up}destek/">Destek</a> · <a href="{up}">HÂL</a></footer>
</main>
</body>
</html>
"""


def load(tanzil, items_path, meal_path):
    quran = {}
    for line in (tanzil / "q.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        s, a, text = line.split("|", 2)
        quran.setdefault(int(s), {})[int(a)] = text
    suras = {}
    for e in ET.parse(tanzil / "meta.xml").getroot().iter("sura"):
        suras[int(e.get("index"))] = (int(e.get("ayas")), e.get("type"), int(e.get("order")))
    items = json.loads(items_path.read_text(encoding="utf-8"))
    verified = {i["translation_key"]: i for i in items if i.get("verified")}
    texts = json.loads(meal_path.read_text(encoding="utf-8"))["texts"]
    meals = {}
    for key, it in verified.items():
        s, a = key.split(":")
        end = it["ayah_end"] or int(a)
        slug_a = f"{s}-{a}" + (f"-{end}" if end != int(a) else "")
        meals[(int(s), int(a))] = (texts[key], end, slug_a)
    return quran, suras, meals


def sure_sayfasi(n, quran, suras, meals):
    count, tip, order = suras[n]
    assert count == len(quran[n]), n
    name = NAMES[n]
    title = f"{name} Suresi Arapça Oku: {count} Ayet, {yer(tip)}"
    desc = (f"{name} Suresi kaç ayet? {count} ayet, {yer(tip)}, iniş sırası {order}. "
            f"Ayet numaralı Arapça metni oku (Tanzil Uthmani).")
    out = [head(title, desc, f"{BASE}/sure/{slug(name)}/")]
    out.append('<p class="marka"><a href="../../">HÂL</a></p>\n')
    out.append(f"<h1>{html.escape(title)}</h1>\n")
    out.append('<p class="muted"><a href="../">Tüm sureler</a></p>\n')
    out.append(f"""<dl class="bilgi">
<dt>Ayet sayısı</dt><dd>{count}</dd>
<dt>İniş yeri</dt><dd>{yer(tip)}</dd>
<dt>İniş sırası</dt><dd>{order}</dd>
<dt>Mushaftaki sıra</dt><dd>{n}</dd>
</dl>
""")
    has_meal = False
    for a in range(1, count + 1):
        out.append(f'<section class="ayet" id="a{a}">\n')
        out.append(f'<p class="arapca" dir="rtl" lang="ar">{html.escape(quran[n][a], quote=False)}'
                   f'<span class="no" dir="ltr">{a}</span></p>\n')
        if (n, a) in meals:
            has_meal = True
            text, end, sl = meals[(n, a)]
            lbl = f"{a}-{end}. ayetler" if end != a else f"{a}. ayet"
            out.append(f'<p class="meal">{lbl}, Elmalılı: {html.escape(text, quote=False)} '
                       f'<a href="../../ayet/{sl}/">Bu ayetin sayfası</a></p>\n')
        out.append("</section>\n")
    out.append(f'<p><a class="indir" href="{STORE}">HÂL\'i App Store\'dan indir</a></p>\n')
    out.append('<p class="muted">Hâline uygun ayet ve dualar, HÂL uygulamasında Arapçası, okunuşu, meali ve kaynağıyla bir arada.</p>\n')
    nav = []
    if n > 1:
        nav.append(f'<a href="../{slug(NAMES[n - 1])}/">&larr; {html.escape(NAMES[n - 1])}</a>')
    else:
        nav.append("<span></span>")
    if n < 114:
        nav.append(f'<a href="../{slug(NAMES[n + 1])}/">{html.escape(NAMES[n + 1])} &rarr;</a>')
    else:
        nav.append("<span></span>")
    out.append(f'<p class="gez">{nav[0]}{nav[1]}</p>\n')
    meal_note = (" Meal: Elmalılı Hamdi Yazır, Hak Dini Kur&#x27;an Dili (Eser, 1979); yalnız ilgili ayetlerde."
                 if has_meal else "")
    out.append(f'<p class="kaynak">Arapça metin: <a href="https://tanzil.net/#{n}:1">Tanzil Project</a> '
               f'(tanzil.net), Uthmani, <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>; '
               f'metin değiştirilmeden alınmıştır, güncellemeler için tanzil.net\'e bakılabilir. '
               f'Sure bilgileri: Tanzil metadata.{meal_note} '
               f'HÂL bir tefsir ya da fetva kaynağı değildir; dini hüküm vermez.</p>\n')
    out.append(foot("../../"))
    return "".join(out)


def index_sayfasi(suras):
    title = "114 Sure: Arapça Oku, Ayet Sayısı ve İniş Yeri"
    desc = "Kur'an'ın 114 suresi: her surenin Arapça metni, ayet sayısı, Mekkî veya Medenî oluşu ve iniş sırası."
    out = [head(title, desc, f"{BASE}/sure/")]
    out.append('<p class="marka"><a href="../">HÂL</a></p>\n')
    out.append(f"<h1>{title}</h1>\n<ul class=\"liste\">\n")
    for n in range(1, 115):
        c, t, _ = suras[n]
        nm = NAMES[n]
        out.append(f'<li><a href="{slug(nm)}/">{n}. {html.escape(nm)} Suresi</a> '
                   f'<span class="muted">· {c} ayet, {yer(t)}</span></li>\n')
    out.append("</ul>\n")
    out.append('<p class="kaynak">Arapça metin: <a href="https://tanzil.net/">Tanzil Project</a> (tanzil.net), '
               'CC BY 3.0, değiştirilmeden. Sure bilgileri: Tanzil metadata.</p>\n')
    out.append(foot("../"))
    return "".join(out)


def check(root, quran, count_pages):
    """Her sure sayfasindaki Arapca metni Tanzil kaynagiyla karakter karakter karsilastirir."""
    bad = 0
    for n in range(1, 115):
        page = (root / "sure" / slug(NAMES[n]) / "index.html").read_text(encoding="utf-8")
        got = [html.unescape(m) for m in re.findall(
            r'<p class="arapca" dir="rtl" lang="ar">(.*?)<span class="no"', page)]
        want = [quran[n][a] for a in sorted(quran[n])]
        if got != want:
            bad += 1
            print("FARK:", n)
    print(f"kontrol: {114 - bad}/114 sure kaynakla birebir; sayfa {count_pages}")
    return bad


def main():
    tanzil, items, meal, root = (Path(a) for a in sys.argv[1:5])
    quran, suras, meals = load(tanzil, items, meal)
    slugs = [slug(NAMES[n]) for n in range(1, 115)]
    assert len(set(slugs)) == 114, "slug cakismasi"
    (root / "sure").mkdir(exist_ok=True)
    pages = 0
    for n in range(1, 115):
        d = root / "sure" / slug(NAMES[n])
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(sure_sayfasi(n, quran, suras, meals), encoding="utf-8", newline="\n")
        pages += 1
    (root / "sure" / "index.html").write_text(index_sayfasi(suras), encoding="utf-8", newline="\n")
    pages += 1
    urls = [f"{BASE}/sure/"] + [f"{BASE}/sure/{s}/" for s in slugs]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{u}</loc><lastmod>{TARIH}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    (root / "sitemap-sure.xml").write_text("\n".join(sm) + "\n", encoding="utf-8", newline="\n")
    used = sum(1 for k in meals)
    print(f"{used} meal kaydi")
    sys.exit(1 if check(root, quran, pages) else 0)


main()
