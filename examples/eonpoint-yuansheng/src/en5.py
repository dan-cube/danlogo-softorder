"""Custom Latin letterforms for EonPoint (no fonts). Cap height 100, baseline y = 100."""
from shapely.geometry import box, Polygon
from type5 import Stroke, Ring, Dot, arc

BIG = 1e4


import math

AXIS = -33.0   # the mark's division axis (A→B), used for every split


def metrics(style):
    if style == "split":
        return dict(X=70.0, wv=19.0, wh=16.5, wd=18.0, ov=1.6, D=24.0, track=5.0, case="lower", cut=2.6)
    if style == "neck":
        return dict(X=72.0, wv=15.0, wh=12.5, wd=14.0, ov=1.4, D=24.0, track=5.5, case="title")
    return dict(X=72.0, wv=4.2, wh=4.2, wd=4.2, ov=0.8, D=24.0, track=26.0, case="upper", node=1.2)


def _axis_cut(cx, cy, L, w):
    u = (math.cos(math.radians(AXIS)), math.sin(math.radians(AXIS)))
    return dict(line=[(cx - u[0] * L, cy - u[1] * L), (cx + u[0] * L, cy + u[1] * L)], w=w)


def glyph(ch, M, style):
    X, wv, wh, ov = M["X"], M["wv"], M["wh"], M["ov"]
    xt = 100 - X
    hv, hh = wv / 2, wh / 2
    G = dict(prims=[], width=0, sb=(1.5, 1.5), cuts=[], extra=[])
    P = G["prims"]
    cw = M.get("cut", 2.4)
    if ch == "E":
        We = 52.0 if style != "node" else 56.0
        P += [Stroke([(hv, 0), (hv, 100)], "v", nodes=(False, False)),
              Stroke([(0, hh), (We, hh)], "h"),
              Stroke([(0, 49.5), (We - 3.5, 49.5)], "h"),
              Stroke([(0, 100 - hh), (We, 100 - hh)], "h")]
        G.update(width=We, sb=(0, 4))
    elif ch == "O":
        R = 50 + ov
        P.append(Ring(R, 50, R, R))
        G.update(width=2 * R, sb=(1, 1))
    elif ch == "N":
        Wn = 74.0
        wd = M["wd"] * 1.05
        sv = dict(M)
        P += [Stroke([(hv, 100), (hv, 0)], "v"), Stroke([(Wn - hv, 0), (Wn - hv, 100)], "v"),
              Stroke([(hv * 0.6, 0), (Wn - hv * 0.6, 100)], "d", nodes=(False, False))]
        G.update(width=Wn, sb=(3, 3), clip=box(-BIG, -ov * 0.2, BIG, 100 + ov * 0.2))
    elif ch == "I":
        P.append(Stroke([(hv, 0), (hv, 100)], "v"))
        G.update(width=wv, sb=(3, 3))
    elif ch == "T":
        Wt = 62.0
        P += [Stroke([(0, hh), (Wt, hh)], "h"), Stroke([(Wt / 2, hh), (Wt / 2, 100)], "v", nodes=(False, True))]
        G.update(width=Wt, sb=(0, 0))
    elif ch == "P":
        Bh = 57.0 if style != "node" else 55.0
        Wp = 56.0
        Rx = Bh / 2
        xb = Wp - Rx
        P += [Stroke([(hv, 100), (hv, 0)], "v", nodes=(True, False)),
              Stroke([(0, hh), (xb, hh)], "h", nodes=(False, False)),
              Ring(xb, Bh / 2, Rx, Bh / 2, clip=box(xb, -BIG, BIG, BIG)),
              Stroke([(0, Bh - hh), (xb, Bh - hh)], "h", nodes=(False, False))]
        G.update(width=Wp, sb=(0, 2))
    elif ch == "o":
        R = X / 2 + ov
        P.append(Ring(R, 100 - X / 2, R, R))
        G["cuts"].append(_axis_cut(R, 100 - X / 2, R * 1.3, cw))
        G.update(width=2 * R, sb=(1, 1))
    elif ch == "e":
        R = X / 2 + ov
        cy = 100 - X / 2
        import math
        a0, a1 = math.radians(2), math.radians(38 if style != "node" else 34)
        far = R * 3
        ap = Polygon([(R, cy + hh * 1.05), (R + far * math.cos(a0), cy + hh * 1.05 + far * math.sin(a0)),
                      (R + far * math.cos(a1), cy + far * math.sin(a1))])
        P += [Ring(R, cy, R, R, aperture=ap), Stroke([(0.5, cy), (2 * R - 0.5, cy)], "h", nodes=(False, False))]
        G.update(width=2 * R, sb=(1, 1))
    elif ch == "n":
        Wn = 58.0 if style != "node" else 60.0
        Ra = Wn / 2
        cy = xt - ov + Ra
        top = xt
        P += [Stroke([(hv, top), (hv, 100)], "v", nodes=(style == "node", True)),
              Ring(Ra, cy, Ra, Ra, clip=box(-BIG, -BIG, BIG, cy)),
              Stroke([(Wn - hv, cy), (Wn - hv, 100)], "v", nodes=(False, True))]
        G["cuts"].append(dict(line=[(wv + cw / 2, xt - 6), (wv + cw / 2, cy + 3)], w=cw))
        G.update(width=Wn, sb=(2.5, 2.5))
    elif ch == "p":
        R = X / 2 + ov
        P += [Stroke([(hv, xt), (hv, 100 + M["D"])], "v", nodes=(False, True)), Ring(R, 100 - X / 2, R, R)]
        G["cuts"].append(dict(line=[(wv + cw / 2, xt - 6), (wv + cw / 2, 100 + 6)], w=cw))
        G.update(width=2 * R, sb=(2.5, 1))
    elif ch == "i":
        if style == "neck":
            # a dividing cell: capsule-topped stem + dot, joined by the mark's neck
            from shapely.geometry import Point
            from type5 import bud
            r = wv * 0.68
            gap = wv * 0.55
            top_c = (hv, xt + hv)
            dot_c = (hv, xt - gap - r)
            P += [Stroke([(hv, xt + hv), (hv, 100)], "v"), Dot(dot_c[0], dot_c[1], r, accent=True)]
            G["extra"] = [Point(top_c).buffer(hv, quad_segs=32), bud(top_c, hv, dot_c, r, hv * 0.36)]
            G["neck_accent"] = True
        else:
            r = wv * 0.66 if style != "node" else wv * M["node"] * 1.0
            gap = wv * 0.62 if style != "node" else 8
            P += [Stroke([(hv, xt), (hv, 100)], "v", nodes=(False, True)),
                  Dot(hv, xt - gap - r, r, accent=True)]
        G.update(width=wv, sb=(2.5, 2.5))
    elif ch == "t":
        Wt = 36.0
        xs = 11.0 + hv
        top = xt - 17
        if style == "node":
            P += [Stroke([(xs, top), (xs, 100)], "v"), Stroke([(0, xt + hh), (Wt, xt + hh)], "h")]
        else:
            rh = 13.0
            pts = [(xs, top), (xs, 100 - hh - rh)] + arc(xs + rh, 100 - hh - rh, rh, 180, 90)[1:] + [(Wt - 1, 100 - hh)]
            P += [Stroke(pts, "v"), Stroke([(0, xt + hh), (Wt - 3, xt + hh)], "h")]
        G.update(width=Wt, sb=(0.5, 0.5))
    else:
        raise KeyError(ch)
    return G


KERN = {("E", "o"): -2, ("P", "o"): -3, ("n", "t"): -1, ("E", "O"): -3, ("P", "O"): -5,
        ("O", "N"): -1, ("O", "I"): -1, ("N", "T"): -1, ("e", "o"): 0, ("p", "o"): -1}


def word_text(style):
    return {"split": "eonpoint", "neck": "EonPoint", "node": "EONPOINT"}[style]
