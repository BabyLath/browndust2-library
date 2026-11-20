"""swg-linkcheck: every link, image, stylesheet, script and link-preview image in the built site must exist.

Reads site/ the way GitHub Pages serves it: under the folder in site_url (/browndust2-library/),
so a link that only works at the site root fails here too. Links to a #section are checked
against the ids on the target page. The planner's #plan=… and #add=… links, outside sites and
mailto: are skipped. No browser or network needed; run it after swg-build.
"""
from __future__ import annotations

import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from .paths import ROOT

SITE = ROOT / "site"
ATTRS = {"a": "href", "link": "href", "img": "src", "script": "src", "source": "src"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        url = a.get(ATTRS.get(tag, ""))
        if url and not (tag == "link" and a.get("rel") in ("canonical", "alternate", "preconnect", "dns-prefetch")):
            self.refs.append((tag, url))
        if tag == "meta" and a.get("property", a.get("name")) in ("og:image", "twitter:image") and a.get("content"):
            self.refs.append(("meta", a["content"]))  # link-preview image, an address on the live site
        if tag == "img" and a.get("srcset"):
            for part in a["srcset"].split(","):
                if part.strip():
                    self.refs.append((tag, part.strip().split()[0]))


def site_url() -> str:
    with (ROOT / "zensical.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]["site_url"]


def check(site: Path = SITE) -> list[str]:
    root_url = site_url()
    base = urlsplit(root_url)
    prefix = base.path if base.path.endswith("/") else base.path + "/"
    origin = f"{base.scheme}://{base.netloc}"
    parsed: dict[Path, Page] = {}

    def parse(path: Path) -> Page:
        if path not in parsed:
            p = Page()
            p.feed(path.read_text(encoding="utf-8", errors="replace"))
            parsed[path] = p
        return parsed[path]

    def target(url_path: str) -> Path | None:
        if not url_path.startswith(prefix):
            return None
        rel = unquote(url_path[len(prefix):])
        f = site / rel
        if url_path.endswith("/") or f.is_dir():
            f = f / "index.html"
        return f

    problems: list[str] = []
    pages = sorted(site.rglob("*.html"))
    for page in pages:
        rel = page.relative_to(site).as_posix()
        page_url = origin + prefix + rel
        for tag, ref in parse(page).refs:
            if ref.startswith(("mailto:", "tel:", "javascript:", "data:", "blob:")):
                continue
            absolute = urljoin(page_url, ref)
            parts = urlsplit(absolute)
            if f"{parts.scheme}://{parts.netloc}" != origin:
                continue  # another site
            if not parts.path.startswith(prefix):
                problems.append(f"{rel}: {ref} points outside the site's folder ({prefix}); it breaks on GitHub Pages.")
                continue
            f = target(parts.path)
            if f is None or not f.exists():
                problems.append(f"{rel}: <{tag}> {ref} -> no such file.")
                continue
            frag = unquote(parts.fragment)
            if frag and "=" not in frag and not frag.startswith("__") and f.suffix == ".html":
                if frag not in parse(f).ids:
                    problems.append(f"{rel}: {ref} -> no #{frag} on that page.")
    return problems


def main():
    if not SITE.exists():
        sys.exit("No site/ folder yet. Run uv run swg-build first.")
    problems = check()
    n = len(list(SITE.rglob("*.html")))
    for p in problems:
        print("BROKEN  " + p)
    if problems:
        sys.exit(f"\n{len(problems)} broken link(s) on {n} pages.")
    print(f"All links, images and files on {n} pages are there.")
