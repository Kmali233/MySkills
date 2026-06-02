---
name: convert-pdf-to-markdown
description: "Split book or long-form PDFs into chapter-based PDF folders, convert each chapter PDF into Markdown, extract embedded images, preserve figure/table captions, create a sibling directory for per-chapter deep book reviews, write one complete deep-review Markdown file for each chapter using the bundled 读书 prompt (详细版).md prompt, and write a RAG knowledge-base training dataset Markdown file using the bundled 生成RAG知识库训练数据集.md prompt. Use when Codex needs to split a PDF by internal outline/bookmarks or visible chapter headings, turn each part into a .md extraction, save PDF images into Markdown asset folders, keep relative links for Typora or other Markdown editors, identify captions such as 图1-1, 图 2-3, 表1-1, Figure 1-1, or Table 1-1, place images near their original captions, generate actual non-empty per-chapter deep review .md files, and generate an actual non-empty RAG training dataset .md file for retrieval training."
---

# Convert PDF to Markdown

Use this skill when the user wants a PDF split by chapter and turned into reusable Markdown, especially when image extraction and downstream reading-analysis assets matter.

## Bundled Resources

- Use `scripts/split_and_convert_by_chapters.py` as the default entry point for book or long-form PDFs.
- Use `scripts/pdf_to_markdown.py` only for a single chapter PDF, a short PDF, or when the user explicitly asks not to split.
- Read `references/读书 prompt (详细版).md` before generating per-chapter deep review Markdown files.
- `references/chapter-deep-review-prompt.md` is a copy of the same detailed reading prompt and may be used as an ASCII-safe alias.
- Read `references/book-review-analysis-prompt.md` only when the user also requests a whole-book review.
- Read `references/生成RAG知识库训练数据集.md` before generating the RAG knowledge-base training dataset Markdown.
- `references/rag-training-dataset-prompt.md` is a copy of the same RAG prompt and may be used as an ASCII-safe alias.

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
4. Create a sibling directory next to the total `output-folder` for per-chapter deep reviews. By default, use `<output-folder>-chapter-reviews`; use `--review-dir` only when the user requests a different location.
5. Plan a RAG knowledge-base training dataset Markdown file next to the total `output-folder`. By default, use `<output-folder>-RAG知识库训练数据集.md`; use `--rag-markdown` only when the user requests a different path.
6. Convert each chapter PDF to Markdown using the same extraction behavior as `scripts/pdf_to_markdown.py`.
7. Save images into the chapter image folder. Prefer relative links from the chapter Markdown; use absolute links only when needed.
8. Match each image with nearby captions below or above the image. Handle Chinese and English figure/table captions:
   - `图1-1 标题`
   - `图 2-3 标题`
   - `表1-1 标题`
   - `Figure 1-1 Title`
   - `Table 1-1 Title`
9. Preserve the reading order by sorting page blocks from top to bottom, left to right.
10. Keep original captions as normal Markdown text near the image. Do not turn figure/table captions into headings unless the document clearly treats them as section headings.
11. Treat the extracted chapter Markdown files as the source text for the additional deliverables. Do not prompt from PDF screenshots when extracted Markdown is available.
12. Generate these outputs unless the user explicitly asks for fewer:
   - One extraction Markdown per chapter folder.
   - One actual, complete, non-empty per-chapter deep review Markdown in the sibling review directory, based on `references/读书 prompt (详细版).md`.
   - One actual, complete, non-empty RAG knowledge-base training dataset Markdown based on `references/生成RAG知识库训练数据集.md`.
13. For each per-chapter deep review:
   - Use the corresponding chapter extraction Markdown as the source text.
   - Use the detailed reading prompt in `references/读书 prompt (详细版).md`.
   - Replace placeholders such as `【书名】` and `【作者名】` if the PDF or user provides them.
   - Adapt whole-book wording in the prompt to the current chapter when necessary, without weakening the requested analytical depth.
   - Save the output as `<index>-<chapter-title>-深度书评.md` in the sibling review directory.
   - The file must contain the generated review content, not a placeholder, target path list, or prompt-only stub.
   - Base every conclusion on the extracted chapter text.
   - If the source text is incomplete or OCR quality is weak, say so explicitly inside the review.
14. For the RAG knowledge-base training dataset:
   - Use `references/生成RAG知识库训练数据集.md` as the prompt.
   - Process chapter by chapter from the extracted chapter Markdown files, not from PDF screenshots.
   - Generate a single combined Markdown dataset file by default at `<output-folder>-RAG知识库训练数据集.md`.
   - Include one dataset section per chapter with the chapter title, core keywords, human-readable summary, and QA table required by the prompt.
   - Keep each chapter's RAG dataset grounded in that chapter only; do not blend in facts from other chapters unless clearly labeled as cross-chapter synthesis requested by the user.
   - The file must contain the generated dataset content, not a placeholder, target path list, or prompt-only stub.
   - If a chapter is too short, front matter, references, or otherwise unsuitable for QA generation, still create a short section explaining why it was skipped or limited.
15. For an optional whole-book review:
   - Replace placeholders such as `【书名】` and `【作者名】` if the PDF or user provides them.
   - Base every conclusion on the extracted chapter Markdown text.
   - If the source text is incomplete or OCR quality is weak, say so explicitly inside the analysis.
16. If the user does not specify names, prefer:
   - `<index>-<chapter-title>/<index>-<chapter-title>.md` for each extraction.
   - `<output-folder>-chapter-reviews/<index>-<chapter-title>-深度书评.md` for each per-chapter deep review.
   - `<output-folder>-RAG知识库训练数据集.md` for the RAG dataset.
17. Validate the result:
   - Count chapter folders and confirm page ranges cover the PDF once.
   - Count per-chapter deep review files and confirm each chapter extraction has one matching review, unless the user asked to skip review generation.
   - Confirm every per-chapter review file is non-empty and contains analysis generated from that chapter, not only a placeholder.
   - Confirm the RAG dataset file exists, is non-empty, and contains chapter-level sections plus QA tables generated from the extracted chapter Markdown.
   - Count Markdown image links across chapter extraction files.
   - List saved image files or summarize image counts by chapter.
   - Check that image links resolve from each chapter Markdown location.
   - Confirm derived Markdown files clearly state their scope and constraints.
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
python scripts/split_and_convert_by_chapters.py input.pdf output-folder --review-dir chapter-review-folder
python scripts/split_and_convert_by_chapters.py input.pdf output-folder --rag-markdown rag-dataset.md
```

Use `--toc-level` when the PDF outline has nested levels and a non-default level is the correct chapter boundary. The default uses the shallowest outline level. If no outline exists, the script uses visible chapter headings as a fallback.

The split script creates the review directory, prints a `review target` path for each chapter, and prints an `RAG dataset target` path. These paths are not the final model-generated outputs by themselves. After extraction, generate each chapter review with `references/读书 prompt (详细版).md` plus the chapter Markdown text, then write the complete generated review Markdown to that target path. Also generate the combined RAG dataset with `references/生成RAG知识库训练数据集.md` plus the extracted chapter Markdown files, then write the complete generated dataset Markdown to the RAG target path.

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
- Keep the prompt templates bundled inside the skill. Do not rely on unrelated workspace files when invoking the skill in another environment.
- If writing to the user's requested directory needs approval, request approval. If approval is unavailable, generate the files in the workspace and clearly report the intended final destination.
