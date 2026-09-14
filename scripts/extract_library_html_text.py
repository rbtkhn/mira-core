from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


BLOCK_TAGS = {
    "address", "blockquote", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6",
    "hr", "li", "p", "section", "table", "td", "th", "tr",
}


class RegionTextParser(HTMLParser):
    def __init__(self, target_id: str) -> None:
        super().__init__(convert_charrefs=True)
        self.target_id = target_id
        self.depth = 0
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if self.depth == 0 and attrs_map.get("id") == self.target_id:
            self.depth = 1
        elif self.depth:
            self.depth += 1
        if self.depth and tag in {"script", "style"}:
            self.skip_depth = self.depth
        if self.depth and not self.skip_depth and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if not self.depth:
            return
        if not self.skip_depth and tag in BLOCK_TAGS:
            self.parts.append("\n")
        if self.skip_depth == self.depth:
            self.skip_depth = 0
        self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.depth and not self.skip_depth:
            self.parts.append(data)


class FragmentTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip += 1
        elif not self.skip and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1
        elif not self.skip and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a named HTML region as provenance-bound UTF-8 text.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-id")
    parser.add_argument("--start-marker")
    parser.add_argument("--end-marker")
    parser.add_argument("--end-last", action="store_true")
    parser.add_argument("--source-url", required=True)
    args = parser.parse_args()

    source_bytes = args.source.read_bytes()
    source_text = source_bytes.decode("utf-8")
    if args.start_marker:
        if not args.end_marker:
            raise SystemExit("--end-marker is required with --start-marker")
        start = source_text.find(args.start_marker)
        end = source_text.rfind(args.end_marker) if args.end_last else source_text.find(args.end_marker, start + len(args.start_marker))
        if start < 0 or end < 0 or end <= start:
            raise SystemExit("HTML fragment markers not found in order")
        extractor = FragmentTextParser()
        extractor.feed(source_text[start:end])
        transformation = f"HTML text extraction between exact markers; navigation markup removed; text order preserved."
    elif args.target_id:
        extractor = RegionTextParser(args.target_id)
        extractor.feed(source_text)
        transformation = f"HTML text extraction from element id={args.target_id}; navigation markup removed; text order preserved."
    else:
        raise SystemExit("provide --target-id or --start-marker/--end-marker")
    if not extractor.parts:
        raise SystemExit(f"target id not found: {args.target_id}")
    body = "".join(extractor.parts).replace("\r", "")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r" *\n *", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    header = (
        "MIRA LIBRARY DERIVED TEXT\n"
        f"Source URL: {args.source_url}\n"
        f"Source SHA256: {source_sha}\n"
        f"Transformation: {transformation}\n\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(header + body + "\n", encoding="utf-8", newline="\n")
    output_bytes = args.output.read_bytes()
    print(json.dumps({"source_sha256": source_sha, "output_sha256": hashlib.sha256(output_bytes).hexdigest(), "output_bytes": len(output_bytes), "output": str(args.output.resolve())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
