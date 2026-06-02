import argparse
import re
import sys
from pathlib import Path

import fitz

from pdf_to_markdown import convert


CHAPTER_HEADING_RE = re.compile(
    r"^\s*(?:"
    r"(?:第\s*[一二三四五六七八九十百零〇\d]+\s*[章节篇部卷][^\n]{0,80})|"
    r"(?:Chapter\s+\d+[^\n]{0,80})|"
    r"(?:CHAPTER\s+\d+[^\n]{0,80})|"
    r"(?:\d+\s*[.．、]\s+[^\n]{2,80})"
    r")\s*$",
    re.IGNORECASE,
)


def safe_name(text, fallback, max_length=90):
    text = (text or "").strip() or fallback
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", " ", text).strip(" ._")
    return (text[:max_length].rstrip(" ._") or fallback)


def chapter_entries_from_toc(doc, level=None):
    toc = doc.get_toc(simple=True)
    if not toc:
        return []
    if level is None:
        level = min(item[0] for item in toc)

    entries = []
    for item_level, title, page_number in toc:
        if item_level == level and 1 <= page_number <= doc.page_count:
            entries.append((title.strip(), page_number - 1))

    return dedupe_entries(entries)


def chapter_entries_from_page_text(doc):
    entries = []
    for page_index in range(doc.page_count):
        text = doc[page_index].get_text("text")
        for raw_line in text.splitlines()[:25]:
            line = re.sub(r"\s+", " ", raw_line).strip()
            if CHAPTER_HEADING_RE.match(line):
                entries.append((line, page_index))
                break
    return dedupe_entries(entries)


def dedupe_entries(entries):
    deduped = []
    seen_pages = set()
    for title, page_index in entries:
        if page_index in seen_pages:
            continue
        seen_pages.add(page_index)
        deduped.append((title, page_index))
    return sorted(deduped, key=lambda item: item[1])


def make_ranges(doc, entries, include_leading_pages=True):
    ranges = []
    if include_leading_pages and entries and entries[0][1] > 0:
        ranges.append(("front-matter", 0, entries[0][1] - 1))

    for index, (title, start_page) in enumerate(entries):
        next_start = entries[index + 1][1] if index + 1 < len(entries) else doc.page_count
        end_page = next_start - 1
        if start_page <= end_page:
            ranges.append((title, start_page, end_page))

    if not ranges:
        ranges.append((doc.name and Path(doc.name).stem or "document", 0, doc.page_count - 1))
    return ranges


def write_pdf_slice(source_doc, output_pdf, start_page, end_page):
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    sliced = fitz.open()
    sliced.insert_pdf(source_doc, from_page=start_page, to_page=end_page)
    sliced.save(output_pdf)
    sliced.close()


def unique_path(path):
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def split_and_convert(
    pdf_path,
    output_dir,
    review_dir=None,
    rag_markdown=None,
    toc_level=None,
    absolute_links=False,
    overwrite_images=False,
    include_leading_pages=True,
):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    review_dir = Path(review_dir) if review_dir else output_dir.with_name(f"{output_dir.name}-chapter-reviews")
    review_dir.mkdir(parents=True, exist_ok=True)
    rag_markdown = Path(rag_markdown) if rag_markdown else output_dir.with_name(
        f"{output_dir.name}-RAG知识库训练数据集.md"
    )
    rag_markdown.parent.mkdir(parents=True, exist_ok=True)
    rag_markdown = unique_path(rag_markdown)

    doc = fitz.open(pdf_path)
    entries = chapter_entries_from_toc(doc, toc_level)
    source = "toc"
    if not entries:
        entries = chapter_entries_from_page_text(doc)
        source = "page text"

    ranges = make_ranges(doc, entries, include_leading_pages=include_leading_pages)
    results = []
    width = max(2, len(str(len(ranges))))

    for index, (title, start_page, end_page) in enumerate(ranges, start=1):
        folder_name = f"{index:0{width}d}-{safe_name(title, f'part-{index}')}"
        chapter_dir = output_dir / folder_name
        chapter_pdf = unique_path(chapter_dir / f"{folder_name}.pdf")
        chapter_md = unique_path(chapter_dir / f"{folder_name}.md")
        image_dir = chapter_dir / "images"
        review_md = unique_path(review_dir / f"{folder_name}-深度书评.md")

        write_pdf_slice(doc, chapter_pdf, start_page, end_page)
        images = convert(
            chapter_pdf,
            chapter_md,
            image_dir,
            absolute_links=absolute_links,
            overwrite_images=overwrite_images,
        )
        results.append(
            {
                "title": title,
                "start_page": start_page + 1,
                "end_page": end_page + 1,
                "pdf": chapter_pdf,
                "markdown": chapter_md,
                "review_markdown": review_md,
                "image_count": len(images),
            }
        )

    doc.close()
    return source, review_dir, rag_markdown, results


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Split a PDF into chapter folders, then convert each chapter PDF to "
            "Markdown and extract embedded images."
        )
    )
    parser.add_argument("pdf")
    parser.add_argument("output_dir")
    parser.add_argument(
        "--review-dir",
        default=None,
        help=(
            "Directory for per-chapter deep-review Markdown files. Defaults to a "
            "sibling directory named <output-dir>-chapter-reviews."
        ),
    )
    parser.add_argument(
        "--rag-markdown",
        default=None,
        help=(
            "Markdown file for the RAG knowledge-base training dataset. Defaults to a "
            "sibling file named <output-dir>-RAG知识库训练数据集.md."
        ),
    )
    parser.add_argument(
        "--toc-level",
        type=int,
        default=None,
        help="TOC level to split on. Defaults to the shallowest level in the PDF outline.",
    )
    parser.add_argument("--absolute-links", action="store_true")
    parser.add_argument("--overwrite-images", action="store_true")
    parser.add_argument(
        "--no-leading-pages",
        action="store_true",
        help="Do not create a front-matter PDF for pages before the first chapter.",
    )
    args = parser.parse_args()

    source, review_dir, rag_markdown, results = split_and_convert(
        args.pdf,
        args.output_dir,
        review_dir=args.review_dir,
        rag_markdown=args.rag_markdown,
        toc_level=args.toc_level,
        absolute_links=args.absolute_links,
        overwrite_images=args.overwrite_images,
        include_leading_pages=not args.no_leading_pages,
    )

    print(f"chapter source: {source}")
    print(f"wrote {len(results)} chapter folders to {args.output_dir}")
    print(f"created chapter review directory: {review_dir}")
    print(f"RAG dataset target: {rag_markdown}")
    for result in results:
        print(
            f"{result['start_page']}-{result['end_page']}: "
            f"{result['markdown']} ({result['image_count']} images); "
            f"review target: {result['review_markdown']}"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
