"""R4 marks — the original composition, measured, then deepened with hidden rules.

Measured from the reference (px): the cluster is a vortex.
  outer orbit  A (top) · C (left) · E (bottom-right)   ≈ 170 px from the centre, ≈ 120° apart
  inner orbit  B · D · capsule                          ≈ 105 px, ≈ 120° apart
  every outer cell links ~70° counter-clockwise to the next inner element.
Read counter-clockwise it is one full division cycle:
  E (round, at rest) → capsule (stretching) → A–B (pinching) → C–D (about to split).
"""
import math
from geo import polar, length, sub, add, mul, unit, rot
from cells import Cluster, gap

PHI = (1 + 5 ** 0.5) / 2
O_IMG = (398.0, 422.0)


def original():
    """Straight trace of the reference, for comparison only."""
    o = O_IMG
    f = lambda p: (p[0] - o[0], p[1] - o[1])
    cells = [(f((447, 254)), 46.5), (f((311, 343)), 45.0), (f((229, 437)), 53.0),
             (f((388, 525)), 47.0), (f((509, 544)), 57.0)]
    bridges = [(0, 1, 19.0, 11.0), (2, 3, 14.0, 11.0)]
    caps = [(f((500, 429)), f((477, 352)), 39.0)]
    return Cluster(cells, bridges, caps, (f((576, 231)), 49.6), (0, 0), "original")


def vortex(theta_a=-73.7, R_o=170.0, R_i=104.0, twist=-70.0, s=46.5, k=1.107, q=0.93,
           pill_ratio=0.68, nu=(0.34, 0.27), bow=0.10, lime_r=1.0, lime_gap=1.6,
           lime_dir=30.0, R_scale=(1, 1, 1), Ri_scale=(1, 1, 1), name="genesis", pill_tilt=0.0,
           pill_shift=0.0, d_ang=(0, 0, 0, 0, 0, 0), waist=1.0):
    """The hidden system.  Positions: two orbits of three, 120° apart, inner ring twisted.
    Sizes: outer cells grow ×k along the flow (A→C→E); daughters ×q; the capsule keeps
    the area of E (volume conservation).  Necks thin along the flow (nu).  The lime point
    has A's size and is flung out lime_dir° off the clockwise tangent at A."""
    ang = [theta_a, theta_a - 120, theta_a - 240]
    rA, rC, rE = s, s * k, s * k * k
    da = d_ang      # small per-element angular offsets (A, C, E, B, D, capsule) — the "irregular" part
    A = polar((0, 0), R_o * R_scale[0], ang[0] + da[0])
    C = polar((0, 0), R_o * R_scale[1], ang[1] + da[1])
    E = polar((0, 0), R_o * R_scale[2], ang[2] + da[2])
    B = polar((0, 0), R_i * Ri_scale[0], ang[0] + twist + da[3])
    D = polar((0, 0), R_i * Ri_scale[1], ang[1] + twist + da[4])
    P = polar((0, 0), R_i * Ri_scale[2], ang[2] + twist + da[5])
    rB, rD = rA * q, rC * q
    # capsule: radius pr, centre-line length L with  π pr² + 2 pr L = π rE²
    pr = rE * pill_ratio
    L = (math.pi * rE * rE - math.pi * pr * pr) / (2 * pr)
    tdir = ang[2] + twist + da[5] - 90 + pill_tilt  # counter-clockwise tangent of the inner orbit
    u = polar((0, 0), 1, tdir)
    P = add(P, mul(u, pill_shift))
    P1 = add(P, mul(u, -L / 2))                     # end near E
    P2 = add(P, mul(u, L / 2))                      # end pointing at A
    cells = [(A, rA), (B, rB), (C, rC), (D, rD), (E, rE)]
    bridges = []
    for (i, j), v in zip(((0, 1), (2, 3)), nu):
        m = min(cells[i][1], cells[j][1])
        w_in = v * m
        bridges.append((i, j, w_in + bow * m, w_in))
    # lime
    lr = rA * lime_r
    tang_cw = ang[0] + 90
    dirv = polar((0, 0), 1, tang_cw - lime_dir)
    g = equal_gap_estimate(cells, (P1, P2, pr))
    Lc = add(A, mul(dirv, rA + lr + lime_gap * g))
    cl = Cluster(cells, bridges, [(P1, P2, pr, waist)], (Lc, lr), (0, 0), name)
    cl.meta = dict(gaps=gaps(cl), L=L, pr=pr, g=g)
    return cl


def gaps(cl):
    (A, B, C, D, E) = cl.cells
    P1, P2, pr = cl.capsules[0][:3]
    return {"A–胶囊": gap(A, (P2, pr)), "B–C": gap(B, C), "D–E": gap(D, E), "胶囊–E": gap((P1, pr), E)}


def equal_gap_estimate(cells, cap):
    (A, B, C, D, E) = cells
    P1, P2, pr = cap[:3]
    gs = [gap(A, (P2, pr)), gap(B, C), gap(D, E), gap((P1, pr), E)]
    return sum(gs) / len(gs)


def nelder_mead(f, x0, step, iters=600):
    n = len(x0)
    pts = [list(x0)] + [[x0[j] + (step[j] if j == i else 0) for j in range(n)] for i in range(n)]
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(n + 1), key=lambda i: vals[i])
        pts = [pts[i] for i in order]
        vals = [vals[i] for i in order]
        c = [sum(p[j] for p in pts[:-1]) / n for j in range(n)]
        xr = [c[j] + (c[j] - pts[-1][j]) for j in range(n)]
        fr = f(xr)
        if fr < vals[0]:
            xe = [c[j] + 2 * (c[j] - pts[-1][j]) for j in range(n)]
            fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = [c[j] + 0.5 * (pts[-1][j] - c[j]) for j in range(n)]
            fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                pts = [pts[0]] + [[pts[0][j] + 0.5 * (p[j] - pts[0][j]) for j in range(n)] for p in pts[1:]]
                vals = [vals[0]] + [f(p) for p in pts[1:]]
    return pts[0], vals[0]


def solve_equal_gaps(base, free, target=None, w_dev=0.002):
    """Tune the free params (dict name->step) so that all four separations are equal
    (optionally == target), staying close to the base values."""
    names = list(free)
    x0 = [base.get(k, 1.0) for k in names]

    def build(x):
        kw = dict(base)
        for k, v in zip(names, x):
            kw[k] = v
        return vortex(**pack(kw))

    def cost(x):
        try:
            cl = build(x)
        except Exception:
            return 1e9
        g = list(cl.meta["gaps"].values())
        m = target if target is not None else sum(g) / len(g)
        c = sum((v - m) ** 2 for v in g)
        c += w_dev * sum(((xi - x0i) / (abs(x0i) + 1)) ** 2 for xi, x0i in zip(x, x0)) * 1e4
        if min(g) < 4:
            c += 1e4
        return c

    x, v = nelder_mead(cost, x0, [free[k] for k in names])
    kw = dict(base)
    kw.update(dict(zip(names, x)))
    return pack(kw), build(x)



def pack(kw):
    """Scalar aliases R0..R2 / Ri0..Ri2 -> the per-element orbit scale tuples."""
    kw = dict(kw)
    if "R0" in kw:
        kw["R_scale"] = (kw.pop("R0"), kw.pop("R1"), kw.pop("R2"))
    if "Ri0" in kw:
        kw["Ri_scale"] = (kw.pop("Ri0"), kw.pop("Ri1"), kw.pop("Ri2"))
    return kw


def solve_rhythm(base, g, notch=PHI, w=1.0):
    """Find the smallest angular / radial offsets from the 120° model that make the
    separations exactly g, g, g and notch·g (B–C, the open vertex of the chevron)."""
    ri = base.get("Ri_scale", (1, 1, 1))

    def make(x):
        kw = dict(base)
        kw.update(d_ang=(0.0, x[0], x[1], x[2], x[3], x[4]),
                  Ri_scale=(ri[0] * (1 + x[5]), ri[1] * (1 + x[6]), ri[2] * (1 + x[7])),
                  pill_tilt=base.get("pill_tilt", 0.0) + x[8])
        return vortex(**kw)

    def cost(x):
        try:
            cl = make(x)
        except Exception:
            return 1e9
        G = cl.meta["gaps"]
        t = {"A–胶囊": g, "B–C": g * notch, "D–E": g, "胶囊–E": g}
        c = sum((G[k] - t[k]) ** 2 for k in t) * 50
        c += w * (sum(v * v for v in x[:5]) + 400 * sum(v * v for v in x[5:8]) + 0.3 * x[8] ** 2)
        return c

    x = [0.0] * 9
    for st in ([4] * 5 + [0.04] * 3 + [5], [1] * 5 + [0.01] * 3 + [1]):
        x, v = nelder_mead(cost, x, st, iters=5000)
    cl = make(x)
    cl.meta["offsets"] = x
    return cl


# ─── the three R4 marks ─────────────────────────────────────────────
FIT = dict(theta_a=-70.4, R_o=169.5, R_i=105.8, twist=-69.9, s=47.5, k=1.095, q=0.923,
           Ri_scale=(1.11, 0.975, 0.905))


def genesis():
    """01 原生 — the reference, with every hidden rule made exact."""
    cl = solve_rhythm(dict(FIT, nu=(0.32, 0.27), bow=0.09, lime_r=1.04, lime_gap=1.7, lime_dir=28), 20.0)
    cl.name = "genesis"
    return cl


def cycle():
    """02 周期 — the division cycle made legible: the capsule starts to pinch, necks thin
    along the flow, bridges bow outward so the cluster turns; the point is smaller, flung further."""
    cl = solve_rhythm(dict(FIT, nu=(0.30, 0.20), bow=0.17, lime_r=0.86, lime_gap=2.1, lime_dir=34,
                           waist=0.84, k=1.11), 21.0)
    cl.name = "cycle"
    return cl


def core():
    """03 凝聚 — the same vortex drawn tighter: shorter, fuller necks and narrow gaps give a
    bold silhouette that survives 16 px."""
    cl = solve_rhythm(dict(FIT, R_o=150.0, R_i=96.0, nu=(0.44, 0.38), bow=0.07, lime_r=1.0,
                           lime_gap=1.25, lime_dir=24), 12.0)
    cl.name = "core"
    return cl
