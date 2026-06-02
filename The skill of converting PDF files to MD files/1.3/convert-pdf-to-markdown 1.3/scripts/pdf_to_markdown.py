import argparse
import re
from pathlib import Path

import fitz


CAPTION_RE = re.compile(
    r"((?:图|表)\s*\d+\s*[-‐-―－]\s*\d+[^\n\r]*|"
    r"(?:Figure|Table)\s+\d+\s*[-‐-―－]\s*\d+[^\n\r]*)",
    re.IGNORECASE,
)


def block_text(block):
    lines = []
    for line in block.get("lines", []):
        line_text = "".join(span.get("text", "") for span in line.get("spans", []))
        if line_text.strip():
            lines.append(line_text.strip())
    return "".join(lines).strip()


def normalize_caption(text):
    match = CAPTION_RE.search(text)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1).strip())


def safe_stem(text, fallback):
    text = normalize_caption(text) or fallback
    text = text.replace("“", "").replace("”", "").replace('"', "")
    text = re.sub(r"[\\/:*?<>|]", "_", text)
    text = re.sub(r"\s+", "_", text).strip("._ ")
    return text[:100] or fallback


def find_caption(blocks, image_index):
    image = blocks[image_index]
    ix0, iy0, ix1, iy1 = image["bbox"]
    image_center = (ix0 + ix1) / 2
    candidates = []

    for idx, block in enumerate(blocks):
        if block.get("type") != 0:
            continue
        caption = normalize_caption(block_text(block))
        if not caption:
            continue
        x0, y0, x1, y1 = block["bbox"]
        center_gap = abs(((x0 + x1) / 2) - image_center)
        if idx > image_index and 0 <= y0 - iy1 <= 100:
            candidates.append((0, y0 - iy1, center_gap, caption))
        elif idx < image_index and 0 <= iy0 - y1 <= 100:
            candidates.append((1, iy0 - y1, center_gap, caption))

    if not candidates:
        return ""
    return sorted(candidates)[0][3]


def markdown_for_text(text):
    if not text:
        return ""
    if CAPTION_RE.fullmatch(text.strip()):
        return text
    if re.fullmatch(r"第\d+章", text):
        return f"# {text}"
    if len(text) <= 28 and not re.search(r"[。！？：；,.!?]", text):
        return f"## {text}"
    return text


def link_path(image_path, markdown_path, absolute_links):
    if absolute_links:
        return image_path.as_posix()
    try:
        return image_path.relative_to(markdown_path.parent).as_posix()
    except ValueError:
        try:
            return Path(
                Path.cwd().joinpath(image_path).resolve()
            ).relative_to(markdown_path.parent.resolve()).as_posix()
        except ValueError:
            return image_path.resolve().as_posix()


def unique_path(path, overwrite):
    if overwrite or not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def convert(pdf_path, markdown_path, image_dir, absolute_links=False, overwrite_images=False):
    pdf_path = Path(pdf_path)
    markdown_path = Path(markdown_path)
    image_dir = Path(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    chunks = []
    saved_images = []
    image_counter = 0

    for page_number, page in enumerate(doc, start=1):
        blocks = sorted(
            page.get_text("dict")["blocks"],
            key=lambda block: (round(block["bbox"][1], 1), block["bbox"][0]),
        )
        for index, block in enumerate(blocks):
            if block.get("type") == 0:
                rendered = markdown_for_text(block_text(block))
                if rendered:
                    chunks.append(rendered)
            elif block.get("type") == 1:
                image_counter += 1
                caption = find_caption(blocks, index)
                ext = (block.get("ext") or "png").lower()
                ext = "jpg" if ext == "jpeg" else ext
                stem = safe_stem(caption, f"page-{page_number}-image-{image_counter}")
                image_path = unique_path(image_dir / f"{stem}.{ext}", overwrite_images)
                image_path.write_bytes(block["image"])
                saved_images.append(image_path)
                alt = caption or image_path.stem
                chunks.append(f"![{alt}]({link_path(image_path, markdown_path, absolute_links)})")

    markdown_path.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
    return saved_images


def main():
    parser = argparse.ArgumentParser(
        description="Convert a PDF to Markdown and extract embedded images."
    )
    parser.add_argument("pdf")
    parser.add_argument("markdown")
    parser.add_argument("image_dir")
    parser.add_argument("--absolute-links", action="store_true")
    parser.add_argument("--overwrite-images", action="store_true")
    args = parser.parse_args()

    saved_images = convert(
        args.pdf,
        args.markdown,
        args.image_dir,
        absolute_links=args.absolute_links,
        overwrite_images=args.overwrite_images,
    )
    print(f"wrote {args.markdown}")
    print(f"saved {len(saved_images)} images to {args.image_dir}")
    for image in saved_images:
        print(image)


if __name__ == "__main__":
    main()
