---
name: convert-pdf-to-markdown
description: "Convert PDFs into Markdown while extracting embedded images and preserving figure/table captions, then generate two additional Markdown deliverables from the extracted text: a deep book-review analysis and a RAG knowledge-base training dataset. Use when Codex needs to turn a book or long-form PDF into a .md extraction, save PDF images into a Markdown asset folder, keep relative image links for Typora or other Markdown editors, identify captions such as 图1-1, 图 2-3, 表1-1, Figure 1-1, or Table 1-1, place images near their original captions, and produce companion Markdown files for reading analysis or retrieval training."
---

# Convert PDF to Markdown

Use this skill when the user wants a PDF turned into reusable Markdown and also wants downstream reading-analysis assets generated from that Markdown.

## Bundled Resources

- Use `scripts/pdf_to_markdown.py` for the PDF extraction pass.
- Read `references/book-review-analysis-prompt.md` before generating the deep review Markdown.
- Read `references/rag-training-dataset-prompt.md` before generating the RAG training dataset Markdown.

## Workflow

1. Locate the input PDF and confirm the requested output directory, extraction Markdown path, and image folder.
2. Use `scripts/pdf_to_markdown.py` for the first pass whenever Python and PyMuPDF are available.
3. Save images into the requested image folder. Prefer the user's requested folder even when it differs from the Markdown file's folder; use relative links when possible and absolute links only when needed.
4. Match each image with nearby captions below or above the image. Handle Chinese and English figure/table captions:
   - `图1-1 标题`
   - `图 2-3 标题`
   - `表1-1 标题`
   - `Figure 1-1 Title`
   - `Table 1-1 Title`
5. Preserve the reading order by sorting page blocks from top to bottom, left to right.
6. Keep original captions as normal Markdown text near the image. Do not turn figure/table captions into headings unless the document clearly treats them as section headings.
7. Treat the extracted Markdown as the source text for the two additional deliverables. Do not prompt from PDF screenshots when the extracted Markdown is available.
8. Generate three Markdown outputs in total unless the user explicitly asks for fewer:
   - The extraction Markdown produced from the PDF.
   - A deep book-review analysis Markdown based on `references/book-review-analysis-prompt.md`.
   - A RAG knowledge-base training dataset Markdown based on `references/rag-training-dataset-prompt.md`.
9. For the book-review analysis:
   - Replace placeholders such as `【书名】` and `【作者名】` if the PDF or user provides them.
   - Base every conclusion on the extracted text.
   - If the source text is incomplete or OCR quality is weak, say so explicitly inside the analysis.
10. For the RAG training dataset:
   - Prefer chapter-by-chapter generation when the book is long.
   - Keep the distinction between source facts and model inference explicit.
   - Do not invent external examples, author background, or facts from other chapters unless the user separately provides them.
11. If the user does not specify names, prefer:
   - `<stem>.md` for the extraction.
   - `<stem>-书评分析.md` for the deep review.
   - `<stem>-RAG训练数据集.md` for the dataset.
12. Validate the result:
   - Count Markdown image links in the extraction file.
   - List saved image files.
   - Check that image links resolve from the extraction Markdown location.
   - Confirm the two derived Markdown files clearly state their scope and constraints.
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
- If the source text is a full book, the review deliverable may work best at whole-book scope, while the RAG deliverable usually works best chapter by chapter.
- If the PDF extraction quality is poor, clean the Markdown before generating the two derivative Markdown files.
- Keep the two prompt templates bundled inside the skill. Do not rely on unrelated workspace files when invoking the skill in another environment.
- If writing to the user's requested directory needs approval, request approval. If approval is unavailable, generate the files in the workspace and clearly report the intended final destination.
