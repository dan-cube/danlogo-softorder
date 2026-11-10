# 维护本仓库的说明（给 AI 编辑者）

这个仓库本身就是一个 skill（`danlogo-softorder`）。如果你是被要求**修改这个 skill** 的 AI（而不是用它做设计），请遵守：

1. **分清两类章节**
   - 风格四章（本风格专属，可以在这里改）：`references/philosophy.md`、`references/style-dna.md`、`references/creative-methods.md`、`references/style-extension.md`。
   - 共用五章（带 `danlogo-core` 标记）：`workflow.md`、`quality-gates.md`、`craft.md`、`deliverables.md`、`feedback-playbook.md`。不要在这里单独改；修改先在 danlogo 系列标准（`danlogo-maker/standard/core/`）中完成，再同步过来。
2. **规则停在原则层**：风格章里不要写具体颜色、形状、标点、工艺或物品的硬规定。具体做法只写进 `cases/` 的案例，并标注“只借方法，不借形式”。
3. **每条规则写清楚为什么**，并配一个可以执行的自检问题。
4. **新增案例**：放进 `cases/<案例名>/`，包含过程、每轮用户原话、被否方向与原因、最终方案、旋钮取值、可借的方法、关键图片。客户信息是否匿名由用户决定。
5. **改完要做的事**：更新 `VERSION`（小改动加第三位，新增案例或规则调整加第二位）与 `CHANGELOG.md`；`SKILL.md` 控制在 150 行以内；frontmatter 的 `name` 必须与文件夹名一致，`description` 不超过 1024 个字符。
6. **不要提交**：`dist/`、项目文件、客户的原始资料。
