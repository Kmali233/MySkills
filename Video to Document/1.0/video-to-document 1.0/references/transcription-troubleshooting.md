# Transcription Troubleshooting

Use this reference when video/audio extraction succeeds but transcription fails before producing text.

## Model download fails with SSL, EOF, snapshot_download, or LocalEntryNotFoundError

This usually means the backend cannot download the Whisper model from Hugging Face or another model host. It is a network/proxy/mirror problem, not a problem with the extracted audio file.

Recommended recovery order:

1. Reuse the extracted audio instead of running ffmpeg again:

   ```bash
   python scripts/video_to_document.py input.mp4 output.md --audio-input input_audio.wav --model small --language zh
   ```

2. Try a Hugging Face mirror for `faster-whisper` downloads:

   ```bash
   python scripts/video_to_document.py input.mp4 output.md --engine faster-whisper --model small --language zh --hf-endpoint https://hf-mirror.com
   ```

3. Use an existing model cache and block network access:

   ```bash
   python scripts/video_to_document.py input.mp4 output.md --engine faster-whisper --model small --download-root /path/to/model-cache --local-files-only
   ```

4. Use a fully downloaded local model directory:

   ```bash
   python scripts/video_to_document.py input.mp4 output.md --engine faster-whisper --model /path/to/faster-whisper-small --local-files-only --language zh
   ```

5. If another transcription tool is available, create a transcript text file and skip Whisper entirely:

   ```bash
   python scripts/video_to_document.py input.mp4 output.md --transcript-file transcript.txt
   ```

## Notes

- `--audio-input` is useful after a previous run already created a `.wav` file. It avoids repeating the expensive audio extraction step.
- `--local-files-only` is intended for cached or fully downloaded models. If the requested model is not present locally, transcription should fail quickly instead of hanging on a network download.
- `--hf-endpoint` sets `HF_ENDPOINT` for the current script process before loading `faster-whisper`.
- For CPU-only environments, try `--device cpu --compute-type int8` if the default compute type is unsupported.
