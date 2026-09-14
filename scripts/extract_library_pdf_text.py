from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a PDF text layer with page boundaries and provenance.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    args = parser.parse_args()

    source_bytes = args.source.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    reader = PdfReader(args.source)
    pages: list[str] = []
    for number, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").replace("\r", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        pages.append(f"[PDF PAGE {number}]\n{text}")
    header = (
        "MIRA LIBRARY DERIVED TEXT\n"
        f"Source URL: {args.source_url}\n"
        f"Source SHA256: {source_sha}\n"
        f"Transformation: pypdf text-layer extraction with {len(pages)} numbered page boundaries; no OCR correction.\n\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(header + "\n\n".join(pages) + "\n", encoding="utf-8", newline="\n")
    output_bytes = args.output.read_bytes()
    print(json.dumps({"pages": len(pages), "source_sha256": source_sha, "output_sha256": hashlib.sha256(output_bytes).hexdigest(), "output_bytes": len(output_bytes), "output": str(args.output.resolve())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
