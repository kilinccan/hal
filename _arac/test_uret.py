import json
import sys
from pathlib import Path

ITEMS = Path(sys.argv[1] if len(sys.argv) > 1 else "C:/Users/lastp/Documents/ckapp-wt/app/assets/content/items.json")
ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "test" / "index.html"
BEGIN, END = "/*VERI*/", "/*VERI-SON*/"
SHORT_ARABIC = 90


def entry(item):
    path = f"{item['surah']}-{item['ayah']}" + (f"-{item['ayah_end']}" if item["ayah_end"] else "")
    if not (ROOT / "ayet" / path / "og.png").is_file():
        raise SystemExit(f"ayet sayfası yok: {path}")
    label = f"{item['surah_name']} {item['surah']}:{item['ayah']}" + (f"-{item['ayah_end']}" if item["ayah_end"] else "")
    return {
        "p": path,
        "s": label,
        "n": item["needs"],
        "k": "d" if item["kind"] == "dua" else "a",
        "u": 1 if len(item["arabic"]) <= SHORT_ARABIC else 0,
    }


items = [i for i in json.loads(ITEMS.read_text(encoding="utf-8")) if i["verified"]]
data = json.dumps([entry(i) for i in items], ensure_ascii=False, separators=(",", ":"))
page = PAGE.read_text(encoding="utf-8")
head, rest = page.split(BEGIN)
_, tail = rest.split(END)
PAGE.write_text(f"{head}{BEGIN}{data}{END}{tail}", encoding="utf-8", newline="\n")
print(len(items), "öğe")
