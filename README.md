# MySkills

MySkills 是一个用于存放、迭代和分发 Codex / ChatGPT Skills 的仓库。当前仓库主要维护 `convert-pdf-to-markdown` 系列技能：把 PDF 拆分为章节级 Markdown，并生成图片资源、章节深度书评和 RAG 知识库训练数据集。

## 仓库内容

| Skill | 版本 | 路径 | 说明 |
| --- | --- | --- | --- |
| `convert-pdf-to-markdown` | 1.0 | `The skill of converting PDF files to MD files/1.0/convert-pdf-to-markdown 1.0/` | PDF 转 Markdown 的初始版本。 |
| `convert-pdf-to-markdown` | 1.1 | `The skill of converting PDF files to MD files/1.1/convert-pdf-to-markdown 1.1/` | 增加读书分析和 RAG 相关提示词资源。 |
| `convert-pdf-to-markdown` | 1.2 | `The skill of converting PDF files to MD files/1.2/convert-pdf-to-markdown 1.2/` | 增加按章节拆分和转换脚本。 |
| `convert-pdf-to-markdown` | 1.3 | `The skill of converting PDF files to MD files/1.3/convert-pdf-to-markdown 1.3/` | 当前推荐版本，支持章节拆分、图片提取、章节深度书评和 RAG 数据集输出。 |

> 建议优先使用最新稳定版本：`The skill of converting PDF files to MD files/1.3/convert-pdf-to-markdown 1.3/`。

## 推荐的 Skill 目录结构

每个可分发 Skill 目录应尽量遵循下面的结构：

```text
skill-name/
├── SKILL.md                 # 必需：Skill 入口说明，包含 front matter
├── agents/                  # 可选：模型或 agent 配置
├── references/              # 可选：提示词、模板、参考文档
└── scripts/                 # 可选：自动化脚本或工具
```

`SKILL.md` 必须包含 YAML front matter：

```markdown
---
name: skill-name
description: "说明该 Skill 什么时候应该被使用"
---

# Skill Title

使用说明……
```

更多规范请见 [`docs/SKILL_REPOSITORY_GUIDE.md`](docs/SKILL_REPOSITORY_GUIDE.md)。

## 本地校验

提交前建议运行：

```bash
python scripts/validate_skills.py
python -m compileall "The skill of converting PDF files to MD files"
```

校验脚本会检查：

- 每个 `SKILL.md` 是否包含 `name` 和 `description`。
- Skill 名称是否使用小写字母、数字和连字符。
- 描述是否足够明确。
- 仓库是否误提交 `__pycache__` 或 `.pyc` 文件。

## GitHub 标准化流程

本仓库已加入以下标准化文件：

- `.editorconfig`：统一基础编辑器格式。
- `.gitignore`：避免提交缓存、构建产物和本地环境文件。
- `.github/workflows/validate-skills.yml`：在 Pull Request 和 push 时运行 Skill 校验与 Python 编译检查。
- `.github/pull_request_template.md`：统一 PR 描述、测试和影响范围。
- `.github/ISSUE_TEMPLATE/`：提供 Bug 和 Skill 需求模板。
- `CONTRIBUTING.md`：说明贡献、版本化和发布前检查流程。

## 贡献方式

1. 新增或修改 Skill 时，优先复制一个已有版本作为基线。
2. 在 `SKILL.md` 中更新 `name`、`description` 和工作流说明。
3. 把大段提示词、示例输入输出和脚本放到 `references/` 或 `scripts/`，避免入口文件过长。
4. 运行本地校验。
5. 按 PR 模板说明改动范围和测试结果。

## 许可

如果你计划公开分发本仓库，请在合并前补充适合项目的 `LICENSE` 文件，并确认每个 Skill 内引用的提示词、脚本和资料允许再分发。
