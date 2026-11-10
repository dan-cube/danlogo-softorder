"""R6 — mark R4-01 原生 + Hara palette + three quiet type variants."""
import math
from shapely import affinity
from shapely.ops import unary_union
from type5 import render, layout, to_d
import en6, cn5
from marks4 import genesis

MARK = genesis()
ORDER = ("su", "kei", "ma")

HARA = dict(shiro="#F5F3EE", kinari="#E9E4D8", ishi="#A7A196", koke="#6B7861", sumi="#2F2E2B", shu="#B8452F")
SWATCHES = [("白 Shiro", "#F5F3EE", "底色"), ("生成 Kinari", "#E9E4D8", "纸张 / 包装"), ("石 Ishi", "#A7A196", "辅助"),
            ("苔 Koke", "#6B7861", "图形"), ("墨 Sumi", "#2F2E2B", "文字"), ("朱 Shu", "#B8452F", "唯一的点")]

MODES = {   # text, cells, point, background
    "color": (HARA["sumi"], HARA["koke"], HARA["shu"], HARA["shiro"]),
    "kinari": (HARA["sumi"], HARA["koke"], HARA["shu"], HARA["kinari"]),
    "dark": (HARA["kinari"], HARA["kinari"], "#C8563F", HARA["sumi"]),
    "mono": (HARA["sumi"], HARA["sumi"], HARA["sumi"], None),
    "white": ("#FFFFFF", "#FFFFFF", "#FFFFFF", None),
}

_cache = {}


def W_of(V):
    return {"v": V["wv"], "h": V["wh"], "d": V["wd"], "c": V["wv"] * 0.86, "node": 1.2}


def en_geom(key):
    k = ("en", key)
    if k not in _cache:
        V = en6.VARIANTS[key]
        gl = []
        for ch in V["text"]:
            G = en6.glyph(ch, V)
            b, a = render(G, "neck", W_of(V))
            gl.append((b, a, G))
        body, acc, wid = layout(gl, V["track"], en6.KERN, V["text"])
        allg = unary_union([body] + ([acc] if acc is not None else []))
        _cache[k] = dict(body=body, acc=acc, width=wid, top=allg.bounds[1], bottom=allg.bounds[3], text=V["text"])
    return _cache[k]


def cn_geom(key, gap=None):
    k = ("cn", key, gap)
    if k not in _cache:
        V = en6.VARIANTS[key]
        M = dict(V["cnm"])
        g = M["gap"] if gap is None else gap
        parts, x = [], 0.0
        for ch in "亿触点":
            G = cn5.glyph(ch, M, "neck")
            b, _ = render(G, "neck", G["W"])
            parts.append(affinity.translate(b, x, 0))
            x += 100 + g
        _cache[k] = dict(body=unary_union(parts), width=x - g)
    return _cache[k]


def svg_doc(vb, inner, px, bg=None):
    h = px * vb[3] / vb[2]
    b = f'<rect x="{vb[0]:.2f}" y="{vb[1]:.2f}" width="{vb[2]:.2f}" height="{vb[3]:.2f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.2f} {vb[1]:.2f} {vb[2]:.2f} {vb[3]:.2f}" '
            f'width="{px:.0f}" height="{h:.0f}">{b}{inner}</svg>')


def mark_frag(cell, point, size=240.0):
    t = MARK.fit(size)
    return t.body_svg(cell) + f'<path d="{t.accent_d()}" fill="{point}"/>', t.bbox()


def place_mark(cell, point, x, y, h):
    frag, (x0, y0, x1, y1) = mark_frag(cell, point)
    k = h / (y1 - y0)
    return f'<g transform="translate({x - x0 * k:.2f} {y - y0 * k:.2f}) scale({k:.4f})">{frag}</g>', (x1 - x0) * k


def en_paths(key, x, y, text, point, k=1.0):
    E = en_geom(key)
    s = f'<path d="{to_d(E["body"], x, y, k)}" fill="{text}" fill-rule="evenodd"/>'
    if E["acc"] is not None:
        s += f'<path d="{to_d(E["acc"], x, y, k)}" fill="{point}"/>'
    return s


def cn_paths(key, x, y, k, text, gap=None):
    return f'<path d="{to_d(cn_geom(key, gap)["body"], x, y, k)}" fill="{text}" fill-rule="evenodd"/>'


def lockup(key, mode="color", bg=True, px=1600):
    """Mark | EN over CN."""
    text, cell, point, bgc = MODES[mode]
    V = en6.VARIANTS[key]
    E, C = en_geom(key), cn_geom(key)
    em = V["cn_em"]
    top = E["top"]
    base = 100.0 + (24.0 if "p" in V["text"] else 0.0)
    cn_top = base + (34.0 if key != "ma" else 44.0)
    Hb = cn_top + em - top
    mh = Hb * (1.0 if key != "ma" else 0.92)
    m, mw = place_mark(cell, point, 0, top + (Hb - mh) / 2, mh)
    tx = mw + Hb * (0.36 if key != "ma" else 0.44)
    k = em / 100
    inner = m + en_paths(key, tx, 0, text, point) + cn_paths(key, tx + 1, cn_top, k, text)
    Wd = tx + max(E["width"], C["width"] * k)
    return svg_doc((0, top, Wd, Hb), inner, px, bgc if bg else None)


def lockup_single(key, mode="color", bg=True, px=1800):
    """Mark  EN  ·  CN on one line (centred on the x-height / cap middle)."""
    text, cell, point, bgc = MODES[mode]
    V = en6.VARIANTS[key]
    E = en_geom(key)
    lower = V["text"].islower()
    mid = 100 - V["X"] / 2 if lower else 50.0
    mh = 150.0
    m, mw = place_mark(cell, point, 0, mid - mh / 2, mh)
    tx = mw + 56
    em = 96.0 if not lower else 86.0
    gap_cn = 70.0
    cx = tx + E["width"] + gap_cn
    k = em / 100
    inner = m + en_paths(key, tx, 0, text, point) + cn_paths(key, cx, mid - em / 2, k, text)
    Wd = cx + cn_geom(key)["width"] * k
    y0 = min(mid - mh / 2, E["top"])
    y1 = max(mid + mh / 2, E["bottom"])
    return svg_doc((0, y0, Wd, y1 - y0), inner, px, bgc if bg else None)


def lockup_stacked(key, mode="color", bg=True, px=1000):
    text, cell, point, bgc = MODES[mode]
    V = en6.VARIANTS[key]
    E = en_geom(key)
    mh = 210.0
    frag, (x0, y0, x1, y1) = mark_frag(cell, point)
    kk = mh / (y1 - y0)
    mw = (x1 - x0) * kk
    tw = max(E["width"], mw)
    m = f'<g transform="translate({(tw - mw) / 2 - x0 * kk:.2f} {-y0 * kk:.2f}) scale({kk:.4f})">{frag}</g>'
    ey = mh + 80 - E["top"]
    base = 100.0 + (24.0 if "p" in V["text"] else 0.0)
    em = V["cn_em"] * 0.82
    gap = max(V["cnm"]["gap"], 30.0)
    C = cn_geom(key, gap)
    k = em / 100
    cy = ey + base + 40
    inner = (m + en_paths(key, (tw - E["width"]) / 2, ey, text, point)
             + cn_paths(key, (tw - C["width"] * k) / 2, cy, k, text, gap))
    return svg_doc((0, 0, tw, cy + em), inner, px, bgc if bg else None)


def wordmark(key, which="en", mode="color", px=1400):
    text, cell, point, bgc = MODES[mode]
    if which == "en":
        E = en_geom(key)
        allg = E["body"].union(E["acc"]) if E["acc"] is not None else E["body"]
        x0, y0, x1, y1 = allg.bounds
        inner = en_paths(key, 0, 0, text, point)
    else:
        C = cn_geom(key)
        x0, y0, x1, y1 = C["body"].bounds
        inner = cn_paths(key, 0, 0, 1.0, text)
    return svg_doc((x0 - 2, y0 - 2, x1 - x0 + 4, y1 - y0 + 4), inner, px)


def mark_svg(mode="color", pad=0.0, px=600, bg=False):
    text, cell, point, bgc = MODES[mode]
    frag, (x0, y0, x1, y1) = mark_frag(cell, point)
    w, h = x1 - x0, y1 - y0
    p = max(w, h) * pad
    return svg_doc((x0 - p, y0 - p, w + 2 * p, h + 2 * p), frag, px, bgc if bg else None)
