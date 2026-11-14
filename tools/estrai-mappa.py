#!/usr/bin/env python3
# Estrae la geografia dalla mappa di mapmiddleearth.com (CC BY-NC 4.0):
# 1. decodifica la pittura JPEG incorporata nel loro SVG (già estratta in painting.jpg)
# 2. classifica mare/terra, traccia coste, isole e laghi
# 3. raddrizza tutto su una griglia in miglia (1 unità = 1 miglio, Hobbiton = 0,10)
#    con una trasformazione a membrana (TPS) calibrata sui luoghi con posizione nota
#    dai libri (distanze di viaggio, Appendici, Atlante di Fonstad come riferimento pubblico)
# 4. genera bozze/mappa-dati.json e lo schizzo HTML dello Stadio 1 (acque e coste)
#Attribuzione: geografia derivata da mapmiddleearth.com, licenza CC BY-NC 4.0.

import re, json, base64, zlib, struct, subprocess, math, os, sys
from collections import deque

D = os.path.join(os.path.dirname(__file__), "..", "fonti", "estrazione", "mme")
D = os.path.abspath(D)
SMALL = 1536  # lato lungo dopo il ridimensionamento

# ---------- 1. immagine ----------
def prepare():
    jpg = os.path.join(D, "painting.jpg")
    if not os.path.exists(jpg):
        s = open(os.path.join(D, "middle-earth-it.svg"), encoding="utf-8").read()
        m = re.search(r'href="data:image/jpeg;base64,([A-Za-z0-9+/=]+)"', s)
        open(jpg, "wb").write(base64.b64decode(m.group(1)))
    png = os.path.join(D, "painting-small.png")
    subprocess.run(["sips", "-s", "format", "png", "-Z", str(SMALL), jpg, "--out", png], check=True, capture_output=True)
    return png

def decode_png(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, w, h, depth, ctype = 8, b"", 0, 0, 0, 0
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos+4])[0]
        typ = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", chunk[:10])
        elif typ == b"IDAT":
            idat += chunk
        pos += 12 + ln
    raw = zlib.decompress(idat)
    nch = {0:1, 2:3, 3:1, 4:2, 6:4}[ctype]
    assert depth == 8, f"profondità {depth}"
    stride = w * nch
    out = bytearray(w * h * nch)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if f == 1:
            for i in range(nch, stride): line[i] = (line[i] + line[i-nch]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-nch] if i >= nch else 0
                b = prev[i]
                c = prev[i-nch] if i >= nch else 0
                pa, pb, pc = abs(b-c), abs(a-c), abs(a+b-2*c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y*stride:(y+1)*stride] = line
        prev = line
    return w, h, nch, out

# ---------- 2. classificazione mare/terra ----------
def classify(w, h, nch, px):
    # riferimenti: mare campionato a ovest dei Porti Grigi e a sud di Umbar
    def patch(x, y, r=3):
        cols = []
        for dy in range(-r, r+1):
            for dx in range(-r, r+1):
                i = ((y+dy)*w + (x+dx)) * nch
                cols.append((px[i], px[i+1], px[i+2]))
        cols.sort()
        return cols[len(cols)//2]
    sea_ref = patch(200, 324)   # mare a ovest del golfo di Lune
    sea2 = patch(560, 960)      # mare a sud-ovest di Umbar
    land_ref = patch(378, 276)  # terra presso Casa Baggins
    land2 = patch(1073, 636)    # terra presso l'Argonath
    sr = tuple((a+b)//2 for a, b in zip(sea_ref, sea2))
    lr = tuple((a+b)//2 for a, b in zip(land_ref, land2))
    print("rif mare:", sr, "rif terra:", lr)
    sea = bytearray(w*h)
    for i in range(w*h):
        j = i*nch
        r, g, b = px[j], px[j+1], px[j+2]
        ds = (r-sr[0])**2 + (g-sr[1])**2 + (b-sr[2])**2
        dl = (r-lr[0])**2 + (g-lr[1])**2 + (b-lr[2])**2
        sea[i] = 1 if ds < dl*0.9 else 0   # leggera preferenza per la terra
    # pulizia: filtro a maggioranza
    for _ in range(2):
        new = bytearray(sea)
        for y in range(1, h-1):
            base = y*w
            for x in range(1, w-1):
                i = base + x
                s = sea[i-w-1]+sea[i-w]+sea[i-w+1]+sea[i-1]+sea[i+1]+sea[i+w-1]+sea[i+w]+sea[i+w+1]
                new[i] = 1 if s > 4 else 0
        sea = new
    return sea

def components(mask, w, h, want_val):
    lab = [0]*(w*h); comps = []; cur = 0
    for start in range(w*h):
        if mask[start] == want_val and lab[start] == 0:
            cur += 1; size = 0; q = deque([start]); lab[start] = cur
            minx = maxx = start % w; miny = maxy = start // w; touches = False
            while q:
                i = q.popleft(); size += 1
                x, y = i % w, i // w
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
                if x == 0 or y == 0 or x == w-1 or y == h-1: touches = True
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny*w + nx
                        if mask[j] == want_val and lab[j] == 0:
                            lab[j] = cur; q.append(j)
            comps.append({"id": cur, "size": size, "bbox": (minx, miny, maxx, maxy), "touches": touches, "label": lab})
    return comps, lab

def trace_boundary(lab, comp_id, w, h, want_val):
    # Moore-neighbor tracing con criterio di arresto di Jacob
    start = None
    for i in range(w*h):
        if lab[i] == comp_id:
            start = i; break
    if start is None: return []
    dirs = [(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1)]
    def val(x, y):
        if x < 0 or y < 0 or x >= w or y >= h: return 0
        return 1 if lab[y*w+x] == comp_id else 0
    sx, sy = start % w, start // w
    bx, by = sx-1, sy                    # backtrack: pixel a ovest (sfondo per costruzione)
    first_back = (bx, by)
    contour = []
    cx, cy = sx, sy
    for _ in range(6*(w+h)):
        contour.append((cx, cy))
        dback = None
        for k in range(8):
            if (cx+dirs[k][0], cy+dirs[k][1]) == (bx, by):
                dback = k; break
        if dback is None: dback = 0
        moved = False
        for k in range(1, 9):
            d = (dback + k) % 8
            nx, ny = cx + dirs[d][0], cy + dirs[d][1]
            if val(nx, ny) == 1:
                pd = (dback + k - 1) % 8
                bx, by = cx + dirs[pd][0], cy + dirs[pd][1]
                cx, cy = nx, ny
                moved = True
                break
        if not moved: break
        if (cx, cy) == (sx, sy) and (bx, by) == first_back:
            break
    return contour

def rdp(pts, eps):
    if len(pts) < 3: return pts
    def d(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx-ax, by-ay
        L = math.hypot(dx, dy) or 1
        return abs(dy*px - dx*py + bx*ay - by*ax) / L
    a, b = pts[0], pts[-1]
    im, idm = -1, 0
    for i in range(1, len(pts)-1):
        dd = d(pts[i], a, b)
        if dd > idm: idm, im = dd, i
    if idm > eps:
        left = rdp(pts[:im+1], eps); right = rdp(pts[im:], eps)
        return left[:-1] + right
    return [a, b]

# ---------- 3. raddrizzamento TPS ----------
def tps_fit(ctrl):
    n = len(ctrl)
    def U(a, b):
        r2 = (a[0]-b[0])**2 + (a[1]-b[1])**2
        return 0 if r2 == 0 else r2 * math.log(r2)
    L = [[0.0]*(n+3) for _ in range(n+3)]
    for i in range(n):
        for j in range(n):
            L[i][j] = U(ctrl[i][:2], ctrl[j][:2])
        L[i][n], L[i][n+1], L[i][n+2] = 1, ctrl[i][0], ctrl[i][1]
        L[n][i], L[n+1][i], L[n+2][i] = 1, ctrl[i][0], ctrl[i][1]
    for r in (n, n+1, n+2):
        for c in (n, n+1, n+2):
            L[r][c] = 0
    def solve(M, v):
        m = len(v)
        A = [row[:] + [vv] for row, vv in zip(M, v)]
        for c in range(m):
            piv = max(range(c, m), key=lambda r: abs(A[r][c]))
            A[c], A[piv] = A[piv], A[c]
            if abs(A[c][c]) < 1e-12: continue
            for r in range(m):
                if r != c and A[r][c] != 0:
                    f = A[r][c] / A[c][c]
                    for k in range(c, m+1):
                        A[r][k] -= f * A[c][k]
        return [A[i][m] / A[i][i] if abs(A[i][i]) > 1e-12 else 0 for i in range(m)]
    Wx = solve(L, [c[2] for c in ctrl] + [0, 0, 0])
    Wy = solve(L, [c[3] for c in ctrl] + [0, 0, 0])
    def warp(p):
        x, y = p
        u = Wx[n] + Wx[n+1]*x + Wx[n+2]*y
        v = Wy[n] + Wy[n+1]*x + Wy[n+2]*y
        for i in range(n):
            u += Wx[i] * U(p, ctrl[i][:2])
            v += Wy[i] * U(p, ctrl[i][:2])
        return [u, v]
    return warp

# punti di controllo: [px_pittura, py_pittura, miglia_x, miglia_y]
CTRL = [
 [756,552,0,10],[1066,600,130,25],[1144,516,235,22],[1380,532,388,5],[890,352,280,-192],
 [724,244,95,-112],[448,648,-240,45],[624,570,-160,-25],[710,596,-55,45],[960,584,105,20],
 [936,970,315,495],[1460,810,442,170],[1444,840,436,183],[1644,660,468,165],[1720,850,552,296],
 [1580,912,505,200],[1630,940,515,295],[1756,1010,548,335],[1360,1096,442,478],[1700,1170,528,565],
 [1490,1144,455,588],[1876,1284,770,780],[1912,1240,800,790],[2056,1264,856,808],[2084,1110,843,748],
 [2380,1256,920,858],[2550,1220,950,828],[2200,380,690,-150],[2230,426,700,-140],[1970,370,560,-95],
 [1430,200,415,-270],[1240,150,310,-345],[1514,1570,565,790],[1850,1476,833,855],[1760,1550,850,870],
 [1640,1600,735,925],[1180,1890,520,1120],[730,1550,330,715],[1410,1280,450,780],[1896,1304,775,782],
 [1336,1156,390,550]
]

def main():
    png = prepare()
    w, h, nch, px = decode_png(png)
    print(f"raster {w}x{h} canali {nch}")
    sea = classify(w, h, nch, px)
    land = bytearray(1-v for v in sea)
    # taglia i margini (cornici/vignettature della pittura)
    M = 18
    for y in range(h):
        for x in range(M): land[y*w+x] = 0
        for x in range(w-M, w): land[y*w+x] = 0
    for x in range(w):
        for y in range(M): land[y*w+x] = 0
        for y in range(h-M, h): land[y*w+x] = 0
    comps, lab = components(land, w, h, 1)
    comps.sort(key=lambda c: -c["size"])
    print("componenti terra:", [(c["size"], c["bbox"], c["touches"]) for c in comps[:8]])
    main_c = comps[0]
    coast_px = trace_boundary(lab, main_c["id"], w, h, 1)
    print("perimetro terraferma:", len(coast_px), "px")
    coast_px = rdp(coast_px, 2.2)
    print("dopo semplificazione:", len(coast_px))
    islands = []
    for c in comps[1:8]:
        if c["size"] > 150:
            b = trace_boundary(lab, c["id"], w, h, 1)
            if len(b) > 24:
                islands.append({"px_area": c["size"], "ring": rdp(b, 1.6)})
    # laghi: componenti di mare non toccanti i bordi
    scomps, slab = components(sea, w, h, 1)
    scomps.sort(key=lambda c: -c["size"])
    print("componenti mare:", [(c["size"], c["touches"]) for c in scomps[:8]])
    lakes = []
    for c in scomps:
        if not c["touches"] and c["size"] > 60 and len(lakes) < 12:
            b = trace_boundary(slab, c["id"], w, h, 1)
            if len(b) > 16:
                lakes.append({"px_area": c["size"], "ring": rdp(b, 1.4)})
    warp = tps_fit([[c[0]/(3072/w), c[1]/(2048/h)] + c[2:] for c in CTRL])  # controllo a scala ridotta
    # ATTENZIONE: i CTRL sono in coordinate pittura piena; le tracce a scala ridotta
    warp_full = tps_fit([[c[0], c[1]] + c[2:] for c in CTRL])
    def W(p):
        return warp_full([p[0]*(3072/w), p[1]*(2048/h)])
    coast = [W(p) for p in coast_px]
    for isl in islands: isl["ring"] = [W(p) for p in isl["ring"]]
    for lk in lakes: lk["ring"] = [W(p) for p in lk["ring"]]
    # marker di riferimento (per verifica e per i dati dei luoghi)
    mk = json.load(open(os.path.join(D, "markers.json")))
    marks = {k: {"title": v["title"], "mi": W(v["xy"])} for k, v in mk.items() if v.get("xy")}
    out = {"coast": coast, "islands": islands, "lakes": lakes, "markers": marks,
           "note": "Geografia derivata dalla mappa di mapmiddleearth.com (CC BY-NC 4.0), raddrizzata su griglia in miglia."}
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "bozze", "mappa-dati.json"), "w"))
    print("marker trasformati (esempi):")
    for k in ("bag-end", "minas-tirith", "erebor", "umbar", "grey-havens"):
        print(" ", k, [round(v, 1) for v in marks[k]["mi"]])
    print("costa:", len(coast), "punti; isole:", len(islands), "; laghi:", len(lakes))

if __name__ == "__main__":
    main()
