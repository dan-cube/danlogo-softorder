#!/usr/bin/env python3
"""R6 exports.  .venv/bin/python src/build6.py [--png]  (needs shapely; PNG via SVG2PNG=/tmp/svg2png)"""
import os, subprocess, sys
from lockup6 import *
from poster6 import poster, card, app_icon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG2PNG = os.environ.get("SVG2PNG")
DIR = {"su": "1_Su_素_推荐", "kei": "2_Kei_轻", "ma": "3_Ma_间"}


def files():
    F = {}
    for k in ORDER:
        d = DIR[k]
        F[f"{d}/wordmark-en.svg"] = wordmark(k, "en")
        F[f"{d}/wordmark-cn.svg"] = wordmark(k, "cn")
        for mode in ("color", "kinari", "dark", "mono", "white"):
            F[f"{d}/lockup-horizontal-{mode}.svg"] = lockup(k, mode, bg=mode not in ("mono", "white"))
        F[f"{d}/lockup-single-line.svg"] = lockup_single(k, "color")
        F[f"{d}/lockup-stacked.svg"] = lockup_stacked(k, "color")
    F["mark/mark-color.svg"] = mark_svg("color")
    F["mark/mark-dark.svg"] = mark_svg("dark", pad=0.16, bg=True)
    F["mark/mark-mono.svg"] = mark_svg("mono")
    for s in ("kinari", "koke", "sumi"):
        F[f"mark/app-icon-{s}.svg"] = app_icon(s)
    F["applications/poster-shiro.svg"] = poster("su")
    F["applications/poster-kinari.svg"] = poster("su", variant="kinari")
    F["applications/card-front.svg"] = card("su", "front")
    F["applications/card-back.svg"] = card("su", "back")
    return F


PNG = {"lockup-horizontal-color.svg": 3000, "lockup-horizontal-dark.svg": 3000, "lockup-single-line.svg": 3200,
       "lockup-stacked.svg": 2000, "mark-color.svg": 2048, "app-icon-kinari.svg": 1024, "app-icon-koke.svg": 1024,
       "poster-shiro.svg": 1600, "poster-kinari.svg": 1600, "card-front.svg": 1800, "card-back.svg": 1800}


def main():
    F = files()
    for rel, svg in F.items():
        p = os.path.join(ROOT, "svg", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(svg)
        n = os.path.basename(rel)
        if "--png" in sys.argv and SVG2PNG and n in PNG:
            q = os.path.join(ROOT, "png", rel[:-4] + ".png")
            os.makedirs(os.path.dirname(q), exist_ok=True)
            subprocess.run([SVG2PNG, p, q, str(PNG[n])], check=True, capture_output=True)
    print(len(F), "svg files")


if __name__ == "__main__":
    main()
