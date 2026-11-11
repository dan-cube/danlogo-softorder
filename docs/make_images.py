#!/usr/bin/env python3
"""Regenerate the README images in docs/images/ (banner, palette, workflow, social-preview).

    .venv/bin/python docs/make_images.py            # writes SVGs
    SVG2PNG=/path/to/svg2png .venv/bin/python docs/make_images.py   # + PNGs
    ... docs/make_images.py social-preview                          # only the named images

Uses the EonPoint example code for the mark; text is set in system fonts
(these are README illustrations, not logo artwork).
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "examples", "eonpoint-yuansheng", "src"))
from lockup6 import mark_frag  # noqa: E402

OUT = os.path.join(HERE, "images")
SHIRO, KINARI, ISHI, KOKE, SUMI, SHU = "#F5F3EE", "#E9E4D8", "#A7A196", "#6B7861", "#2F2E2B", "#B8452F"
TXT2 = "#6E6A62"
SANS = "Helvetica Neue, PingFang SC, sans-serif"
CN = "PingFang SC, Helvetica Neue, sans-serif"


def mark(cx, cy, size, cell=KOKE, point=SHU):
    frag, (x0, y0, x1, y1) = mark_frag(cell, point)
    k = size / max(x1 - x0, y1 - y0)
    return (f'<g transform="translate({cx - (x0 + x1) / 2 * k:.1f} {cy - (y0 + y1) / 2 * k:.1f}) '
            f'scale({k:.4f})">{frag}</g>')


def t(x, y, s, size, col=SUMI, weight=300, anchor="start", ls=0, fam=SANS):
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
            f'letter-spacing="{ls}" text-anchor="{anchor}" fill="{col}">{s}</text>')


def doc(w, h, inner, bg):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{inner}</svg>')


def banner():
    W, H = 2400, 1000
    g = [mark(640, 500, 560),
         t(1180, 400, "Soft Order", 132, SUMI, 300, ls=2),
         t(1186, 488, "柔性秩序", 54, SUMI, 300, ls=6, fam=CN),
         f'<rect x="1186" y="548" width="120" height="2" fill="{ISHI}"/>',
         t(1186, 626, "Organic form, machine precision.", 34, TXT2, 400),
         t(1186, 676, "Soft parts in hidden order; one relation left open.", 34, TXT2, 400),
         t(1186, 746, "有机的形，机械的精度：柔软的部分按看不见的规则成群，只让一处打开。", 30, TXT2, 400, fam=CN),
         t(120, 120, "DANLOGO-SOFTORDER", 22, ISHI, 500, ls=6),
         t(2280, 900, "A logo-design skill for Claude &amp; Codex", 22, ISHI, 400, "end", ls=2)]
    return doc(W, H, "".join(g), SHIRO)


def palette():
    W, H = 2400, 560
    sw = [("白", "Shiro", SHIRO, "底色 · Ground"), ("生成", "Kinari", KINARI, "纸张 · Paper"),
          ("石", "Ishi", ISHI, "辅助 · Line"), ("苔", "Koke", KOKE, "图形 · Mark"),
          ("墨", "Sumi", SUMI, "文字 · Type"), ("朱", "Shu", SHU, "唯一的强调 · The one accent")]
    g = []
    x0, gap, w = 120, 40, (W - 240 - 5 * 40) / 6
    for i, (cn, en, hx, role) in enumerate(sw):
        x = x0 + i * (w + gap)
        stroke = f' stroke="{ISHI}" stroke-width="2"' if hx == SHIRO else ""
        g.append(f'<rect x="{x:.0f}" y="100" width="{w:.0f}" height="240" rx="8" fill="{hx}"{stroke}/>')
        g.append(t(x, 400, f"{cn} {en}", 34, SUMI, 400, fam=CN))
        g.append(t(x, 446, hx, 26, TXT2, 400))
        g.append(t(x, 486, role, 24, TXT2, 400, fam=CN))
    return doc(W, H, "".join(g), "#FBFAF7")


def workflow():
    W, H = 2400, 620
    stages = [("简报", "Brief", ""), ("概念", "Concept", "×5"), ("原型", "Prototype", "≥3"),
              ("图形", "Mark", ""), ("定稿", "Type + Color", ""), ("体系", "System", ""),
              ("场景", "Scenes", ""), ("提案", "Pitch", ""), ("总结", "Retro", "")]
    g = []
    x0, x1, cy = 180, 2220, 250
    step = (x1 - x0) / (len(stages) - 1)
    g.append(f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{ISHI}" stroke-width="2"/>')
    for i, (cn, en, note) in enumerate(stages):
        x = x0 + i * step
        last = i == len(stages) - 1
        g.append(f'<circle cx="{x:.0f}" cy="{cy}" r="58" fill="{SHU if last else KOKE}"/>')
        g.append(t(x, cy + 16, str(i + 1), 44, SHIRO, 400, "middle"))
        g.append(t(x, cy + 130, cn, 38, SUMI, 400, "middle", fam=CN))
        g.append(t(x, cy + 178, en, 26, TXT2, 400, "middle"))
        if note:
            g.append(t(x, cy - 88, note, 30, KOKE, 500, "middle"))
    g.append(t(W / 2, 560, "每个阶段都等你确认 · Every stage ends with your sign-off", 26, TXT2, 400, "middle", fam=CN))
    return doc(W, H, "".join(g), SHIRO)


def social():
    """GitHub social preview (1280x640), uploaded by hand in Settings -> Social preview."""
    W, H = 1280, 640
    g = [t(96, 160, "DANLOGO", 20, ISHI, 500, ls=6),
         f'<circle cx="252" cy="153" r="4" fill="{SHU}"/>',
         t(270, 160, "SOFT ORDER", 20, ISHI, 500, ls=6),
         t(90, 314, "柔性秩序", 128, SUMI, 300, ls=8, fam=CN),
         t(96, 386, "Complete logo identity systems,", 32, SUMI, 300),
         t(96, 428, "organic and quietly precise", 32, SUMI, 300),
         t(96, 472, "for AI tools such as Claude &amp; Codex · brief to delivery", 22, TXT2, 300),
         f'<rect x="96" y="512" width="64" height="1.5" fill="{ISHI}"/>',
         t(96, 556, "有机的形，机械的精度", 24, TXT2, 300, fam=CN),
         mark(992, 340, 360)]
    return doc(W, H, "".join(g), SHIRO)


def main():
    os.makedirs(OUT, exist_ok=True)
    svg2png = os.environ.get("SVG2PNG")
    jobs = (("banner", banner, 2400), ("palette", palette, 2400), ("workflow", workflow, 2400),
            ("social-preview", social, 1280))
    only = set(sys.argv[1:])
    for name, fn, px in jobs:
        if only and name not in only:
            continue
        p = os.path.join(OUT, name + ".svg")
        open(p, "w").write(fn())
        if svg2png:
            subprocess.run([svg2png, p, os.path.join(OUT, name + ".png"), str(px)], check=True, capture_output=True)
            os.remove(p)
    print("ok")


if __name__ == "__main__":
    main()
