"""R6 Latin — quiet geometric sans for the Hara direction. No gimmicks: true-circle
bowls, thinned joins, round dots. Cap height 100, baseline y = 100."""
import math
from shapely.geometry import box, Polygon
from type5 import Stroke, Ring, Dot

BIG = 1e4

VARIANTS = {
    # 素 Su — the recommended one: regular weight, title case
    "su": dict(cn="素", en="Su", text="EonPoint", X=71.0, wv=10.0, wh=8.6, wd=9.6, ov=1.3, D=24.0, track=8.0,
               cnm=dict(wv=9.6, wh=7.6, wd=9.1, gap=16.0, dot=0.62), cn_em=80.0),
    # 轻 Kei — light, all lowercase, MUJI-quiet
    "kei": dict(cn="轻", en="Kei", text="eonpoint", X=72.0, wv=6.9, wh=6.1, wd=6.6, ov=1.1, D=24.0, track=10.0,
                cnm=dict(wv=7.2, wh=6.0, wd=6.8, gap=18.0, dot=0.66), cn_em=78.0),
    # 间 Ma — spaced capitals, generous air
    "ma": dict(cn="间", en="Ma", text="EONPOINT", X=72.0, wv=8.4, wh=7.6, wd=8.2, ov=1.2, D=24.0, track=30.0,
               cnm=dict(wv=8.6, wh=7.2, wd=8.2, gap=44.0, dot=0.64), cn_em=68.0),
}


def glyph(ch, V):
    X, wv, wh, ov = V["X"], V["wv"], V["wh"], V["ov"]
    xt = 100 - X
    hv, hh = wv / 2, wh / 2
    sh = wv * 0.16                     # optical thinning where bowls meet stems
    G = dict(prims=[], width=0, sb=(2, 2), cuts=[], extra=[])
    P = G["prims"]
    if ch == "E":
        We = 49.0
        P += [Stroke([(hv, 0), (hv, 100)], "v"),
              Stroke([(0, hh), (We, hh)], "h"),
              Stroke([(0, 49.0), (We - 4.0, 49.0)], "h"),
              Stroke([(0, 100 - hh), (We, 100 - hh)], "h")]
        G.update(width=We, sb=(0, 5))
    elif ch == "P":
        Bh = 55.0
        Rx = Bh / 2 + 0.5
        Wp = 53.0
        xb = Wp - Rx
        P += [Stroke([(hv, 100), (hv, 0)], "v"),
              Stroke([(0, hh), (xb, hh)], "h"),
              Ring(xb, Bh / 2, Rx, Bh / 2, clip=box(xb, -BIG, BIG, BIG)),
              Stroke([(0, Bh - hh), (xb, Bh - hh)], "h")]
        G.update(width=Wp, sb=(0, 3))
    elif ch == "O":
        R = 50 + ov
        P.append(Ring(R, 50, R, R, irx=R - wv * 1.04, iry=R - wh))
        G.update(width=2 * R, sb=(1.5, 1.5))
    elif ch == "N":
        Wn = 72.0
        ws = wv * 0.86
        P += [Stroke([(ws / 2, 100), (ws / 2, 0)], "c"), Stroke([(Wn - ws / 2, 0), (Wn - ws / 2, 100)], "c"),
              Stroke([(ws * 0.35, 0), (Wn - ws * 0.35, 100)], "d")]
        G.update(width=Wn, sb=(5, 5), clip=box(-BIG, 0, BIG, 100))
    elif ch == "I":
        P.append(Stroke([(hv, 0), (hv, 100)], "v"))
        G.update(width=wv, sb=(5, 5))
    elif ch == "T":
        Wt = 58.0
        P += [Stroke([(0, hh), (Wt, hh)], "h"), Stroke([(Wt / 2, 0), (Wt / 2, 100)], "v")]
        G.update(width=Wt, sb=(0.5, 0.5))
    elif ch == "o":
        R = X / 2 + ov
        P.append(Ring(R, 100 - X / 2, R, R, irx=R - wv * 1.03, iry=R - wh))
        G.update(width=2 * R, sb=(1.5, 1.5))
    elif ch == "e":
        R = X / 2 + ov
        cy = 100 - X / 2
        a1 = math.radians(36)
        far = R * 3
        ap = Polygon([(R, cy + hh * 0.92), (R + far, cy + hh * 0.92),
                      (R + far * math.cos(a1), cy + far * math.sin(a1))])
        P += [Ring(R, cy, R, R, aperture=ap, irx=R - wv * 1.03, iry=R - wh),
              Stroke([(1, cy - 0.5), (2 * R - 1, cy - 0.5)], "h")]
        G.update(width=2 * R, sb=(1.5, 1.5))
    elif ch == "n":
        Wn = 56.0
        # outer arch: a circle through the stem's top-right corner, tangent to the right side and
        # to the overshoot line —  (Ra-a)^2 + (b-Ra)^2 = Ra^2  →  Ra = a+b-sqrt(2ab)
        a, b = Wn - wv, ov
        Ra = a + b - math.sqrt(2 * a * b)
        cx, cy = Wn - Ra, xt - ov + Ra
        arch = Ring(cx, cy, Ra, Ra, clip=box(hv, -BIG, BIG, cy), idx=-sh, irx=Ra - wv + sh, iry=Ra - wh * 1.02)
        P += [Stroke([(hv, xt), (hv, 100)], "v"), arch, Stroke([(Wn - hv, cy), (Wn - hv, 100)], "v")]
        G.update(width=Wn, sb=(3.5, 3.5))
    elif ch == "p":
        R = X / 2 + ov
        P += [Stroke([(hv, xt), (hv, 100 + V["D"])], "v"),
              Ring(R, 100 - X / 2, R, R, idx=-sh * 0.0, irx=R - wv * 1.03, iry=R - wh)]
        G.update(width=2 * R, sb=(3.5, 1.5))
    elif ch == "i":
        r = wv * 0.66
        gap = wv * 0.62 + 3.0
        P += [Stroke([(hv, xt), (hv, 100)], "v"), Dot(hv, xt - gap - r, r, accent=True)]
        G.update(width=wv, sb=(3.5, 3.5))
    elif ch == "t":
        Wt = 33.0
        xs = 11.0 + hv
        top = xt - X * 0.24
        P += [Stroke([(xs, top), (xs, 100)], "v"), Stroke([(0, xt + hh), (Wt, xt + hh)], "h")]
        G.update(width=Wt, sb=(0.5, 0.5))
    else:
        raise KeyError(ch)
    return G


KERN = {("E", "o"): -2.5, ("P", "o"): -3.5, ("n", "t"): -1.5, ("E", "O"): -3, ("P", "O"): -5,
        ("O", "N"): -1, ("O", "I"): -1, ("N", "T"): -2, ("p", "o"): -1, ("e", "o"): -0.5, ("o", "i"): 0.5}
