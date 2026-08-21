#!/usr/bin/env python3
"""Dependency-free structural checks for the static site."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.glob("*.html"))


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self.meta: list[dict[str, str]] = []
        self.link_tags: list[dict[str, str]] = []
        self.main_count = 0
        self.json_ld: list[str] = []
        self._in_json_ld = False
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "main":
            self.main_count += 1
        if tag in {"a", "link"} and values.get("href"):
            self.links.append((tag, values["href"]))
        if tag in {"img", "script", "source"} and values.get("src"):
            self.links.append((tag, values["src"]))
        if tag == "source" and values.get("srcset"):
            for candidate in values["srcset"].split(","):
                self.links.append((tag, candidate.strip().split()[0]))
        if tag == "img":
            self.images.append(values)
        if tag == "button":
            self.buttons.append(values)
        if tag == "meta":
            self.meta.append(values)
        if tag == "link":
            self.link_tags.append(values)
        if tag == "script" and values.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_parts))
            self._in_json_ld = False
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._json_parts.append(data)


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def local_target(page: Path, url: str) -> tuple[Path, str] | None:
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc or url.startswith(("mailto:", "tel:", "data:")):
        return None
    raw_path = unquote(parsed.path)
    target = page if not raw_path else (page.parent / raw_path).resolve()
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def main() -> int:
    errors: list[str] = []
    pages = {path.resolve(): parse_page(path) for path in HTML_FILES}

    for page, parser in pages.items():
        label = page.relative_to(ROOT)
        if parser.main_count != 1:
            errors.append(f"{label}: expected one <main>, found {parser.main_count}")
        duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        if duplicates:
            errors.append(f"{label}: duplicate IDs: {', '.join(duplicates)}")
        descriptions = [meta.get("content") for meta in parser.meta if meta.get("name") == "description"]
        if not descriptions or not descriptions[0]:
            errors.append(f"{label}: missing meta description")
        if not any(link.get("rel") == "canonical" and link.get("href") for link in parser.link_tags):
            errors.append(f"{label}: missing canonical link")
        if "skip-link" not in page.read_text(encoding="utf-8"):
            errors.append(f"{label}: missing skip link")
        for image in parser.images:
            for attribute in ("alt", "width", "height"):
                if not image.get(attribute):
                    errors.append(f"{label}: image missing {attribute}: {image.get('src', '<unknown>')}")
        for button in parser.buttons:
            for attribute in ("aria-label", "aria-expanded", "aria-controls"):
                if not button.get(attribute):
                    errors.append(f"{label}: navigation button missing {attribute}")
        for raw_json in parser.json_ld:
            try:
                json.loads(raw_json)
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON-LD: {exc}")
        for tag, url in parser.links:
            if url.startswith("mailto:"):
                errors.append(f"{label}: direct email link is not allowed")
                continue
            resolved = local_target(page, url)
            if resolved is None:
                continue
            target, fragment = resolved
            if not target.exists():
                errors.append(f"{label}: broken local {tag} reference: {url}")
                continue
            if fragment and target.suffix == ".html":
                target_parser = pages.get(target.resolve()) or parse_page(target)
                if fragment not in target_parser.ids:
                    errors.append(f"{label}: missing fragment target: {url}")

    for xml_name in ("sitemap.xml", "feed.xml"):
        try:
            ET.parse(ROOT / xml_name)
        except (ET.ParseError, FileNotFoundError) as exc:
            errors.append(f"{xml_name}: {exc}")

    try:
        json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        errors.append(f"site.webmanifest: {exc}")

    if (ROOT / "IMG_0226.jpeg").exists():
        errors.append("IMG_0226.jpeg: unoptimized legacy image is still present")

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Site validation passed for {len(HTML_FILES)} HTML pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
