"""mockup.py — 场景示意（第 7 阶段，danlogo 系列）

把本项目的 SVG 放进扁平的场景模板：名片、App 图标、官网首屏、形象墙、提案封面、手提袋。
比例按真实尺寸，个人信息用占位条，不编造；这是示意，不是实拍效果图。

命令行：
  python3 mockup.py 输出.svg card    --assets 正面.svg 背面.svg
  python3 mockup.py 输出.svg phone   --assets 图标.svg [--label 品牌名]
  python3 mockup.py 输出.svg browser --assets 横式组合.svg 主视觉.svg
  python3 mockup.py 输出.svg wall    --assets 竖式组合.svg
  python3 mockup.py 输出.svg slide   --assets 组合.svg [--bg "#8E1B2A"]
  python3 mockup.py 输出.svg bag     --assets 浅底标志.svg 深底标志.svg [--bg "#231F1C"]
可选 --paper（场景底色）。生成的 SVG 再用 render.sh 转成 PNG 查看。

在代码里：from mockup import card, phone, browser, wall, slide, bag —— 每个函数返回 (svg 字符串, 宽, 高)。
只依赖 Python 标准库。
"""
import argparse
import re

PAPER = "#EDE8DF"
CARD = "#F7F4EE"
BAR = "#D9D2C6"
LINE = "#CFC7BA"
INK = "#231F1C"

DEFS = ('<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="150%">'
        '<feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity=".12"/></filter>'
        '<filter id="sh2" x="-20%" y="-20%" width="140%" height="150%">'
        '<feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000" flood-opacity=".10"/></filter></defs>')


def asset(path, x, y, w, h, align="xMidYMid"):
    """把一个 SVG 文件按比例放进 (x, y, w, h)。"""
    s = open(path, encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    body = re.sub(r"^.*?<svg[^>]*>", "", s, count=1, flags=re.S).rsplit("</svg>", 1)[0]
    return (f'<svg x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" viewBox="{vb}" '
            f'preserveAspectRatio="{align} meet">{body}</svg>')


def bar(x, y, w, h=8, c=BAR):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{c}"/>'


def wrap(w, h, body, paper=PAPER):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">{DEFS}<rect width="{w}" height="{h}" fill="{paper}"/>{body}</svg>', w, h


def card(front, back, paper=PAPER, stock=CARD):
    """名片正反面，90 × 54 mm。正面放标志（可用压印版），背面放小标志与占位信息。"""
    W, H, cw, ch = 800, 520, 342, 205
    fx, fy, bx, by = 64, 70, 394, 246
    b = [f'<rect x="{fx}" y="{fy}" width="{cw}" height="{ch}" rx="3" fill="{stock}" filter="url(#sh)"/>',
         asset(front, fx + cw * 0.2, fy + ch * 0.18, cw * 0.6, ch * 0.64),
         f'<rect x="{bx}" y="{by}" width="{cw}" height="{ch}" rx="3" fill="{stock}" filter="url(#sh)"/>',
         asset(back, bx + 26, by + 24, cw * 0.42, ch * 0.24, "xMinYMin"),
         bar(bx + 26, by + ch - 86, 92, 9, "#BDB4A6"), bar(bx + 26, by + ch - 68, 62, 6),
         bar(bx + 26, by + ch - 44, 150, 5), bar(bx + 26, by + ch - 32, 120, 5), bar(bx + 26, by + ch - 20, 136, 5)]
    return wrap(W, H, "".join(b), paper)


def phone(icon, label="", paper=PAPER):
    """手机桌面上的 App 图标，旁边是三个常用尺寸。"""
    W, H = 800, 520
    px, py, pw, ph = 90, 40, 240, 450
    b = [f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="36" fill="{INK}" filter="url(#sh)"/>',
         f'<rect x="{px + 9}" y="{py + 9}" width="{pw - 18}" height="{ph - 18}" rx="28" fill="#F3EFE8"/>']
    s, g = 40, 13
    gx0 = px + (pw - (4 * s + 3 * g)) / 2
    for r in range(5):
        for c in range(4):
            x, y = gx0 + c * (s + g), py + 58 + r * (s + 24)
            if (r, c) == (1, 1):
                b.append(asset(icon, x, y, s, s))
                if label:
                    b.append(f'<text x="{x + s / 2}" y="{y + s + 13}" font-size="7.5" text-anchor="middle" '
                             f'font-family="PingFang SC, Helvetica" fill="#6B6560">{label}</text>')
            else:
                b.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="10" fill="#E2DCD2"/>')
    b.append(f'<rect x="{px + 22}" y="{py + ph - 74}" width="{pw - 44}" height="56" rx="18" fill="#E8E3DA"/>')
    for i, sz in enumerate((180, 60, 29)):
        x = 410 + [0, 210, 300][i]
        y = 260 - sz / 2
        b.append(asset(icon, x, y, sz, sz))
        b.append(f'<text x="{x + sz / 2}" y="{360}" font-size="12" text-anchor="middle" '
                 f'font-family="PingFang SC, Helvetica" fill="#9A938B">{sz} pt</text>')
    return wrap(W, H, "".join(b), paper)


def browser(logo, hero, paper=PAPER, page="#FBF9F5"):
    """官网首屏：左上横式组合，右侧主视觉，左侧标题与正文占位。"""
    W, H = 800, 520
    x, y, w, h = 50, 46, 700, 430
    b = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{page}" filter="url(#sh)"/>',
         f'<path d="M{x} {y + 10} a10 10 0 0 1 10 -10 h{w - 20} a10 10 0 0 1 10 10 v24 h-{w} z" fill="#E6E0D6"/>']
    for i, c in enumerate(("#E0857A", "#E7C26E", "#9CC48A")):
        b.append(f'<circle cx="{x + 18 + i * 16}" cy="{y + 17}" r="5" fill="{c}"/>')
    b += [f'<rect x="{x + 230}" y="{y + 9}" width="240" height="16" rx="8" fill="#F4F0E9"/>',
          asset(logo, x + 34, y + 54, 170, 30, "xMinYMid")]
    for i in range(4):
        b.append(bar(x + w - 250 + i * 56, y + 66, 40, 6))
    b += [bar(x + 34, y + 160, 250, 14, "#CFC7BA"), bar(x + 34, y + 186, 200, 14, "#CFC7BA"),
          bar(x + 34, y + 226, 270, 6), bar(x + 34, y + 242, 240, 6), bar(x + 34, y + 258, 256, 6),
          f'<rect x="{x + 34}" y="{y + 296}" width="96" height="30" rx="15" fill="{INK}"/>',
          asset(hero, x + 380, y + 110, 270, 270)]
    return wrap(W, H, "".join(b), paper)


def wall(lockup, paper="#F3EFE8", floor="#D8D0C3", desk="#E6DFD4"):
    """前台形象墙：墙、地面、前台与墙上的竖式组合。"""
    W, H = 800, 520
    b = [f'<rect width="{W}" height="390" fill="{paper}"/>', f'<rect y="390" width="{W}" height="130" fill="{floor}"/>',
         f'<rect y="384" width="{W}" height="6" fill="#E3DBCF"/>',
         asset(lockup, 250, 70, 300, 190),
         f'<rect x="220" y="318" width="360" height="104" rx="2" fill="{desk}" filter="url(#sh2)"/>',
         f'<rect x="220" y="318" width="360" height="8" fill="#D9D1C4"/>',
         f'<ellipse cx="400" cy="436" rx="210" ry="10" fill="#000" opacity=".06"/>']
    return wrap(W, H, "".join(b), "#FFFFFF")


def slide(lockup, bg="#F7F4EE", paper=PAPER, bars="#D9D2C6"):
    """提案封面（16:9）。"""
    W, H = 800, 520
    x, y, w, h = 80, 52, 640, 360
    b = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{bg}" filter="url(#sh)"/>',
         asset(lockup, x + 60, y + 70, 340, 130, "xMinYMid"),
         bar(x + 60, y + h - 86, 220, 9, bars), bar(x + 60, y + h - 66, 150, 6, bars),
         bar(x + w - 120, y + h - 40, 60, 5, bars)]
    return wrap(W, H, "".join(b), paper)


def bag(light, dark, bg="#231F1C", paper=PAPER, stock="#F3EFE8"):
    """两只手提袋：浅色袋配标准标志，深色袋配反白标志。"""
    W, H = 800, 520

    def one(x, color, mark):
        y, w, h = 150, 210, 270
        return (f'<path d="M{x + 60} {y} C{x + 60} {y - 70} {x + w - 60} {y - 70} {x + w - 60} {y}" fill="none" '
                f'stroke="{LINE}" stroke-width="5"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" filter="url(#sh)"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="14" fill="#000" opacity=".05"/>'
                + asset(mark, x + w * 0.22, y + h * 0.26, w * 0.56, h * 0.42))
    return wrap(W, H, one(150, stock, light) + one(440, bg, dark), paper)


def main():
    ap = argparse.ArgumentParser(description="场景示意")
    ap.add_argument("out")
    ap.add_argument("kind", choices=["card", "phone", "browser", "wall", "slide", "bag"])
    ap.add_argument("--assets", nargs="+", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--bg")
    ap.add_argument("--paper", default=PAPER)
    a = ap.parse_args()
    k, x = a.kind, a.assets
    if k == "card":
        svg = card(x[0], x[1], a.paper)
    elif k == "phone":
        svg = phone(x[0], a.label, a.paper)
    elif k == "browser":
        svg = browser(x[0], x[1], a.paper)
    elif k == "wall":
        svg = wall(x[0])
    elif k == "slide":
        svg = slide(x[0], a.bg or "#F7F4EE", a.paper)
    else:
        svg = bag(x[0], x[1], a.bg or INK, a.paper)
    open(a.out, "w", encoding="utf-8").write(svg[0])
    print(a.out)


if __name__ == "__main__":
    main()
