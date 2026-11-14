#!/usr/bin/env python3
"""Rende lo Stadio 1 (acque e coste) da bozze/costa.json."""
import json, math, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "bozze", "costa.json")
OUT = os.path.join(ROOT, "bozze", "mappa-stadio1.html")

# luoghi (frame approvato v3): [x, y, etichetta, dx, dy, anchor]
PLACES = [
    (-240, 45, "Porti Grigi", -12, 4, "end"),
    (0, 10, "Hobbiville", 0, 30, "middle"),
    (130, 25, "Brea", 12, 4, "start"),
    (280, -192, "Fornost", 12, 4, "start"),
    (235, 22, "Amon Sûl", 12, 14, "start"),
    (388, 5, "Gran Burrone", 12, 4, "start"),
    (325, -318, "Angmar", 12, 4, "start"),
    (468, 165, "Campo Gaggiolo", 12, 4, "start"),
    (552, 296, "Dol Guldur", -12, 18, "end"),
    (690, -150, "Erebor", 12, 4, "start"),
    (650, -95, "Pontelagolungo", -12, 18, "end"),
    (436, 183, "Moria", -12, 4, "end"),
    (505, 200, "Lothlórien", 12, 24, "start"),
    (525, 430, "Fangorn", -12, 22, "end"),
    (442, 478, "Isengard", -12, 4, "end"),
    (455, 588, "Fosso di Helm", -12, 4, "end"),
    (515, 295, "Campi del Celebrant", -12, 24, "end"),
    (800, 700, "Dagorlad", 12, 4, "start"),
    (770, 780, "Minas Tirith", -12, 4, "end"),
    (800, 790, "Osgiliath", 10, 22, "start"),
    (856, 808, "Minas Morgul", 12, 4, "start"),
    (920, 858, "Monte Fato", 12, 16, "start"),
    (950, 828, "Barad-dûr", 12, 4, "start"),
    (543, 338, "Parth Galen", -12, 4, "end"),
    (575, -330, "Montagne Grigie", 0, 26, "middle"),
    (434, -55, "Montagne Nebbiose", -12, 4, "end"),
    (815, 820, "Ithilien", 8, -10, "start"),
    (95, -112, "Annúminas", 12, -6, "start"),
    (315, 495, "Tharbad", 12, 14, "start"),
    (528, 565, "Edoras", 12, 14, "start"),
    (833, 855, "Pelargir", 12, 14, "start"),
    (570, 790, "Dol Amroth", 12, 14, "start"),
    (520, 1120, "Umbar", 12, 14, "start"),
]

REGIONS = [
    (-120, -600, "FORODWAITH", 22, 0),
    (150, 250, "ERIADOR", 26, 0),
    (740, 130, "RHOVANION", 22, 0),
    (500, 520, "ROHAN", 20, 0),
    (650, 720, "GONDOR", 22, 0),
    (1000, 700, "MORDOR", 20, 0),
    (700, 1240, "HARAD", 22, 0),
    (200, 560, "ENEDWAITH", 14, 0),
    (390, 470, "DUNLAND", 13, 0),
    (380, 200, "EREGION", 14, 0),
    (-190, 330, "MINHIRIATH", 13, 0),
    (-440, 200, "BELEGAER", 22, -68),
    (-1050, 0, "", 1, 0),
]

WATERS = [
    (-392, -500, "Baia di Forochel", 13, -10),
    (-560, 120, "BELEGAER", 24, -68),
    (-186, -52, "Golfo di Lune", 11, 0),
    (-120, 900, "Baia di Belfalas", 15, -4),
    (1040, 96, "Mare di Rhûn", 14, 0),
    (960, 902, "Núrnen", 10, 0),
    (-1080, 0, "", 1, 0),
]


def poly(pts, close=True):
    s = "M%.1f %.1f" % pts[0]
    s += "".join("L%.1f %.1f" % p for p in pts[1:])
    return s + ("Z" if close else "")


def main():
    d = json.load(open(DATA))
    coast = [tuple(p) for p in d["coast"]]
    seas = {k: [tuple(p) for p in v] for k, v in d["seas"].items()}
    islands = {k: [tuple(p) for p in v] for k, v in d["islands"].items()}

    vx, vy, vw, vh = -560, -680, 1780, 2170
    sea_poly = coast + [(vx + vw, coast[-1][1]), (vx + vw, vy + vh), (vx, vy + vh), (vx, vy)]

    grid = []
    gx = math.floor(vx / 200) * 200
    while gx <= vx + vw:
        grid.append('<line x1="%d" y1="%d" x2="%d" y2="%d"/>' % (gx, vy, gx, vy + vh))
        gx += 200
    gy = math.floor(vy / 200) * 200
    while gy <= vy + vh:
        grid.append('<line x1="%d" y1="%d" x2="%d" y2="%d"/>' % (vx, gy, vx + vw, gy))
        gy += 200

    places = "".join(
        '<g class="place"><circle cx="%d" cy="%d" r="5"/><text x="%d" y="%d" text-anchor="%s">%s</text></g>'
        % (x, y, x + dx, y + dy, an, html.escape(n))
        for x, y, n, dx, dy, an in PLACES)

    regions = "".join(
        '<text class="region" x="%d" y="%d" font-size="%d"%s text-anchor="middle">%s</text>'
        % (x, y, s, ' transform="rotate(%d %d %d)"' % (r, x, y) if r else "", html.escape(n))
        for x, y, n, s, r in REGIONS if n)
    waters = "".join(
        '<text class="water" x="%d" y="%d" font-size="%d"%s text-anchor="middle">%s</text>'
        % (x, y, s, ' transform="rotate(%d %d %d)"' % (r, x, y) if r else "", html.escape(n))
        for x, y, n, s, r in WATERS if n)

    doc = """<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cronologia di Arda · Stadio 1 — acque e coste</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{--land:#f5f1e6;--sea:#cfe0e2;--ink:#3c4a4f;--grid:rgba(60,74,79,.10);--accent:#b23a2e}
*{box-sizing:border-box}
body{margin:0;background:#eef2f2;color:var(--ink);font:400 15px/1.5 "Space Grotesk",Helvetica,Arial,sans-serif}
main{max-width:1150px;margin:0 auto;padding:24px}
h1{font:500 .82rem/1.35 sans-serif;letter-spacing:.26em;text-transform:uppercase;margin:0 0 6px}
p{color:#5d6c71;font-size:.84rem;max-width:70em;margin:0 0 4px}
svg{display:block;width:100%;height:auto;margin-top:14px;border:1px solid #d9e0e1}
svg text{font-family:"Space Grotesk",Helvetica,Arial,sans-serif}
.grid{stroke:var(--grid);stroke-width:1}
.sea{fill:var(--sea);stroke:var(--ink);stroke-width:1.6;stroke-linejoin:round}
.island{fill:var(--land);stroke:var(--ink);stroke-width:1.1}
.lake{fill:var(--sea);stroke:var(--ink);stroke-width:1}
.place circle{fill:var(--accent)}
.place text{font-size:12.5px;fill:var(--ink)}
.region{fill:#8a979b;letter-spacing:.3em;opacity:.75}
.water{fill:#6f8b91;letter-spacing:.26em;opacity:.8;font-style:italic}
</style></head><body><main>
<h1>Stadio 1 — acque e coste · in scala (1 unità = 1 miglio)</h1>
<p>Base originale. Costa disegnata su punti guida con distanze reali e dettaglio procedurale multi-scala; posizioni dei luoghi invariate rispetto alla v3 approvata. Griglia ogni 200 miglia. Mancano rilievo, fiumi, vegetazione, strade.</p>
<svg viewBox="{vx} {vy} {vw} {vh}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Costa della Terra di Mezzo in scala">
<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="var(--land)"/>
<g class="grid">{grid}</g>
<path class="sea" d="{sea}"/>
{islands}
{seas}
{places}
{regions}
{waters}
<g transform="translate({sx},{sy})" class="scale">
<rect x="0" y="-2" width="200" height="4" fill="#3c4a4f"/>
<rect x="0" y="-2" width="100" height="4" fill="#f5f1e6"/>
<line x1="0" y1="-9" x2="0" y2="9" stroke="#3c4a4f" stroke-width="2"/>
<line x1="100" y1="-6" x2="100" y2="6" stroke="#3c4a4f" stroke-width="1.2"/>
<line x1="200" y1="-9" x2="200" y2="9" stroke="#3c4a4f" stroke-width="2"/>
<text x="100" y="-15" text-anchor="middle" font-size="13" fill="#3c4a4f">200 miglia</text>
</g>
</svg>
<p style="margin-top:9px;font-size:.76rem;color:#6d7a7e">Bozza tecnica: le forme delle insenature sono una ricostruzione originale, non un ricalco.</p>
</main></body></html>"""

    doc = (doc.replace("{vx}", str(vx)).replace("{vy}", str(vy))
              .replace("{vw}", str(vw)).replace("{vh}", str(vh))
              .replace("{grid}", "".join(grid))
              .replace("{sea}", poly(sea_poly))
              .replace("{islands}", "".join('<path class="island" d="%s"/>' % poly(r) for r in islands.values()))
              .replace("{seas}", "".join('<path class="lake" d="%s"/>' % poly(r) for r in seas.values()))
              .replace("{places}", places).replace("{regions}", regions).replace("{waters}", waters)
              .replace("{sx}", str(vx + 60)).replace("{sy}", str(vy + vh - 60)))
    open(OUT, "w", encoding="utf-8").write(doc)
    print("scritto", OUT)


if __name__ == "__main__":
    main()
