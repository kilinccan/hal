"""Günün ayeti: sayfa, gömülebilir kutu, RSS ve site haritası üretir. Bağımlılık yok."""
import json
import sys
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from urllib.parse import quote

KOK = Path(__file__).resolve().parent.parent
BASE = "https://kilinccan.github.io/hal/"
STORE = "https://apps.apple.com/tr/app/id6837715909"
TR = timezone(timedelta(hours=3))
ADIM = 37  # 124 ile aralarında asal: her ayet bir kez, komşu günler birbirine yakın değil
GUN_SAYISI = 14

AYETLER = json.loads((KOK / "_arac" / "gunluk.json").read_text(encoding="utf8"))
CSS = (KOK / "_arac" / "stil.css").read_text(encoding="utf8")


def ayet_gun(gun):
    return AYETLER[(gun.toordinal() * ADIM) % len(AYETLER)]


def etiket(a):
    son = f"-{a['ayet_end']}" if a["ayet_end"] else ""
    return f"{a['sure_adi']} Suresi {a['ayet']}{son}. ayet"


def kaynak(a):
    return f"{etiket(a)} ({a['sure']}:{a['ayet']}{'-' + str(a['ayet_end']) if a['ayet_end'] else ''})"


def yaz(yol, icerik):
    p = KOK / yol
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(icerik, encoding="utf8", newline="\n")


def sayfa(a, gun):
    url = BASE + "gunun-ayeti/"
    ayet_url = BASE + a["yol"]
    tarih = gun.strftime("%d.%m.%Y")
    baslik = f"Günün Ayeti: {etiket(a)} ({tarih})"
    ozet = f"{kaynak(a)}: {a['meal']}"
    wa = quote(f"Günün ayeti, {etiket(a)}: {a['meal']}\n{ayet_url}", safe="")
    iframe = (
        f'<iframe src="{BASE}gunun-ayeti/kutu/" width="100%" height="320" '
        'style="border:0;max-width:480px" title="HÂL günün ayeti" loading="lazy"></iframe>'
    )
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="max-image-preview:large">
<title>{escape(baslik)}</title>
<meta name="description" content="{escape(ozet)}">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/rss+xml" title="HÂL günün ayeti" href="{BASE}feed.xml">
<meta property="og:type" content="article">
<meta property="og:site_name" content="HÂL">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{escape(baslik)}">
<meta property="og:description" content="{escape(ozet)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ayet_url}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{ayet_url}og.png">
<style>
{CSS}  .kod {{ width: 100%; box-sizing: border-box; font: 13px/1.4 ui-monospace, Menlo, Consolas, monospace;
         padding: 10px; border: 1px solid var(--line); border-radius: 8px; background: transparent; color: var(--fg); }}
</style>
</head>
<body>
<main>
<p class="marka"><a href="../">HÂL</a></p>
<h1>Günün Ayeti</h1>
<p class="muted">{tarih} · {escape(etiket(a))}</p>
<h2>Arapçası</h2>
<p class="arapca" dir="rtl" lang="ar">{escape(a['arapca'])}</p>
<h2>Okunuşu</h2>
<p>{escape(a['okunus'])}</p>
<h2>Meali (Elmalılı Hamdi Yazır)</h2>
<p>{escape(a['meal'])}</p>
<p><a href="../{a['yol']}">Bu ayetin sayfası</a> · <a href="{BASE}feed.xml">RSS</a></p>
<p><a class="gonder" href="https://wa.me/?text={wa}" rel="noopener">WhatsApp'ta gönder</a></p>
<p><a class="indir" href="{STORE}">HÂL'i App Store'dan indir</a></p>
<p class="muted">Hâline uygun ayet ve dualar, HÂL uygulamasında Arapçası, okunuşu, meali ve kaynağıyla bir arada.</p>
<h2>Sitene ekle</h2>
<p class="muted">Aşağıdaki kodu sayfana yapıştır; kutu her sabah kendiliğinden yenilenir. İzleme ve çerez yoktur.</p>
<input class="kod" readonly value="{escape(iframe)}" aria-label="Gömme kodu" onclick="this.select()">
<p class="kaynak">Arapça: Tanzil Uthmani (tanzil.net, CC BY 3.0, değiştirilmeden). Meal: Elmalılı, Hak Dini Kur&#x27;an Dili, Eser 1979. Okunuş: HÂL, Arapça metinden kelime kelime.<br>HÂL bir tefsir ya da fetva kaynağı değildir; dini hüküm vermez. Amacı, günün içinde kısa bir an durup okumana eşlik etmektir.</p>
<footer><a href="../gizlilik/">Gizlilik</a> · <a href="../destek/">Destek</a> · <a href="../">HÂL</a></footer>
</main>
</body>
</html>
"""


def kutu(a):
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>HÂL günün ayeti</title>
<style>
  :root {{ --bg: #F8F6F0; --fg: #1F2A25; --muted: #5B6660; --accent: #23483B; --line: #E0DCCF; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #151C19; --fg: #ECE9E1; --muted: #A3ACA7; --accent: #A9C7B8; --line: #2B3530; }}
  }}
  body {{ margin: 0; background: var(--bg); color: var(--fg);
         font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  .kutu {{ padding: 16px; border: 1px solid var(--line); border-radius: 12px; margin: 4px; }}
  .baslik {{ color: var(--accent); font-weight: 600; letter-spacing: .15em; font-size: .8rem; margin: 0 0 .6em; }}
  .arapca {{ font-size: 1.35rem; line-height: 2.1; margin: 0 0 .5em; }}
  p {{ margin: 0 0 .6em; }}
  .kaynak {{ color: var(--muted); font-size: .8rem; margin: 0; }}
  a {{ color: var(--accent); font-weight: 600; }}
  a:focus-visible {{ outline: 3px solid var(--fg); outline-offset: 3px; }}
</style>
</head>
<body>
<div class="kutu">
<p class="baslik">GÜNÜN AYETİ</p>
<p class="arapca" dir="rtl" lang="ar">{escape(a['arapca'])}</p>
<p>{escape(a['meal'])}</p>
<p class="kaynak">{escape(etiket(a))} · Elmalılı · <a href="{BASE}gunun-ayeti/" target="_blank" rel="noopener">HÂL ile</a></p>
</div>
</body>
</html>
"""


def feed(bugun):
    ogeler = []
    for i in range(GUN_SAYISI):
        g = bugun - timedelta(days=i)
        a = ayet_gun(g)
        yayin = format_datetime(datetime(g.year, g.month, g.day, 6, 0, tzinfo=TR))
        ogeler.append(
            f"""<item>
<title>{escape(etiket(a))}</title>
<link>{BASE}{a['yol']}</link>
<guid isPermaLink="false">hal-gunun-ayeti-{g.isoformat()}</guid>
<pubDate>{yayin}</pubDate>
<description>{escape(a['meal'])}</description>
</item>"""
        )
    son = format_datetime(datetime(bugun.year, bugun.month, bugun.day, 6, 0, tzinfo=TR))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>HÂL Günün Ayeti</title>
<link>{BASE}gunun-ayeti/</link>
<description>Her sabah bir ayet: Elmalılı meali ile.</description>
<language>tr</language>
<lastBuildDate>{son}</lastBuildDate>
{chr(10).join(ogeler)}
</channel>
</rss>
"""


def sitemap(bugun):
    s = bugun.isoformat()
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>{BASE}gunun-ayeti/</loc><lastmod>{s}</lastmod></url>
</urlset>
"""


def main():
    bugun = datetime.now(TR).date()
    if len(sys.argv) > 1:
        bugun = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    a = ayet_gun(bugun)
    yaz("gunun-ayeti/index.html", sayfa(a, bugun))
    yaz("gunun-ayeti/kutu/index.html", kutu(a))
    yaz("feed.xml", feed(bugun))
    yaz("sitemap-gunluk.xml", sitemap(bugun))
    print(bugun, a["id"])


main()
