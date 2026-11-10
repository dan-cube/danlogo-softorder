"""review.py — 图形感与辨识度审看板（danlogo 系列）

用法：
  python3 review.py 输出.png 原型1.svg [原型2.svg ...] [--labels "P1 说明" "P2 说明" ...] [--small P1-s.svg - P3-s.svg ...]

--small 按顺序给每个原型配一个小尺寸版（没有的写 -），审看板会多两列：小尺寸版的 32 px 与 16 px。
墨迹碰到画布边缘时会提示；有意截取、让形出血的原型可以忽略这条提示。

每个 SVG 生成一行：原图 · 剪影（外轮廓涂黑）· 反白 · 32 px 放大 · 16 px 放大 · 实际大小 · 圆形头像。
小尺寸与头像先裁到墨迹的外接框再缩小，所以画布留白多少不影响测试。
标签后面附“墨 xx%”：墨迹占它外接框的比例，只作判断“轻”的参考，不是标准（倾斜的形外接框偏大，比例会偏低）。
墨迹碰到画布边缘时，标签会注明，并在终端提示：形可能超出了 viewBox。
用来跑 quality-gates.md 的图形感与辨识度检查，结果一张图看完。

只用 Python 标准库，加 macOS 自带的 sips；SVG 渲染调用同目录的 render.sh。
（第二轮试跑时，测试 AI 各自写过类似工具，这里合并为系列自带的版本。）
"""
import argparse
import base64
import os
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = 240                      # 每个格子的边长（像素）
BG = (233, 229, 222)            # 审看板底色


def sh(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ───────── 位图读写（经由 BMP）─────────
def read(png):
    tmp = tempfile.mktemp(suffix=".bmp")
    sh("sips", "-s", "format", "bmp", png, "--out", tmp)
    d = open(tmp, "rb").read()
    os.remove(tmp)
    off = struct.unpack("<I", d[10:14])[0]
    w, h, _, bpp = struct.unpack("<iiHH", d[18:30])
    top_down, h = h < 0, abs(h)
    step, row = bpp // 8, ((w * bpp + 31) // 32) * 4
    px = []
    for y in range(h):
        base = off + (y if top_down else h - 1 - y) * row
        line = []
        for x in range(w):
            p = d[base + x * step: base + x * step + step]
            a = p[3] if step == 4 else 255
            line.append(tuple(int(c * a / 255 + 255 * (1 - a / 255)) for c in (p[2], p[1], p[0])))
        px.append(line)
    return px


def write(px, png):
    h, w = len(px), len(px[0])
    row = ((w * 24 + 31) // 32) * 4
    data = bytearray()
    for y in range(h - 1, -1, -1):
        line = bytearray()
        for (r, g, b) in px[y]:
            line += bytes((b, g, r))
        data += line + b"\0" * (row - len(line))
    hdr = struct.pack("<2sIHHI", b"BM", 54 + len(data), 0, 0, 54)
    info = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 24, 0, len(data), 2835, 2835, 0, 0)
    tmp = tempfile.mktemp(suffix=".bmp")
    open(tmp, "wb").write(hdr + info + data)
    sh("sips", "-s", "format", "png", tmp, "--out", png)
    os.remove(tmp)
    return png


# ───────── 各种视图 ─────────
def square(png, out, size):
    """先补白成正方形，再缩到 size×size（先补后缩，避免边缘出现灰条）。"""
    px = read(png)
    h, w = len(px), len(px[0])
    n = max(h, w)
    oy, ox = (n - h) // 2, (n - w) // 2
    canvas = [[(255, 255, 255)] * n for _ in range(n)]
    for y in range(h):
        canvas[oy + y][ox:ox + w] = px[y]
    write(canvas, out)
    sh("sips", "-z", str(size), str(size), out, "--out", out)
    return out


def silhouette(px):
    """从四边向内泛洪找背景，其余（包括内腔）全部涂黑：只看外轮廓。"""
    h, w = len(px), len(px[0])
    ink = [[sum(p) / 3 < 160 for p in r] for r in px]
    bg = [[False] * w for _ in range(h)]
    stack = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
            [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    while stack:
        x, y = stack.pop()
        if 0 <= x < w and 0 <= y < h and not bg[y][x] and not ink[y][x]:
            bg[y][x] = True
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [[(255, 255, 255) if bg[y][x] else (20, 20, 20) for x in range(w)] for y in range(h)]


def invert(px):
    """黑白反转：墨变纯白，白变纯黑（中间的灰按比例）。"""
    out = []
    for r in px:
        line = []
        for p in r:
            v = 255 - sum(p) / 3
            v = 255 if v > 200 else (0 if v < 30 else int(v))
            line.append((v, v, v))
        out.append(line)
    return out


def enlarge(px, k):
    out = []
    for r in px:
        big = [p for p in r for _ in range(k)]
        out += [list(big) for _ in range(k)]
    return out


def crop_to_ink(png, out, margin=0.08):
    """裁到墨迹的外接框（加一点边距），用于小尺寸与头像：留白多的标志不会缩成一个点。
    返回 (裁好的 png, 墨迹占外接框的比例, 墨迹是否碰到画布边缘)。"""
    px = read(png)
    h, w = len(px), len(px[0])
    ys = [y for y in range(h) if any(sum(p) / 3 < 200 for p in px[y])]
    xs = [x for x in range(w) if any(sum(px[y][x]) / 3 < 200 for y in ys)] if ys else []
    if not ys or not xs:
        return png, 0.0, False
    y0, y1, x0, x1 = min(ys), max(ys), min(xs), max(xs)
    edge = y0 == 0 or x0 == 0 or y1 == h - 1 or x1 == w - 1
    dark = sum(1 for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if sum(px[y][x]) / 3 < 128)
    ratio = dark / ((y1 - y0 + 1) * (x1 - x0 + 1))
    m = int(max(x1 - x0, y1 - y0) * margin)
    y0, y1, x0, x1 = max(0, y0 - m), min(h - 1, y1 + m), max(0, x0 - m), min(w - 1, x1 + m)
    return write([row[x0:x1 + 1] for row in px[y0:y1 + 1]], out), ratio, edge


def avatar(px):
    """把标志（已缩到格子的约 62%）放进圆形头像。"""
    n = CELL
    h, w = len(px), len(px[0])
    oy, ox = (n - h) // 2, (n - w) // 2
    cx = cy = n / 2
    rr = (n / 2) ** 2
    out = []
    for y in range(n):
        line = []
        for x in range(n):
            if (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 > rr:
                line.append(BG)
            elif oy <= y < oy + h and ox <= x < ox + w:
                line.append(px[y - oy][x - ox])
            else:
                line.append((255, 255, 255))
        out.append(line)
    return out


def b64(png):
    return base64.b64encode(open(png, "rb").read()).decode()


# ───────── 审看板 ─────────
def board(out, svgs, labels, smalls=()):
    tmp = tempfile.mkdtemp()
    cols = ["原图", "剪影", "反白", "32 px", "16 px", "实际 32 / 16", "圆形头像"]
    smalls = list(smalls) + ["-"] * (len(svgs) - len(smalls))
    if any(s != "-" for s in smalls):
        cols += ["小尺寸版 32 px", "小尺寸版 16 px"]
    gap, head, lab = 16, 40, 30
    rows, inks = [], []
    for i, svg in enumerate(svgs):
        big = os.path.join(tmp, f"{i}.png")
        subprocess.run([os.path.join(HERE, "render.sh"), svg, "720", big], check=True,
                       stdout=subprocess.DEVNULL)
        tight, ink, edge = crop_to_ink(big, os.path.join(tmp, f"{i}t.png"))
        inks.append((ink, edge))
        if edge:
            print(f"注意：{os.path.basename(svg)} 的墨迹碰到了画布边缘，形可能超出 viewBox 被裁掉了", file=sys.stderr)
        cell = square(big, os.path.join(tmp, f"{i}c.png"), CELL)
        px = read(cell)
        views = [cell,
                 write(silhouette(px), os.path.join(tmp, f"{i}s.png")),
                 write(invert(px), os.path.join(tmp, f"{i}r.png"))]
        for n, k in ((32, 7), (16, 15)):
            small = square(tight, os.path.join(tmp, f"{i}_{n}.png"), n)
            views.append(write(enlarge(read(small), k), os.path.join(tmp, f"{i}_{n}x.png")))
        actual = (square(tight, os.path.join(tmp, f"{i}_a32.png"), 32),
                  square(tight, os.path.join(tmp, f"{i}_a16.png"), 16))
        views.append(actual)
        views.append(write(avatar(read(square(tight, os.path.join(tmp, f"{i}av0.png"), int(CELL * 0.62)))),
                           os.path.join(tmp, f"{i}av.png")))
        if len(cols) > 7:
            if smalls[i] != "-":
                sbig = os.path.join(tmp, f"{i}s_big.png")
                subprocess.run([os.path.join(HERE, "render.sh"), smalls[i], "720", sbig], check=True,
                               stdout=subprocess.DEVNULL)
                stight = crop_to_ink(sbig, os.path.join(tmp, f"{i}s_t.png"))[0]
                for n, k in ((32, 7), (16, 15)):
                    sn = square(stight, os.path.join(tmp, f"{i}s_{n}.png"), n)
                    views.append(write(enlarge(read(sn), k), os.path.join(tmp, f"{i}s_{n}x.png")))
            else:
                views += [None, None]
        rows.append(views)

    W = len(cols) * (CELL + gap) + gap
    H = head + len(svgs) * (CELL + lab + gap) + gap
    parts = [f'<rect width="{W}" height="{H}" fill="rgb{BG}"/>']
    for c, name in enumerate(cols):
        parts.append(f'<text x="{gap + c * (CELL + gap)}" y="{head - 12}" font-size="15" '
                     f'font-family="PingFang SC, Helvetica" fill="#6B6560">{name}</text>')
    for r, views in enumerate(rows):
        y = head + r * (CELL + lab + gap)
        for c, v in enumerate(views):
            x = gap + c * (CELL + gap)
            if v is None:
                continue
            if isinstance(v, tuple):
                parts.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="#FFFFFF"/>')
                parts.append(f'<image x="{x + 60}" y="{y + 104}" width="32" height="32" href="data:image/png;base64,{b64(v[0])}"/>')
                parts.append(f'<image x="{x + 150}" y="{y + 112}" width="16" height="16" href="data:image/png;base64,{b64(v[1])}"/>')
            else:
                parts.append(f'<image x="{x}" y="{y}" width="{CELL}" height="{CELL}" href="data:image/png;base64,{b64(v)}"/>')
        label = labels[r] if r < len(labels) else os.path.basename(svgs[r])
        ink, edge = inks[r]
        label = f"{label} · 墨 {ink * 100:.0f}%{' · 碰到画布边缘' if edge else ''}".replace("&", "&amp;").replace("<", "&lt;")
        parts.append(f'<text x="{gap}" y="{y + CELL + 21}" font-size="15" '
                     f'font-family="PingFang SC, Helvetica" fill="#231F1C">{label}</text>')
    svg_out = os.path.join(tmp, "board.svg")
    open(svg_out, "w", encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>')
    subprocess.run([os.path.join(HERE, "render.sh"), svg_out, str(W), out], check=True,
                   stdout=subprocess.DEVNULL)
    return out


def main():
    ap = argparse.ArgumentParser(description="图形感与辨识度审看板")
    ap.add_argument("out")
    ap.add_argument("svgs", nargs="+")
    ap.add_argument("--labels", nargs="*", default=[])
    ap.add_argument("--small", nargs="*", default=[], help="每个原型的小尺寸版，按顺序对应；没有的写 -")
    a = ap.parse_args()
    smalls = [s if s == "-" else os.path.abspath(s) for s in a.small]
    print(board(os.path.abspath(a.out), [os.path.abspath(s) for s in a.svgs], a.labels, smalls))


if __name__ == "__main__":
    main()
