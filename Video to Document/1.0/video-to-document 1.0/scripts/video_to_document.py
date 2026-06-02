#!/usr/bin/env python3
"""Create a Markdown document from a video/audio file or an existing transcript.

The document always contains three required sections:
- 原文
- 概述
- 总结
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SENTENCE_RE = re.compile(r"(?<=[。！？.!?])\s+")
SPACE_RE = re.compile(r"[ \t]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a video/audio file or transcript into a Markdown document."
    )
    parser.add_argument("source", help="Input video/audio path. Used for metadata even when --transcript-file is provided.")
    parser.add_argument("output", help="Output Markdown path.")
    parser.add_argument("--transcript-file", help="Existing transcript text file; skips local transcription.")
    parser.add_argument("--title", help="Document title. Defaults to the source file stem.")
    parser.add_argument("--language", help="Optional transcription language hint, such as zh or en.")
    parser.add_argument("--model", default="base", help="Whisper model name or local model directory. Defaults to base.")
    parser.add_argument(
        "--engine",
        choices=("auto", "faster-whisper", "openai-whisper"),
        default="auto",
        help="Transcription backend. Defaults to auto, which tries faster-whisper first.",
    )
    parser.add_argument("--audio-input", help="Existing extracted audio path; skips ffmpeg extraction.")
    parser.add_argument("--audio-output", help="Path for extracted WAV audio. Defaults to a temporary file.")
    parser.add_argument("--keep-audio", action="store_true", help="Keep the extracted temporary audio file.")
    parser.add_argument("--download-root", help="Model cache/download directory for Whisper backends.")
    parser.add_argument("--hf-endpoint", help="Hugging Face endpoint mirror for faster-whisper downloads, such as https://hf-mirror.com.")
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Do not download models; require --model or cached model files to exist locally.",
    )
    parser.add_argument("--device", default="auto", help="Device for faster-whisper, such as auto, cpu, or cuda. Defaults to auto.")
    parser.add_argument("--compute-type", default="default", help="Compute type for faster-whisper. Defaults to default.")
    parser.add_argument("--no-timestamps", action="store_true", help="Do not include segment timestamps in 原文.")
    return parser.parse_args()


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"{label} not found: {path}")
    if not path.is_file():
        raise SystemExit(f"{label} is not a file: {path}")


def run_ffmpeg_extract_audio(source: Path, audio_path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit(
            "ffmpeg is required to extract audio when no --transcript-file is provided. "
            "Install ffmpeg or provide --transcript-file."
        )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(audio_path),
    ]
    subprocess.run(cmd, check=True)


def format_timestamp(seconds: float | int | None) -> str:
    if seconds is None:
        return "00:00:00"
    total = int(max(0, float(seconds)))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def normalize_text(text: str) -> str:
    lines = [SPACE_RE.sub(" ", line).strip() for line in text.replace("\r\n", "\n").split("\n")]
    collapsed: list[str] = []
    for line in lines:
        if line or (collapsed and collapsed[-1]):
            collapsed.append(line)
    return "\n".join(collapsed).strip()


def segments_to_transcript(segments: Iterable[dict[str, Any]], include_timestamps: bool) -> str:
    lines: list[str] = []
    for segment in segments:
        text = normalize_text(str(segment.get("text", "")))
        if not text:
            continue
        if include_timestamps:
            start = format_timestamp(segment.get("start"))
            end = format_timestamp(segment.get("end"))
            lines.append(f"[{start} - {end}] {text}")
        else:
            lines.append(text)
    return "\n".join(lines).strip()


def package_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def transcribe_with_openai_whisper(
    audio_path: Path,
    model_name: str,
    language: str | None,
    include_timestamps: bool,
    download_root: str | None,
) -> str:
    if not package_available("whisper"):
        raise RuntimeError("openai-whisper package is not installed")

    whisper = importlib.import_module("whisper")
    model_kwargs: dict[str, Any] = {}
    if download_root:
        model_kwargs["download_root"] = download_root
    model = whisper.load_model(model_name, **model_kwargs)
    options: dict[str, Any] = {}
    if language:
        options["language"] = language
    result = model.transcribe(str(audio_path), **options)
    segments = result.get("segments") or []
    if segments:
        return segments_to_transcript(segments, include_timestamps)
    return normalize_text(str(result.get("text", "")))


def transcribe_with_faster_whisper(
    audio_path: Path,
    model_name: str,
    language: str | None,
    include_timestamps: bool,
    download_root: str | None,
    local_files_only: bool,
    device: str,
    compute_type: str,
) -> str:
    if not package_available("faster_whisper"):
        raise RuntimeError("faster-whisper package is not installed")

    faster_whisper = importlib.import_module("faster_whisper")
    model_kwargs: dict[str, Any] = {
        "device": device,
        "compute_type": compute_type,
        "local_files_only": local_files_only,
    }
    if download_root:
        model_kwargs["download_root"] = download_root
    model = faster_whisper.WhisperModel(model_name, **model_kwargs)
    kwargs: dict[str, Any] = {}
    if language:
        kwargs["language"] = language
    segments_iter, _info = model.transcribe(str(audio_path), **kwargs)
    segments = [
        {"start": segment.start, "end": segment.end, "text": segment.text}
        for segment in segments_iter
    ]
    return segments_to_transcript(segments, include_timestamps)


def transcribe_audio(
    audio_path: Path,
    model_name: str,
    language: str | None,
    include_timestamps: bool,
    engine: str,
    download_root: str | None,
    hf_endpoint: str | None,
    local_files_only: bool,
    device: str,
    compute_type: str,
) -> str:
    if hf_endpoint:
        os.environ["HF_ENDPOINT"] = hf_endpoint

    engine_order = ["faster-whisper", "openai-whisper"] if engine == "auto" else [engine]
    errors: list[str] = []
    for selected_engine in engine_order:
        try:
            if selected_engine == "faster-whisper":
                transcript = transcribe_with_faster_whisper(
                    audio_path,
                    model_name,
                    language,
                    include_timestamps,
                    download_root,
                    local_files_only,
                    device,
                    compute_type,
                )
            else:
                transcript = transcribe_with_openai_whisper(
                    audio_path, model_name, language, include_timestamps, download_root
                )
        except Exception as exc:  # noqa: BLE001 - surface backend/network failures with actionable guidance.
            errors.append(f"{selected_engine}: {exc}")
            continue
        if transcript:
            return transcript
        errors.append(f"{selected_engine}: returned an empty transcript")

    guidance = [
        "Transcription failed before a transcript could be produced.",
        "Backend errors:",
        *(f"- {error}" for error in errors),
        "",
        "If the failure mentions huggingface_hub, SSL, EOF, snapshot_download, or "
        "LocalEntryNotFoundError, the model download failed. Use one of these fixes:",
        "1. Download/cache the model on a machine with working network, then rerun with --model <local-model-dir> --local-files-only.",
        "2. Reuse an existing cache with --download-root <cache-dir> --local-files-only.",
        "3. Try a Hugging Face mirror with --hf-endpoint https://hf-mirror.com.",
        "4. If audio extraction already succeeded, rerun with --audio-input <extracted-audio.wav> to avoid repeating ffmpeg.",
        "5. If another tool produced text, rerun with --transcript-file <transcript.txt>.",
    ]
    raise SystemExit("\n".join(guidance))


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\[[0-9:]+\s*-\s*[0-9:]+\]", "", text)
    cleaned = normalize_text(cleaned).replace("\n", " ")
    if not cleaned:
        return []
    parts = SENTENCE_RE.split(cleaned)
    if len(parts) == 1:
        parts = re.split(r"(?<=[。！？.!?])", cleaned)
    return [part.strip() for part in parts if part.strip()]


def make_draft_overview(transcript: str) -> str:
    sentences = split_sentences(transcript)
    if not sentences:
        return "待根据原文补充概述。"
    selected = sentences[: min(5, len(sentences))]
    return "本视频主要围绕以下内容展开：" + " ".join(selected)


def make_draft_summary(transcript: str) -> str:
    sentences = split_sentences(transcript)
    if not sentences:
        return "- 待根据原文补充总结。"
    selected: list[str] = []
    if sentences:
        selected.append(sentences[0])
    if len(sentences) > 2:
        selected.append(sentences[len(sentences) // 2])
    if len(sentences) > 1:
        selected.append(sentences[-1])
    unique: list[str] = []
    for sentence in selected:
        if sentence not in unique:
            unique.append(sentence)
    return "\n".join(f"- {sentence}" for sentence in unique[:5])


def render_markdown(title: str, source: Path, transcript: str) -> str:
    generated_at = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
    overview = make_draft_overview(transcript)
    summary = make_draft_summary(transcript)
    return f"""# {title}

- 来源视频：`{source}`
- 生成时间：{generated_at}
- 说明：概述和总结为基于转写文本生成的初稿；交付前请根据原文复核并补充具体细节。

## 原文

{transcript}

## 概述

{overview}

## 总结

{summary}
"""


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    require_file(source, "source")

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    audio_path: Path | None = None
    try:
        if args.transcript_file:
            transcript_path = Path(args.transcript_file).expanduser().resolve()
            require_file(transcript_path, "transcript")
            transcript = normalize_text(transcript_path.read_text(encoding="utf-8"))
        else:
            if args.audio_input:
                audio_path = Path(args.audio_input).expanduser().resolve()
                require_file(audio_path, "audio input")
            elif source.suffix.lower() == ".wav":
                audio_path = source
            else:
                if args.audio_output:
                    audio_path = Path(args.audio_output).expanduser().resolve()
                    audio_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    temp_dir = tempfile.TemporaryDirectory(prefix="video-to-document-")
                    audio_path = Path(temp_dir.name) / "audio.wav"
                run_ffmpeg_extract_audio(source, audio_path)
            transcript = transcribe_audio(
                audio_path,
                args.model,
                args.language,
                not args.no_timestamps,
                args.engine,
                args.download_root,
                args.hf_endpoint,
                args.local_files_only,
                args.device,
                args.compute_type,
            )

        if not transcript:
            raise SystemExit("Transcript is empty; cannot create a useful Markdown document.")

        title = args.title or source.stem
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_markdown(title, source, transcript), encoding="utf-8")
        print(f"Wrote Markdown document: {output}")
        return 0
    finally:
        if temp_dir is not None and not args.keep_audio:
            temp_dir.cleanup()


if __name__ == "__main__":
    sys.exit(main())
