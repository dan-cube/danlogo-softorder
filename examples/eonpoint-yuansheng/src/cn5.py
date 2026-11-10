"""Custom 亿触点 (no fonts). Em 100, y down. One skeleton, three renderings."""
import math
from type5 import Stroke, Ring, Dot, arc
from en5 import AXIS


def metrics(style):
    if style == "split":
        return dict(wv=13.5, wh=10.5, wd=12.8, gap=12.0, cut=2.2)
    if style == "neck":
        return dict(wv=11.0, wh=8.4, wd=10.4, gap=12.0)
    return dict(wv=5.0, wh=5.0, wd=5.0, gap=30.0, node=1.05)


WEIGHT = {"触": 0.86}   # the densest character carries a lighter stroke so all three read the same grey


def quad(p0, c, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def _box(x0, y0, x1, y1, W):
    """口: four strokes that close cleanly at the corners (each extended over the other's width)."""
    ev, eh = W["v"] / 2, W["h"] / 2
    foot = 1.0
    return [Stroke([(x0, y0 - eh), (x0, y1 + eh * foot)], "v", nodes=(False, False)),
            Stroke([(x1, y0 - eh), (x1, y1 + eh)], "v", nodes=(False, False)),
            Stroke([(x0 - ev, y0), (x1 + ev, y0)], "h", nodes=(False, False)),
            Stroke([(x0, y1), (x1, y1)], "h", nodes=(False, False))]


def _axis_cut(cx, cy, L, w):
    u = (math.cos(math.radians(AXIS)), math.sin(math.radians(AXIS)))
    return dict(line=[(cx - u[0] * L, cy - u[1] * L), (cx + u[0] * L, cy + u[1] * L)], w=w)


def glyph(ch, M, style):
    k = WEIGHT.get(ch, 1.0)
    W = {"v": M["wv"] * k, "h": M["wh"] * k, "d": M["wd"] * k, "c": (M["wv"] * 0.55 + M["wh"] * 0.45) * k,
         "node": M.get("node", 1.25)}
    G = dict(prims=[], width=100, sb=(0, 0), cuts=[], extra=[], W=W)
    P = G["prims"]
    cw = M.get("cut", 2.2)
    dot_r = W["v"] * (M.get("dot", 0.70) if style != "node" else W["node"] * 1.05)
    if ch == "亿":
        pie = quad((31, 5), (25, 28), (6, 46))
        xv = 20.5
        yv = next(p[1] for a, p in zip(pie, pie[1:]) if p[0] <= xv)      # where the 撇 crosses the vertical
        P += [Stroke(pie, "d", taper=0.78 if style != "node" else None),
              Stroke([(xv, yv + 1.0), (xv, 97)], "v", nodes=(False, True)),
              Stroke([(41, 15.5), (86.5, 15.5), (48, 57), (48, 79)] + arc(60, 79, 12, 180, 90)[1:] + [(83, 91)] +
                     arc(83, 82, 9, 90, 0)[1:] + [(92, 74)], "c", nodes=(True, True))]
        if style == "split":
            G["cuts"] += [dict(line=[(14, 17), (30, 26)], w=cw)]          # 亻: the vertical leaves the 撇
    elif ch == "触":
        xl, xm, xr = 8.5, 25.0, 41.5
        top, h1, h2 = 29.0, 46.5, 63.5
        P += [Stroke([(20.5, 2.5), (9, 18)], "d", taper=0.82 if style != "node" else None, nodes=(True, False)),
              Stroke([(16.2, 10.5), (35.5, 10.5), (27.5, top - W["h"] / 2)], "h", nodes=(False, False)),
              Stroke([(xl, top - W["h"] / 2), (xl, 78)] + quad((xl, 78), (xl, 90), (2.5, 97))[1:], "v", nodes=(False, True)),
              Stroke([(xl - W["v"] / 2, top), (xr + W["v"] / 2, top)], "h", nodes=(False, False)),
              Stroke([(xr, top - W["h"] / 2), (xr, 97)], "v", nodes=(False, True)),
              Stroke([(xl, h1), (xr, h1)], "h", nodes=(False, False)),
              Stroke([(xl, h2), (xr, h2)], "h", nodes=(False, False)),
              Stroke([(xm, top), (xm, h2)], "v", nodes=(False, False))]
        bx0, bx1, by0, by1 = 57.0, 92.5, 26.0, 59.5
        P += _box(bx0, by0, bx1, by1, W)
        cxv = (bx0 + bx1) / 2
        P += [Stroke([(cxv, by0), (cxv, 92.0)], "v", nodes=(False, False)),
              Stroke([(53.5, 96), (86, 89)], "d", taper=0.85 if style != "node" else None),
              Dot(87.5, 79.5, dot_r * 0.84, accent=False)]
        if style == "split":
            G["cuts"].append(_axis_cut(89.5, 80.0, dot_r * 1.4, cw))
    elif ch == "点":
        P += [Stroke([(47, 2.5), (47, 38)], "v", nodes=(True, False)),
              Stroke([(47, 19.5), (79.5, 19.5)], "h", nodes=(False, True))]
        P += _box(20, 38.5, 80, 65.5, W)
        y = 88.5
        P += [Dot(12.5, y, dot_r), Dot(37.5, y, dot_r), Dot(62.5, y, dot_r), Dot(87.5, y, dot_r)]
        if style == "split":
            for x in (12.5, 37.5, 62.5, 87.5):
                G["cuts"].append(_axis_cut(x, y, dot_r * 1.4, cw))
    else:
        raise KeyError(ch)
    return G
