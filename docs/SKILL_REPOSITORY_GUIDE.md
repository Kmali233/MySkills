# Skill Repository Guide

本文档定义 MySkills 仓库中 Skill 的组织、版本化和发布前检查规范。

## 1. Skill 入口规范

每个可分发 Skill 目录必须包含 `SKILL.md`。文件开头必须是 YAML front matter：

```markdown
---
name: convert-pdf-to-markdown
description: "在用户需要把 PDF 按章节拆分并转换为 Markdown 时使用……"
---
```

字段要求：

- `name`：使用小写字母、数字和连字符，例如 `convert-pdf-to-markdown`。
- `description`：说明触发条件、主要能力、输出物和边界条件；不要只写一句泛泛描述。
- 正文：包含工作流、脚本用法、输出结构和验证步骤。

## 2. 目录结构规范

推荐结构：

```text
<skill-group>/<version>/<skill-name>/
├── SKILL.md
├── agents/
├── references/
└── scripts/
```

目录用途：

- `agents/`：保存 agent 或模型配置。
- `references/`：保存提示词、模板、示例和长参考资料。
- `scripts/`：保存可复用自动化脚本。

避免把临时输出、测试生成文件、PDF 原文或大型二进制文件放入 Skill 目录；如确有必要，应在 PR 中说明来源、用途和许可。

## 3. 版本化规范

- 新增能力但可能改变输出结构时，新增版本目录。
- 修复拼写、补充说明或不影响使用方式的小修可以直接改当前版本。
- README 中应标明当前推荐版本。
- 旧版本目录原则上不删除，除非确认无人依赖且 PR 中说明迁移方式。

## 4. 脚本规范

- Python 脚本应能通过 `python -m compileall <path>`。
- 不要提交 `__pycache__` 或 `.pyc` 文件。
- 脚本应提供命令行帮助或在 `SKILL.md` 中说明参数。
- 如果脚本依赖外部包，应在 `SKILL.md` 或版本说明中写明安装方式和替代方案。

## 5. 发布前检查

提交前运行：

```bash
python scripts/validate_skills.py
python -m compileall "The skill of converting PDF files to MD files"
```

PR 合并前确认：

- `README.md` Skill 清单已更新。
- `SKILL.md` 的 front matter 可被校验脚本识别。
- 所有新增脚本均已通过基本编译或测试。
- 没有误提交缓存、临时文件或敏感信息。
