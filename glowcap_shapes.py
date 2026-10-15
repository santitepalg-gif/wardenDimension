"""Formas 3D de los hongos luminosos (unidades de 1/16 de bloque).
Las usan gen_polish.py (modelos JSON) y render3.py (vista previa)."""


def mushroom(cx, cz, stem_h, stem_w, cap_w, cap_t):
    hs = stem_w / 2.0
    hc = cap_w / 2.0
    cr = cap_w * 0.35
    return [
        ("stem", (cx - hs, 0, cz - hs), (cx + hs, stem_h, cz + hs)),
        ("cap", (cx - hc, stem_h - 0.5, cz - hc), (cx + hc, stem_h + cap_t, cz + hc)),
        ("cap", (cx - cr, stem_h + cap_t, cz - cr), (cx + cr, stem_h + cap_t + 1.5, cz + cr)),
    ]


VARIANTS = {
    # a: un hongo alto y solitario
    "a": mushroom(8, 8, 7, 3, 10, 3),
    # b: uno mediano con uno pequeño al lado
    "b": mushroom(5.5, 6, 5, 2.5, 7, 2.5) + mushroom(11.5, 10.5, 3, 2, 4.5, 2),
    # c: grupito de tres
    "c": mushroom(8, 8, 6, 2.5, 8, 2.5) + mushroom(3.5, 12.5, 3, 2, 5, 2) + mushroom(12.5, 4, 2.5, 1.5, 3.5, 1.5),
}

# peso de cada variante en el blockstate (por cada una de las 4 rotaciones)
WEIGHTS = {"a": 3, "b": 2, "c": 1}


def rot90(boxes, k):
    out = []
    for kind, lo, hi in boxes:
        for _ in range(k):
            lo, hi = (16 - hi[2], lo[1], lo[0]), (16 - lo[2], hi[1], hi[0])
        out.append((kind, lo, hi))
    return out
