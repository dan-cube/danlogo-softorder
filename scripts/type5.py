"""R5 lettering engine — custom letterforms, no fonts.

Every glyph is a list of primitives on a 100-unit cap height (y grows downward,
baseline at y = 100).  The same skeleton is rendered in three styles that borrow
the mark's grammar:

  cell  笔画是拉长的细胞：圆头，交接处像分裂颈一样柔和融合
  neck  笔画利落平切；每个内交角被一道圆弧“缢缩”切进去（墨阱）
  node  极细笔画；每一个自由端点都是一个圆点——笔画的尽头就是触点
"""
import math
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import affinity

QS = 24  # quarter-circle resolution


# ───────────────────────────── primitives ─────────────────────────────

class Stroke:
    """Open or closed centre-line with a role ('v' vertical-ish, 'h' horizontal-ish,
    'd' diagonal, 'c' curve) and optional taper (end width factor)."""

    def __init__(self, pts, role="v", closed=False, taper=None, nodes=(True, True)):
        self.pts, self.role, self.closed, self.taper, self.nodes = pts, role, closed, taper, nodes


class Ring:
    """Ellipse ring: outer (rx, ry); inner shrunk by wv sideways / wh top & bottom.
    clip: optional shapely geometry the ring is intersected with."""

    def __init__(self, cx, cy, rx, ry, clip=None, aperture=None, idx=0.0, irx=None, iry=None):
        self.cx, self.cy, self.rx, self.ry, self.clip, self.aperture = cx, cy, rx, ry, clip, aperture
        self.idx, self.irx, self.iry = idx, irx, iry      # inner-ellipse offset / radii (optical thinning)


class Dot:
    def __init__(self, cx, cy, r, accent=False):
        self.cx, self.cy, self.r, self.accent = cx, cy, r, accent


def arc(cx, cy, r, a0, a1, steps=None, ry=None):
    """Points along an arc, angles in degrees (screen coords: 0 = right, 90 = down)."""
    ry = r if ry is None else ry
    steps = steps or max(6, int(abs(a1 - a0) / 4))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]


def _taper_poly(pts, w0, w1):
    """Polygon around a polyline whose width runs linearly from w0 to w1."""
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = L[-1] or 1
    left, right = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = (w0 + (w1 - w0) * L[i] / tot) / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    return Polygon(left + right[::-1]).buffer(0)


def _shorten(pts, d0, d1):
    pts = list(pts)

    def cut(seq, d):
        while d > 0 and len(seq) > 1:
            a, b = seq[0], seq[1]
            l = math.hypot(b[0] - a[0], b[1] - a[1])
            if l > d:
                t = d / l
                seq[0] = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                return seq
            seq.pop(0)
            d -= l
        return seq
    pts = cut(pts, d0)
    pts = cut(pts[::-1], d1)[::-1]
    return pts


def stroke_geom(s, W, cap="flat"):
    w = W[s.role]
    if cap == "round" and not s.closed:
        pts = _shorten(s.pts, w / 2, w / 2)
        if len(pts) >= 2:
            s = Stroke(pts, s.role, s.closed, s.taper, s.nodes)
    if s.closed:
        return Polygon(s.pts).exterior.buffer(w / 2, join_style="mitre", mitre_limit=8, quad_segs=QS)
    if s.taper:
        g = _taper_poly(s.pts, w, w * s.taper)
        return g.buffer(w * 0.5, quad_segs=QS) .buffer(-w * 0.5, quad_segs=QS) if cap == "round" else g
    return LineString(s.pts).buffer(w / 2, cap_style=cap, join_style="mitre", mitre_limit=8, quad_segs=QS)


def ring_geom(r, W):
    outer = affinity.scale(Point(0, 0).buffer(1, quad_segs=QS * 3), r.rx, r.ry, origin=(0, 0))
    irx = r.irx if r.irx is not None else r.rx - W["v"]
    iry = r.iry if r.iry is not None else r.ry - W["h"]
    inner = affinity.translate(affinity.scale(Point(0, 0).buffer(1, quad_segs=QS * 3), irx, iry, origin=(0, 0)), r.idx, 0)
    g = affinity.translate(outer.difference(inner), r.cx, r.cy)
    if r.clip is not None:
        g = g.intersection(r.clip)
    if r.aperture is not None:
        g = g.difference(r.aperture)
    return g


# ───────────────────────────── styles ─────────────────────────────

def _reflex_vertices(poly, min_turn=28.0):
    out = []
    p = orient(poly, sign=1.0)
    for ring in [p.exterior] + list(p.interiors):
        cs = list(ring.coords)[:-1]
        n = len(cs)
        for i in range(n):
            a, b, c = cs[i - 1], cs[i], cs[(i + 1) % n]
            v1 = (b[0] - a[0], b[1] - a[1])
            v2 = (c[0] - b[0], c[1] - b[1])
            cr = v1[0] * v2[1] - v1[1] * v2[0]
            dt = v1[0] * v2[0] + v1[1] * v2[1]
            turn = math.degrees(math.atan2(cr, dt))
            if turn < -min_turn:            # right turn with material on the left = concave corner
                # bisector pointing into the material
                l1 = math.hypot(*v1) or 1
                l2 = math.hypot(*v2) or 1
                u1 = (v1[0] / l1, v1[1] / l1)
                u2 = (v2[0] / l2, v2[1] / l2)
                bis = (-u1[0] + u2[0], -u1[1] + u2[1])
                lb = math.hypot(*bis) or 1
                out.append((b, (bis[0] / lb, bis[1] / lb), -turn))
    return out


def polys(g):
    return [g] if isinstance(g, Polygon) else [x for x in getattr(g, "geoms", []) if isinstance(x, Polygon)]


def render(glyph, style, W, dot_scale=1.0):
    """-> (body geometry, accent geometry or None)."""
    parts = []
    cap = "flat"
    for prim in glyph["prims"]:
        if isinstance(prim, Stroke):
            parts.append(stroke_geom(prim, W, cap))
        elif isinstance(prim, Ring):
            parts.append(ring_geom(prim, W))
    g = unary_union(parts) if parts else Polygon()
    if glyph.get("clip") is not None:
        g = g.intersection(glyph["clip"])
    if style == "split":
        # the dividing moment: hairline cuts through bowls / at junctions
        cuts = [LineString(c["line"]).buffer(c.get("w", W["v"] * 0.16) / 2, cap_style="flat") for c in glyph.get("cuts", [])]
        if cuts:
            g = g.difference(unary_union(cuts))
        soft = W["h"] * 0.05
        g = g.buffer(-soft, quad_segs=8).buffer(soft, quad_segs=8)
    elif style == "neck":
        soft = W["h"] * 0.04
        g = g.buffer(-soft, quad_segs=8).buffer(soft, quad_segs=8)
    elif style == "node":
        nodes = []
        strokes = [p for p in glyph["prims"] if isinstance(p, Stroke)]
        others_all = [stroke_geom(s, W, "flat") for s in strokes] + [ring_geom(r, W) for r in glyph["prims"] if isinstance(r, Ring)]
        for i, s in enumerate(strokes):
            if s.closed:
                continue
            others = unary_union([o for j, o in enumerate(others_all) if j != i])
            for k, pt in ((0, s.pts[0]), (1, s.pts[-1])):
                if not s.nodes[k]:
                    continue
                if others.is_empty or others.distance(Point(pt)) > W["v"] * 0.8:
                    nodes.append(Point(pt).buffer(W["v"] * W.get("node", 1.25), quad_segs=QS))
        g = unary_union([g] + nodes)
    for extra in glyph.get("extra", []):
        g = unary_union([g, extra])
    acc = None
    dots = [d for d in glyph["prims"] if isinstance(d, Dot)]
    dg = [Point(d.cx, d.cy).buffer(d.r * dot_scale, quad_segs=QS * 2) for d in dots if not d.accent]
    ag = [Point(d.cx, d.cy).buffer(d.r * dot_scale, quad_segs=QS * 2) for d in dots if d.accent]
    if dg:
        g = unary_union([g] + dg)
        if style == "split" and glyph.get("cuts"):
            cut = unary_union([LineString(c["line"]).buffer(c.get("w", W["v"] * 0.16) / 2, cap_style="flat") for c in glyph["cuts"]])
            g = g.difference(cut)
    if ag:
        acc = unary_union(ag)
    return g, acc


def to_d(g, dx=0.0, dy=0.0, k=1.0, tol=0.035):
    out = []
    g = g.simplify(tol, preserve_topology=True)
    for p in polys(g):
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)[:-1]
            out.append("M" + "L".join(f"{(x * k + dx):.1f} {(y * k + dy):.1f}".replace(".0 ", " ") for x, y in cs) + "Z")
    return "".join(out)


def layout(glyphs, track=0.0, kern=None, text=""):
    """glyphs: list of (geom, accent, glyph-dict). -> (body, accent, width)."""
    kern = kern or {}
    x = 0.0
    body, accs = [], []
    prev = None
    for ch, (g, a, G) in zip(text, glyphs):
        if prev is not None:
            x += track + kern.get((prev, ch), 0)
        x += G["sb"][0]
        body.append(affinity.translate(g, x, 0))
        if a is not None:
            accs.append(affinity.translate(a, x, 0))
        x += G["width"] + G["sb"][1]
        prev = ch
    width = x - glyphs[-1][2]["sb"][1]
    return unary_union(body), (unary_union(accs) if accs else None), width


def bud(c1, r1, c2, r2, half):
    """Fillet neck between two discs (the mark's division neck) as a polygon."""
    from geo import neck
    from outline4 import parse
    d = neck(c1, r1, c2, r2, half=half)
    pts = parse(d)[0][0]
    return Polygon(pts).buffer(0)
