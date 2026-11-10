# 在 Claude 中使用（Claude Code、Claude 桌面版、claude.ai）

- **安装位置**：Claude Code 的用户级 skill 目录 `~/.claude/skills/danlogo-softorder/`（仓库里运行 `./install.sh claude`）。claude.ai 网页版或桌面聊天：`./install.sh package` 生成 `dist/danlogo-softorder.skill`，在 claude.ai 的技能设置里上传；更新后需要重新上传。
- **调用**：描述匹配时自动启用；也可以直接说“用 danlogo-softorder 做……”。
- **看图**：渲染 PNG 后用 Read 工具打开图片亲眼检查；macOS 上 `scripts/render.sh` 无需安装即可工作。
- **展示与审阅**：如果有 Artifact 能力，第 2–5 阶段可用设计画布（Design）把每轮方案并排展示，第 8 阶段用演示文稿（Slides）做提报文档，可导出 PDF / PPTX。没有时，生成自包含的 HTML 页面或 PPTX。
- **网页与搜索**：查重时用网页搜索与内置浏览器做图片检索；不要把用户未发布的设计上传到第三方以图搜图服务。
- **项目存档**：在项目文件夹维护 `decisions.md`；同一项目可以在 Claude 与 Codex 之间切换，只要先读它。
