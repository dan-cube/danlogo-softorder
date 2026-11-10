# scripts · 通用工具

只依赖 Python 3 标准库与系统命令。新项目开始时，把需要的文件复制到项目的 `src/`。

| 文件 | 作用 |
|---|---|
| `geom.py` | 几何与 SVG 生成：填充 `F`、圆 `C`、闭合多边形 `poly`、挖空 `hole`、截取 `clip_poly`、圆弧点列 `arc_pts`、对称补全 `symmetric`、翻转 `mirror`、旋转 `rotate`、描边 `S`、圆环路径 `ring`、平移缩放 `move`、包围盒 `bbox`、按角色上色渲染 `render`、输出文档 `svg_doc` |
| `sheet.py` | 把多个 SVG 拼成一张对比审看图，可用 `--labels` 加标签 |
| `render.sh` | SVG → PNG（依次尝试 rsvg-convert、cairosvg、macOS Quick Look；Quick Look 输出会按 viewBox 比例自动裁边；带超时与重试） |
| `review.py` | 图形感与辨识度审看板：每个 SVG 一行——原图、剪影、反白、32 px 与 16 px 像素放大、实际大小、圆形头像，标签后附墨色比例；形碰到画布边缘时会提示；`--small` 可给每个原型配小尺寸版，多两列（32 / 16 px）对照。小尺寸与头像按墨迹裁切，画布留白多少不影响结果。反白按黑白取反，彩色稿请另看各色彩版本 |
| `mockup.py` | 场景示意（第 7 阶段）：名片、App 图标、官网首屏、形象墙、提案封面、手提袋的扁平模板，放入本项目的 SVG 即可。用法：`python3 mockup.py card.svg card --assets 正面.svg 背面.svg`。个人信息用占位条，这是示意，不是实拍 |

## 最小示例

下面的形只是为了演示写法，不是任何造型建议。

```python
from geom import F, poly, render, svg_doc, bbox

shapes = [F(poly([(0, 0), (100, 0), (100, 100), (0, 100)]), "body")]   # 仅演示 API
colors = {None: "#231F1C", "body": "#231F1C"}
open("mark.svg", "w").write(svg_doc(render(shapes, colors), bbox(shapes), pad=6))
```

```bash
python3 sheet.py sketches.svg c1.svg c2.svg --labels "C1" "C2" --cols 2
./render.sh sketches.svg
python3 review.py board.png p1.svg p2.svg --labels "P1" "P2"   # 图形感与辨识度审看板
```

## 约定

- 形状和颜色分离：形状只标角色（`role`），导出时按色彩版本替换颜色。
- 所有尺寸从一个基准数推出，写在文件顶部。
- 判断好不好看，一律看渲染出的 PNG；第 2 阶段的速写可以、第 3 阶段起的每个原型必须用 `review.py` 出一张审看板。
- 图形优先用填充的面来构造（`F`、`C`、`poly`）；描边只用于确实是线的部分。
- 用了描边的 SVG，正式交付前把描边转成填充路径（见 `references/craft.md`）。
- `hole()` 按 evenodd 规则挖空：几个内轮廓互相重叠时，重叠处会被“抵消”回实心；需要并集时先把内轮廓合成一个。
- `review.py` 在墨迹碰到画布边缘时会提示；有意截取、让形出血的原型可以忽略。

完整的工程示例见各 skill 的 `examples/<案例名>/src/`（只学写法，不复用造型）。

## 本风格的柔性几何工具

这几件来自 EonPoint 案例的工程，把“相切过渡、规则参数化、最小偏差、定制字”做成了可复用的模块。它们只提供**构造方法**，不带任何造型：形状、过程、数量都要在新项目里重新设计。

| 文件 | 作用 | 依赖 |
|---|---|---|
| `geo.py` | 向量与圆的基础运算；两圆之间由相切圆弧构成的颈（`neck`，按最窄宽度求解，处理不等大的两圆）；胶囊；极坐标 | 标准库 |
| `cells.py` | `Cluster`：几个体 + 非对称的颈 + 拉长 / 缢缩体 + 强调元素，`fit(size)` 归一化，`body_svg(fill)` 输出 | 标准库 |
| `solve.py` | `nelder_mead` 求解；`fit` 从参考稿拟合骨架参数；`minimal_offsets` 在满足约束（等距、比例、守恒）的前提下求最小偏差 | 标准库 |
| `type5.py` | 定制字的笔画引擎：`Stroke`（骨架笔画，可渐细）、`Ring`（字碗，可设内轮廓）、`Dot`；视觉修正（横细于竖、内碗收窄、肩部过渡）；`render` 出轮廓，`layout` 排字距 | shapely |
| `outline4.py` | SVG path 解析与圆角化 | shapely |
| `svg2png.swift` | macOS 上的 SVG → PNG：`swiftc -O svg2png.swift -o svg2png`，`./svg2png in.svg out.png 2000` | macOS |

需要 shapely 时：

```bash
python3 -m venv .venv && .venv/bin/pip install shapely
```

字形定义的约定：大写高 100，基线 y = 100，y 向下；每个字形返回 `dict(prims=[...], width=W, sb=(左, 右))`。完整示例见 `examples/eonpoint-yuansheng/src/en6.py`（英文）与 `cn5.py`（中文）——只学写法，字形本身是那个品牌的。
