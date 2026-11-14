#!/usr/bin/env python3
"""Estrae la costa dalla pittura di mapmiddleearth.com (CC BY-NC 4.0).

Perche' non si classifica per colore: nel dipinto mare e terra hanno lo stesso
colore pergamena. Il mare si riconosce dal tratteggio e dal fatto di essere
chiuso dalla linea di costa, che e' inchiostro piu' scuro del tratteggio.

Metodo:
1. inchiostro forte (luminanza bassa, ispessito di 1 px) = barriera
2. componenti connesse dello spazio libero: continente, mare, isole, laghi
3. contorni subpixel (marching squares) + semplificazione RDP
4. raddrizzamento su griglia in miglia (TPS, 41 punti di controllo)

Output: bozze/mappa-dati.json + fonti/estrazione/mme/debug-costa.png
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import measure

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MME = os.path.join(ROOT, "fonti", "estrazione", "mme")
OUT_JSON = os.path.join(ROOT, "bozze", "mappa-dati.json")
DEBUG_PNG = os.path.join(MME, "debug-costa.png")
MARKERS = os.path.join(MME, "markers.json")

INK = 120            # inchiostro forte (linea di costa), il tratteggio e' piu' chiaro
DILATE = 1           # chiude i micro-buchi della linea
MIN_ISOLAND = 900    # px^2 minima per un'isola
MIN_LAKE = 400       # px^2 minima per un lago
RDP_EPS = 1.6        # tolleranza di semplificazione, px

# semi in mare aperto (x, y) in pixel del dipinto
SEA_SEEDS = [(120, 760), (200, 1150), (420, 1500), (700, 1750), (1100, 1900),
             (60, 500), (300, 900), (160, 300)]
# laghi riconosciuti per nome (marker) o per seme
LAKE_NAMES = ("lake-evendim", "long-lake", "mirrormere")
LAKE_SEEDS = [(2780, 800)]      # Mare di Rhûn


def load():
    img = Image.open(os.path.join(MME, "painting.jpg")).convert("RGB")
    return np.asarray(img, dtype=np.float32)


def segment(lum):
    ink = ndi.binary_dilation(lum < INK, iterations=DILATE)
    free = ~ink
    lab, n = ndi.label(free)
    sizes = ndi.sum(free, lab, range(1, n + 1))
    return lab, sizes


def contours(mask, min_area=0.0):
    """Contorni chiusi (x, y) di una maschera, ordinati per area decrescente."""
    padded = np.pad(mask.astype(np.float32), 3, mode="constant")
    m = ndi.gaussian_filter(padded, 1.0)
    out = []
    for c in measure.find_contours(m, 0.5):
        if len(c) < 10:
            continue
        poly = np.stack([c[:, 1], c[:, 0]], axis=1) - 3.0
        x, y = poly[:, 0], poly[:, 1]
        area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
        if area < min_area:
            continue
        out.append((poly, float(area)))
    out.sort(key=lambda t: -t[1])
    return out


def rdp(pts, eps=RDP_EPS):
    pts = np.asarray(pts, dtype=np.float64)
    if len(pts) > 2 and np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    if len(pts) < 3:
        return pts
    keep = np.zeros(len(pts), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        p0, p1 = pts[a], pts[b]
        seg = p1 - p0
        L = math.hypot(*seg) or 1e-9
        sub = pts[a + 1:b]
        d = np.abs(seg[0] * (sub[:, 1] - p0[1]) - seg[1] * (sub[:, 0] - p0[0])) / L
        i = int(np.argmax(d))
        if d[i] > eps:
            k = a + 1 + i
            keep[k] = True
            stack.append((a, k))
            stack.append((k, b))
    return pts[keep]


def tps_fit(ctrl):
    n = len(ctrl)

    def U(a, b):
        r2 = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
        return 0.0 if r2 == 0 else r2 * math.log(r2)

    L = np.zeros((n + 3, n + 3))
    for i in range(n):
        for j in range(n):
            L[i, j] = U(ctrl[i][:2], ctrl[j][:2])
        L[i, n], L[i, n + 1], L[i, n + 2] = 1.0, ctrl[i][0], ctrl[i][1]
        L[n, i], L[n + 1, i], L[n + 2, i] = 1.0, ctrl[i][0], ctrl[i][1]
    Wx = np.linalg.solve(L, np.array([c[2] for c in ctrl] + [0, 0, 0]))
    Wy = np.linalg.solve(L, np.array([c[3] for c in ctrl] + [0, 0, 0]))
    C = np.array([c[:2] for c in ctrl])

    def warp(P):
        P = np.atleast_2d(np.asarray(P, dtype=np.float64))
        dx = P[:, None, 0] - C[None, :, 0]
        dy = P[:, None, 1] - C[None, :, 1]
        r2 = dx * dx + dy * dy
        Uv = np.where(r2 > 0, r2 * np.log(np.maximum(r2, 1e-12)), 0.0)
        x = Wx[n] + Wx[n + 1] * P[:, 0] + Wx[n + 2] * P[:, 1] + Uv @ Wx[:n]
        y = Wy[n] + Wy[n + 1] * P[:, 0] + Wy[n + 2] * P[:, 1] + Uv @ Wy[:n]
        return np.stack([x, y], axis=1)

    return warp


def load_ctrl():
    import importlib.util
    spec = importlib.util.spec_from_file_location("em", os.path.join(ROOT, "tools", "estrai-mappa.py"))
    em = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(em)
    return [[float(c[0]), float(c[1]), float(c[2]), float(c[3])] for c in em.CTRL]


def main():
    rgb = load()
    h, w = rgb.shape[:2]
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    lab, sizes = segment(lum)
    print(f"dipinto {w}x{h} | inchiostro<{INK} (+{DILATE}px)")

    land_id = int(lab[552, 756])          # Casa Baggins
    if land_id == 0:
        raise SystemExit("l'ancora della Contea e' finita sull'inchiostro: abbassare INK")
    land = ndi.binary_fill_holes(lab == land_id)
    print(f"  continente: {int(land.sum())} px")

    sea_ids = {int(lab[y, x]) for x, y in SEA_SEEDS} - {0}
    if len(sea_ids) != 1:
        print("  attenzione: semi di mare in", len(sea_ids), "componenti:", sea_ids)
    sea = np.isin(lab, list(sea_ids))
    print(f"  mare: {len(sea_ids)} componenti, {int(sea.sum())} px")
    lake_ids = {int(lab[y, x]) for x, y in LAKE_SEEDS} - {0, land_id}
    mk = json.load(open(MARKERS, encoding="utf-8"))
    for name in LAKE_NAMES:
        if name in mk and mk[name].get("xy"):
            x, y = mk[name]["xy"]
            cid = int(lab[int(y), int(x)])
            if cid not in (0, land_id) and sizes[cid - 1] > MIN_LAKE:
                lake_ids.add(cid)
    lakes = [lab == cid for cid in lake_ids]
    print(f"  laghi: {len(lakes)}")

    # isole = buchi del mare (terra circondata dall'acqua)
    holes = ndi.binary_fill_holes(sea) & ~sea
    hlab, hn = ndi.label(holes)
    islands = []
    for cid in range(1, hn + 1):
        m = hlab == cid
        a = int(m.sum())
        if a < MIN_ISOLAND:
            continue
        ys, xs = np.nonzero(m)
        bw, bh = xs.max() - xs.min(), ys.max() - ys.min()
        if bw < 4 or bh < 4 or a < 0.25 * bw * bh:
            continue
        islands.append(m)
    print(f"  isole: {len(islands)}")

    warp = tps_fit(load_ctrl())

    def warp_poly(poly, eps=RDP_EPS):
        q = warp(rdp(poly, eps))
        return [[round(float(a), 1), round(float(b), 1)] for a, b in q]

    def to_miles(mask, eps=RDP_EPS):
        return warp_poly(contours(mask, 100)[0][0], eps)

    sea_polys = []
    for cid in sea_ids:
        m = lab == cid
        if m.sum() < 40000:
            continue
        sea_polys.append(to_miles(m, eps=1.3))
    islands_out = [to_miles(m) for m in islands]
    lakes_out = [to_miles(m) for m in lakes]

    marks = {k: {"title": v["title"],
                 "mi": [round(float(a), 1), round(float(b), 1)]}
             for k, v in mk.items() if v.get("xy")
             for a, b in warp([[v["xy"][0], v["xy"][1]]])}

    data = {
        "sea": sea_polys,
        "islands": [{"ring": r} for r in islands_out],
        "lakes": [{"ring": r} for r in lakes_out],
        "markers": marks,
        "source": "Geografia derivata da mapmiddleearth.com (CC BY-NC 4.0), ridisegnata e raddrizzata su griglia in miglia.",
        "meta": {"sea_polys": len(sea_polys),
                 "points": [len(p) for p in sea_polys],
                 "islands": len(islands_out), "lakes": len(lakes_out), "ink": INK},
    }
    json.dump(data, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"  mare: {[len(p) for p in sea_polys]} punti | isole {len(islands_out)} | laghi {len(lakes_out)}")

    # --- debug ---
    arr = rgb.astype(np.uint8).copy()
    arr[sea] = (arr[sea] * 0.55 + np.array([40, 120, 150]) * 0.45).astype(np.uint8)
    dbg = Image.fromarray(arr)
    d = ImageDraw.Draw(dbg)
    for cid in sea_ids:
        for poly, _a in contours(lab == cid, 40000)[:1]:
            d.line([(float(x), float(y)) for x, y in poly], fill=(200, 30, 30), width=5)
    for m in islands:
        for poly, _a in contours(m, 100)[:1]:
            d.line([(float(x), float(y)) for x, y in poly], fill=(250, 160, 20), width=5)
    dbg.save(DEBUG_PNG)
    print("  debug:", DEBUG_PNG)

    for k in ("bag-end", "minas-tirith", "erebor", "umbar", "grey-havens"):
        print("   ", k, marks[k]["mi"])


if __name__ == "__main__":
    main()
