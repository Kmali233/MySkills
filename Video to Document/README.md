# Video to Document

`Video to Document` 是一个把视频或音频转换为 Markdown 文档的 Codex skill。输出文档必须包含：

- `原文`：视频或音频的原始转写文本，可包含时间戳。
- `概述`：对视频主题、结构、主要内容和上下文的整体说明。
- `总结`：对关键结论、要点、行动项或最终观点的精炼总结。

## 当前版本

| 版本 | 路径 | 说明 |
| --- | --- | --- |
| `1.0` | `1.0/video-to-document 1.0/` | 首个版本，包含 skill 指南、Markdown 模板、UI 元数据、转写/生成辅助脚本和模型下载故障处理说明。 |

## 使用入口

请从最新版本目录中的 `SKILL.md` 开始使用：

```text
Video to Document/1.0/video-to-document 1.0/SKILL.md
```


## 当前已覆盖的阻塞场景

如果 `ffmpeg` 已成功抽取音频，但 `faster-whisper` 在下载 `small`、`base` 等模型时因为 Hugging Face SSL/EOF/network 问题失败，可以使用最新脚本参数：

- `--audio-input`：复用已抽取的 `.wav`，避免重复跑 ffmpeg。
- `--hf-endpoint`：为 `faster-whisper` 设置 Hugging Face 镜像端点。
- `--download-root`：指定模型缓存目录。
- `--local-files-only`：只使用本地缓存或本地模型目录，避免继续卡在网络下载。
- `--model /path/to/local-model`：直接使用已经下载好的本地模型目录。
