# Contributing Guide

感谢你为 MySkills 贡献 Skill、脚本和文档。为了让仓库便于维护、安装和审查，请遵循以下流程。

## 贡献原则

- **一个变更聚焦一个目标**：新增 Skill、修复脚本、更新提示词或调整文档尽量拆成独立 PR。
- **保留版本历史**：已有版本如果仍有用户依赖，优先新增版本目录，而不是直接覆盖旧版本。
- **入口清晰**：每个可用 Skill 都必须有 `SKILL.md`，并在开头写明 `name` 和 `description`。
- **资源内聚**：Skill 运行所需脚本、提示词、模板和说明应放在该 Skill 目录内，避免依赖仓库外文件。
- **不提交生成缓存**：不要提交 `__pycache__`、`.pyc`、虚拟环境、临时输出或大体积生成文件。

## 新增或升级 Skill

1. 选择目录命名：
   - 新 Skill：`<category>/<version>/<skill-name>/`。
   - 新版本：在同一类别下新增版本目录，如 `1.4/<skill-name> 1.4/`。
2. 编写 `SKILL.md`：
   - 必须包含 YAML front matter。
   - `name` 使用小写字母、数字和连字符。
   - `description` 要写明触发场景和主要能力。
3. 放置附加资源：
   - 脚本放在 `scripts/`。
   - 提示词、模板和背景资料放在 `references/`。
   - Agent 配置放在 `agents/`。
4. 更新根目录 `README.md` 中的 Skill 清单和推荐版本。
5. 运行校验并在 PR 中填写测试结果。

## 本地检查清单

```bash
python scripts/validate_skills.py
python -m compileall "The skill of converting PDF files to MD files"
```

如果新增了其他语言的脚本，也请运行对应语言的 lint 或测试命令，并在 PR 中说明。

## PR 要求

PR 描述应包含：

- 改动摘要。
- 影响的 Skill 和版本。
- 测试或校验命令。
- 是否存在兼容性影响。

请使用仓库默认 PR 模板填写。
