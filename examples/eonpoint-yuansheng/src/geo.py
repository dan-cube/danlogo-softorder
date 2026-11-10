"""Geometry kernel — every curve in the EonPoint marks is built from circles.

A "cell" is a circle. A "neck" (the moment of division) is the region between
two cells bounded by two fillet arcs that are tangent to both cells.  The
fillet radius is solved so the narrowest point of the neck has an exact width,
which is what keeps every connection in the system visually identical.
"""
import math


def n(x):
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def P(x, y):
    return (float(x), float(y))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, k):
    return (a[0] * k, a[1] * k)


def length(a):
    return math.hypot(a[0], a[1])


def unit(a):
    l = length(a)
    return (a[0] / l, a[1] / l)


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def polar(c, r, deg):
    t = math.radians(deg)
    return (c[0] + r * math.cos(t), c[1] + r * math.sin(t))


def rot(p, deg, c=(0, 0)):
    t = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(t) - y * math.sin(t), c[1] + x * math.sin(t) + y * math.cos(t))


def circle(c, r):
    x, y = c
    return (f"M{n(x - r)} {n(y)}A{n(r)} {n(r)} 0 1 0 {n(x + r)} {n(y)}"
            f"A{n(r)} {n(r)} 0 1 0 {n(x - r)} {n(y)}Z")


def _fillet(p1, r1, p2, r2, R, side):
    d = length(sub(p2, p1))
    u = unit(sub(p2, p1))
    nrm = (-u[1], u[0]) if side > 0 else (u[1], -u[0])
    a, b = r1 + R, r2 + R
    x = (a * a - b * b + d * d) / (2 * d)
    h2 = a * a - x * x
    if h2 <= 0:
        return None
    h = math.sqrt(h2)
    F = add(add(p1, mul(u, x)), mul(nrm, h))
    T1 = add(p1, mul(unit(sub(F, p1)), r1))
    T2 = add(p2, mul(unit(sub(F, p2)), r2))
    return F, T1, T2, h - R


def neck_halfwidth(p1, r1, p2, r2, R):
    f = _fillet(p1, r1, p2, r2, R, 1)
    return None if f is None else f[3]


def solve_R(p1, r1, p2, r2, half):
    """Fillet radius giving a neck whose narrowest half-width == half."""
    d = length(sub(p2, p1))
    lo = max((d - r1 - r2) / 2 + 1e-9, 1e-6)
    # half-width rises then falls for unequal cells: walk up to the first R that reaches it
    hi, best = lo, (lo, -1e9)
    while hi < 1e4:
        w = neck_halfwidth(p1, r1, p2, r2, hi)
        if w is not None and w > best[1]:
            best = (hi, w)
        if w is not None and w >= half:
            break
        lo, hi = hi, hi * 1.08
    else:
        return best[0]
    for _ in range(200):
        mid = (lo + hi) / 2
        w = neck_halfwidth(p1, r1, p2, r2, mid)
        if w is None or w < half:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def neck(p1, r1, p2, r2, half=None, R=None):
    """Path for the bridge between two cells. Give either neck half-width or fillet R."""
    if R is None:
        R = solve_R(p1, r1, p2, r2, half)
    up = _fillet(p1, r1, p2, r2, R, 1)
    dn = _fillet(p1, r1, p2, r2, R, -1)
    Fu, T1u, T2u, _ = up
    Fd, T1d, T2d, _ = dn
    s1 = 1 if cross(sub(T1u, Fu), sub(T2u, Fu)) > 0 else 0
    s2 = 1 if cross(sub(T2d, Fd), sub(T1d, Fd)) > 0 else 0
    return (f"M{n(T1u[0])} {n(T1u[1])}A{n(R)} {n(R)} 0 0 {s1} {n(T2u[0])} {n(T2u[1])}"
            f"L{n(T2d[0])} {n(T2d[1])}A{n(R)} {n(R)} 0 0 {s2} {n(T1d[0])} {n(T1d[1])}Z")


def neck_info(p1, r1, p2, r2, half=None, R=None):
    if R is None:
        R = solve_R(p1, r1, p2, r2, half)
    up = _fillet(p1, r1, p2, r2, R, 1)
    dn = _fillet(p1, r1, p2, r2, R, -1)
    return {"R": R, "Fu": up[0], "Fd": dn[0], "T": (up[1], up[2], dn[1], dn[2]), "half": up[3]}


def capsule(p1, p2, r):
    u = unit(sub(p2, p1))
    nv = (-u[1], u[0])
    a1, a2 = add(p1, mul(nv, r)), add(p2, mul(nv, r))
    b2, b1 = add(p2, mul(nv, -r)), add(p1, mul(nv, -r))
    return (f"M{n(a1[0])} {n(a1[1])}L{n(a2[0])} {n(a2[1])}A{n(r)} {n(r)} 0 0 0 {n(b2[0])} {n(b2[1])}"
            f"L{n(b1[0])} {n(b1[1])}A{n(r)} {n(r)} 0 0 0 {n(a1[0])} {n(a1[1])}Z")


def bbox_circles(cells):
    xs0 = min(c[0][0] - c[1] for c in cells)
    ys0 = min(c[0][1] - c[1] for c in cells)
    xs1 = max(c[0][0] + c[1] for c in cells)
    ys1 = max(c[0][1] + c[1] for c in cells)
    return xs0, ys0, xs1, ys1


class Mark:
    """A mark = cells + necks (+ an accent point), normalised into a box."""

    def __init__(self, cells, necks, accent=None, name=""):
        # cells: list of ((x,y), r); necks: list of (i, j, half) ; accent: ((x,y), r)
        self.cells = cells
        self.necks = necks
        self.accent = accent
        self.name = name

    def all_circles(self):
        return self.cells + ([self.accent] if self.accent else [])

    def transformed(self, size=240, pad=0.0):
        allc = self.all_circles()
        x0, y0, x1, y1 = bbox_circles(allc)
        w, h = x1 - x0, y1 - y0
        k = (size * (1 - 2 * pad)) / max(w, h)
        ox = (size - w * k) / 2 - x0 * k
        oy = (size - h * k) / 2 - y0 * k
        f = lambda c: ((c[0][0] * k + ox, c[0][1] * k + oy), c[1] * k)
        m = Mark([f(c) for c in self.cells], [(i, j, hw * k) for i, j, hw in self.necks],
                 f(self.accent) if self.accent else None, self.name)
        return m

    def body_parts(self):
        """List of path data; drawn as separate <path>s so winding never punches holes."""
        parts = [circle(c, r) for c, r in self.cells]
        for i, j, hw in self.necks:
            (p1, r1), (p2, r2) = self.cells[i], self.cells[j]
            parts.append(neck(p1, r1, p2, r2, half=hw))
        return parts

    def body_svg(self, fill):
        return "".join(f'<path d="{d}" fill="{fill}"/>' for d in self.body_parts())

    def accent_d(self):
        if not self.accent:
            return ""
        return circle(*self.accent)
