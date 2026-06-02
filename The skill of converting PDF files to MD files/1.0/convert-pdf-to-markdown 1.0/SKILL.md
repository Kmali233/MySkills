---
name: convert-pdf-to-markdown
description: Convert PDFs into Markdown while extracting embedded images and preserving figure/table captions. Use when Codex needs to turn a PDF into a .md file, save PDF images into a Markdown asset folder, keep relative image links for Typora or other Markdown editors, identify captions such as 图1-1, 图 2-3, 表1-1, Figure 1-1, or Table 1-1, and place images near their original captions.
---

# Convert PDF to Markdown

Use this skill for PDF-to-Markdown conversion when image handling matters.

## Workflow

1. Locate the input PDF and confirm the requested Markdown output path and image folder.
2. Use `scripts/pdf_to_markdown.py` for the first pass whenever Python and PyMuPDF are available.
3. Save images into the requested image folder. Prefer the user's requested folder even when it differs from the Markdown file's folder; use relative links when possible and absolute links only when needed.
4. Match each image with nearby captions below or above the image. Handle Chinese and English figure/table captions:
   - `图1-1 标题`
   - `图 1-1 标题`
   - `表1-1 标题`
   - `Figure 1-1 Title`
   - `Table 1-1 Title`
5. Preserve the reading order by sorting page blocks from top to bottom, left to right.
6. Keep original captions as normal Markdown text near the image. Do not turn figure/table captions into headings unless the document clearly treats them as section headings.
7. Validate the result:
   - Count Markdown image links.
   - List saved image files.
   - Check that image links resolve from the Markdown file location.
   - Spot-check pages with figures or tables if visual fidelity is important.

## Script Usage

Run:

```bash
python scripts/pdf_to_markdown.py input.pdf output.md image-folder
```

Optional flags:

```bash
python scripts/pdf_to_markdown.py input.pdf output.md image-folder --absolute-links
python scripts/pdf_to_markdown.py input.pdf output.md image-folder --overwrite-images
```

Use `--absolute-links` when the Markdown file and image directory are on different Windows drives and a relative path cannot be computed.

## Notes

- If `fitz` is missing, install PyMuPDF or fall back to local PDF tooling already available in the environment.
- For image quality, prefer extracting embedded image bytes over full-page screenshots.
- If a PDF stores tables as images, keep them as image links and preserve the `表x-x` caption.
- If writing to the user's requested directory needs approval, request approval. If approval is unavailable, generate the files in the workspace and clearly report the intended final destination.
