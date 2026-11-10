"""Hara-style applications for R6 (poster, card, signage, web header)."""
from lockup6 import *


def poster(key="su", px=800, variant="shiro"):
    """4:5 — a small mark in a field of white; the lockup low and quiet."""
    W, H = 800.0, 1000.0
    bg = HARA["shiro"] if variant == "shiro" else HARA["kinari"]
    m, mw = place_mark(HARA["koke"], HARA["shu"], 0, 0, 150)
    frag = m
    mx, my = W / 2 - mw / 2, 330
    big = f'<g transform="translate({mx:.1f} {my:.1f})">{frag}</g>'
    E, C = en_geom(key), cn_geom(key)
    ks = 0.36
    ex = (W - E["width"] * ks) / 2
    ey = 760
    kc = ks * 0.80
    cy = ey + (100 + (24 if "p" in E["text"] else 0) + 30) * ks
    text = en_paths(key, ex, ey, HARA["sumi"], HARA["shu"], ks) + cn_paths(key, (W - C["width"] * kc) / 2, cy, kc, HARA["sumi"])
    rule = f'<rect x="{W / 2 - 0.5}" y="560" width="1" height="120" fill="{HARA["ishi"]}" opacity="0.6"/>'
    return svg_doc((0, 0, W, H), f'<rect width="{W}" height="{H}" fill="{bg}"/>{big}{rule}{text}', px)


def card(key="su", side="front", px=900):
    W, H = 900.0, 540.0
    if side == "front":
        inner = f'<rect width="{W}" height="{H}" fill="{HARA["shiro"]}"/>'
        s = lockup(key, "color", bg=False, px=10)
        vb = s.split('viewBox="')[1].split('"')[0].split()
        vx, vy, vw, vh = map(float, vb)
        body = s.split(">", 1)[1].rsplit("</svg>", 1)[0]
        k = 430 / vw
        inner += f'<g transform="translate({(W - vw * k) / 2 - vx * k:.1f} {(H - vh * k) / 2 - vy * k:.1f}) scale({k:.4f})">{body}</g>'
    else:
        m, mw = place_mark(HARA["kinari"], "#C8563F", 0, 0, 70)
        inner = (f'<rect width="{W}" height="{H}" fill="{HARA["koke"]}"/>'
                 f'<g transform="translate(70 70)">{m}</g>'
                 f'<rect x="70" y="360" width="160" height="2.5" fill="{HARA["kinari"]}" opacity="0.7"/>'
                 f'<rect x="70" y="392" width="260" height="2.5" fill="{HARA["kinari"]}" opacity="0.45"/>'
                 f'<rect x="70" y="424" width="210" height="2.5" fill="{HARA["kinari"]}" opacity="0.45"/>')
    return svg_doc((0, 0, W, H), inner, px)


def squircle(s, e=5.0, steps=240):
    import math
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, si = math.cos(t), math.sin(t)
        pts.append((s / 2 + math.copysign(abs(c) ** (2 / e), c) * s / 2, s / 2 + math.copysign(abs(si) ** (2 / e), si) * s / 2))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def app_icon(style="kinari", px=1024):
    s = 1024
    bg, cell, point = {"kinari": (HARA["kinari"], HARA["koke"], HARA["shu"]),
                       "koke": (HARA["koke"], HARA["kinari"], "#C8563F"),
                       "sumi": (HARA["sumi"], HARA["kinari"], "#C8563F")}[style]
    frag, (x0, y0, x1, y1) = mark_frag(cell, point)
    k = s * 0.54 / max(x1 - x0, y1 - y0)
    inner = (f'<path d="{squircle(s)}" fill="{bg}"/><g transform="translate({s / 2 - (x0 + x1) / 2 * k:.1f} '
             f'{s / 2 + 6 - (y0 + y1) / 2 * k:.1f}) scale({k:.4f})">{frag}</g>')
    return svg_doc((0, 0, s, s), inner, px)
