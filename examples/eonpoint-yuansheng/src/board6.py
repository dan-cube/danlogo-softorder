#!/usr/bin/env python3
"""R6 board -> ../index.html"""
import os, re
from lockup6 import *
from poster6 import poster, card, app_icon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R5 = os.path.join(os.path.dirname(ROOT), "EonPoint_Cell_R5", "svg", "combo", "C3_Node_触点_x_Hara_原研", "lockup-horizontal.svg")


def inline(svg, cls="", style=""):
    head, rest = svg.split(">", 1)
    head = re.sub(r'\s(width|height)="[^"]*"', "", head)
    extra = (f' class="{cls}"' if cls else "") + (f' style="{style}"' if style else "")
    return head + extra + ' preserveAspectRatio="xMidYMid meet">' + rest


def dedupe(html):
    """Wordmark paths are defined once and <use>d everywhere."""
    defs, n = [], 0
    for m in sorted(set(re.findall(r'<path d="(M[^"]{4000,})"', html)), key=len, reverse=True):
        sid = f"w{n}"
        n += 1
        pat = re.compile(r'<path d="' + re.escape(m) + r'"( fill="[^"]+")?( fill-rule="evenodd")?/>')
        html = pat.sub(lambda g: f'<use href="#{sid}"{g.group(1) or ""}/>', html)
        defs.append(f'<path id="{sid}" d="{m}" fill-rule="evenodd"/>')
    sprite = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{"".join(defs)}</defs></svg>'
    return html.replace("<body>", "<body>" + sprite, 1)


CSS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "board6.css")).read()

RULES = [("正圆的字怀", "o、P、p 的字怀都是正圆，与图形里的细胞同一种圆。"),
         ("竖粗横细", "横画略细于竖画，圆弧在与竖画相接处轻轻收细——只做光学修正，不加装饰。"),
         ("圆形的点", "i 的点、“点”下四点、“虫”的一点都是正圆；只有 i 的点用朱色，呼应图形里那一粒朱。")]

VAR_NOTE = {"su": "推荐。常规字重、首字母大写，最均衡，从名片到招牌都稳。",
            "kei": "更轻、全小写，像无印良品的标签，适合纸张、包装与安静的空间。",
            "ma": "全大写、宽字距，最有“间”的留白感，适合展陈、发布与出版物。"}


def main():
    hero = inline(lockup("su", "color", bg=False), "hero-lockup")
    try:
        raw = open(R5).read()
        raw = re.sub(r'(<svg[^>]*>)<rect[^>]*/>', r'\1', raw, count=1)     # drop its background plate
        before = inline(raw, "cmp-lock")
    except OSError:
        before = ""
    after = inline(lockup("su", "color", bg=False), "cmp-lock")
    en_big = inline(wordmark("su", "en"), "", "width:100%;max-width:640px")
    cn_big = inline(wordmark("su", "cn"), "", "width:100%;max-width:380px")
    rules = "".join(f"<div><em>0{i + 1}</em><b>{a}</b><span>{b}</span></div>" for i, (a, b) in enumerate(RULES))
    alts = "".join(
        f'<figure class="alt"><div class="alt-in">{inline(lockup(k, "color", bg=False))}</div>'
        f'<figcaption><b>{en6.VARIANTS[k]["cn"]} {en6.VARIANTS[k]["en"]}</b>{VAR_NOTE[k]}</figcaption></figure>' for k in ORDER)
    sw = "".join(f'<div class="sw"><div class="chip" style="background:{h}"></div><div class="sw-t"><b>{n}</b><span>{h} · {r}</span></div></div>'
                 for n, h, r in SWATCHES)
    ratio = "".join(f'<i style="flex:{f};background:{h}"></i>' for h, f in
                    (("#F5F3EE", 62), ("#E9E4D8", 20), ("#A7A196", 6), ("#6B7861", 7), ("#2F2E2B", 4.4), ("#B8452F", 0.6)))
    lks = (f'<figure class="lk wide" style="background:#F5F3EE">{inline(lockup_single("su", "color", bg=False))}<figcaption>单行组合</figcaption></figure>'
           f'<figure class="lk" style="background:#E9E4D8">{inline(lockup_stacked("su", "kinari", bg=False))}<figcaption>竖版 · 生成色底</figcaption></figure>'
           f'<figure class="lk dark" style="background:#2F2E2B">{inline(lockup("su", "dark", bg=False))}<figcaption>墨色底</figcaption></figure>'
           f'<figure class="lk" style="background:#FFFFFF">{inline(lockup("su", "mono", bg=False))}<figcaption>单色</figcaption></figure>'
           f'<figure class="lk dark" style="background:#6B7861">{inline(lockup("su", "white", bg=False))}<figcaption>苔色底 · 反白</figcaption></figure>')
    sizes = "".join(f'<div class="sz"><div style="width:{s}px;height:{s}px">{inline(mark_svg("color"))}</div><span>{s}px</span></div>'
                    for s in (64, 40, 28, 20, 16))
    sl = lockup_single("su", "color", bg=False)
    apps = f'''
    <div class="apps6">
      <figure class="ap poster">{inline(poster("su"))}<figcaption>海报 · 白</figcaption></figure>
      <figure class="ap poster">{inline(poster("su", variant="kinari"))}<figcaption>海报 · 生成色</figcaption></figure>
      <div class="ap-col">
        <figure class="ap cardf">{inline(card("su", "front"))}</figure>
        <figure class="ap cardf">{inline(card("su", "back"))}<figcaption>名片 · 正 / 反</figcaption></figure>
        <div class="icons">{"".join(f'<div class="ic">{inline(app_icon(s))}</div>' for s in ("kinari", "koke", "sumi"))}</div>
      </div>
      <figure class="ap web"><div class="nav">{inline(sl, "", "height:22px;width:auto")}<div class="menu"><span>产品</span><span>Agent</span><span>云服务</span><span>软件授权</span><span>关于</span></div></div>
        <div class="web-hero"><p class="k">AI · Agent · Cloud · SaaS · Software · Licensing</p><h4>让每一家企业，<br/>都拥有自己的 AI Agent。</h4></div><figcaption>官网首屏</figcaption></figure>
    </div>'''
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>EonPoint 亿触点 · R6 原研</title><style>{CSS}</style></head>
<body><div class="wrap">
<div class="top"><span><b>EonPoint 亿触点</b> · AI · Agent · Cloud</span><span>R6 · 原研色系 · 字标简化 · 2026.10</span></div>
<section class="cover">
  <p class="kicker">Identity R6 · Hara</p>
  <h1>回到安静。</h1>
  <p class="lead">选定原研色系。字标做减法：去掉出芽、切分、触点这些装饰，只留下三件事——正圆的字怀、竖粗横细、圆形的点。图形不变。</p>
  <div class="hero">{hero}</div>
</section>
<section class="block">
  <h2>繁 → 简</h2>
  <p class="intro">左：上一版 C 触点（每个笔画端点都有圆点）。右：这一版。去掉的是装饰，留下的是比例。</p>
  <div class="cmp"><figure>{before}<figcaption>R5 · C 触点</figcaption></figure><figure class="now">{after}<figcaption>R6 · 素（推荐）</figcaption></figure></div>
</section>
<section class="block">
  <h2>字标 · 素 Su</h2>
  <p class="intro">中英文都从零绘制，未使用任何现成字体。中文与英文同一重量感，“触”笔画最密，单独减重，让三个字灰度一致。</p>
  <div class="spec"><div class="spec-en">{en_big}</div><div class="spec-cn">{cn_big}</div></div>
  <div class="princ three">{rules}</div>
</section>
<section class="block">
  <h2>同样简洁的另外两种气质</h2>
  <p class="intro">三者只在字重、大小写与字距上不同，规则完全一致。</p>
  <div class="alts">{alts}</div>
</section>
<section class="block">
  <h2>色彩 · 原研</h2>
  <p class="intro">以白和生成色为主，苔绿给图形，墨给文字，朱只给一个点。用量比例大致如下。</p>
  <div class="pal six">{sw}</div>
  <div class="ratio">{ratio}</div>
  <p class="note">白 62% · 生成 20% · 石 6% · 苔 7% · 墨 4% · 朱 &lt;1%</p>
</section>
<section class="block"><h2>组合与底色</h2><div class="lks6">{lks}</div>
  <h3 class="sec">小尺寸</h3><div class="small"><div class="sizes">{sizes}</div><div class="small-lock"><div>{inline(sl, "", "height:24px;width:auto")}</div><div>{inline(sl, "", "height:16px;width:auto")}</div><span>页眉 24px / 16px</span></div></div>
</section>
<section class="block"><h2>应用</h2>{apps}</section>
<section class="block">
  <h2>交付文件</h2>
  <div class="files">
    <div><b>矢量 SVG</b> · <code>svg/</code><ul><li>wordmark：素 / 轻 / 间 的英文、中文字标（已转曲）</li><li>lockup：横版、单行、竖版 × 白 / 生成 / 墨 / 苔 / 单色</li><li>mark、app-icon（三色）、poster、card</li></ul></div>
    <div><b>位图 PNG</b> · <code>png/</code><ul><li>常用文件高清导出</li><li>生成脚本 <code>src/build6.py</code></li><li>定稿后建议：中文字形光学微调 + 商标近似检索</li></ul></div>
  </div>
</section>
<footer>EonPoint 亿触点 · R6 · 图形与字标由 <code>src/</code> 中的几何规则生成，未使用任何字体文件。</footer>
</div></body></html>'''
    html = dedupe(html)
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(html)
    print("index.html", len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
