---
name: convert-pdf-to-markdown
description: "Split book or long-form PDFs into chapter-based PDF folders before converting each chapter PDF into Markdown, extracting embedded images, preserving figure/table captions, and optionally generating two additional Markdown deliverables from the extracted text: a deep book-review analysis and a RAG knowledge-base training dataset. Use when Codex needs to split a PDF by internal outline/bookmarks or visible chapter headings, turn each part into a .md extraction, save PDF images into Markdown asset folders, keep relative links for Typora or other Markdown editors, identify captions such as 图1-1, 图 2-3, 表1-1, Figure 1-1, or Table 1-1, place images near their original captions, and produce companion Markdown files for reading analysis or retrieval training."
---

# Convert PDF to Markdown

Use this skill when the user wants a PDF split by chapter and turned into reusable Markdown, especially when image extraction and downstream reading-analysis assets matter.

## Bundled Resources

- Use `scripts/split_and_convert_by_chapters.py` as the default entry point for book or long-form PDFs.
- Use `scripts/pdf_to_markdown.py` only for a single chapter PDF, a short PDF, or when the user explicitly asks not to split.
- Read `references/book-review-analysis-prompt.md` before generating the deep review Markdown.
- Read `references/rag-training-dataset-prompt.md` before generating the RAG training dataset Markdown.

## Workflow

1. Locate the input PDF and confirm or choose one output directory for the chapter folders.
2. Split the PDF before extraction:
   - Prefer PDF outline/bookmark entries via `scripts/split_and_convert_by_chapters.py`.
   - If the PDF has no outline, let the script fall back to visible page headings such as `第1章 ...`, `Chapter 1 ...`, or numbered headings.
   - Keep pages before the first detected chapter in a `front-matter` folder unless the user says to omit them.
3. Put each chapter in its own folder. Each folder should contain:
   - The chapter PDF slice.
   - The chapter extraction Markdown.
   - An `images/` folder for images extracted from that chapter.
4. Convert each chapter PDF to Markdown using the same extraction behavior as `scripts/pdf_to_markdown.py`.
5. Save images into the chapter image folder. Prefer relative links from the chapter Markdown; use absolute links only when needed.
6. Match each image with nearby captions below or above the image. Handle Chinese and English figure/table captions:
   - `图1-1 标题`
   - `图 2-3 标题`
   - `表1-1 标题`
   - `Figure 1-1 Title`
   - `Table 1-1 Title`
7. Preserve the reading order by sorting page blocks from top to bottom, left to right.
8. Keep original captions as normal Markdown text near the image. Do not turn figure/table captions into headings unless the document clearly treats them as section headings.
9. Treat the extracted chapter Markdown files as the source text for the two additional deliverables. Do not prompt from PDF screenshots when extracted Markdown is available.
10. Generate these outputs unless the user explicitly asks for fewer:
   - One extraction Markdown per chapter folder.
   - A deep book-review analysis Markdown based on `references/book-review-analysis-prompt.md`.
   - A RAG knowledge-base training dataset Markdown based on `references/rag-training-dataset-prompt.md`.
11. For the book-review analysis:
   - Replace placeholders such as `【书名】` and `【作者名】` if the PDF or user provides them.
   - Base every conclusion on the extracted chapter Markdown text.
   - If the source text is incomplete or OCR quality is weak, say so explicitly inside the analysis.
12. For the RAG training dataset:
   - Prefer one section per chapter folder when the book is long.
   - Keep the distinction between source facts and model inference explicit.
   - Do not invent external examples, author background, or facts from other chapters unless the user separately provides them.
13. If the user does not specify names, prefer:
   - `<index>-<chapter-title>/<index>-<chapter-title>.md` for each extraction.
   - `<stem>-书评分析.md` for the deep review.
   - `<stem>-RAG训练数据集.md` for the dataset.
14. Validate the result:
   - Count chapter folders and confirm page ranges cover the PDF once.
   - Count Markdown image links across chapter extraction files.
   - List saved image files or summarize image counts by chapter.
   - Check that image links resolve from each chapter Markdown location.
   - Confirm the two derived Markdown files clearly state their scope and constraints.
   - Spot-check pages with figures or tables if visual fidelity is important.

## Script Usage

Run:

```bash
python scripts/split_and_convert_by_chapters.py input.pdf output-folder
```

Optional flags:

```bash
python scripts/split_and_convert_by_chapters.py input.pdf output-folder --toc-level 1
python scripts/split_and_convert_by_chapters.py input.pdf output-folder --absolute-links
python scripts/split_and_convert_by_chapters.py input.pdf output-folder --overwrite-images
python scripts/split_and_convert_by_chapters.py input.pdf output-folder --no-leading-pages
```

Use `--toc-level` when the PDF outline has nested levels and a non-default level is the correct chapter boundary. The default uses the shallowest outline level. If no outline exists, the script uses visible chapter headings as a fallback.

For a single PDF without chapter splitting, run:

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
- If the source text is a full book, the review deliverable may work best at whole-book scope, while the RAG deliverable usually works best chapter by chapter.
- If the PDF extraction quality is poor, clean the Markdown before generating the two derivative Markdown files.
- Keep the two prompt templates bundled inside the skill. Do not rely on unrelated workspace files when invoking the skill in another environment.
- If writing to the user's requested directory needs approval, request approval. If approval is unavailable, generate the files in the workspace and clearly report the intended final destination.
