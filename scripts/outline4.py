"""Turn the centre-line lettering into soft-cornered outlines (needs shapely).

The stroke skeletons come from letters.py; here they are expanded, unioned and given
a small corner radius so the type shares the softness of the cells without becoming
a "rounded font".
"""
import math, re
from shapely.geometry import LineString, LinearRing, Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from geo import n

TOK = re.compile(r"[MLHVAZ]|-?\d*\.?\d+(?:e-?\d+)?")


def _arc_points(x1, y1, rx, ry, phi, fa, fs, x2, y2, seg=10):
    # SVG endpoint -> centre parameterisation (rx == ry, phi == 0 in our glyphs)
    r = rx
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    d2 = dx * dx + dy * dy
    if d2 > r * r:
        r = math.sqrt(d2)
    sign = -1 if fa == fs else 1
    co = sign * math.sqrt(max(0.0, (r * r - d2) / d2)) if d2 else 0
    cx = co * dy + (x1 + x2) / 2
    cy = -co * dx + (y1 + y2) / 2
    t1 = math.atan2(y1 - cy, x1 - cx)
    t2 = math.atan2(y2 - cy, x2 - cx)
    dt = t2 - t1
    if fs and dt < 0:
        dt += 2 * math.pi
    elif not fs and dt > 0:
        dt -= 2 * math.pi
    steps = max(2, int(abs(dt) / (math.pi / 2) * seg))
    return [(cx + r * math.cos(t1 + dt * i / steps), cy + r * math.sin(t1 + dt * i / steps)) for i in range(1, steps + 1)]


def parse(d):
    """-> list of (points, closed) sub-paths."""
    toks = TOK.findall(d)
    i, cur, subs, pts, closed = 0, (0.0, 0.0), [], [], False
    cmd = None
    while i < len(toks):
        t = toks[i]
        if t in "MLHVAZ":
            cmd = t
            i += 1
            if cmd == "Z":
                subs.append((pts, True))
                pts = []
                continue
        if cmd == "M":
            if pts:
                subs.append((pts, False))
            cur = (float(toks[i]), float(toks[i + 1]))
            pts = [cur]
            i += 2
            cmd = "L"
        elif cmd == "L":
            cur = (float(toks[i]), float(toks[i + 1]))
            pts.append(cur)
            i += 2
        elif cmd == "H":
            cur = (float(toks[i]), cur[1])
            pts.append(cur)
            i += 1
        elif cmd == "V":
            cur = (cur[0], float(toks[i]))
            pts.append(cur)
            i += 1
        elif cmd == "A":
            rx, ry, phi, fa, fs, x, y = [float(v) for v in toks[i:i + 7]]
            pts += _arc_points(cur[0], cur[1], rx, ry, phi, int(fa), int(fs), x, y)
            cur = (x, y)
            i += 7
    if pts:
        subs.append((pts, False))
    return subs


def stroke_geom(d, w, dx=0.0):
    geoms = []
    for pts, closed in parse(d):
        pts = [(x + dx, y) for x, y in pts]
        if closed:
            # closed outlines (o rings, 口 boxes): ring = outer buffer minus inner
            geoms.append(LinearRing(pts).buffer(w / 2, join_style="mitre", mitre_limit=10))
        else:
            geoms.append(LineString(pts).buffer(w / 2, cap_style="flat", join_style="mitre", mitre_limit=10))
    return geoms


def soften(g, convex, concave):
    if concave:
        g = g.buffer(concave, join_style="round", quad_segs=8).buffer(-concave, join_style="round", quad_segs=8)
    if convex:
        g = g.buffer(-convex, join_style="round", quad_segs=8).buffer(convex, join_style="round", quad_segs=8)
    return g


def to_path(g):
    polys = [g] if isinstance(g, Polygon) else list(getattr(g, "geoms", []))
    out = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)[:-1]
            out.append("M" + "L".join(f"{x:.2f} {y:.2f}".replace(".00", "") for x, y in cs) + "Z")
    return "".join(out)


def outline(strokes, w, dots=(), convex=2.0, concave=1.0):
    """strokes: [(d, dx)] centre-lines; dots: [(x, y, r)] -> one soft-cornered path."""
    gs = []
    for d, dx in strokes:
        gs += stroke_geom(d, w, dx)
    g = unary_union(gs)
    g = soften(g, convex, concave)
    for x, y, r in dots:
        g = g.union(Point(x, y).buffer(r, quad_segs=24))
    return to_path(g)
