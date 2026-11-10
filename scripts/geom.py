"""geom.py — 通用几何与 SVG 生成工具（danlogo 系列）

形状用一个列表表示，每个形状是一个字典：
  {"k": "s", "d": path, "w": 线宽}      描边路径（stroke）
  {"k": "c", "x":, "y":, "r":}          实心圆
  {"k": "f", "d": path}                 填充路径
可选 "role" 字段（例如 "line"、"point"）用来在导出时按角色上色：
  render(shapes, {None: "#222", "point": "#C33"})

坐标：x 向右，y 向下。路径只使用绝对命令 M L H V A Q C Z。
只依赖 Python 标准库。

图形优先用填充的面（F、C、poly）来构造，描边 S 只用于确实是“线”的部分——
几根描边很容易读成字或符号（见 references/craft.md“先想外形和面”）。
对称形：先画一半的轮廓点，用 symmetric() 补全，再用 poly() 闭合；整组形状可用 mirror() 翻转。
旋转用 rotate()；挖空用 hole(外轮廓, 内轮廓…)（按 evenodd 规则填充，内轮廓就是空）；
截取用 clip_poly(形的点列, 凸多边形点列)；圆弧点列用 arc_pts()。
"""
import math


def n(v):
    s = f"{v:.2f}"
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ───────────────────────────── primitives ─────────────────────────────
# a shape list is a list of dicts:
#   {"k": "s", "d": path, "w": stroke}        stroked path
#   {"k": "c", "x":, "y":, "r":}              filled circle
#   {"k": "f", "d": path}                     filled path
#   optional "role": "accent" / "a1" / "a2" … used for colouring


def S(d, w, role=None):
    return {"k": "s", "d": d, "w": w, "role": role}


def C(x, y, r, role=None):
    return {"k": "c", "x": x, "y": y, "r": r, "role": role}


def F(d, role=None):
    return {"k": "f", "d": d, "role": role}


def ring(cx, cy, r):
    return (f"M{n(cx - r)} {n(cy)}A{n(r)} {n(r)} 0 1 1 {n(cx + r)} {n(cy)}"
            f"A{n(r)} {n(r)} 0 1 1 {n(cx - r)} {n(cy)}")


def poly(points):
    """闭合多边形路径：[(x, y), ...] → "M..L..Z"。"""
    head, *rest = points
    return f"M{n(head[0])} {n(head[1])}" + "".join(f"L{n(x)} {n(y)}" for x, y in rest) + "Z"


def symmetric(half, axis_x):
    """给出对称轴一侧的轮廓点（从轴上一点开始，到轴上另一点结束），返回完整的闭合点列。"""
    other = [(2 * axis_x - x, y) for x, y in reversed(half[1:-1])]
    return list(half) + other


def mirror(shapes, x=None, y=None):
    """把整组形状沿竖线 x=… 或横线 y=… 翻转（返回新列表）；圆弧的方向会一并翻转。"""
    fx = (lambda v: 2 * x - v) if x is not None else (lambda v: v)
    fy = (lambda v: 2 * y - v) if y is not None else (lambda v: v)
    flip = (x is None) != (y is None)
    return _map_shapes(shapes, lambda px, py: (fx(px), fy(py)), flip=flip, sign=-1 if flip else 1)


def rotate(shapes, deg, cx=0, cy=0):
    """绕 (cx, cy) 旋转 deg 度（正值为顺时针，因为 y 轴向下）。返回新列表。"""
    t = math.radians(deg)
    c, s_ = math.cos(t), math.sin(t)

    def f(px, py):
        dx, dy = px - cx, py - cy
        return cx + dx * c - dy * s_, cy + dx * s_ + dy * c
    return _map_shapes(shapes, f, dang=deg)


def hole(outer, *inners, role=None):
    """挖空：外轮廓路径 + 若干内轮廓路径，按 evenodd 填充，内轮廓处成为空。"""
    return {"k": "f", "d": " ".join((outer,) + inners), "role": role, "rule": "evenodd"}


def clip_poly(subject, clipper):
    """多边形裁切（交集）：subject 为任意简单多边形点列，clipper 必须是凸多边形（顺时针或逆时针均可）。
    返回裁切后的点列（可直接交给 poly()）；用于“截取”。差集请用 hole()。"""
    def inside(p, a, b, sgn):
        return sgn * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) >= 0

    def cross(p, q, a, b):
        x1, y1, x2, y2, x3, y3, x4, y4 = *p, *q, *a, *b
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        return x1 + t * (x2 - x1), y1 + t * (y2 - y1)
    area = sum(clipper[i][0] * clipper[(i + 1) % len(clipper)][1] - clipper[(i + 1) % len(clipper)][0] * clipper[i][1]
               for i in range(len(clipper)))
    sgn = 1 if area > 0 else -1
    out = list(subject)
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            if inside(q, a, b, sgn):
                if not inside(p, a, b, sgn):
                    out.append(cross(p, q, a, b))
                out.append(q)
            elif inside(p, a, b, sgn):
                out.append(cross(p, q, a, b))
        if not out:
            break
    return out


def arc_pts(cx, cy, r, a0, a1, steps=48):
    """圆弧上的点列（角度为度，0° 向右，顺时针为正），用来把弧拼进 poly() 或 clip_poly()。"""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / steps)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / steps))) for k in range(steps + 1)]


def _map_shapes(shapes, f, flip=False, dang=0, sign=1):
    out = []
    for sh in shapes:
        sh = dict(sh)
        if sh["k"] == "c":
            sh["x"], sh["y"] = f(sh["x"], sh["y"])
        else:
            sh["d"] = _map_path(sh["d"], f, flip=flip, dang=dang, sign=sign)
        out.append(sh)
    return out


def _map_path(d, f, flip=False, dang=0, sign=1):
    """逐点映射一条绝对路径（M L H V A Q C Z）。H、V 会改写成 L；
    flip=True 时翻转圆弧的 sweep 标志；dang 加到椭圆弧的旋转角上。"""
    import re
    toks = re.findall(r"[MLHVAQCZ]|-?\d*\.?\d+(?:e-?\d+)?", d)
    out, i, cmd = [], 0, None
    cx = cy = sx = sy = 0.0

    def pt(x, y):
        X, Y = f(x, y)
        return f"{n(X)} {n(Y)}"
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == "Z":
                out.append("Z")
                cx, cy = sx, sy
                continue
            if cmd not in ("H", "V"):
                out.append(cmd)
        if cmd in ("M", "L"):
            cx, cy = float(toks[i]), float(toks[i + 1]); i += 2
            if cmd == "M":
                sx, sy = cx, cy
            out.append(pt(cx, cy))
        elif cmd in ("H", "V"):
            if cmd == "H":
                cx = float(toks[i])
            else:
                cy = float(toks[i])
            i += 1
            out.append("L" + pt(cx, cy))
        elif cmd == "A":
            rx, ry, rot, la, sw, x, y = toks[i:i + 7]; i += 7
            sw = str(1 - int(sw)) if flip else sw
            rot = n(sign * float(rot) + dang)
            cx, cy = float(x), float(y)
            out.append(f"{rx} {ry} {rot} {la} {sw} {pt(cx, cy)}")
        elif cmd in ("Q", "C"):
            k = 4 if cmd == "Q" else 6
            v = [float(t) for t in toks[i:i + k]]; i += k
            out.append(" ".join(pt(v[j], v[j + 1]) for j in range(0, k, 2)))
            cx, cy = v[k - 2], v[k - 1]
    return "".join(out).strip()


def move(shapes, dx=0, dy=0, s=1.0):
    """translate + uniform scale a shape list (returns new list)."""
    out = []
    for sh in shapes:
        sh = dict(sh)
        if sh["k"] == "c":
            sh["x"], sh["y"], sh["r"] = sh["x"] * s + dx, sh["y"] * s + dy, sh["r"] * s
        else:
            sh["d"] = _xform_path(sh["d"], dx, dy, s)
            if sh["k"] == "s":
                sh["w"] = sh["w"] * s
        out.append(sh)
    return out


def _xform_path(d, dx, dy, s):
    """transform an absolute-command path (M L H V A Q C Z only)."""
    import re
    toks = re.findall(r"[MLHVAQCZ]|-?\d*\.?\d+(?:e-?\d+)?", d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            if cmd == "Z":
                continue
        if cmd in ("M", "L"):
            x, y = float(toks[i]), float(toks[i + 1]); i += 2
            out.append(f"{n(x * s + dx)} {n(y * s + dy)}")
        elif cmd == "H":
            out.append(n(float(toks[i]) * s + dx)); i += 1
        elif cmd == "V":
            out.append(n(float(toks[i]) * s + dy)); i += 1
        elif cmd == "A":
            rx, ry, rot, la, sw, x, y = toks[i:i + 7]; i += 7
            out.append(f"{n(float(rx) * s)} {n(float(ry) * s)} {rot} {la} {sw} "
                       f"{n(float(x) * s + dx)} {n(float(y) * s + dy)}")
        elif cmd == "Q":
            v = [float(t) for t in toks[i:i + 4]]; i += 4
            out.append(" ".join(n(v[j] * s + (dx if j % 2 == 0 else dy)) for j in range(4)))
        elif cmd == "C":
            v = [float(t) for t in toks[i:i + 6]]; i += 6
            out.append(" ".join(n(v[j] * s + (dx if j % 2 == 0 else dy)) for j in range(6)))
        elif cmd == "Z":
            pass
    return "".join(out).replace("M", "M").strip()


def bbox(shapes):
    """approximate bbox (stroke aware; arcs sampled crudely via endpoints + radii)."""
    xs, ys = [], []
    import re
    for sh in shapes:
        if sh["k"] == "c":
            xs += [sh["x"] - sh["r"], sh["x"] + sh["r"]]
            ys += [sh["y"] - sh["r"], sh["y"] + sh["r"]]
            continue
        hw = sh.get("w", 0) / 2 if sh["k"] == "s" else 0
        pts = _sample(sh["d"])
        for x, y in pts:
            xs += [x - hw, x + hw]
            ys += [y - hw, y + hw]
    return min(xs), min(ys), max(xs), max(ys)


def _sample(d):
    """sample points along an absolute path (good enough for bboxes)."""
    import re
    toks = re.findall(r"[MLHVAQCZ]|-?\d*\.?\d+(?:e-?\d+)?", d)
    pts, i, cmd, cx, cy, sx, sy = [], 0, None, 0, 0, 0, 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == "Z":
                cx, cy = sx, sy
                continue
        if cmd == "M":
            cx, cy = float(toks[i]), float(toks[i + 1]); i += 2; sx, sy = cx, cy; pts.append((cx, cy))
        elif cmd == "L":
            cx, cy = float(toks[i]), float(toks[i + 1]); i += 2; pts.append((cx, cy))
        elif cmd == "H":
            cx = float(toks[i]); i += 1; pts.append((cx, cy))
        elif cmd == "V":
            cy = float(toks[i]); i += 1; pts.append((cx, cy))
        elif cmd == "Q":
            x1, y1, x, y = map(float, toks[i:i + 4]); i += 4
            for k in range(1, 11):
                u = k / 10
                pts.append(((1 - u) ** 2 * cx + 2 * (1 - u) * u * x1 + u * u * x,
                            (1 - u) ** 2 * cy + 2 * (1 - u) * u * y1 + u * u * y))
            cx, cy = x, y
        elif cmd == "C":
            x1, y1, x2, y2, x, y = map(float, toks[i:i + 6]); i += 6
            for k in range(1, 11):
                u = k / 10
                a, b, c_, d_ = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
                pts.append((a * cx + b * x1 + c_ * x2 + d_ * x, a * cy + b * y1 + c_ * y2 + d_ * y))
            cx, cy = x, y
        elif cmd == "A":
            rx, ry, rot, la, sw, x, y = toks[i:i + 7]; i += 7
            pts += _arc_pts(cx, cy, float(rx), int(la), int(sw), float(x), float(y))
            cx, cy = float(x), float(y)
    return pts


def _arc_pts(x1, y1, r, la, sw, x2, y2):
    # circle arc endpoint → centre parameterisation
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    d2 = dx * dx + dy * dy
    if d2 == 0:
        return []
    r = max(r, math.sqrt(d2))
    f = math.sqrt(max(r * r - d2, 0) / d2)
    if la == sw:
        f = -f
    cxp, cyp = f * dy, -f * dx
    cx, cy = cxp + (x1 + x2) / 2, cyp + (y1 + y2) / 2
    a1 = math.atan2(y1 - cy, x1 - cx)
    a2 = math.atan2(y2 - cy, x2 - cx)
    da = a2 - a1
    if sw and da < 0:
        da += 2 * math.pi
    if not sw and da > 0:
        da -= 2 * math.pi
    return [(cx + r * math.cos(a1 + da * k / 24), cy + r * math.sin(a1 + da * k / 24)) for k in range(25)]


# ───────────────────────────── rendering ─────────────────────────────

def render(shapes, colors, cap="butt", join="miter"):
    """colors: dict role → colour (key None = default)."""
    out = []
    for sh in shapes:
        col = colors.get(sh.get("role"), colors[None])
        if sh["k"] == "c":
            out.append(f'<circle cx="{n(sh["x"])}" cy="{n(sh["y"])}" r="{n(sh["r"])}" fill="{col}"/>')
        elif sh["k"] == "f":
            rule = f' fill-rule="{sh["rule"]}"' if sh.get("rule") else ""
            out.append(f'<path d="{sh["d"]}" fill="{col}"{rule}/>')
        else:
            out.append(f'<path d="{sh["d"]}" fill="none" stroke="{col}" stroke-width="{n(sh["w"])}" '
                       f'stroke-linecap="{sh.get("cap", cap)}" stroke-linejoin="{join}" stroke-miterlimit="10"/>')
    return "".join(out)


def svg_doc(inner, box, bg=None, pad=0, width=None):
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    w, h = x1 - x0, y1 - y0
    wa = f' width="{n(width)}" height="{n(width * h / w)}"' if width else ""
    bgr = f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{n(x0)} {n(y0)} {n(w)} {n(h)}"{wa}>'
            f'{bgr}{inner}</svg>')
