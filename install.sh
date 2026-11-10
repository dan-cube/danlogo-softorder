#!/usr/bin/env bash
# 安装 / 更新 danlogo-softorder 到本机的 AI 工具。
#
#   ./install.sh            安装到 Claude Code 和 Codex
#   ./install.sh claude     只装 Claude Code   (~/.claude/skills/)
#   ./install.sh codex      只装 Codex         (~/.agents/skills/)
#   ./install.sh package    打包成 dist/danlogo-softorder.skill（上传到 claude.ai）
#
# 更新：git pull && ./install.sh
# 目标目录可用环境变量覆盖：CLAUDE_SKILLS_DIR、CODEX_SKILLS_DIR
set -euo pipefail

NAME="danlogo-softorder"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CODEX_DIR="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
# 这些文件只在仓库里用，不装进 AI 工具
EXCLUDES=(--exclude ".git" --exclude "/.gitignore" --exclude "dist" --exclude "__pycache__" --exclude ".DS_Store"
          --exclude "/install.sh" --exclude "/AGENTS.md" --exclude "/README.md" --exclude "/README.zh-CN.md" --exclude "/CHANGELOG.md" --exclude "/docs")
# 以 / 开头的规则只排除仓库根目录下的文件，scripts/README.md 等子目录说明会保留

copy_to() {
  local dest="$1/$NAME"
  mkdir -p "$1"
  rsync -a --delete "${EXCLUDES[@]}" "$SRC/" "$dest/"
  echo "✓ 已安装到 $dest （版本 $(cat "$SRC/VERSION")）"
}

package() {
  mkdir -p "$SRC/dist"
  local tmp; tmp="$(mktemp -d)"
  rsync -a "${EXCLUDES[@]}" "$SRC/" "$tmp/$NAME/"
  (cd "$tmp" && rm -f "$SRC/dist/$NAME.skill" && zip -qr "$SRC/dist/$NAME.skill" "$NAME")
  rm -rf "$tmp"
  echo "✓ 已打包：$SRC/dist/$NAME.skill"
}

case "${1:-all}" in
  claude)  copy_to "$CLAUDE_DIR" ;;
  codex)   copy_to "$CODEX_DIR"; echo "  提示：重启 Codex 后生效" ;;
  package) package ;;
  all)     copy_to "$CLAUDE_DIR"; copy_to "$CODEX_DIR"; echo "  提示：重启 Codex 后生效" ;;
  *)       echo "用法：./install.sh [claude|codex|package]"; exit 1 ;;
esac
