"""R4 geometry: organic cell clusters with hidden order.

Elements
  cell     (c, r)                      a round cell
  capsule  (p1, p2, r)                 an elongating cell
  bridge   (i, j, w_out, w_in)         an asymmetric neck between cells i and j;
                                       w_out / w_in are the distances of the two
                                       fillet-bounded edges from the centre line,
                                       so a larger w_out bows the bridge outward.
"""
import math
from geo import n, add, sub, mul, length, unit, cross, polar, circle, _fillet, neck_halfwidth, solve_R


def bridge_path(p1, r1, p2, r2, w_out, w_in, out_side):
    """Neck whose two edges sit w_out / w_in from the axis (out_side = +1/-1 picks which normal is 'out')."""
    Ro = solve_R(p1, r1, p2, r2, w_out)
    Ri = solve_R(p1, r1, p2, r2, w_in)
    Fo, T1o, T2o, _ = _fillet(p1, r1, p2, r2, Ro, out_side)
    Fi, T1i, T2i, _ = _fillet(p1, r1, p2, r2, Ri, -out_side)
    s1 = 1 if cross(sub(T1o, Fo), sub(T2o, Fo)) > 0 else 0
    s2 = 1 if cross(sub(T2i, Fi), sub(T1i, Fi)) > 0 else 0
    d = (f"M{n(T1o[0])} {n(T1o[1])}A{n(Ro)} {n(Ro)} 0 0 {s1} {n(T2o[0])} {n(T2o[1])}"
         f"L{n(T2i[0])} {n(T2i[1])}A{n(Ri)} {n(Ri)} 0 0 {s2} {n(T1i[0])} {n(T1i[1])}Z")
    return d, dict(Fo=Fo, Ro=Ro, Fi=Fi, Ri=Ri)


def capsule_path(p1, p2, r):
    u = unit(sub(p2, p1))
    nv = (-u[1], u[0])
    a1, a2 = add(p1, mul(nv, r)), add(p2, mul(nv, r))
    b2, b1 = add(p2, mul(nv, -r)), add(p1, mul(nv, -r))
    return (f"M{n(a1[0])} {n(a1[1])}L{n(a2[0])} {n(a2[1])}A{n(r)} {n(r)} 0 0 0 {n(b2[0])} {n(b2[1])}"
            f"L{n(b1[0])} {n(b1[1])}A{n(r)} {n(r)} 0 0 0 {n(a1[0])} {n(a1[1])}Z")


class Cluster:
    def __init__(self, cells, bridges, capsules, accent, center=(0, 0), name="", meta=None):
        self.cells = cells          # [(c, r)]
        self.bridges = bridges      # [(i, j, w_out, w_in)]
        self.capsules = capsules    # [(p1, p2, r)]
        self.accent = accent        # (c, r)
        self.center = center
        self.name = name
        self.meta = meta or {}

    # every round extent, for bounding boxes
    def discs(self):
        d = list(self.cells)
        for cap in self.capsules:
            d += [(cap[0], cap[2]), (cap[1], cap[2])]
        if self.accent:
            d.append(self.accent)
        return d

    def bbox(self):
        ds = self.discs()
        return (min(c[0] - r for c, r in ds), min(c[1] - r for c, r in ds),
                max(c[0] + r for c, r in ds), max(c[1] + r for c, r in ds))

    def map(self, f, k):
        """Apply point map f and scale k to every element."""
        return Cluster([(f(c), r * k) for c, r in self.cells],
                       [(i, j, wo * k, wi * k) for i, j, wo, wi in self.bridges],
                       [(f(c[0]), f(c[1]), c[2] * k) + tuple(c[3:]) for c in self.capsules],
                       (f(self.accent[0]), self.accent[1] * k) if self.accent else None,
                       f(self.center), self.name, self.meta)

    def fit(self, size=240.0):
        x0, y0, x1, y1 = self.bbox()
        k = size / max(x1 - x0, y1 - y0)
        ox = (size - (x1 - x0) * k) / 2 - x0 * k
        oy = (size - (y1 - y0) * k) / 2 - y0 * k
        return self.map(lambda p: (p[0] * k + ox, p[1] * k + oy), k)

    def out_side(self, i, j):
        """Which normal of the i→j axis points away from the cluster centre."""
        (p1, _), (p2, _) = self.cells[i], self.cells[j]
        u = unit(sub(p2, p1))
        nrm = (-u[1], u[0])
        mid = mul(add(p1, p2), 0.5)
        return 1 if (nrm[0] * (mid[0] - self.center[0]) + nrm[1] * (mid[1] - self.center[1])) > 0 else -1

    def body_parts(self):
        parts = [circle(c, r) for c, r in self.cells]
        for i, j, wo, wi in self.bridges:
            (p1, r1), (p2, r2) = self.cells[i], self.cells[j]
            parts.append(bridge_path(p1, r1, p2, r2, wo, wi, self.out_side(i, j))[0])
        for cap in self.capsules:
            a, b, r = cap[:3]
            waist = cap[3] if len(cap) > 3 else 1.0
            if waist >= 0.999:
                parts.append(capsule_path(a, b, r))
            else:
                # an elongating cell that has just begun to pinch: two lobes + a shallow neck
                parts += [circle(a, r), circle(b, r), bridge_path(a, r, b, r, waist * r, waist * r, 1)[0]]
        return parts

    def bridge_info(self):
        out = []
        for i, j, wo, wi in self.bridges:
            (p1, r1), (p2, r2) = self.cells[i], self.cells[j]
            out.append(bridge_path(p1, r1, p2, r2, wo, wi, self.out_side(i, j))[1])
        return out

    def body_svg(self, fill):
        return "".join(f'<path d="{d}" fill="{fill}"/>' for d in self.body_parts())

    def accent_d(self):
        return circle(*self.accent) if self.accent else ""


def gap(a, b):
    """Edge-to-edge distance between two discs."""
    return length(sub(a[0], b[0])) - a[1] - b[1]
