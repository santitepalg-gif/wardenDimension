#!/usr/bin/env python3
"""Pulido 1.1 de la Dimension Warden.
 - texturas con mas detalle
 - capas que brillan (emisivas) solo donde tiene sentido (venas, savia, esporas, runas, cristales, hongos)
 - hongos 3D con 3 variantes x 4 rotaciones
 - arreglo de la generacion de hongos (etiqueta de bloques validos, sin musgo verde vanilla)
Es idempotente: se puede correr varias veces. Va DESPUES de los gen_*.py viejos."""
import numpy as np, random, os, json, math, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glowcap_shapes import VARIANTS, WEIGHTS, rot90

MOD = "warden_dimension"
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = f"{BASE}/src/main/resources"
A = f"{ROOT}/assets/{MOD}"
D = f"{ROOT}/data/{MOD}"
TEX = f"{A}/textures/block"
MD = f"{A}/models/block"
BS = f"{A}/blockstates"
JAVA = f"{BASE}/src/main/java/com/wardendimension"
T = lambda n: f"{MOD}:block/{n}"


def wj(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(json.dumps(o, indent=2))


# ----------------------------------------------------------------- utilidades
def vn(seed, s=4):
    r = np.random.RandomState(seed); g = r.rand(s, s)
    ys, xs = np.mgrid[0:16, 0:16] / 16.0 * s
    x0 = np.floor(xs).astype(int) % s; y0 = np.floor(ys).astype(int) % s
    x1 = (x0 + 1) % s; y1 = (y0 + 1) % s
    fx = xs - np.floor(xs); fy = ys - np.floor(ys)
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    return (g[y0, x0] * (1 - fx) + g[y0, x1] * fx) * (1 - fy) + (g[y1, x0] * (1 - fx) + g[y1, x1] * fx) * fy


def ramp(cols, t):
    t = np.clip(t, 0, 0.9999) * (len(cols) - 1); i = t.astype(int); f = (t - i)[..., None]
    c = np.array(cols, float)
    return c[i] * (1 - f) + c[np.minimum(i + 1, len(cols) - 1)] * f


def mix(*n):
    return sum(n) / len(n)


def rgba(rgb, a=None):
    out = np.zeros((16, 16, 4), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255)
    out[..., 3] = 255 if a is None else a
    return out


def glow_layer(rgb, mask):
    """capa emisiva: solo los pixeles de la mascara, con el mismo color que la textura base"""
    out = np.zeros((16, 16, 4), np.uint8)
    out[mask, :3] = np.clip(rgb[mask], 0, 255)
    out[mask, 3] = 255
    return out


def save(name, arr):
    os.makedirs(TEX, exist_ok=True)
    Image.fromarray(np.asarray(arr, np.uint8), "RGBA").save(f"{TEX}/{name}.png")


STONE = [(6, 14, 24), (12, 28, 42), (20, 46, 64), (32, 70, 92), (46, 96, 120)]
CY = [(8, 70, 90), (14, 120, 140), (22, 178, 200), (70, 226, 240), (170, 250, 255)]
VI = [(24, 12, 60), (52, 28, 108), (86, 52, 170), (140, 100, 235), (214, 180, 255)]
GC = [(8, 60, 92), (16, 120, 160), (34, 190, 220), (120, 236, 250), (210, 255, 255)]  # sombrero del hongo


def cracks(rgb, seed, n=3, col=(4, 10, 18)):
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.randint(0, 15), r.randint(0, 15)
        for _ in range(r.randint(4, 8)):
            rgb[y % 16, x % 16] = col; x += r.choice((-1, 0, 1, 1)); y += r.choice((0, 1, 1))
    return rgb


# ----------------------------------------------------------------- piedra sculk
def stone_base(seed):
    rs = np.random.RandomState(seed)
    n = mix(vn(seed, 4), vn(seed + 1, 8))
    rgb = ramp(STONE, n * 0.85 + rs.rand(16, 16) * 0.16)
    for y in (rs.randint(2, 5), rs.randint(8, 11), rs.randint(12, 15)):  # estratos finos
        for x in range(16):
            if rs.rand() < 0.75: rgb[y, x] *= 0.9
    for _ in range(9): rgb[rs.randint(16), rs.randint(16)] = STONE[4]  # motas claras
    return rgb


def veins(rgb, seed, n=2):
    r = random.Random(seed); mask = np.zeros((16, 16), bool)
    for _ in range(n):
        x, y = r.randint(0, 15), r.randint(0, 15)
        for _ in range(r.randint(5, 8)):
            mask[y % 16, x % 16] = True
            if r.random() < 0.3: mask[y % 16, (x + r.choice((-1, 1))) % 16] = True
            x += r.choice((-1, 0, 1, 1)); y += r.choice((0, 1, 1))
    halo = np.zeros((16, 16), bool)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        halo |= np.roll(np.roll(mask, dy, 0), dx, 1)
    halo &= ~mask
    rgb[halo] = rgb[halo] * 0.55 + np.array(CY[0]) * 0.45  # borde tenue, no brilla
    ys, xs = np.nonzero(mask)
    for i, (y, x) in enumerate(zip(ys, xs)):
        rgb[y, x] = CY[3] if i % 3 == 0 else CY[2]
    rgb[ys[-1], xs[-1]] = CY[4]
    return rgb, mask


TX = {}   # texturas normales
GL = {}   # capas emisivas (<nombre>_glow)

rgb = stone_base(1); rgb = cracks(rgb, 11, 3); rgb, m = veins(rgb, 12, 2)
TX["sculk_stone"] = rgb; GL["sculk_stone"] = glow_layer(rgb, m)


# ----------------------------------------------------------------- musgo eco y sculk crepuscular
def moss_top(pal, seed):
    rs = np.random.RandomState(seed)
    n = mix(vn(seed, 4), vn(seed + 1, 8), rs.rand(16, 16) * 0.6)
    rgb = ramp(pal, n * 0.85 + 0.05); r = random.Random(seed)
    for _ in range(5):  # mechones
        x, y = r.randint(0, 15), r.randint(0, 15)
        rgb[y, x] = pal[3]; rgb[(y + 1) % 16, x] = pal[1]; rgb[y, (x + 1) % 16] = pal[2]
    for _ in range(14): rgb[r.randint(0, 15), r.randint(0, 15)] = pal[3]
    for _ in range(4): rgb[r.randint(0, 15), r.randint(0, 15)] = pal[4]
    return rgb


def moss_side(pal, seed, stone_seed, crack_seed):
    rgb = stone_base(stone_seed); rgb = cracks(rgb, crack_seed, 2); r = random.Random(seed)
    for x in range(16):
        hgt = 4 + r.randint(0, 2) + (1 if x % 5 == 2 else 0)
        for y in range(hgt):
            c = pal[2] if y < hgt - 2 else pal[1] if y < hgt - 1 else pal[0]
            rgb[y, x] = np.array(c) * (0.85 + 0.3 * r.random())
        if r.random() < 0.35: rgb[hgt, x] = pal[0]
        if x % 6 == 1:  # hebras que cuelgan
            for k in (2, 3): rgb[hgt - 1 + k, x] = pal[1] if k == 2 else pal[0]
    for _ in range(3): rgb[r.randint(0, 3), r.randint(0, 15)] = pal[3]
    return rgb


TX["echo_moss_top"] = moss_top(CY, 2)
TX["echo_moss_side"] = moss_side(CY, 6, 5, 13)
TX["twilight_sculk_top"] = moss_top(VI, 7)
TX["twilight_sculk_side"] = moss_side(VI, 9, 10, 14)


# ----------------------------------------------------------------- ladrillos
def bricks():
    rs = np.random.RandomState(15); rgb = np.zeros((16, 16, 3)); MORT = np.array((4, 10, 18))
    for row in range(4):
        off = 4 if row % 2 else 0
        for y in range(4):
            for x in range(16):
                bx = (x - off) % 8
                if y == 0 or bx == 0:
                    c = MORT.astype(float)
                else:
                    c = np.array(STONE[2]) * (0.85 + 0.3 * rs.rand())
                    if y == 1 or bx == 1: c = np.maximum(c, np.array(STONE[3]))
                    if y == 3: c = np.array(STONE[1]) * (0.9 + 0.2 * rs.rand())
                rgb[row * 4 + y, x] = c
    for _ in range(7):
        ry, rx = rs.randint(16), rs.randint(16)
        if rgb[ry, rx].sum() > 90: rgb[ry, rx] *= 0.78
    rgb = cracks(rgb, 16, 1)  # una grieta chica
    return rgb


TX["sculk_bricks"] = bricks()


# ----------------------------------------------------------------- tronco resonante
def log_side(seed=17):
    r = np.random.RandomState(seed); rgb = np.zeros((16, 16, 3))
    cols = [(12, 34, 50), (18, 48, 68), (26, 66, 90), (16, 42, 60)]
    for x in range(16):
        for y in range(16):
            rgb[y, x] = np.array(cols[x % 4]) * (0.82 + 0.3 * r.rand())
    for x in range(0, 16, 4):  # grietas de la corteza
        y = r.randint(0, 15)
        for k in range(r.randint(3, 6)):
            rgb[(y + k) % 16, x] = (5, 14, 22)
    for (kx, ky) in ((5, 4), (12, 11)):  # nudos
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            rgb[(ky + dy) % 16, (kx + dx) % 16] = (6, 16, 26)
        rgb[(ky - 1) % 16, kx % 16] = (30, 74, 98)
    mask = np.zeros((16, 16), bool)
    for bx, ph in ((2, 0.0), (10, 2.1)):  # savia luminosa que baja por la corteza
        for y in range(16):
            if (y + int(ph * 3)) % 6 == 5: continue  # cortes: queda punteada
            x = bx + int(round(math.sin(y * 0.5 + ph)))
            mask[y, x % 16] = True
    halo = np.zeros((16, 16), bool)
    for dx in (-1, 1): halo |= np.roll(mask, dx, 1)
    halo &= ~mask
    rgb[halo] = rgb[halo] * 0.6 + np.array(CY[0]) * 0.4
    ys, xs = np.nonzero(mask)
    for i, (y, x) in enumerate(zip(ys, xs)):
        rgb[y, x] = CY[3] if i % 5 == 0 else CY[2]
    return rgb, mask


rgb, m = log_side()
TX["resonant_log"] = rgb; GL["resonant_log"] = glow_layer(rgb, m)


# ----------------------------------------------------------------- hojas (celdas tipo hoja + esporas brillantes)
def voronoi(seed, n):
    r = np.random.RandomState(seed); pts = r.rand(n, 2) * 16
    ys, xs = np.mgrid[0:16, 0:16] + 0.5; ds = []
    for qx, qy in pts:
        dx = np.abs(xs - qx); dx = np.minimum(dx, 16 - dx)
        dy = np.abs(ys - qy); dy = np.minimum(dy, 16 - dy)
        ds.append(np.hypot(dx, dy))
    ds = np.sort(np.stack(ds), axis=0)
    return ds[0], ds[1]


def leaves(pal, seed):
    r = np.random.RandomState(seed); d1, d2 = voronoi(seed, 9); edge = d2 - d1
    t = 0.30 + 0.55 * np.clip(1 - d1 / 4.2, 0, 1) + (mix(vn(seed + 3, 4), vn(seed + 4, 8)) - 0.5) * 0.25
    rgb = ramp(pal, t)
    rgb[edge < 0.9] = np.array(pal[0]) * 0.9  # venas / bordes oscuros
    a = np.full((16, 16), 255, np.uint8)
    a[(edge < 0.55) & (r.rand(16, 16) < 0.6)] = 0  # huecos entre hojas
    mask = np.zeros((16, 16), bool)
    cand = np.argwhere((edge > 1.3) & (a == 255)); r.shuffle(cand)
    for y, x in cand[:7]:  # esporas brillantes aisladas
        rgb[y, x] = pal[4]; mask[y, x] = True
    out = rgba(rgb, a); lay = glow_layer(rgb, mask)
    return out, lay


TX["resonant_leaves"], GL["resonant_leaves"] = leaves(CY, 20)
TX["twilight_leaves"], GL["twilight_leaves"] = leaves(VI, 21)


# ----------------------------------------------------------------- cristal luminoso
def crystal():
    r = np.random.RandomState(22); rgb = np.zeros((16, 16, 3))
    for y in range(16):
        for x in range(16):
            f = ((x - y) // 4) % 3; d = max(abs(x - 7.5), abs(y - 7.5)) / 7.5
            base = np.array([CY[2], CY[3], CY[1]][f]) * (1.1 - 0.4 * d)
            if ((x + y) // 5) % 2: base = base * 0.93
            rgb[y, x] = base * (0.92 + 0.16 * r.rand())
    for i in range(16):
        for p in ((i, 0), (i, 15), (0, i), (15, i)): rgb[p[1], p[0]] = CY[0]
    for p in ((5, 5), (6, 6), (7, 7), (8, 8), (10, 4), (4, 10), (11, 11), (3, 6)): rgb[p[1], p[0]] = CY[4]
    inner = np.zeros((16, 16), bool); inner[1:15, 1:15] = True
    mask = (rgb.mean(axis=2) > 138) & inner  # brillan las facetas claras; las aristas oscuras no
    return rgb, mask


rgb, m = crystal()
TX["glow_crystal_block"] = rgb; GL["glow_crystal_block"] = glow_layer(rgb, m)


# ----------------------------------------------------------------- marco del warden (runa brillante)
def frame():
    r = np.random.RandomState(23); rgb = np.zeros((16, 16, 3)); mask = np.zeros((16, 16), bool)
    for y in range(16):
        for x in range(16):
            e = min(x, y, 15 - x, 15 - y)
            if e == 0: c = np.array(STONE[4])
            elif e == 1: c = np.array(STONE[2])
            elif e == 2: c = np.array((6, 12, 20))
            else: c = np.array((10, 22, 34)) * (0.8 + 0.4 * r.rand())
            rgb[y, x] = c
    for p in ((1, 1), (14, 1), (1, 14), (14, 14)):
        rgb[p[1], p[0]] = CY[3]; mask[p[1], p[0]] = True
    for p in ((7, 1), (8, 1), (7, 14), (8, 14), (1, 7), (1, 8), (14, 7), (14, 8)):
        rgb[p[1], p[0]] = CY[2]; mask[p[1], p[0]] = True
    rune = ["....##....", "...####...", "..##..##..", ".##.##.##.", "##.####.##", "##.####.##", ".##.##.##.", "..##..##..", "...####...", "....##...."]
    for j, row in enumerate(rune):
        for i, ch in enumerate(row):
            if ch == "#":
                rgb[3 + j, 3 + i] = CY[3] if (i + j) % 2 else CY[4]; mask[3 + j, 3 + i] = True
    return rgb, mask


rgb, m = frame()
TX["warden_frame"] = rgb; GL["warden_frame"] = glow_layer(rgb, m)


# ----------------------------------------------------------------- hebra colgante (se mece y es continua al apilarse)
def strand():
    im = np.zeros((16, 16, 4), np.uint8)

    def P(x, y, c): im[y % 16, x % 16] = list(map(int, c)) + [255]

    for y in range(16):
        x = 8 + int(round(math.sin(2 * math.pi * y / 16)))
        P(x, y, STONE[3] if y % 4 else CY[1])
    for ny in (3, 9, 13):  # nodos
        x = 8 + int(round(math.sin(2 * math.pi * ny / 16)))
        P(x, ny, CY[4]); P(x - 1, ny, CY[2]); P(x + 1, ny, CY[2])
    P(8 + int(round(math.sin(2 * math.pi * 6 / 16))) + 1, 6, CY[1])
    P(8 + int(round(math.sin(2 * math.pi * 11 / 16))) - 1, 11, CY[1])
    return im


TX_RAW = {"dangling_strand": strand()}


# ----------------------------------------------------------------- hongo luminoso (sombrero, laminillas, tallo, icono)
def cap_tex():
    rs = np.random.RandomState(40); n = mix(vn(40, 4), vn(41, 8), rs.rand(16, 16) * 0.5)
    rgb = ramp(GC, 0.25 + n * 0.6); dark = np.zeros((16, 16), bool)
    for (x, y) in ((3, 3), (11, 2), (7, 8), (13, 10), (2, 12), (9, 13)):  # manchas violeta
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            X, Y = (x + dx) % 16, (y + dy) % 16; rgb[Y, X] = VI[2]; dark[Y, X] = True
        rgb[y % 16, (x - 1) % 16] = GC[3]; rgb[(y - 1) % 16, x % 16] = GC[3]
    mask = (rgb.mean(axis=2) > 105) & ~dark
    return rgb, mask


def gills_tex():
    rs = np.random.RandomState(41); rgb = np.zeros((16, 16, 3)); mask = np.zeros((16, 16), bool)
    for y in range(16):
        for x in range(16):
            if x % 2 == 0 and rs.rand() < 0.85:
                rgb[y, x] = np.array(VI[2]) * (0.9 + 0.2 * rs.rand()); mask[y, x] = True
            else:
                rgb[y, x] = np.array(VI[0]) * (0.8 + 0.5 * rs.rand())
    return rgb, mask


def stem_tex():
    rs = np.random.RandomState(42); rgb = np.zeros((16, 16, 3))
    for y in range(16):
        for x in range(16):
            sh = [1.08, 1.0, 0.92, 0.86][x % 4]
            rgb[y, x] = np.array((118, 160, 184)) * sh * (0.94 + 0.12 * rs.rand())
    for y in (5, 6): rgb[y, :] *= 0.72  # anillo
    return rgb


def sprite():
    im = np.zeros((16, 16, 4), np.uint8)

    def P(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16: im[y, x] = list(map(int, c)) + [255]

    def mush(cx, base, sh, sw, rx, ry, spots):
        x0 = cx - sw // 2
        for y in range(base - sh + 1, base + 1):
            for xx in range(x0, x0 + sw):
                c = (196, 230, 240) if xx == x0 else (150, 196, 214)
                if sh > 3 and y == base - sh + 3: c = (104, 144, 170)
                P(xx, y, c)
        cy = base - sh; inside = set()
        for y in range(cy - ry, cy + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2 <= 1.0: inside.add((x, y))
        for (x, y) in inside:
            t = (y - (cy - ry)) / max(ry, 1)
            edge = any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, -1)))
            if y == cy: c = VI[1]
            elif edge: c = GC[1]
            elif t < 0.34: c = GC[3]
            elif t < 0.75: c = GC[2]
            else: c = GC[1]
            P(x, y, c)
        for (dx, dy, c) in spots: P(cx + dx, cy + dy, c)
        P(cx - rx + 1, cy - ry + 1, GC[4])

    mush(3, 15, 3, 1, 2, 2, [])
    mush(13, 15, 2, 1, 2, 2, [])
    mush(8, 15, 6, 2, 4, 3, [(-1, -1, VI[3]), (2, -2, VI[3]), (1, 0 - 1, GC[4])])
    return im


rgb, m = cap_tex(); TX["glowcap_cap"] = rgb; GL["glowcap_cap"] = glow_layer(rgb, m)
rgb, m = gills_tex(); TX["glowcap_gills"] = rgb; GL["glowcap_gills"] = glow_layer(rgb, m)
TX["glowcap_stem"] = stem_tex()
TX_RAW["glowcap"] = sprite()

# ----------------------------------------------------------------- guardar texturas
for k, v in TX.items():
    arr = v if v.ndim == 3 and v.shape[2] == 4 else rgba(v)
    save(k, arr)
for k, v in TX_RAW.items():
    save(k, v)
for k, v in GL.items():
    save(f"{k}_glow", v)
print("texturas:", len(TX) + len(TX_RAW), " capas de brillo:", len(GL))

# ----------------------------------------------------------------- modelos
DIRS = ["down", "up", "north", "south", "west", "east"]
SIDES = ["north", "south", "west", "east"]


def fb(light=15):
    return {"block_light": light, "sky_light": light, "ambient_occlusion": False}


def face(tex, d, glow=False, light=15):
    f = {"uv": [0, 0, 16, 16], "texture": "#" + tex, "cullface": d}
    if glow: f["forge_data"] = fb(light)
    return f


def cube_glow(name, textures, tex_for, glow_for, render="minecraft:cutout"):
    els = [{"from": [0, 0, 0], "to": [16, 16, 16], "faces": {d: face(tex_for[d], d) for d in DIRS}}]
    if glow_for:
        els.append({"from": [-0.01] * 3, "to": [16.01] * 3, "shade": False,
                    "faces": {d: face(glow_for[d], d, glow=True) for d in glow_for}})
    wj(f"{MD}/{name}.json", {"textures": textures, "render_type": render, "elements": els})


allf = lambda v: {d: v for d in DIRS}
sidef = lambda v: {d: v for d in SIDES}

cube_glow("sculk_stone", {"particle": T("sculk_stone"), "all": T("sculk_stone"), "glow": T("sculk_stone_glow")},
          allf("all"), allf("glow"))
cube_glow("glow_crystal_block", {"particle": T("glow_crystal_block"), "all": T("glow_crystal_block"), "glow": T("glow_crystal_block_glow")},
          allf("all"), allf("glow"))
cube_glow("warden_frame", {"particle": T("warden_frame"), "all": T("warden_frame"), "glow": T("warden_frame_glow")},
          allf("all"), allf("glow"))
cube_glow("resonant_leaves", {"particle": T("resonant_leaves"), "all": T("resonant_leaves"), "glow": T("resonant_leaves_glow")},
          allf("all"), allf("glow"), render="minecraft:cutout_mipped")
cube_glow("twilight_leaves", {"particle": T("twilight_leaves"), "all": T("twilight_leaves"), "glow": T("twilight_leaves_glow")},
          allf("all"), allf("glow"), render="minecraft:cutout_mipped")
log_tex = dict(allf("side")); log_tex["up"] = "end"; log_tex["down"] = "end"
cube_glow("resonant_log", {"particle": T("resonant_log"), "end": T("resonant_log_top"), "side": T("resonant_log"), "glow": T("resonant_log_glow")},
          log_tex, sidef("glow"))


def cross_model(name, tex, light):
    def plane(frm, to, faces):
        return {"from": frm, "to": to, "rotation": {"origin": [8, 8, 8], "axis": "y", "angle": 45, "rescale": True},
                "shade": False, "faces": {d: {"uv": [0, 0, 16, 16], "texture": "#cross", "forge_data": fb(light)} for d in faces}}
    wj(f"{MD}/{name}.json", {"ambient_occlusion": False, "textures": {"particle": T(tex), "cross": T(tex)}, "render_type": "minecraft:cutout",
                              "elements": [plane([0.8, 0, 8], [15.2, 16, 8], ("north", "south")),
                                           plane([8, 0, 0.8], [8, 16, 15.2], ("west", "east"))]})


cross_model("dangling_strand", "dangling_strand", 11)  # la hebra entera brilla suave (el bloque ya emite luz 7)

# portal: brilla entero
for ax in ("x", "z"):
    p = f"{MD}/warden_portal_{ax}.json"; d = json.load(open(p))
    for el in d["elements"]:
        for f in el["faces"].values(): f["forge_data"] = fb(15)
    wj(p, d)


# hongos: 3 variantes x 4 rotaciones, sombrero con capa emisiva
def box_el(lo, hi, side, top, bot, glow=False, pad=0.0):
    w, h, d = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]

    def f(tex, uv):
        o = {"uv": [round(u, 3) for u in uv], "texture": "#" + tex}
        if glow: o["forge_data"] = fb(15)
        return o

    faces = {"north": f(side, (0, 0, w, h)), "south": f(side, (0, 0, w, h)), "west": f(side, (0, 0, d, h)),
             "east": f(side, (0, 0, d, h)), "up": f(top, (0, 0, w, d)), "down": f(bot, (0, 0, w, d))}
    el = {"from": [round(v - pad, 3) for v in lo], "to": [round(v + pad, 3) for v in hi], "faces": faces}
    if glow: el["shade"] = False
    return el


for vn_, boxes in VARIANTS.items():
    els = []
    for kind, lo, hi in boxes:
        if kind == "stem": els.append(box_el(lo, hi, "stem", "stem", "stem"))
        else: els.append(box_el(lo, hi, "cap", "cap", "gills"))
    for kind, lo, hi in boxes:
        if kind == "cap": els.append(box_el(lo, hi, "capglow", "capglow", "gillglow", glow=True, pad=0.03))
    wj(f"{MD}/glowcap_{vn_}.json", {"ambient_occlusion": False, "render_type": "minecraft:cutout",
        "textures": {"particle": T("glowcap_cap"), "cap": T("glowcap_cap"), "stem": T("glowcap_stem"), "gills": T("glowcap_gills"),
                     "capglow": T("glowcap_cap_glow"), "gillglow": T("glowcap_gills_glow")}, "elements": els})

variants = []
for vn_, w in WEIGHTS.items():
    for y in (0, 90, 180, 270):
        v = {"model": f"{MOD}:block/glowcap_{vn_}", "weight": w}
        if y: v["y"] = y
        variants.append(v)
wj(f"{BS}/glowcap.json", {"variants": {"": variants}})
# el icono del item sigue siendo el sprite 2D (glowcap.png)
wj(f"{A}/models/item/glowcap.json", {"parent": "minecraft:item/generated", "textures": {"layer0": T("glowcap")}})
# modelo viejo en cruz ya no se usa
old = f"{MD}/glowcap.json"
if os.path.exists(old): os.remove(old)

# ----------------------------------------------------------------- datos: arreglo de la generacion de hongos
wj(f"{D}/tags/blocks/glowcap_placeable.json", {"replace": False, "values": [
    f"{MOD}:echo_moss_block", f"{MOD}:twilight_sculk", f"{MOD}:sculk_stone", f"{MOD}:sculk_bricks", "minecraft:sculk"]})


def patch(tries, spread):
    return {"type": "minecraft:random_patch", "config": {"tries": tries, "xz_spread": spread, "y_spread": 3, "feature": {
        "feature": {"type": "minecraft:simple_block", "config": {"to_place": {
            "type": "minecraft:simple_state_provider", "state": {"Name": f"{MOD}:glowcap"}}}},
        "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:all_of", "predicates": [
            {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
            {"type": "minecraft:matching_block_tag", "offset": [0, -1, 0], "tag": f"{MOD}:glowcap_placeable"}]}}]}}}


wj(f"{D}/worldgen/configured_feature/glowcap_patch.json", patch(64, 6))
wj(f"{D}/worldgen/configured_feature/glowcap_patch_sparse.json", patch(28, 5))
surf = [{"type": "minecraft:in_square"}, {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"}, {"type": "minecraft:biome"}]
cnt = lambda a, b: {"type": "minecraft:count", "count": {"type": "minecraft:uniform", "min_inclusive": a, "max_inclusive": b}}
wj(f"{D}/worldgen/placed_feature/glowcap_patch.json", {"feature": f"{MOD}:glowcap_patch", "placement": [cnt(2, 4)] + surf})
wj(f"{D}/worldgen/placed_feature/glowcap_patch_sparse.json", {"feature": f"{MOD}:glowcap_patch_sparse",
   "placement": [{"type": "minecraft:rarity_filter", "chance": 2}, cnt(1, 2)] + surf})

# los Paramos Abisales (sculk / deepslate) usan el parche escaso
p = f"{D}/worldgen/biome/abyssal_barrens.json"; b = json.load(open(p))
b["features"][9] = [f"{MOD}:glowcap_patch_sparse" if x == f"{MOD}:glowcap_patch" else x for x in b["features"][9]]
wj(p, b)

# ----------------------------------------------------------------- java: sobre que bloques crece + esporas
open(f"{JAVA}/GlowcapBlock.java", "w").write('''package com.wardendimension;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.BushBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public class GlowcapBlock extends BushBlock {
    // Mismo conjunto que usa el worldgen (data/warden_dimension/tags/blocks/glowcap_placeable.json)
    public static final TagKey<Block> PLACEABLE_ON =
            TagKey.create(Registries.BLOCK, new ResourceLocation(WardenDimension.MODID, "glowcap_placeable"));
    private static final VoxelShape SHAPE = Block.box(2, 0, 2, 14, 12, 14);

    public GlowcapBlock(Properties props) { super(props); }

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter getter, BlockPos pos) {
        return state.is(PLACEABLE_ON);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter getter, BlockPos pos, CollisionContext ctx) { return SHAPE; }

    // esporas que flotan de vez en cuando
    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(12) == 0) {
            double x = pos.getX() + 0.5 + (random.nextDouble() - 0.5) * 0.6;
            double y = pos.getY() + 0.6 + random.nextDouble() * 0.5;
            double z = pos.getZ() + 0.5 + (random.nextDouble() - 0.5) * 0.6;
            level.addParticle(ParticleTypes.GLOW, x, y, z, 0.0, 0.02, 0.0);
        }
    }
}
''')
print("modelos, datos y java listos")
