# MySkills

这个仓库用于保存和迭代可复用的 Codex skills。每个 skill 都放在独立的主题文件夹中，并按版本号归档，方便后续升级、回滚和对比。

## 仓库基础信息

- 仓库名称：`MySkills`
- 仓库用途：集中管理个人或团队使用的 Codex skills
- 目录组织：`<Skill 主题>/<版本>/<skill-name 版本>/`
- 当前包含的 skills：
  - `Video to Document`：把视频或音频转换为 Markdown 文档，输出原文转写、概述和总结。
  - `The skill of converting PDF files to MD files`：把 PDF 转换为 Markdown，并支持图片、章节和衍生分析文档。

## Skill 目录

| Skill | 最新版本 | 说明 |
| --- | --- | --- |
| `Video to Document` | `1.0` | 将视频/音频转写为 Markdown，包含 `原文`、`概述`、`总结` 三个部分。 |
| `The skill of converting PDF files to MD files` | `1.3` | 将 PDF 转换为 Markdown，支持章节拆分、图片提取、章节书评和 RAG 知识库训练数据集。 |

## 新增或更新 skill 的约定

1. 为每个 skill 创建独立主题文件夹，例如 `Video to Document/`。
2. 在主题文件夹下按版本号创建目录，例如 `1.0/`、`1.1/`。
3. 在版本目录中放置完整 skill 文件夹，至少包含 `SKILL.md`；如有脚本、模板或 UI 元数据，也一并放入该 skill 文件夹。
4. 在版本目录中保留 `说明.txt`，用一句话描述该版本的用途。
5. 修改、新增或删除 skill 后，同步更新本 README 的基础信息和 skill 目录。
