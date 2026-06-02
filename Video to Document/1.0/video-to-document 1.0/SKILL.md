---
name: video-to-document
description: "Convert video files into Markdown documents that include the original transcript, an overview, and a summary. Use when Codex needs to process a local video or extracted audio, transcribe speech from formats such as mp4, mov, mkv, webm, avi, m4v, mp3, m4a, or wav, preserve timestamped original text, clean transcript artifacts, and write a structured .md document with sections for 原文, 概述, and 总结."
---

# Video to Document

Use this skill to turn a video or audio file into a Markdown document that contains the original transcript, an overview, and a summary.

## Bundled Resources

- Use `scripts/video_to_document.py` as the default helper for audio extraction, local transcription when a supported transcription package is installed, and Markdown scaffolding.
- Use `references/document-template.md` as the required output structure and section naming guide.
- Read `references/transcription-troubleshooting.md` when ffmpeg extraction succeeds but Whisper model loading or download fails.

## Workflow

1. Locate the user's input video or audio file. Accept common formats such as `.mp4`, `.mov`, `.mkv`, `.webm`, `.avi`, `.m4v`, `.mp3`, `.m4a`, and `.wav`.
2. Choose an output Markdown path. If the user does not specify one, write `<video-stem>.md` next to the source file or in the user's requested output directory.
3. Transcribe the source:
   - Prefer running `scripts/video_to_document.py` when the environment has `ffmpeg` and either `openai-whisper` or `faster-whisper` installed.
   - If the user already provides a transcript, pass it with `--transcript-file` and skip transcription.
   - If a previous run already extracted a `.wav` file, pass it with `--audio-input` to avoid repeating ffmpeg.
   - If Whisper model download fails with SSL, EOF, `snapshot_download`, or `LocalEntryNotFoundError`, treat it as a network/proxy issue. Read `references/transcription-troubleshooting.md`, then use `--hf-endpoint`, `--download-root`, `--local-files-only`, or a local model directory.
   - If local transcription tools are missing, extract or request a transcript using whatever transcription method is available in the environment, then continue with the Markdown generation.
4. Preserve the original transcript in the `## 原文` section. Keep timestamps when they are available because they make the document auditable.
5. Clean only obvious transcription artifacts before summarizing. Do not silently rewrite the `## 原文` section into a paraphrase; it must remain the original transcript text.
6. Write `## 概述` as a coherent overview of the video's topic, structure, major sections, speakers if identifiable, and the purpose of the content.
7. Write `## 总结` as the final synthesis. Prefer concise bullet points for key takeaways, decisions, action items, or conclusions.
8. Ground every overview and summary statement in the transcript. If audio is unclear, speaker names are unknown, or the transcript has gaps, say so explicitly in the Markdown.
9. For long videos, summarize by timestamped chunks first, then combine the chunk summaries into the final overview and summary. Keep the final Markdown readable rather than dumping internal chunk notes unless the user asks for them.
10. Validate the deliverable:
    - Confirm the Markdown file exists and is non-empty.
    - Confirm it contains `## 原文`, `## 概述`, and `## 总结` sections.
    - Confirm the `## 原文` section contains transcript text, not only a placeholder.
    - Confirm the overview and summary are substantive, grounded in the transcript, and not generic placeholders.

## Script Usage

Create a Markdown document by transcribing a video locally:

```bash
python scripts/video_to_document.py input.mp4 output.md
```

Create a Markdown document from an existing transcript:

```bash
python scripts/video_to_document.py input.mp4 output.md --transcript-file transcript.txt
```

Useful options:

```bash
python scripts/video_to_document.py input.mp4 output.md --language zh --model small
python scripts/video_to_document.py input.mp4 output.md --audio-input input_audio.wav --model small --language zh
python scripts/video_to_document.py input.mp4 output.md --engine faster-whisper --model small --hf-endpoint https://hf-mirror.com
python scripts/video_to_document.py input.mp4 output.md --engine faster-whisper --model /path/to/faster-whisper-small --local-files-only
python scripts/video_to_document.py input.mp4 output.md --title "课程第 1 讲" --keep-audio
python scripts/video_to_document.py input.mp4 output.md --no-timestamps
```

The script may create a first-pass overview and summary from the transcript. Treat those as a draft: revise them with Codex so the final Markdown is accurate, specific, and useful.

## Notes

- `ffmpeg` is required for extracting audio from video files when no transcript is provided.
- `openai-whisper` or `faster-whisper` is required for local transcription by the bundled script. If neither package is installed, install one or use another available transcription source.
- `faster-whisper` model names such as `base` or `small` may require downloading from Hugging Face. For restricted networks, prefer a local model directory or cached model plus `--local-files-only`.
- For Chinese content, keep section headings in Chinese: `原文`, `概述`, and `总结`.
- For multilingual videos, preserve the original language in `## 原文`; summarize in the language requested by the user, or in Chinese if no preference is specified.
