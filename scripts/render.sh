#!/usr/bin/env bash
# render.sh — 把 SVG 渲染成 PNG，用来亲眼审看（danlogo 系列）
#
#   ./render.sh 文件.svg [宽度像素，默认 1600] [输出.png]
#
# 依次尝试：rsvg-convert → Python cairosvg → macOS Quick Look（qlmanage，系统自带）。
# Quick Look 只输出正方形图；这里按 SVG 的 viewBox 比例用 sips 裁掉多余的白边。
set -euo pipefail

SVG="${1:?用法：./render.sh 文件.svg [宽度] [输出.png]}"
W="${2:-1600}"
OUT="${3:-${SVG%.svg}.png}"
[[ -f "$SVG" ]] || { echo "找不到文件：$SVG" >&2; exit 1; }

if command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -w "$W" "$SVG" -o "$OUT"
elif python3 -c "import cairosvg" >/dev/null 2>&1; then
  python3 -c "import cairosvg,sys; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], output_width=int(sys.argv[3]))" "$SVG" "$OUT" "$W"
elif command -v qlmanage >/dev/null 2>&1; then
  TMP="$(mktemp -d)"
  # Quick Look 偶尔会卡住：限时 60 秒，失败就重试一次
  for _ in 1 2; do
    perl -e 'alarm 60; exec @ARGV' qlmanage -t -s "$W" -o "$TMP" "$SVG" >/dev/null 2>&1 && break || true
  done
  [[ -f "$TMP/$(basename "$SVG").png" ]] || { echo "Quick Look 渲染失败：$SVG" >&2; rm -rf "$TMP"; exit 1; }
  mv "$TMP/$(basename "$SVG").png" "$OUT"
  rm -rf "$TMP"
  # 按 viewBox 比例裁掉 Quick Look 加上的白边
  read -r CW CH < <(python3 - "$SVG" "$W" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'viewBox="([^"]+)"', s)
W = int(sys.argv[2])
if not m:
    print(W, W); raise SystemExit
_, _, w, h = [float(v) for v in m.group(1).replace(",", " ").split()]
cw, ch = (W, round(W * h / w)) if w >= h else (round(W * w / h), W)
print(cw, ch)
PY
)
  if [[ "$CW" != "$CH" ]]; then
    sips -c "$CH" "$CW" "$OUT" >/dev/null 2>&1 || true
  fi
else
  echo "没有可用的渲染器：请安装 librsvg（rsvg-convert）或 pip install cairosvg" >&2
  exit 1
fi
echo "$OUT"
