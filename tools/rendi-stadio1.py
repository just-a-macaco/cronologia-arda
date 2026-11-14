#!/usr/bin/env python3
"""Genera lo schizzo dello Stadio 1 (acque e coste) da bozze/mappa-dati.json."""
import json, math, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "bozze", "mappa-dati.json")
OUT = os.path.join(ROOT, "bozze", "mappa-stadio1.html")

LABELS = {
    "grey-havens": "Porti Grigi", "bag-end": "Hobbiville", "bree": "Brea",
    "fornost": "Fornost", "rivendell": "Gran Burrone", "moria": "Moria",
    "isengard": "Isengard", "edoras": "Edoras", "helms-deep": "Fosso di Helm",
    "minas-tirith": "Minas Tirith", "osgiliath": "Osgiliath",
    "minas-morgul": "Minas Morgul", "mount-doom": "Monte Fato",
    "barad-dur": "Barad-dûr", "erebor": "Erebor", "lake-town": "Pontelagolungo",
    "umbar": "Umbar", "dol-amroth": "Dol Amroth", "pelargir": "Pelargir",
    "dol-guldur": "Dol Guldur", "caradhras": "Caradhras",
    "thranduils-halls": "Sale di Thranduil", "annuminas": "Annúminas",
    "argonath": "Argonath", "black-gate": "Cancello Nero",
    "mount-gundabad": "Gundabad", "carn-dum": "Carn Dûm",
}


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    sea = d["sea"]
    islands = [i["ring"] for i in d["islands"]]
    lakes = [l["ring"] for l in d["lakes"]]
    marks = d["markers"]

    pts = [p for poly in sea for p in poly]
    for r in islands + lakes:
        pts += r
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = 140
    vx, vy = math.floor(min(xs) - pad), math.floor(min(ys) - pad)
    vw, vh = math.ceil(max(xs) - min(xs) + 2 * pad), math.ceil(max(ys) - min(ys) + 2 * pad)

    def path(poly, close=True):
        s = "M{:.1f} {:.1f}".format(*poly[0])
        s += "".join("L{:.1f} {:.1f}".format(*p) for p in poly[1:])
        return s + ("Z" if close else "")

    grid = []
    gx = math.floor(vx / 200) * 200
    while gx <= vx + vw:
        grid.append(f'<line x1="{gx}" y1="{vy}" x2="{gx}" y2="{vy + vh}"/>')
        gx += 200
    gy = math.floor(vy / 200) * 200
    while gy <= vy + vh:
        grid.append(f'<line x1="{vx}" y1="{gy}" x2="{vx + vw}" y2="{gy}"/>')
        gy += 200

    dots = "".join(
        f'<circle cx="{m["mi"][0]:.1f}" cy="{m["mi"][1]:.1f}" r="3.5" class="dot"/>'
        for m in marks.values()
    )
    labels = []
    for k, txt in LABELS.items():
        if k not in marks:
            continue
        x, y = marks[k]["mi"]
        anchor = "end" if x > (vx + vw / 2) else "start"
        dx = -12 if anchor == "end" else 12
        labels.append(
            f'<g class="place"><circle cx="{x:.1f}" cy="{y:.1f}" r="5"/>'
            f'<text x="{x + dx:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}">{html.escape(txt)}</text></g>'
        )

    sea_paths = "".join(f'<path d="{path(p)}" class="sea"/>' for p in sea)
    isl_paths = "".join(f'<path d="{path(r)}" class="island"/>' for r in islands)
    lake_paths = "".join(f'<path d="{path(r)}" class="lake"/>' for r in lakes)

    doc = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cronologia di Arda · Stadio 1 — acque e coste</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--land:#f5f1e6;--sea:#cfe0e2;--sea-line:#8fa8ae;--ink:#3c4a4f;--grid:rgba(60,74,79,.10);--accent:#b23a2e}}
*{{box-sizing:border-box}}
body{{margin:0;background:#eef2f2;color:var(--ink);font:400 15px/1.5 "Space Grotesk",Helvetica,Arial,sans-serif}}
main{{max-width:1250px;margin:0 auto;padding:24px}}
h1{{font:500 .82rem/1.35 "Space Grotesk",sans-serif;letter-spacing:.26em;text-transform:uppercase;margin:0 0 6px}}
p{{margin:0 0 4px;color:#5d6c71;font-size:.84rem;max-width:72em}}
svg{{display:block;width:100%;height:auto;margin-top:16px;border:1px solid #d9e0e1}}
svg text{{font-family:"Space Grotesk",Helvetica,Arial,sans-serif}}
.landbg{{fill:var(--land)}}
.sea{{fill:var(--sea);stroke:var(--ink);stroke-width:1.5;stroke-linejoin:round}}
.island{{fill:var(--land);stroke:var(--ink);stroke-width:1.1}}
.lake{{fill:var(--sea);stroke:var(--ink);stroke-width:.9}}
.grid{{stroke:var(--grid);stroke-width:1}}
.dot{{fill:var(--accent);opacity:.55}}
.place circle{{fill:var(--accent)}}
.place text{{font-size:12.5px;fill:var(--ink)}}
.scale text{{font-size:13px;fill:var(--ink)}}
.attr{{margin-top:10px;font-size:.76rem;color:#6d7a7e}}
</style>
</head>
<body>
<main>
<h1>Stadio 1 — Acque e coste</h1>
<p>Costa derivata dalla mappa di <em>mapmiddleearth.com</em> (CC BY-NC 4.0) e raddrizzata su una griglia in miglia (1 unità = 1 miglio) con trasformazione a membrana su 41 punti di controllo. Punti rossi: i 109 luoghi della reference, per verificare la tenuta della scala. Bozza tecnica: mancano rilievo, fiumi, vegetazione, strade.</p>
<svg viewBox="{vx} {vy} {vw} {vh}" xmlns="http://www.w3.org/2000/svg" aria-label="Costa della Terra di Mezzo in scala">
<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" class="landbg"/>
<g class="grids">{''.join(grid)}</g>
{sea_paths}
{isl_paths}
{lake_paths}
{dots}
{''.join(labels)}
<g transform="translate({vx + 70},{vy + vh - 55})" class="scale">
<rect x="0" y="-2" width="200" height="4" fill="#3c4a4f"/>
<rect x="0" y="-2" width="100" height="4" fill="#f5f1e6"/>
<line x1="0" y1="-8" x2="0" y2="8" stroke="#3c4a4f" stroke-width="2"/>
<line x1="100" y1="-6" x2="100" y2="6" stroke="#3c4a4f" stroke-width="1.2"/>
<line x1="200" y1="-8" x2="200" y2="8" stroke="#3c4a4f" stroke-width="2"/>
<text x="100" y="-14" text-anchor="middle">200 miglia</text>
</g>
</svg>
<p class="attr">Geografia derivata da <em>mapmiddleearth.com</em>, © autori originali, licenza <a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a>; ridisegno, raddrizzamento e resa originali per «Cronologia di Arda».</p>
</main>
</body>
</html>
"""
    open(OUT, "w", encoding="utf-8").write(doc)
    print("scritto", OUT, "| viewBox", vx, vy, vw, vh)


if __name__ == "__main__":
    main()
