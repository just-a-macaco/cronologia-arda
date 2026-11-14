#!/usr/bin/env python3
"""Warp robusto: affine (pixel->miglia) + campo di spostamento regolarizzato su griglia.

Niente TPS: il campo e' una media pesata gaussiana dei residui, campionata su una
griglia grossolana e interpolata bilinearmente. Fuori dai punti di controllo il
campo resta costante (clamp), quindi non esplode e non produce pieghe.
"""
import numpy as np, importlib.util, math, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('ec', os.path.join(ROOT, 'tools', 'estrai-costa.py'))
ec = importlib.util.module_from_spec(spec); spec.loader.exec_module(ec)
from scipy import ndimage as ndi

W, H = 3072, 2048
SIGMA = 420.0          # px, larghezza della regolarizzazione
GX, GY = 110, 74       # nodi della griglia


def build_warp():
    ctrl = np.array(ec.load_ctrl(), dtype=float)
    P = np.hstack([ctrl[:, :2], np.ones((len(ctrl), 1))])
    M = ctrl[:, 2:4]
    coef = np.linalg.lstsq(P, M, rcond=None)[0]          # pixel -> miles

    resid = M - P @ coef                                  # miglia di correzione
    xs = np.linspace(0, W, GX)
    ys = np.linspace(0, H, GY)
    NX, NY = np.meshgrid(xs, ys)

    # media pesata gaussiana dei residui su ogni nodo
    d2 = (NX[..., None] - ctrl[None, None, :, 0]) ** 2 + (NY[..., None] - ctrl[None, None, :, 1]) ** 2
    w = np.exp(-d2 / (2 * SIGMA ** 2)) + 1e-12
    field = np.einsum('ijc,ck->ijk', w, resid) / w.sum(-1, keepdims=True)

    def warp(pts):
        pts = np.atleast_2d(np.asarray(pts, dtype=float))
        base = np.hstack([pts, np.ones((len(pts), 1))]) @ coef
        gx = np.clip(pts[:, 0] / W * (GX - 1), 0, GX - 1.0001)
        gy = np.clip(pts[:, 1] / H * (GY - 1), 0, GY - 1.0001)
        x0 = gx.astype(int); y0 = gy.astype(int)
        fx = (gx - x0)[:, None]; fy = (gy - y0)[:, None]
        f00 = field[y0, x0]; f10 = field[y0, x0 + 1]
        f01 = field[y0 + 1, x0]; f11 = field[y0 + 1, x0 + 1]
        disp = (f00 * (1 - fx) * (1 - fy) + f10 * fx * (1 - fy) +
                f01 * (1 - fx) * fy + f11 * fx * fy)
        return base + disp

    return warp, resid, ctrl


def main():
    warp, resid, ctrl = build_warp()
    print('residui miglia: mediana %.0f  max %.0f' % (np.median(np.linalg.norm(resid, axis=1)),
                                                      np.max(np.linalg.norm(resid, axis=1))))

    rgb = ec.load()
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    lab, sizes = ec.segment(lum)
    sea_ids = {int(lab[y, x]) for x, y in ec.SEA_SEEDS} - {0}
    sea = np.isin(lab, list(sea_ids))
    holes = ndi.binary_fill_holes(sea) & ~sea
    hl, hn = ndi.label(holes)
    islands = []
    for cid in range(1, hn + 1):
        m = hl == cid
        a = int(m.sum())
        if a < 900:
            continue
        ys_, xs_ = np.nonzero(m)
        bw, bh = xs_.max() - xs_.min(), ys_.max() - ys_.min()
        if bw < 4 or bh < 4 or a < 0.25 * bw * bh:
            continue
        islands.append(m)

    def poly(mask, eps=1.2):
        p, _ = ec.contours(mask, 100)[0]
        return ec.rdp(p, eps)

    seas = [warp(poly(lab == cid)) for cid in sea_ids if (lab == cid).sum() > 40000]
    isls = [warp(poly(m)) for m in islands]

    allp = np.vstack(seas)
    print('mare in miglia: x %.0f..%.0f  y %.0f..%.0f' % (allp[:, 0].min(), allp[:, 0].max(),
                                                          allp[:, 1].min(), allp[:, 1].max()))

    mk = json.load(open(os.path.join(ROOT, 'fonti', 'estrazione', 'mme', 'markers.json'), encoding='utf-8'))
    dots = ''
    for k, v in mk.items():
        if not v.get('xy'):
            continue
        q = warp([[v['xy'][0], v['xy'][1]]])[0]
        dots += f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.5" class="dot"/>'

    def path(p):
        return 'M' + 'L'.join('%.1f %.1f' % (x, y) for x, y in p) + 'Z'

    pad = 140
    vx, vy = math.floor(allp[:, 0].min() - pad), math.floor(allp[:, 1].min() - pad)
    vw = math.ceil(allp[:, 0].max() - allp[:, 0].min() + 2 * pad)
    vh = math.ceil(allp[:, 1].max() - allp[:, 1].min() + 2 * pad)

    svg = (f'<svg viewBox="{vx} {vy} {vw} {vh}" xmlns="http://www.w3.org/2000/svg">'
           f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="#f5f1e6"/>'
           + ''.join(f'<path d="{path(p)}" class="sea"/>' for p in seas)
           + ''.join(f'<path d="{path(p)}" class="island"/>' for p in isls)
           + dots + '</svg>')

    doc = ('<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><title>Prova warp robusto</title>'
           '<style>body{margin:0;background:#eef2f2;font:400 15px/1.5 "Space Grotesk",Helvetica,Arial,sans-serif;color:#3c4a4f}'
           'main{max-width:1250px;margin:0 auto;padding:24px}'
           'svg{width:100%;height:auto;background:#f5f1e6;border:1px solid #d9e0e1}'
           '.sea{fill:#cfe0e2;stroke:#3c4a4f;stroke-width:2;stroke-linejoin:round}'
           '.island{fill:#f5f1e6;stroke:#3c4a4f;stroke-width:1.4}'
           '.dot{fill:#b23a2e;opacity:.45}</style></head><body><main>' + svg + '</main></body></html>')
    open(os.path.join(ROOT, 'bozze', 'prova-warp.html'), 'w', encoding='utf-8').write(doc)
    print('scritto bozze/prova-warp.html')


if __name__ == '__main__':
    main()
