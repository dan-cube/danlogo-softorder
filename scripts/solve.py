"""Tiny dependency-free optimiser for logo geometry.

Two uses (see references/hidden-order.md):

  fit(model, params0, steps, measured)    – recover a parametric skeleton from a reference
  nelder_mead(cost, x0, steps)            – find the smallest offsets that satisfy constraints

Example — fit "three cells on one orbit, 120° apart" to measured centres:

    from geo import polar
    def model(p):                       # p = [radius, start_angle]
        return [polar((0, 0), p[0], p[1] + 120 * k) for k in range(3)]
    best, err = fit(model, [100, -90], [10, 5], measured_centres)
"""
import math


def nelder_mead(f, x0, step, iters=2000, tol=1e-10):
    """Minimise f(x) from x0. step: initial simplex size per variable."""
    n = len(x0)
    pts = [list(x0)] + [[x0[j] + (step[j] if j == i else 0) for j in range(n)] for i in range(n)]
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(n + 1), key=lambda i: vals[i])
        pts = [pts[i] for i in order]
        vals = [vals[i] for i in order]
        if abs(vals[-1] - vals[0]) < tol:
            break
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


def fit(model, params0, steps, measured, restarts=3):
    """model(params) -> list of points; measured -> list of points (same order).
    Returns (best_params, rms_error)."""
    def cost(p):
        try:
            pts = model(p)
        except Exception:
            return 1e18
        return sum((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 for a, b in zip(pts, measured))
    x, v = list(params0), cost(params0)
    for r in range(restarts):
        x, v = nelder_mead(cost, x, [s / (2 ** r) for s in steps])
    return x, math.sqrt(v / max(1, len(measured)))


def minimal_offsets(build, constraints, n_vars, weight=1.0, scale=None, steps=None):
    """Find offsets x (len n_vars) that make constraints(build(x)) ~ 0 while keeping x small.

    build(x)        -> any geometry object
    constraints(g)  -> list of residuals (each should be 0 when satisfied)
    scale           -> per-variable scale for the size penalty (default 1)
    """
    scale = scale or [1.0] * n_vars

    def cost(x):
        try:
            g = build(x)
        except Exception:
            return 1e18
        res = constraints(g)
        return 50 * sum(r * r for r in res) + weight * sum((xi / s) ** 2 for xi, s in zip(x, scale))
    x = [0.0] * n_vars
    for st in (steps or [1.0] * n_vars, [s / 4 for s in (steps or [1.0] * n_vars)]):
        x, _ = nelder_mead(cost, x, st)
    return x
