"""Birine ayet hediye et: /hediye/ sayfası, OG görseli (--og) ve site haritası üretir. Bağımlılık yok.

Veri: uygulama içeriği (items.json needs) + gunluk.json (Arapça, meal Elmalılı ile birebir).
Kullanım: python -X utf8 -I _arac/hediye_uret.py <items.json> [--og]
"""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
BASE = "https://kilinccan.github.io/hal/"
STORE = "https://apps.apple.com/tr/app/id6837715909"
FONT = Path("C:/Users/lastp/Documents/hal-sosyal-v2/uret/sinema/fonts/Fraunces.ttf")
CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"
TR = timezone(timedelta(hours=3))

# Hâl -> uygulamadaki needs etiketleri
HALLER = {
    "yorgun": ["patience", "strength", "comfort", "calm"],
    "kaygılı": ["calm", "trust", "comfort"],
    "kırgın": ["forgiveness", "patience", "comfort"],
    "şükür dolu": ["gratitude"],
    "yalnız": ["closeness", "comfort", "guidance"],
    "umutsuz": ["hope", "wish", "strength"],
    "yeni bir başlangıçta": ["guidance", "hope", "trust"],
}

CSS = (KOK / "_arac" / "stil.css").read_text(encoding="utf8")
EK_CSS = """
  label, legend { display: block; font-weight: 600; margin: 1.2em 0 .4em; padding: 0; }
  input[type=text], .kod { width: 100%; box-sizing: border-box; font: inherit; padding: 12px; color: var(--fg);
          background: transparent; border: 1px solid var(--muted); border-radius: 10px; }
  .kod { font: 14px/1.4 ui-monospace, Menlo, Consolas, monospace; }
  fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
  .secenekler { display: flex; flex-wrap: wrap; gap: 8px; }
  .secenekler input { position: absolute; opacity: 0; }
  .secenekler label { margin: 0; font-weight: 400; padding: 10px 16px; border: 1px solid var(--muted);
          border-radius: 999px; cursor: pointer; }
  .secenekler input:checked + label { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
  .secenekler input:focus-visible + label, input[type=text]:focus-visible, .kod:focus-visible,
  button:focus-visible { outline: 3px solid var(--fg); outline-offset: 3px; }
  button, .dugme { font: inherit; font-weight: 600; padding: 14px 26px; border-radius: 14px; cursor: pointer;
          border: 1px solid var(--accent); background: var(--accent); color: var(--on-accent); text-decoration: none;
          display: inline-block; }
  .ikincil { background: transparent; color: var(--accent); }
  .hata { color: #B3261E; font-weight: 600; min-height: 1.6em; margin: .8em 0 0; }
  @media (prefers-color-scheme: dark) { .hata { color: #F2B8B5; } }
  .islemler { display: flex; flex-wrap: wrap; gap: 12px; margin: 1em 0; }
  .hediye-baslik { font-size: 1.5rem; }
  .meal-kutu { border-left: 3px solid var(--accent); padding-left: 14px; }
  [hidden] { display: none !important; }
"""

JS = r"""
(function () {
  var D = JSON.parse(document.getElementById("veri").textContent);
  var BASE = "__BASE__";
  var AD = /^[\p{L}]+(?: [\p{L}]+)*$/u;
  var $ = function (id) { return document.getElementById(id); };
  var byId = {};
  D.ayetler.forEach(function (a) { byId[a.i] = a; });

  function temiz(s) {
    s = (s || "").replace(/\s+/g, " ").trim();
    return s.length > 0 && s.length <= 24 && AD.test(s) ? s : "";
  }
  function karma(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return h;
  }
  function bugun() {
    var p = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Istanbul" }).format(new Date());
    return p;
  }
  function sec(ad, hal) {
    var gerekli = D.haller[hal];
    var adaylar = D.ayetler.filter(function (a) { return a.d.some(function (n) { return gerekli.indexOf(n) >= 0; }); });
    return adaylar[karma(ad.toLocaleLowerCase("tr") + "|" + bugun() + "|" + hal) % adaylar.length];
  }
  function metin(el, t) { el.textContent = t; }

  function gonderen() {
    $("alici").hidden = true;
    $("gonderen").hidden = false;
  }

  function alici(a, k, g) {
    $("gonderen").hidden = true;
    $("alici").hidden = false;
    metin($("a-baslik"), k ? k + ", bugün bu ayet senin için seçildi" : "Bugün bu ayet senin için seçildi");
    metin($("a-kimden"), g ? g + " gönderdi" : "");
    $("a-kimden").hidden = !g;
    metin($("a-arapca"), a.r);
    metin($("a-meal"), a.m);
    metin($("a-kaynak"), a.e + " · Elmalılı Hamdi Yazır");
    $("a-sayfa").href = "../" + a.y;
  }

  function goster() {
    var q = new URLSearchParams(location.hash.slice(1));
    var a = byId[q.get("a")];
    if (a) { alici(a, temiz(q.get("k")), temiz(q.get("g"))); } else { gonderen(); }
  }

  function linkYap(a, k, g) {
    var q = "a=" + encodeURIComponent(a.i) + "&k=" + encodeURIComponent(k);
    if (g) { q += "&g=" + encodeURIComponent(g); }
    return BASE + "hediye/#" + q;
  }

  $("form").addEventListener("submit", function (e) {
    e.preventDefault();
    var k = temiz($("ad").value), g = $("gonderen-ad").value.trim() ? temiz($("gonderen-ad").value) : "";
    var hal = (document.querySelector("input[name=hal]:checked") || {}).value;
    var hata = "";
    if (!k) { hata = "Alıcının adını yaz: en çok 24 harf, rakam ve işaret olmadan."; }
    else if ($("gonderen-ad").value.trim() && !g) { hata = "Senin adın da en çok 24 harf olmalı, rakam ve işaret olmadan."; }
    else if (!hal) { hata = "Bir hâl seç."; }
    metin($("hata"), hata);
    if (hata) { return; }
    var a = sec(k, hal);
    var link = linkYap(a, k, g);
    $("link").value = link;
    metin($("o-kaynak"), a.e);
    metin($("o-meal"), a.m);
    $("wa").href = "https://wa.me/?text=" + encodeURIComponent("Sana bir ayet hediye ettim \uD83E\uDD0D " + link);
    $("sonuc").hidden = false;
    $("sonuc").scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  $("kopyala").addEventListener("click", function () {
    var t = $("link").value;
    var tamam = function () { metin($("durum"), "Link kopyalandı."); };
    var yedek = function () { $("link").select(); metin($("durum"), "Linki seçtim; kopyalamak için basılı tut."); };
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(t).then(tamam, yedek); } else { yedek(); }
  });

  $("yeni").addEventListener("click", function () { history.pushState(null, "", location.pathname); goster(); window.scrollTo(0, 0); });
  window.addEventListener("hashchange", goster);
  $("js-yok").hidden = true;
  goster();
})();
"""


def etiket(a):
    son = f"-{a['ayet_end']}" if a["ayet_end"] else ""
    return f"{a['sure_adi']} Suresi {a['ayet']}{son}. ayet"


def veri(items_yol):
    gunluk = {a["id"]: a for a in json.loads((KOK / "_arac" / "gunluk.json").read_text(encoding="utf8"))}
    items = json.loads(Path(items_yol).read_text(encoding="utf8"))
    cikti = []
    for it in items:
        if not it.get("verified"):
            continue
        g = gunluk[it["id"]]
        cikti.append({"i": it["id"], "e": etiket(g), "r": g["arapca"], "m": g["meal"], "y": g["yol"], "d": it["needs"]})
    bilinen = {n for c in cikti for n in c["d"]}
    for hal, needs in HALLER.items():
        assert any(n in bilinen for n in needs), hal
    return {"haller": HALLER, "ayetler": cikti}


def sayfa(v):
    url = BASE + "hediye/"
    baslik = "Birine ayet hediye et | HÂL"
    ozet = "Adını yaz, hâlini seç; ona özel bir ayet linki oluşsun ve WhatsApp'tan gönder. Hiçbir veri kaydedilmez."
    secenekler = "".join(
        f'<input type="radio" name="hal" id="hal{i}" value="{escape(h)}"><label for="hal{i}">{escape(h)}</label>'
        for i, h in enumerate(HALLER)
    )
    veri_json = json.dumps(v, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{baslik}</title>
<meta name="description" content="{escape(ozet)}">
<meta name="apple-itunes-app" content="app-id=6837715909">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="HÂL">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="Sana bir ayet hediye edildi">
<meta property="og:description" content="{escape(ozet)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{url}og.png">
<style>
{CSS}{EK_CSS}</style>
</head>
<body>
<main>
<p class="marka"><a href="../">HÂL</a></p>

<section id="js-yok">
<h1>Birine ayet hediye et</h1>
<p>Bu sayfa, birinin adını ve hâlini seçince ona özel bir ayet linki oluşturur. Çalışması için tarayıcında JavaScript açık olmalı. Hiçbir veri sunucuya gönderilmez.</p>
<p>Bu arada ayetlere buradan bakabilirsin:</p>
<ul class="konular">
<li><a href="../ayetler/">Tüm ayetler</a></li>
<li><a href="../gunun-ayeti/">Günün ayeti</a></li>
<li><a href="../dua/">Dualar</a></li>
</ul>
</section>

<section id="gonderen" hidden>
<h1>Birine ayet hediye et</h1>
<p class="muted">Adını yaz, hâlini seç. Sana özel bir link oluşsun, WhatsApp'tan gönder. Ad yalnız linkin içinde durur; hiçbir yere gönderilmez ya da kaydedilmez.</p>
<form id="form" novalidate>
<label for="ad">Alıcının adı</label>
<input type="text" id="ad" maxlength="24" autocomplete="off" aria-describedby="hata">
<fieldset>
<legend>Şu an hâli nasıl?</legend>
<div class="secenekler">{secenekler}</div>
</fieldset>
<label for="gonderen-ad">Senin adın (isteğe bağlı)</label>
<input type="text" id="gonderen-ad" maxlength="24" autocomplete="off" aria-describedby="hata">
<p id="hata" class="hata" role="alert"></p>
<button type="submit">Hediye linkini oluştur</button>
</form>
<div id="sonuc" hidden>
<h2>Hediyen hazır</h2>
<p class="meal-kutu"><span id="o-kaynak" class="muted"></span><br><span id="o-meal"></span></p>
<label for="link">Hediye linki</label>
<input type="text" class="kod" id="link" readonly>
<div class="islemler">
<a class="dugme" id="wa" href="https://wa.me/" rel="noopener">WhatsApp'ta gönder</a>
<button type="button" class="ikincil" id="kopyala">Linki kopyala</button>
</div>
<p id="durum" role="status" class="muted"></p>
</div>
</section>

<section id="alici" hidden>
<h1 id="a-baslik" class="hediye-baslik"></h1>
<p id="a-kimden" class="muted" hidden></p>
<p class="arapca" id="a-arapca" dir="rtl" lang="ar"></p>
<p class="meal-kutu" id="a-meal"></p>
<p class="muted" id="a-kaynak"></p>
<p><a id="a-sayfa" href="../ayetler/">Bu ayetin sayfası</a></p>
<p><a class="indir" href="{STORE}">Her gün hâline uygun bir ayet: HÂL</a></p>
<p><button type="button" class="ikincil" id="yeni">Sen de birine hediye et</button></p>
</section>

<p class="kaynak">Arapça: Tanzil Uthmani (tanzil.net, CC BY 3.0, değiştirilmeden). Meal: Elmalılı, Hak Dini Kur&#x27;an Dili, Eser 1979. Ad ve hâl yalnız linkin # kısmında taşınır; bu kısım sunucuya gitmez. İzleme ve çerez yoktur.<br>HÂL bir tefsir ya da fetva kaynağı değildir; dini hüküm vermez.</p>
<footer><a href="../gizlilik/">Gizlilik</a> · <a href="../destek/">Destek</a> · <a href="../">HÂL</a></footer>
</main>
<script type="application/json" id="veri">{veri_json}</script>
<script>{JS.replace("__BASE__", BASE)}</script>
</body>
</html>
"""


def og_html():
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Fraunces Hal"; src: url("{FONT.as_uri()}"); font-weight: 100 900; }}
html, body {{ margin: 0; width: 1200px; height: 630px; background: radial-gradient(circle at 50% 45%, #FBFAF6, #F3F0E8); font-family: "Fraunces Hal", serif; color: #1F2A25; }}
.m {{ position: absolute; left: 0; right: 0; top: 190px; text-align: center; font-size: 68px; line-height: 1.25; padding: 0 120px; }}
.a {{ position: absolute; left: 90px; bottom: 44px; font-size: 30px; color: #7A5C1E; letter-spacing: .04em; }}
.h {{ position: absolute; right: 90px; bottom: 44px; font-size: 38px; letter-spacing: .25em; }}
</style></head><body>
<div class="m">Sana bir ayet<br>hediye edildi &#x1F90D;</div>
<div class="a">Birine ayet hediye et</div><div class="h">HÂL</div>
</body></html>
"""


def og():
    with tempfile.TemporaryDirectory() as d:
        h = Path(d) / "og.html"
        h.write_text(og_html(), encoding="utf8")
        hedef = KOK / "hediye" / "og.png"
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", f"--screenshot={hedef}",
             "--window-size=1200,630", "--force-device-scale-factor=1", h.as_uri()],
            check=True,
        )


def main():
    v = veri(sys.argv[1])
    (KOK / "hediye").mkdir(exist_ok=True)
    (KOK / "hediye" / "index.html").write_text(sayfa(v), encoding="utf8", newline="\n")
    bugun = datetime.now(TR).date().isoformat()
    (KOK / "sitemap-hediye.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"<url><loc>{BASE}hediye/</loc><lastmod>{bugun}</lastmod></url>\n</urlset>\n",
        encoding="utf8", newline="\n",
    )
    if "--og" in sys.argv:
        og()
    print(len(v["ayetler"]), "ayet")


main()
