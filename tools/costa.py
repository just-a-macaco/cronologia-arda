#!/usr/bin/env python3
"""Base cartografica originale, in scala vera (1 unita' = 1 miglio).

Coordinate: x verso est, y verso sud, origine a Hobbiville (0,0).
Le posizioni dei luoghi sono quelle gia' approvate (v3); la costa e' disegnata
ex novo: pochi punti guida con la geografia giusta + dettaglio procedurale
multi-scala lungo la normale, cosi' da avere centinaia di punti e un profilo
naturale invece di una spezzata.

Output: bozze/costa.json  (polilinee in miglia)
"""
import json, math, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "bozze", "costa.json")

# ---------------------------------------------------------------- punti guida
# costa principale: da Forochel (nord-ovest) lungo Lindon, Eriador, Andrast,
# Belfalas, delta dell'Anduin, Umbar, costa di Harad fino al bordo sud.
COAST = [
    # baia di Forochel: golfo a U aperto verso nord, tagliato dal bordo mappa
    (-430, -660), (-452, -606), (-470, -552), (-482, -500), (-478, -468),
    (-452, -452), (-418, -444), (-382, -452), (-348, -474), (-322, -506),
    (-306, -548), (-294, -596), (-286, -640),
    # costa nord verso Lindon
    (-280, -600), (-292, -556), (-280, -512), (-294, -468), (-278, -424),
    (-288, -380), (-272, -336), (-284, -292), (-268, -248), (-278, -208),
    # Forlindon
    (-262, -170), (-244, -140), (-228, -116),
    # golfo di Lune: fiordo verso est, bocca a Mithlond
    (-204, -104), (-172, -92), (-140, -78), (-116, -58),
    (-140, -38), (-176, -22), (-212, -6), (-240, 12), (-254, 34),
    # Harlindon e costa dell'Eriador (rigonfiamento a ovest)
    (-266, 68), (-248, 106), (-262, 146), (-246, 186), (-270, 226),
    (-252, 266), (-276, 306), (-258, 346), (-282, 386), (-296, 426),
    (-284, 466), (-302, 506),
    # penisola di Andrast, capo a sud-ovest
    (-330, 544), (-358, 582), (-382, 618), (-396, 646), (-380, 668),
    (-346, 676), (-318, 690),
    # baia di Belfalas, costa nord da ovest a est
    (-276, 716), (-228, 740), (-172, 760), (-108, 776), (-40, 788),
    (28, 796), (100, 802), (172, 806), (244, 806), (316, 804),
    (388, 800), (460, 796), (532, 794), (600, 798), (662, 808),
    (716, 824),
    # delta dell'Anduin: piu' bocche
    (752, 844), (776, 866), (782, 890), (806, 902), (820, 880),
    (836, 908), (858, 900), (866, 926), (846, 948),
    # Lebennin e Harondor verso sud-ovest
    (818, 978), (786, 1010), (746, 1040), (700, 1066), (648, 1088),
    (598, 1104),
    # Umbar e capo
    (566, 1116), (544, 1138), (562, 1162),
    # costa di Harad
    (598, 1192), (642, 1222), (694, 1250), (752, 1278), (814, 1306),
    (882, 1334), (954, 1362), (1030, 1390), (1110, 1418), (1190, 1444),
]

# Mari e laghi (in miglia): Rhun a est, Nurnen dentro Mordor
SEAS = {
    "rhun": [(916, 66), (938, 22), (988, -4), (1044, -16), (1098, -6),
             (1136, 22), (1152, 62), (1150, 108), (1128, 148), (1088, 172),
             (1040, 180), (994, 168), (958, 148), (934, 120), (920, 96)],
    "nurnen": [(946, 862), (974, 868), (992, 890), (990, 916), (972, 934),
               (948, 938), (928, 924), (922, 900), (930, 878)],
}

# isole
ISLANDS = {
    "himling": [(-322, -556), (-300, -568), (-278, -558), (-274, -540),
                (-294, -528), (-316, -534)],
    "tol-fuin": [(-250, -498), (-226, -508), (-202, -498), (-198, -482),
                 (-222, -470), (-244, -476)],
    "tolfalas": [(742, 918), (778, 928), (800, 954), (790, 982), (758, 988),
                 (736, 966), (728, 940)],
}

# cavità / insenature da non riempire di dettaglio (ampiezza ridotta)
DETAIL = [26.0, 13.0, 6.0, 3.0, 1.4, 0.6]   # ampiezze per ottava, miglia
WAVES = [340.0, 150.0, 70.0, 32.0, 14.0, 6.0]  # lunghezze d'onda, miglia
SEED = 20261114


def catmull(pts, step=2.0):
    """Polilinea densa lungo una spline di Catmull-Rom, ricampionata a passo fisso."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        seg = math.dist(p1, p2)
        n = max(2, int(seg / step * 2))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(tuple(pts[-1]))
    return out


def resample(path, step=1.5):
    acc = [path[0]]
    carry = 0.0
    for i in range(1, len(path)):
        a, b = acc[-1], path[i]
        d = math.dist(a, b)
        if d == 0:
            continue
        t = (step - carry) / d
        while t <= 1.0:
            acc.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            a = acc[-1]
            d = math.dist(a, b)
            if d == 0:
                break
            t = step / d
        carry = math.dist(acc[-1], path[i])
    if acc[-1] != tuple(path[-1]):
        acc.append(tuple(path[-1]))
    return acc


def detail(path, closed=False, scale=1.0, seed=0):
    """Sposta i punti lungo la normale con rumore multi-ottava deterministico."""
    rng = random.Random(SEED + seed)
    pts = resample(catmull(path), 1.5)
    n = len(pts)
    total = sum(math.dist(pts[i], pts[i + 1]) for i in range(n - 1))

    # rumore: per ogni ottava, controllo casuale interpolato lungo l'arco
    phases = []
    for wl, amp in zip(WAVES, DETAIL):
        k = max(4, int(total / wl) + 2)
        vals = [rng.uniform(-1, 1) for _ in range(k)]
        phases.append((wl, amp * scale, vals))

    out = []
    s = 0.0
    for i in range(n):
        if i > 0:
            s += math.dist(pts[i - 1], pts[i])
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        off = 0.0
        for wl, amp, vals in phases:
            u = s / wl
            j = int(u) % len(vals)
            t = u - int(u)
            t = t * t * (3 - 2 * t)                     # smoothstep
            off += amp * (vals[j] * (1 - t) + vals[(j + 1) % len(vals)] * t)
        # smorza il dettaglio agli estremi (per non sfilacciare i bordi mappa)
        if not closed:
            edge = min(1.0, min(s, total - s) / 40.0)
            off *= edge
        out.append((pts[i][0] + nx * off, pts[i][1] + ny * off))
    return out


def rdp(pts, eps=1.2):
    pts = list(pts)
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        (x0, y0), (x1, y1) = pts[a], pts[b]
        seg = (x1 - x0, y1 - y0)
        L = math.hypot(*seg) or 1e-9
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(seg[0] * (py - y0) - seg[1] * (px - x0)) / L
            if d > best:
                best, bi = d, i
        if best > eps:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def main():
    data = {
        "coast": rdp(detail(COAST, seed=1), 0.9),
        "seas": {k: rdp(detail(v, closed=True, scale=0.55, seed=i + 10), 0.7)
                 for i, (k, v) in enumerate(SEAS.items())},
        "islands": {k: rdp(detail(v, closed=True, scale=0.6, seed=i + 20), 0.6)
                    for i, (k, v) in enumerate(ISLANDS.items())},
    }
    json.dump(data, open(OUT, "w"), separators=(",", ":"))
    print("costa:", len(data["coast"]), "punti |",
          "mari:", {k: len(v) for k, v in data["seas"].items()},
          "| isole:", {k: len(v) for k, v in data["islands"].items()})


if __name__ == "__main__":
    main()
