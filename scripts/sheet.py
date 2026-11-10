"""sheet.py — 把多个 SVG 拼成一张对比审看图（danlogo 系列）

用法：
  python3 sheet.py 输出.svg 文件1.svg 文件2.svg ... [--labels "C1 说明" "C2 说明" ...] [--cols 3] [--cell 420] [--bg "#E9E5DE"]

每个文件按原比例缩放进一个格子，下方标注标签（没给标签时用文件名）。生成的 SVG 再用 render.sh 转成 PNG 查看。
只依赖 Python 标准库。
"""
import argparse
import os
import re


def inner_svg(path):
    s = open(path, encoding="utf-8").read()
    m = re.search(r'viewBox="([^"]+)"', s)
    if not m:
        raise SystemExit(f"{path}: 缺少 viewBox")
    vb = [float(v) for v in m.group(1).replace(",", " ").split()]
    body = re.sub(r"^.*?<svg[^>]*>", "", s, count=1, flags=re.S).rsplit("</svg>", 1)[0]
    return vb, body


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser(description="多个 SVG 拼成对比审看图")
    ap.add_argument("out")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--cell", type=float, default=420, help="格子宽度")
    ap.add_argument("--bg", default="#E9E5DE")
    ap.add_argument("--labels", nargs="*", default=[], help="每个文件的标签，按顺序对应")
    a = ap.parse_args()

    parts, x, y, row_h = [], 0.0, 0.0, 0.0
    gap, label = 20, 30
    for i, f in enumerate(a.files):
        vb, body = inner_svg(f)
        w = a.cell
        h = w * vb[3] / vb[2]
        if h > a.cell * 0.9:
            h = a.cell * 0.9
            w = h * vb[2] / vb[3]
        parts.append(f'<svg x="{x + (a.cell - w) / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'viewBox="{" ".join(map(str, vb))}">{body}</svg>')
        parts.append(f'<text x="{x + 4:.1f}" y="{y + h + 18:.1f}" font-size="13" font-family="PingFang SC, Helvetica, monospace" '
                     f'fill="#666">{_esc(a.labels[i] if i < len(a.labels) else os.path.basename(f))}</text>')
        row_h = max(row_h, h + label)
        x += a.cell + gap
        if (i + 1) % a.cols == 0:
            x, y, row_h = 0.0, y + row_h + gap, 0.0
    total_h = y + row_h
    total_w = a.cols * (a.cell + gap)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 {total_w + 20:.0f} {total_h + 20:.0f}">'
                 f'<rect x="-10" y="-10" width="{total_w + 20:.0f}" height="{total_h + 20:.0f}" fill="{a.bg}"/>'
                 f'{"".join(parts)}</svg>')
    print(a.out)


if __name__ == "__main__":
    main()
