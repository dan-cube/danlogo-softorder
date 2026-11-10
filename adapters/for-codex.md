# 在 Codex 中使用（CLI、IDE 插件、桌面版）

- **安装位置**：用户级 skill 目录 `~/.agents/skills/danlogo-softorder/`（仓库里运行 `./install.sh codex`）。Codex 在启动时加载 skill，安装或更新后需要重启。目录约定以 OpenAI 官方文档（developers.openai.com/codex/skills）为准。
- **调用**：在消息里写 `$danlogo-softorder` 显式调用；描述匹配时也会自动启用。
- **看图**：渲染 PNG 后用 Codex 的看图能力打开检查；如果当前环境不能看图，把审看图路径交给用户，请用户确认后再继续。
- **展示与审阅**：每轮方案做成自包含的 HTML 对比页，告诉用户文件路径，用浏览器打开。
- **提报文档（第 8 阶段）**：用 python-pptx 生成 PPTX（图片先导出为 PNG，按 `references/deliverables.md` 的结构排版，演讲备注写进备注栏），或做成自包含的 HTML 幻灯片。
- **PNG 导出**：`scripts/render.sh` 会依次尝试 rsvg-convert、cairosvg、macOS Quick Look。
- **项目存档**：同样使用 `decisions.md`；同一项目可以在 Codex 与 Claude 之间切换，只要先读它。
- **多个 danlogo 风格**：用户没有指定风格时，先问用哪一个。
