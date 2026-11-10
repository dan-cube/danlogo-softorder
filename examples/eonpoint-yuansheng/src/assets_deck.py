#!/usr/bin/env python3
"""Every image the pitch deck needs -> ../_deck/*.svg (+ .png via SVG2PNG)."""
import math, os, re, subprocess, sys
from shapely.geometry import Point
from lockup6 import *
from poster6 import card, app_icon, squircle
from marks4 import original
from geo import length, sub, add, mul, unit
from cells import gap as cgap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "提案素材_deck_assets")
SVG2PNG = os.environ.get("SVG2PNG")
C = HARA
TXT2 = "#6E6A62"
WOOD = "#C9B79C"
KRAFT = "#CDB592"


# ───────────────────────────── helpers ─────────────────────────────

def inner_of(svg):
    vb = [float(v) for v in svg.split('viewBox="')[1].split('"')[0].split()]
    body = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    return vb, body


def place(svg, x, y, w=None, h=None, anchor="tl"):
    """Embed a generated svg document scaled to width w (or height h)."""
    (vx, vy, vw, vh), body = inner_of(svg)
    k = (w / vw) if w is not None else (h / vh)
    W, H = vw * k, vh * k
    if anchor == "c":
        x, y = x - W / 2, y - H / 2
    elif anchor == "cx":
        x = x - W / 2
    return f'<g transform="translate({x - vx * k:.2f} {y - vy * k:.2f}) scale({k:.5f})">{body}</g>', W, H


def mark_g(cx, cy, size, cell=None, point=None):
    cell = cell or C["koke"]
    point = point or C["shu"]
    frag, (x0, y0, x1, y1) = mark_frag(cell, point)
    k = size / max(x1 - x0, y1 - y0)
    return f'<g transform="translate({cx - (x0 + x1) / 2 * k:.2f} {cy - (y0 + y1) / 2 * k:.2f}) scale({k:.5f})">{frag}</g>'


def shadow(x, y, w, h, r=6, a=0.035, n=9, dy=10):
    s = ""
    for i in range(n, 0, -1):
        g = i * 2.2
        s += (f'<rect x="{x - g:.1f}" y="{y - g + dy * i / n:.1f}" width="{w + 2 * g:.1f}" height="{h + 2 * g:.1f}" '
              f'rx="{r + g:.1f}" fill="#2F2E2B" opacity="{a:.3f}"/>')
    return s


def doc(w, h, inner, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{b}{inner}</svg>'


def T(x, y, s, size=20, col=None, anchor="start", weight=400, ls=0, fam="PingFang SC, Helvetica Neue, sans-serif"):
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" letter-spacing="{ls}" '
            f'text-anchor="{anchor}" fill="{col or C["sumi"]}">{s}</text>')


def bar(x, y, w, h=3, col=None, op=0.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{col or C["ishi"]}" opacity="{op}"/>'


F = {}


def asset(name, w=None):
    def deco(fn):
        F[name] = (fn, w)
        return fn
    return deco


# ───────────────────────────── logo assets ─────────────────────────────

@asset("lockup", 2400)
def _():
    return lockup("su", "color", bg=False)


@asset("lockup-single", 2600)
def _():
    return lockup_single("su", "color", bg=False)


@asset("lockup-stacked", 1400)
def _():
    return lockup_stacked("su", "color", bg=False)


@asset("wordmark-en", 2200)
def _():
    return wordmark("su", "en")


@asset("wordmark-cn", 1600)
def _():
    return wordmark("su", "cn")


for _bg, _mode, _nm in (("shiro", "color", "lock-shiro"), ("kinari", "kinari", "lock-kinari"),
                        ("sumi", "dark", "lock-sumi"), ("koke", "white", "lock-koke"), ("white", "mono", "lock-mono")):
    def _mk(bg=_bg, mode=_mode):
        col = {"shiro": C["shiro"], "kinari": C["kinari"], "sumi": C["sumi"], "koke": C["koke"], "white": "#FFFFFF"}[bg]
        g, W, H = place(lockup("su", mode, bg=False), 600, 400, w=760, anchor="c")
        return doc(1200, 800, g, col)
    F[_nm] = (_mk, 1200)


def mark_tile(bg, cell, point, size=1200):
    return doc(size, size, mark_g(size / 2, size / 2, size * 0.56, cell, point), bg)


F["mark-shiro"] = (lambda: mark_tile(C["shiro"], C["koke"], C["shu"]), 1200)
F["mark-kinari"] = (lambda: mark_tile(C["kinari"], C["koke"], C["shu"]), 1000)
F["mark-sumi"] = (lambda: mark_tile(C["sumi"], C["kinari"], "#C8563F"), 1000)
F["mark-koke"] = (lambda: mark_tile(C["koke"], C["kinari"], "#C8563F"), 1000)

COLORWAYS = [("standard", C["shiro"], C["koke"], C["shu"]), ("sumi", C["shiro"], C["sumi"], C["shu"]),
             ("mono", C["shiro"], C["sumi"], C["sumi"]), ("reverse", C["koke"], C["kinari"], "#C8563F"),
             ("night", C["sumi"], C["kinari"], "#C8563F"), ("shu", C["shu"], C["shiro"], C["shiro"])]
for _n, _bg, _c, _p in COLORWAYS:
    F[f"cw-{_n}"] = ((lambda bg=_bg, c=_c, p=_p: mark_tile(bg, c, p, 800)), 800)

for _k in ORDER:
    F[f"var-{_k}"] = ((lambda k=_k: lockup(k, "color", bg=False)), 1800)

F["icon-kinari"] = (lambda: app_icon("kinari"), 800)
F["icon-koke"] = (lambda: app_icon("koke"), 800)
F["icon-sumi"] = (lambda: app_icon("sumi"), 800)


@asset("avatar", 800)
def _():
    return doc(512, 512, f'<circle cx="256" cy="256" r="256" fill="{C["koke"]}"/>' + mark_g(256, 262, 290, C["kinari"], "#C8563F"))


@asset("favicon", 600)
def _():
    s = ""
    x = 20
    for px in (64, 32, 16):
        k = px / 64
        s += (f'<g transform="translate({x} {80 - px / 2}) scale({k})"><rect width="64" height="64" rx="14" fill="{C["koke"]}"/>'
              f'{mark_g(32, 33, 44, C["kinari"], "#C8563F")}</g>')
        x += px + 40
    return doc(260, 160, s)


# ───────────────────────────── concept diagrams ─────────────────────────────

@asset("hidden-order", 1800)
def _():
    t = MARK.fit(240.0)
    x0, y0, x1, y1 = t.bbox()
    pad = 34
    vb = (x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad)
    O = t.center
    A, B, Cc, D, E = [c for c, _ in t.cells]
    P1, P2, pr = t.capsules[0][:3]
    Pm = mul(add(P1, P2), 0.5)
    Ro = sum(length(sub(p, O)) for p in (A, Cc, E)) / 3
    Ri = sum(length(sub(p, O)) for p in (B, D, Pm)) / 3
    g = [f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{C["shiro"]}"/>',
         f'<g opacity="0.22">{t.body_svg(C["koke"])}<path d="{t.accent_d()}" fill="{C["shu"]}"/></g>',
         f'<circle cx="{O[0]:.2f}" cy="{O[1]:.2f}" r="{Ro:.2f}" fill="none" stroke="{C["ishi"]}" stroke-width="0.7" stroke-dasharray="3 3"/>',
         f'<circle cx="{O[0]:.2f}" cy="{O[1]:.2f}" r="{Ri:.2f}" fill="none" stroke="{C["ishi"]}" stroke-width="0.7" stroke-dasharray="1.2 2.4"/>']
    for p in (A, Cc, E):
        q = add(O, mul(unit(sub(p, O)), Ro + 16))
        g.append(f'<line x1="{O[0]:.2f}" y1="{O[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" stroke="{C["ishi"]}" stroke-width="0.6"/>')
    for a, b in ((A, B), (Cc, D), (E, Pm)):
        u = unit(sub(b, a))
        tip = add(b, mul(u, -3))
        nrm = (-u[1], u[0])
        h1 = add(tip, add(mul(u, -6), mul(nrm, 3)))
        h2 = add(tip, add(mul(u, -6), mul(nrm, -3)))
        g.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{tip[0]:.2f}" y2="{tip[1]:.2f}" stroke="{C["shu"]}" stroke-width="1"/>'
                 f'<path d="M{h1[0]:.2f} {h1[1]:.2f}L{tip[0]:.2f} {tip[1]:.2f}L{h2[0]:.2f} {h2[1]:.2f}" fill="none" stroke="{C["shu"]}" stroke-width="1"/>')
    for (c, r) in t.cells:
        g.append(f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="{r:.2f}" fill="none" stroke="{C["sumi"]}" stroke-width="0.7"/>'
                 f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="1.3" fill="{C["sumi"]}"/>')
    g.append(f'<circle cx="{O[0]:.2f}" cy="{O[1]:.2f}" r="2" fill="{C["sumi"]}"/>')
    for a, b in ((A, Cc), (Cc, E), (E, A)):
        mid = unit(add(unit(sub(a, O)), unit(sub(b, O))))
        q = add(O, mul(mid, 24))
        g.append(f'<text x="{q[0]:.2f}" y="{q[1] + 3:.2f}" text-anchor="middle" font-size="8" font-family="Helvetica" fill="{TXT2}">120°</text>')
    k = 1800 / vb[2]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.2f} {vb[1]:.2f} {vb[2]:.2f} {vb[3]:.2f}" '
            f'width="1800" height="{vb[3] * k:.0f}">{"".join(g)}</svg>')


@asset("rhythm", 1800)
def _():
    t = MARK.fit(240.0)
    x0, y0, x1, y1 = t.bbox()
    pad = 30
    vb = (x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad)
    A, B, Cc, D, E = t.cells
    P1, P2, pr = t.capsules[0][:3]
    g = [f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{C["kinari"]}"/>',
         t.body_svg(C["koke"]), f'<path d="{t.accent_d()}" fill="{C["shu"]}"/>']
    pairs = [(A, (P2, pr), C["sumi"]), (D, E, C["sumi"]), ((P1, pr), E, C["sumi"]), (B, Cc, C["shu"])]
    for u_, v_, col in pairs:
        d = unit(sub(v_[0], u_[0]))
        a = add(u_[0], mul(d, u_[1]))
        b = add(v_[0], mul(d, -v_[1]))
        g.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/>')
    # capsule = circle (area): ghost circle of equal area beside the capsule
    k = 1800 / vb[2]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.2f} {vb[1]:.2f} {vb[2]:.2f} {vb[3]:.2f}" '
            f'width="1800" height="{vb[3] * k:.0f}">{"".join(g)}</svg>')


@asset("cycle", 2600)
def _():
    """① rest → ② stretch → ③ pinch → ④ split → the point — drawn with the mark's own parts."""
    from cells import Cluster
    W, H = 2600, 760
    t = MARK.fit(240.0)
    A, B, Cc, D, E = t.cells
    P1, P2, pr, waist = t.capsules[0]

    def stage(parts, cx, cy, k):
        return f'<g transform="translate({cx:.1f} {cy:.1f}) scale({k:.3f})">{parts}</g>'
    out = []
    xs = [260, 820, 1380, 1940, 2400]
    cy = 330
    kk = 3.4
    # ① single cell
    out.append(stage(f'<circle cx="0" cy="0" r="{E[1]:.2f}" fill="{C["koke"]}"/>', xs[0], cy, kk))
    # ② capsule (horizontal)
    L = length(sub(P2, P1))
    cap = Cluster([], [], [((-L / 2, 0), (L / 2, 0), pr)], None).body_svg(C["koke"])
    out.append(stage(cap, xs[1], cy, kk))
    # ③ A–B pair (pinching) and ④ C–D pair (about to split), laid flat
    for (p, q), x in (((A, B), xs[2]), ((Cc, D), xs[3])):
        dd = length(sub(q[0], p[0]))
        cl = Cluster([((-dd / 2, 0), p[1]), ((dd / 2, 0), q[1])], [], [], None)
        i = (A, B, Cc, D).index(p)
        hw = min(p[1], q[1]) * (0.52 if i == 0 else 0.20)     # ③ still thick · ④ nearly apart
        cl.bridges = [(0, 1, hw, hw)]
        out.append(stage(cl.body_svg(C["koke"]), x, cy, kk * 0.82))
    # the point
    out.append(stage(f'<circle cx="0" cy="0" r="{t.accent[1]:.2f}" fill="{C["shu"]}"/>', xs[4], cy, kk))
    for a, b in zip(xs, xs[1:]):
        x = (a + b) / 2 + (20 if a == xs[3] else 0)
        out.append(f'<path d="M{x - 26} {cy}H{x + 22}M{x + 10} {cy - 11}L{x + 24} {cy}L{x + 10} {cy + 11}" fill="none" stroke="{C["ishi"]}" stroke-width="3"/>')
    labels = ["① 静止", "② 拉长", "③ 缢缩", "④ 分裂", "新的触点"]
    for x, s in zip(xs, labels):
        out.append(T(x, 640, s, 40, C["sumi"] if s != "新的触点" else C["shu"], "middle", 400, 4))
    return doc(W, H, "".join(out))


# ───────────────────────────── type details ─────────────────────────────

def _glyph_geom(ch):
    V = en6.VARIANTS["su"]
    G = en6.glyph(ch, V)
    b, a = render(G, "neck", W_of(V))
    return V, G, b, a


@asset("type-counters", 1400)
def _():
    from type5 import to_d
    out = []
    x = 30
    for ch in ("o", "P", "p"):
        V, G, b, a = _glyph_geom(ch)
        out.append(f'<path d="{to_d(b, x, 20)}" fill="{C["sumi"]}" fill-rule="evenodd"/>')
        if ch in "op":
            R = V["X"] / 2 + V["ov"]
            out.append(f'<circle cx="{x + R:.1f}" cy="{20 + 100 - V["X"] / 2:.1f}" r="{R:.1f}" fill="none" stroke="{C["shu"]}" stroke-width="0.8" stroke-dasharray="2 2"/>')
        else:
            Bh = 55.0
            Rx = Bh / 2 + 0.5
            xb = 53 - Rx
            out.append(f'<circle cx="{x + xb:.1f}" cy="{20 + Bh / 2:.1f}" r="{Bh / 2:.1f}" fill="none" stroke="{C["shu"]}" stroke-width="0.8" stroke-dasharray="2 2"/>')
        x += G["width"] + 30
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x} 160" width="1400" height="{160 * 1400 / x:.0f}"><rect width="{x}" height="160" fill="{C["shiro"]}"/>{"".join(out)}</svg>'


@asset("type-optical", 1400)
def _():
    from type5 import to_d
    V, G, b, a = _glyph_geom("n")
    _, GE, bE, _ = _glyph_geom("E")
    xt = 100 - V["X"]
    out = [f'<path d="{to_d(bE, 20, 10)}" fill="{C["sumi"]}" fill-rule="evenodd"/>',
           f'<path d="{to_d(b, 110, 10)}" fill="{C["sumi"]}" fill-rule="evenodd"/>']
    # measurement ticks: vertical stem vs horizontal arm
    wv, wh = V["wv"], V["wh"]
    out.append(f'<line x1="20" y1="{10 + 100 + 8}" x2="{20 + wv}" y2="{10 + 100 + 8}" stroke="{C["shu"]}" stroke-width="1.2"/>')
    out.append(f'<line x1="{20 + 52}" y1="10" x2="{20 + 52}" y2="{10 + wh}" stroke="{C["shu"]}" stroke-width="1.2"/>')
    out.append(f'<circle cx="{110 + wv + 3}" cy="{10 + xt + 9}" r="7" fill="none" stroke="{C["shu"]}" stroke-width="0.8" stroke-dasharray="1.6 1.6"/>')
    W = 200
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 135" width="1400" height="{135 * 1400 / W:.0f}"><rect width="{W}" height="135" fill="{C["shiro"]}"/>{"".join(out)}</svg>'


@asset("type-dots", 1400)
def _():
    from type5 import to_d
    V, G, b, a = _glyph_geom("i")
    Cg = cn5.glyph("点", dict(V["cnm"]), "neck")
    bc, _ = render(Cg, "neck", Cg["W"])
    out = [f'<path d="{to_d(b, 20, 0)}" fill="{C["sumi"]}"/>', f'<path d="{to_d(a, 20, 0)}" fill="{C["shu"]}"/>',
           f'<path d="{to_d(bc, 70, 4, 0.96)}" fill="{C["sumi"]}" fill-rule="evenodd"/>',
           mark_g(250, 52, 92)]
    W = 310
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -12 {W} 124" width="1400" height="{124 * 1400 / W:.0f}"><rect y="-12" width="{W}" height="124" fill="{C["shiro"]}"/>{"".join(out)}</svg>'


# ───────────────────────────── system specs ─────────────────────────────

@asset("clearspace", 2000)
def _():
    s = lockup("su", "color", bg=False)
    (vx, vy, vw, vh), body = inner_of(s)
    # x = diameter of the 朱 point inside the lockup
    t = MARK.fit(240.0)
    bx0, by0, bx1, by1 = t.bbox()
    mh = vh  # mark is placed at the block height
    km = mh / (by1 - by0)
    x = t.accent[1] * 2 * km
    pad = x * 1.6
    W, H = vw + 2 * pad, vh + 2 * pad
    g = [f'<rect width="{W:.1f}" height="{H:.1f}" fill="{C["shiro"]}"/>',
         f'<rect x="{pad - x:.1f}" y="{pad - x:.1f}" width="{vw + 2 * x:.1f}" height="{vh + 2 * x:.1f}" fill="none" stroke="{C["shu"]}" stroke-width="{x * 0.04:.2f}" stroke-dasharray="{x * 0.12:.1f} {x * 0.1:.1f}"/>',
         f'<rect x="{pad:.1f}" y="{pad:.1f}" width="{vw:.1f}" height="{vh:.1f}" fill="none" stroke="{C["ishi"]}" stroke-width="{x * 0.02:.2f}"/>',
         f'<g transform="translate({pad - vx:.1f} {pad - vy:.1f})">{body}</g>']
    for cx, cy in ((pad - x / 2, pad + vh / 2), (pad + vw + x / 2, pad + vh / 2), (pad + vw / 2, pad - x / 2), (pad + vw / 2, pad + vh + x / 2)):
        g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{x / 2:.1f}" fill="{C["shu"]}" opacity="0.18"/>'
                 f'<text x="{cx:.1f}" y="{cy + x * 0.16:.1f}" text-anchor="middle" font-family="Helvetica" font-size="{x * 0.42:.1f}" fill="{C["shu"]}">x</text>')
    k = 2000 / W
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="2000" height="{H * k:.0f}">{"".join(g)}</svg>'


@asset("minsize", 2000)
def _():
    out = []
    x = 40
    for w, lab in ((420, "≥ 30 mm / 160 px"), (240, ""), (160, "")):
        g, W, H = place(lockup("su", "color", bg=False), x, 60, w=w)
        out.append(g)
        x += w + 70
    x += 30
    for px in (64, 32, 20):
        out.append(mark_g(x + px / 2, 60 + 45, px))
        x += px + 50
    return doc(int(x + 20), 190, "".join(out), C["shiro"])


# ───────────────────────────── supporting graphics ─────────────────────────────

@asset("pattern", 2400)
def _():
    """分裂纹样: a quiet field of the mark's four division stages, all turning the same way."""
    from cells import Cluster
    t = MARK.fit(240.0)
    A, B, Cc, D, E = t.cells
    P1, P2, pr, waist = t.capsules[0]
    W, H = 2400, 1350
    shapes = []
    L = length(sub(P2, P1))
    unitk = 0.42
    motifs = [f'<circle r="{E[1]:.1f}"/>',
              Cluster([], [], [((-L / 2, 0), (L / 2, 0), pr)], None).body_svg("inherit"),
              Cluster([((-length(sub(B[0], A[0])) / 2, 0), A[1]), ((length(sub(B[0], A[0])) / 2, 0), B[1])],
                      [(0, 1, (t.bridges[0][2] + t.bridges[0][3]) / 2, (t.bridges[0][2] + t.bridges[0][3]) / 2)], [], None).body_svg("inherit")]
    import random
    rnd = random.Random(7)
    sx, sy = 220, 200
    for j in range(8):
        for i in range(12):
            if (i, j) == (7, 3):
                continue
            cx = 60 + i * sx + (sx / 2 if j % 2 else 0)
            cy = 40 + j * sy
            m = motifs[(i + j) % 3]
            ang = -33 + rnd.uniform(-6, 6)
            shapes.append(f'<g transform="translate({cx} {cy}) rotate({ang:.1f}) scale({unitk})" fill="{C["kinari"]}">{m}</g>')
    point = f'<circle cx="{60 + 7 * sx + sx / 2}" cy="{40 + 3 * sy}" r="{t.accent[1] * unitk:.1f}" fill="{C["shu"]}"/>'
    return doc(W, H, "".join(shapes).replace('fill="inherit"', "") + point, C["shiro"])


@asset("orbit", 2400)
def _():
    """轨道线: the hidden structure as a hairline graphic, one 朱 point."""
    W, H = 2400, 1350
    cx, cy = 1560, 640
    out = []
    for r, op in ((520, 0.9), (330, 0.7), (760, 0.45), (980, 0.3)):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["ishi"]}" stroke-width="1.6" opacity="{op}"/>')
    for a in (-70.4, 49.6, 169.6):
        x2 = cx + 1100 * math.cos(math.radians(a))
        y2 = cy + 1100 * math.sin(math.radians(a))
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{C["ishi"]}" stroke-width="1.2" opacity="0.5"/>')
    a = math.radians(-70.4 + 28)
    out.append(f'<circle cx="{cx + 760 * math.cos(a):.0f}" cy="{cy + 760 * math.sin(a):.0f}" r="26" fill="{C["shu"]}"/>')
    return doc(W, H, "".join(out), C["shiro"])


# ───────────────────────────── don'ts ─────────────────────────────

def dont_tile(kind):
    S = 600
    bg = C["shiro"]
    cell, point = C["koke"], C["shu"]
    frag, (x0, y0, x1, y1) = mark_frag(cell, point)
    k = S * 0.52 / max(x1 - x0, y1 - y0)
    base = lambda extra="": f'<g transform="translate({S / 2 - (x0 + x1) / 2 * k:.1f} {S / 2 - (y0 + y1) / 2 * k:.1f}) scale({k:.4f}){extra}">'
    if kind == "stretch":
        g = f'<g transform="translate({S / 2} {S / 2}) scale(1.45 0.72) translate({-S / 2} {-S / 2})">{base()}{frag}</g></g>'
    elif kind == "rotate":
        g = f'<g transform="rotate(38 {S / 2} {S / 2})">{base()}{frag}</g></g>'
    elif kind == "recolor":
        f2, _ = mark_frag("#00C27A", "#FFD400")
        g = base() + f2 + "</g>"
    elif kind == "point":
        f2, _ = mark_frag(cell, "#3A6BFF")
        g = base() + f2 + "</g>"
    elif kind == "outline":
        t = MARK.fit(240.0)
        f2 = "".join(f'<path d="{d}" fill="none" stroke="{cell}" stroke-width="3"/>' for d in t.body_parts())
        f2 += f'<path d="{t.accent_d()}" fill="none" stroke="{point}" stroke-width="3"/>'
        g = base() + f2 + "</g>"
    elif kind == "gradient":
        t = MARK.fit(240.0)
        f2 = ('<defs><linearGradient id="dg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16C79A"/>'
              '<stop offset="1" stop-color="#3B2CFF"/></linearGradient></defs>' + t.body_svg("url(#dg)") +
              f'<path d="{t.accent_d()}" fill="#FF3D7F"/>')
        g = base() + f2 + "</g>"
    elif kind == "rearrange":
        t = MARK.fit(240.0)
        f2 = t.body_svg(cell) + f'<g transform="translate(-150 120)"><path d="{t.accent_d()}" fill="{point}"/></g>'
        g = base() + f2 + "</g>"
    else:  # busy background
        stripes = "".join(f'<rect x="{i * 40}" y="0" width="20" height="{S}" fill="#8C9A83" opacity="0.55"/>' for i in range(16))
        bg = "#A9B49E"
        g = stripes + base() + frag + "</g>"
    cross = (f'<g stroke="{C["shu"]}" stroke-width="7" stroke-linecap="round"><line x1="{S - 76}" y1="40" x2="{S - 40}" y2="76"/>'
             f'<line x1="{S - 40}" y1="40" x2="{S - 76}" y2="76"/></g>')
    return doc(S, S, f'<rect width="{S}" height="{S}" fill="{bg}"/>{g}{cross}')


DONTS = [("stretch", "不要拉伸变形"), ("rotate", "不要旋转"), ("recolor", "不要更换为非标准色"), ("point", "不要改变“点”的颜色"),
         ("outline", "不要改为描边"), ("gradient", "不要添加渐变与特效"), ("rearrange", "不要移动或重排元素"), ("busy", "不要置于杂乱或低对比背景")]
for _k, _ in DONTS:
    F[f"dont-{_k}"] = ((lambda k=_k: dont_tile(k)), 600)


# ───────────────────────────── applications ─────────────────────────────

@asset("app-cards", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["kinari"]}"/>']
    front, back = card("su", "front"), card("su", "back")
    for svg, x, y, rot in ((back, 380, 300, -5), (front, 1100, 640, 3)):
        g, w, h = place(svg, 0, 0, w=1000)
        out.append(f'<g transform="translate({x} {y}) rotate({rot} {w / 2} {h / 2})">{shadow(0, 0, w, h, 8, 0.03, 10, 18)}{g}</g>')
    # back side: name lines as text
    return doc(W, H, "".join(out))


@asset("app-stationery", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["shiro"]}"/>']
    # letterhead A4 (210x297)
    lw, lh = 760, 760 * 297 / 210
    lx, ly = 260, 170
    out.append(shadow(lx, ly, lw, lh, 2, 0.03, 10, 16) + f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="#FCFBF8"/>')
    g, _, _ = place(lockup("su", "color", bg=False), lx + 64, ly + 70, w=230)
    out.append(g)
    for i in range(14):
        out.append(bar(lx + 64, ly + 260 + i * 34, lw - 128 - (180 if i % 5 == 4 else 0), 3, C["ishi"], 0.35))
    out.append(bar(lx + 64, ly + lh - 80, 220, 3, C["koke"], 0.6))
    out.append(f'<circle cx="{lx + lw - 70}" cy="{ly + lh - 78}" r="6" fill="{C["shu"]}"/>')
    # envelope DL (220x110)
    ew, eh = 900, 450
    ex, ey = 1180, 300
    out.append(shadow(ex, ey, ew, eh, 2, 0.03, 10, 16) + f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="{C["kinari"]}"/>')
    out.append(mark_g(ex + 90, ey + 92, 90))
    out.append(T(ex + 150, ey + 86, "EonPoint 亿触点", 22, C["sumi"]))
    out.append(T(ex + 150, ey + 118, "AI · Agent · Cloud · SaaS · Software · Licensing", 18, TXT2))
    out.append(bar(ex + 520, ey + 280, 300, 3, C["ishi"], 0.5) + bar(ex + 520, ey + 320, 260, 3, C["ishi"], 0.5))
    # badge
    bw, bh = 330, 500
    bx, by = 1640, 880
    out.append(f'<rect x="{bx + bw / 2 - 18}" y="{by - 90}" width="36" height="110" fill="{C["koke"]}"/>')
    out.append(shadow(bx, by, bw, bh, 18, 0.035, 10, 14) + f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18" fill="#FCFBF8"/>')
    out.append(f'<rect x="{bx + bw / 2 - 40}" y="{by + 24}" width="80" height="14" rx="7" fill="{C["kinari"]}"/>')
    out.append(mark_g(bx + bw / 2, by + 170, 120))
    out.append(T(bx + bw / 2, by + 320, "Name 姓名", 30, C["sumi"], "middle"))
    out.append(T(bx + bw / 2, by + 360, "Title 职位", 20, TXT2, "middle"))
    out.append(f'<rect x="{bx}" y="{by + bh - 60}" width="{bw}" height="60" fill="{C["koke"]}"/>'
               f'<rect x="{bx}" y="{by + bh - 60}" width="{bw}" height="20" fill="{C["koke"]}"/>')
    g, _, _ = place(lockup_single("su", "white", bg=False), bx + bw / 2, by + bh - 30, w=200, anchor="c")
    out.append(g)
    return doc(W, H, "".join(out))


@asset("app-wall", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["kinari"]}"/>',
           f'<rect y="1080" width="{W}" height="420" fill="#D9D1C1"/>',
           f'<rect y="1074" width="{W}" height="6" fill="#CFC6B4"/>']
    # wall panel (wood) with the lockup in sumi
    out.append(f'<rect x="420" y="160" width="1560" height="760" fill="#E3D9C7"/>')
    for i in range(0, 1560, 52):
        out.append(f'<rect x="{420 + i}" y="160" width="2" height="760" fill="#D6CAB4" opacity="0.6"/>')
    g, w, h = place(lockup("su", "color", bg=False), 1200, 520, w=900, anchor="c")
    out.append(g)
    # reception desk
    out.append(shadow(700, 900, 1000, 220, 4, 0.03, 8, 10) + f'<rect x="700" y="900" width="1000" height="220" fill="#F7F5F0"/>'
               f'<rect x="700" y="900" width="1000" height="16" fill="#EDE8DE"/>')
    out.append(f'<ellipse cx="1200" cy="1160" rx="620" ry="26" fill="#2F2E2B" opacity="0.06"/>')
    # pendant lights
    for x in (900, 1200, 1500):
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="120" stroke="{C["sumi"]}" stroke-width="2"/><circle cx="{x}" cy="132" r="14" fill="{C["sumi"]}"/>')
    # wayfinding sign
    out.append(f'<rect x="2060" y="430" width="200" height="420" fill="{C["koke"]}"/>')
    out.append(mark_g(2160, 520, 90, C["kinari"], "#C8563F"))
    for i, s in enumerate(("会议室", "前台", "展厅")):
        out.append(T(2090, 640 + i * 60, s, 28, C["kinari"]))
        out.append(T(2230, 640 + i * 60, "→", 26, C["kinari"], "end"))
    return doc(W, H, "".join(out))


@asset("app-web", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["kinari"]}"/>']
    bx, by, bw, bh = 220, 140, 1960, 1220
    out.append(shadow(bx, by, bw, bh, 18, 0.03, 10, 18) + f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18" fill="#FCFBF8"/>')
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="64" rx="18" fill="#EFEBE3"/><rect x="{bx}" y="{by + 40}" width="{bw}" height="24" fill="#EFEBE3"/>')
    for i, col in enumerate(("#D9D3C7", "#D9D3C7", "#D9D3C7")):
        out.append(f'<circle cx="{bx + 40 + i * 30}" cy="{by + 32}" r="9" fill="{col}"/>')
    out.append(f'<rect x="{bx + 640}" y="{by + 16}" width="680" height="32" rx="16" fill="#F8F6F1"/>')
    out.append(T(bx + 980, by + 39, "EonPoint 亿触点 · 官网", 18, TXT2, "middle"))
    ny = by + 64
    g, _, _ = place(lockup_single("su", "color", bg=False), bx + 80, ny + 44, h=40)
    out.append(g)
    for i, s in enumerate(("产品", "Agent", "云服务", "软件授权", "关于我们")):
        out.append(T(bx + 1240 + i * 130, ny + 72, s, 22, C["sumi"]))
    out.append(f'<rect x="{bx}" y="{ny + 128}" width="{bw}" height="1" fill="{C["hara" if False else "ishi"]}" opacity="0.4"/>')
    # hero
    hy = ny + 129
    out.append(f'<rect x="{bx}" y="{hy}" width="{bw}" height="720" fill="{C["shiro"]}"/>')
    out.append(T(bx + 140, hy + 230, "AI · AGENT · CLOUD · SAAS · SOFTWARE · LICENSING", 20, TXT2, "start", 400, 6))
    out.append(T(bx + 140, hy + 340, "让每一家企业，", 70, C["sumi"], "start", 300, 4))
    out.append(T(bx + 140, hy + 440, "都拥有自己的 AI Agent。", 70, C["sumi"], "start", 300, 4))
    out.append(f'<rect x="{bx + 140}" y="{hy + 520}" width="200" height="60" rx="30" fill="{C["koke"]}"/>')
    out.append(T(bx + 240, hy + 558, "联系我们", 22, C["kinari"], "middle"))
    out.append(mark_g(bx + 1540, hy + 360, 420))
    # cards row
    cy0 = hy + 760
    for i, (t1, t2) in enumerate((("AI Agent", "企业级智能体研发"), ("Cloud", "云服务与部署"), ("Licensing", "软件正版授权"))):
        x = bx + 140 + i * 590
        out.append(f'<rect x="{x}" y="{cy0}" width="540" height="250" rx="10" fill="#F6F3EC"/>')
        out.append(f'<circle cx="{x + 50}" cy="{cy0 + 60}" r="10" fill="{C["shu"] if i == 0 else C["koke"]}"/>')
        out.append(T(x + 40, cy0 + 140, t1, 34, C["sumi"], "start", 400))
        out.append(T(x + 40, cy0 + 190, t2, 22, TXT2))
    return doc(W, H, "".join(out))


def phone(x, y, w, inner, bg):
    h = w * 2.05
    r = w * 0.14
    s = shadow(x, y, w, h, r, 0.035, 10, 18)
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#1F1E1C"/>'
    m = w * 0.035
    s += f'<rect x="{x + m}" y="{y + m}" width="{w - 2 * m}" height="{h - 2 * m}" rx="{r - m}" fill="{bg}"/>'
    s += f'<g transform="translate({x + m} {y + m})">{inner}</g>'
    s += f'<rect x="{x + w / 2 - w * 0.14}" y="{y + m + 16}" width="{w * 0.28}" height="{w * 0.07}" rx="{w * 0.035}" fill="#1F1E1C"/>'
    return s


@asset("app-mobile", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["kinari"]}"/>']
    pw = 560
    sw = pw * 0.93
    # splash
    sp = mark_g(sw / 2, 440, 200)
    g, _, _ = place(lockup_stacked("su", "color", bg=False), sw / 2, 760, w=230, anchor="cx")
    sp = mark_g(sw / 2, 480, 190) + place(lockup_single("su", "color", bg=False), sw / 2, 980, w=300, anchor="cx")[0]
    sp += T(sw / 2, 1040, "AI · Agent · Cloud", 16, TXT2, "middle", 400, 4)
    out.append(phone(340, 110, pw, sp, C["shiro"]))
    # WeCom-like list
    rows = ""
    rows += T(40, 110, "消息", 34, C["sumi"], "start", 500)
    names = [("亿触点 EonPoint", "Agent 部署完成，已接入 12 个系统"), ("", ""), ("", ""), ("", ""), ("", "")]
    for i, (n_, m_) in enumerate(names):
        y = 160 + i * 132
        if i == 0:
            rows += f'<rect x="16" y="{y - 10}" width="{sw - 32}" height="120" rx="16" fill="#FCFBF8"/>'
            rows += f'<circle cx="80" cy="{y + 50}" r="40" fill="{C["koke"]}"/>' + mark_g(80, y + 52, 48, C["kinari"], "#C8563F")
            rows += T(140, y + 40, n_, 24, C["sumi"], "start", 500) + T(140, y + 78, m_, 18, TXT2)
            rows += T(sw - 36, y + 40, "09:41", 16, TXT2, "end")
        else:
            rows += f'<circle cx="80" cy="{y + 50}" r="40" fill="#DEDAD1"/>' + bar(140, y + 30, 160, 14, "#DEDAD1", 1) + bar(140, y + 64, 260, 12, "#E6E2DA", 1)
    out.append(phone(1060, 110, pw, rows, "#F3F1EC"))
    # app icon on its own
    g, _, _ = place(app_icon("koke"), 1800, 520, w=260)
    out.append(shadow(1800, 520, 260, 260, 56, 0.03, 8, 12) + g)
    out.append(T(1930, 830, "EonPoint", 28, C["sumi"], "middle"))
    return doc(W, H, "".join(out))


@asset("app-ppt", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["shiro"]}"/>']
    # slide cover 16:9
    sx, sy, sw_, sh_ = 150, 150, 1000, 562
    out.append(shadow(sx, sy, sw_, sh_, 6, 0.03, 10, 16) + f'<rect x="{sx}" y="{sy}" width="{sw_}" height="{sh_}" fill="{C["kinari"]}"/>')
    g, _, _ = place(lockup("su", "color", bg=False), sx + 64, sy + 64, w=220)
    out.append(g)
    out.append(T(sx + 64, sy + 350, "企业 AI Agent 解决方案", 48, C["sumi"], "start", 300, 3))
    out.append(T(sx + 64, sy + 406, "2026 · 产品发布", 24, TXT2))
    out.append(f'<circle cx="{sx + sw_ - 84}" cy="{sy + sh_ - 84}" r="15" fill="{C["shu"]}"/>')
    # inner page
    sy2 = sy + sh_ + 70
    out.append(shadow(sx, sy2, sw_, sh_, 6, 0.03, 10, 16) + f'<rect x="{sx}" y="{sy2}" width="{sw_}" height="{sh_}" fill="#FCFBF8"/>')
    out.append(T(sx + 64, sy2 + 110, "三步接入企业 Agent", 36, C["sumi"], "start", 400, 2))
    for i in range(3):
        x = sx + 64 + i * 300
        out.append(f'<rect x="{x}" y="{sy2 + 170}" width="270" height="260" rx="8" fill="{C["shiro"]}"/>')
        out.append(f'<circle cx="{x + 40}" cy="{sy2 + 214}" r="9" fill="{C["shu"] if i == 0 else C["koke"]}"/>')
        out.append(bar(x + 30, sy2 + 280, 190, 6, C["ishi"], 0.55) + bar(x + 30, sy2 + 310, 150, 6, C["ishi"], 0.35))
    g, _, _ = place(lockup_single("su", "color", bg=False), sx + 64, sy2 + sh_ - 60, h=24)
    out.append(g + T(sx + sw_ - 64, sy2 + sh_ - 42, "02", 20, TXT2, "end"))
    # stage backdrop with a roll-up standing in front
    bx, by, bw, bh = 1270, 150, 1000, 900
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{C["koke"]}"/>')
    out.append(mark_g(bx + bw / 2 - 160, by + 330, 300, C["kinari"], "#C8563F"))
    g, _, _ = place(lockup_single("su", "white", bg=False), bx + bw / 2 - 160, by + 560, w=460, anchor="cx")
    out.append(g)
    out.append(T(bx + bw / 2 - 160, by + 700, "AI · AGENT · CLOUD · SAAS", 22, C["kinari"], "middle", 400, 8))
    out.append(f'<rect x="{bx - 40}" y="{by + bh}" width="{bw + 80}" height="44" fill="#D9D1C1"/>')
    rx, ry, rw, rh = 2000, 640, 240, 500
    out.append(shadow(rx, ry, rw, rh, 2, 0.04, 8, 10) + f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{C["shiro"]}"/>')
    out.append(mark_g(rx + rw / 2, ry + 150, 120))
    out.append(place(lockup_single("su", "color", bg=False), rx + rw / 2, ry + 270, w=190, anchor="cx")[0])
    out.append(T(rx + rw / 2, ry + 420, "AI · Agent · Cloud", 16, TXT2, "middle", 400, 3))
    out.append(f'<rect x="{rx - 16}" y="{ry + rh}" width="{rw + 32}" height="16" rx="6" fill="#B9B09E"/>')
    return doc(W, H, "".join(out))


@asset("app-merch", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["kinari"]}"/>']
    # tote bag
    tx, ty, tw, th = 300, 420, 700, 820
    out.append(f'<path d="M{tx + 170} {ty}C{tx + 170} {ty - 260} {tx + 530} {ty - 260} {tx + 530} {ty}" fill="none" stroke="#E6DFCF" stroke-width="34"/>')
    out.append(shadow(tx, ty, tw, th, 4, 0.03, 10, 16) + f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="#F1ECE1"/>')
    out.append(mark_g(tx + tw / 2, ty + 330, 300))
    g, _, _ = place(lockup_single("su", "color", bg=False), tx + tw / 2, ty + 600, w=360, anchor="cx")
    out.append(g)
    # kraft box
    bx, by, bw, bh = 1180, 640, 760, 560
    out.append(shadow(bx, by, bw, bh, 4, 0.035, 10, 16))
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{KRAFT}"/>')
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="70" fill="#C4AA84"/>')
    g, _, _ = place(lockup("su", "mono", bg=False), bx + 70, by + 150, w=330)
    out.append(g)
    out.append(T(bx + 70, by + bh - 70, "AI · AGENT · CLOUD · SAAS", 18, "#5D5241", "start", 400, 5))
    out.append(f'<circle cx="{bx + bw - 90}" cy="{by + 160}" r="30" fill="{C["shu"]}"/>')
    # sticker / seal on box
    # mug
    mx, my = 2030, 900
    out.append(f'<rect x="{mx}" y="{my}" width="230" height="290" rx="20" fill="{C["shiro"]}"/>'
               f'<path d="M{mx + 230} {my + 70}C{mx + 320} {my + 70} {mx + 320} {my + 220} {mx + 230} {my + 220}" fill="none" stroke="{C["shiro"]}" stroke-width="26"/>')
    out.append(mark_g(mx + 115, my + 145, 110))
    out.append(f'<ellipse cx="{mx + 130}" cy="{my + 300}" rx="170" ry="16" fill="#2F2E2B" opacity="0.07"/>')
    return doc(W, H, "".join(out))


@asset("app-social", 2400)
def _():
    W, H = 2400, 1500
    out = [f'<rect width="{W}" height="{H}" fill="{C["shiro"]}"/>']
    # article cover 2.35:1
    ax, ay, aw = 160, 160, 1300
    ah = aw / 2.35
    out.append(shadow(ax, ay, aw, ah, 8, 0.03, 10, 14) + f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah:.0f}" rx="8" fill="{C["koke"]}"/>')
    out.append(mark_g(ax + aw - 280, ay + ah / 2, 300, C["kinari"], "#C8563F"))
    out.append(T(ax + 90, ay + 200, "从一个点，", 60, C["kinari"], "start", 300, 4))
    out.append(T(ax + 90, ay + 290, "到亿个触点。", 60, C["kinari"], "start", 300, 4))
    out.append(T(ax + 90, ay + 380, "EonPoint 亿触点 · 品牌焕新", 24, "#DCD6C8"))
    # square post
    qx, qy, qs = 1580, 160, 660
    out.append(shadow(qx, qy, qs, qs, 8, 0.03, 10, 14) + f'<rect x="{qx}" y="{qy}" width="{qs}" height="{qs}" rx="8" fill="{C["kinari"]}"/>')
    out.append(mark_g(qx + qs / 2, qy + 270, 260))
    g, _, _ = place(lockup_single("su", "color", bg=False), qx + qs / 2, qy + 500, w=340, anchor="cx")
    out.append(g)
    # 3 vertical story / poster thumbnails
    for i, (bg, cell, pt, line) in enumerate(((C["shiro"], C["koke"], C["shu"], "AI Agent"), (C["sumi"], C["kinari"], "#C8563F", "Cloud"), (C["kinari"], C["koke"], C["shu"], "Licensing"))):
        x = 160 + i * 460
        y = 840
        w, h = 400, 600
        out.append(shadow(x, y, w, h, 8, 0.03, 8, 12) + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{bg}"/>')
        out.append(mark_g(x + w / 2, y + 230, 150, cell, pt))
        col = C["kinari"] if bg == C["sumi"] else C["sumi"]
        out.append(T(x + w / 2, y + 430, line, 40, col, "middle", 300, 4))
        out.append(T(x + w / 2, y + 480, "EonPoint 亿触点", 18, col, "middle", 400, 3))
    # profile avatar row
    out.append(f'<circle cx="1910" cy="1140" r="150" fill="{C["koke"]}"/>' + mark_g(1910, 1146, 170, C["kinari"], "#C8563F"))
    out.append(T(1910, 1350, "官方账号头像", 24, TXT2, "middle"))
    return doc(W, H, "".join(out))


def main():
    os.makedirs(OUT, exist_ok=True)
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for name, (fn, w) in F.items():
        if only and name not in only:
            continue
        svg = fn()
        p = os.path.join(OUT, name + ".svg")
        open(p, "w").write(svg)
        if SVG2PNG and "--png" in sys.argv:
            subprocess.run([SVG2PNG, p, os.path.join(OUT, name + ".png"), str(w or 1600)], check=True, capture_output=True)
    print(len(F), "assets")


if __name__ == "__main__":
    main()
