"""Turn lib/ + content/ into generated-docs/ that Zensical can build.

Steps:
  1. Copy lib/ (styles, scripts, images, Markdown) into generated-docs/.
  2. Expand ```board fences into HTML board diagrams.
  3. Give unit guides (lib/units/<id>.md) their title and header card from the catalog.
  4. Write catalog-driven pages: units, gear, tiles, buffs/debuffs, seasons, builds index.
  5. Write the Zensical config with a generated nav.
"""
from __future__ import annotations

import re
import shutil
import tomllib
from pathlib import Path

import tomli_w
import yaml

from . import render
from .catalog import Catalog, Problem, suggest
from .paths import BASE_CONFIG, BUILD_CONFIG, GENERATED, LIB, SITE

FENCE_RE = re.compile(r"^```board[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)


def split_front_matter(text: str) -> tuple[dict, str, int]:
    """Return (front matter, body, number of lines the front matter used)."""
    m = FM_RE.match(text)
    if not m:
        return {}, text, 0
    return (yaml.safe_load(m.group(1)) or {}), text[m.end():], m.group(0).count("\n")


def dump_front_matter(fm: dict) -> str:
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n"


class Generator:
    def __init__(self, cat: Catalog, dest: Path = GENERATED):
        self.cat = cat
        self.dest = dest
        self.problems: list[Problem] = []
        self.guides = {p.stem for p in (LIB / "units").glob("*.md") if p.stem != "index"}
        self.pages: dict[str, dict] = {}  # rel path -> front matter (for nav)

    # ---------- validation helpers ----------
    def err(self, path: Path, line: int | None, msg: str, level: str = "error"):
        self.problems.append(Problem(path, line, msg, level))

    def check_id(self, path, line, kind: str, value, pool: dict) -> bool:
        if value in pool:
            return True
        self.err(path, line, f"unknown {kind} id '{value}'.{suggest(str(value), pool)}")
        return False

    # ---------- board fences ----------
    def expand_boards(self, path: Path, body: str, line_offset: int, prefix: str) -> str:
        def repl(m: re.Match) -> str:
            line = body.count("\n", 0, m.start()) + line_offset + 1
            try:
                spec = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError as ex:
                self.err(path, line, f"board fence isn't valid YAML: {ex}")
                return m.group(0)
            self.validate_board(path, line, spec)
            return render.board(self.cat, spec, self.guides, prefix)
        return FENCE_RE.sub(repl, body)

    def validate_board(self, path: Path, line: int, spec: dict):
        cat = self.cat
        rows = [r.replace(" ", "") for r in str(spec.get("layout") or "").strip("\n").splitlines()]
        if rows and len(rows) != render.GRID or any(len(r) != render.GRID for r in rows):
            self.err(path, line, f"board layout must be {render.GRID} rows of {render.GRID} characters (use . for empty squares).")
        pieces = {str(k): v for k, v in (spec.get("pieces") or {}).items()}
        used = {ch for r in rows for ch in r if ch != "."}
        for ch in sorted(used - pieces.keys()):
            self.err(path, line, f"layout uses '{ch}' but pieces doesn't say what it is.")
        for ch in sorted(pieces.keys() - used if rows else []):
            self.err(path, line, f"piece '{ch}' isn't placed in the layout.", "warning")
        for ch, pid in pieces.items():
            if pid in cat.units and pid in cat.tiles:
                self.err(path, line, f"'{pid}' is both a unit and a tile id; rename one.")
            elif pid not in cat.units and pid not in cat.tiles:
                self.err(path, line, f"piece {ch}: '{pid}' isn't a unit or tile.{suggest(str(pid), [*cat.units, *cat.tiles])}")
        for ch, gl in (spec.get("gear") or {}).items():
            if str(ch) not in pieces or pieces[str(ch)] not in cat.units:
                self.err(path, line, f"gear is attached to '{ch}', which isn't a unit in this board.")
            for gid in gl if isinstance(gl, list) else [gl]:
                self.check_id(path, line, "gear", gid, cat.gear)
        if spec.get("season") and not cat.season(str(spec["season"])):
            self.err(path, line, f"unknown season '{spec['season']}'.{suggest(str(spec['season']), [s['id'] for s in cat.seasons])}")

    # ---------- pages ----------
    def process_markdown(self, src: Path, rel: Path):
        text = src.read_text(encoding="utf-8")
        fm, body, fm_lines = split_front_matter(text)
        depth = len(rel.parts) - 1 + (0 if rel.name == "index.md" else 1)
        prefix = "../" * depth  # path back to site root from this page's URL

        if rel.parts[0] == "units" and rel.name != "index.md":
            body = self.unit_guide(src, fm, body)
            fm = {"title": self.cat.unit_label(fm["unit"]) if fm.get("unit") in self.cat.units else rel.stem,
                  "description": fm.get("summary") or "", **{k: v for k, v in fm.items() if k in ("order",)}}
        else:
            for k in ("title", "description"):
                if not fm.get(k):
                    self.err(src, 1, f"front matter needs '{k}'.")

        body = self.expand_boards(src, body, fm_lines, prefix)
        body = body.replace("<!-- swg:season -->", render.season_card(self.cat))
        self.pages[rel.as_posix()] = fm
        out = self.dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(dump_front_matter(fm) + body, encoding="utf-8")

    def unit_guide(self, src: Path, fm: dict, body: str) -> str:
        cat = self.cat
        uid = fm.get("unit")
        if uid != src.stem:
            self.err(src, 2, f"unit: '{uid}' should match the file name '{src.stem}'.")
        if not self.check_id(src, 2, "unit", uid, cat.units):
            return body
        if fm.get("role") and fm["role"] not in cat.meta.get("roles", []):
            self.err(src, None, f"unknown role '{fm['role']}'.{suggest(fm['role'], cat.meta.get('roles', []))}")
        if fm.get("rating") and str(fm["rating"]) not in map(str, cat.meta.get("ratings", [])):
            self.err(src, None, f"unknown rating '{fm['rating']}'. Use one of {cat.meta.get('ratings')}.")
        for w in fm.get("works_well_with") or []:
            self.check_id(src, None, "unit", w, cat.units)
        return f"# {cat.unit_label(uid)}\n\n" + render.unit_card(cat, uid, fm, self.guides) + "\n" + body

    def write(self, rel: str, text: str):
        path = self.dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        fm, _, _ = split_front_matter(text)
        self.pages[rel] = fm

    def builds_index(self):
        builds = sorted(p for p in (LIB / "builds").glob("*.md") if p.name != "index.md")
        items = []
        for p in builds:
            fm, _, _ = split_front_matter(p.read_text(encoding="utf-8"))
            items.append(f"- [{fm.get('title', p.stem)}]({p.stem}.md): {fm.get('description', '')}")
        intro = ""
        if (LIB / "builds" / "index.md").exists():
            _, intro, _ = split_front_matter((LIB / "builds" / "index.md").read_text(encoding="utf-8"))
        self.write("builds/index.md", "---\ntitle: Builds\ndescription: Board layouts that clear the current season.\n---\n\n"
                   + (intro.strip() or "# Builds") + "\n\n" + ("\n".join(items) or "No builds yet. Copy templates/build.md into lib/builds/.") + "\n")

    # ---------- nav ----------
    def nav(self) -> list:
        def title(rel): return self.pages.get(rel, {}).get("title", Path(rel).stem)
        def section(folder: str) -> list:
            files = [r for r in self.pages if r.startswith(folder + "/") and r.count("/") == 1 and not r.endswith("index.md")]
            files.sort(key=lambda r: (self.pages[r].get("order", 999), title(r)))
            head = [f"{folder}/index.md"] if f"{folder}/index.md" in self.pages else []
            return head + [{title(r): r} for r in files]
        return [
            {"Home": "index.md"},
            {"Guide": section("guide")},
            {"Units": section("units")},
            {"Builds": section("builds")},
            {"Reference": ["reference/gear.md", "reference/tiles.md", "reference/statuses.md", "seasons.md"]},
            {"Calculators": "tools/calculators.md"},
            {"Changelog": "changelog.md"},
        ]

    # ---------- run ----------
    def run(self, write_config: bool = True) -> list[Problem]:
        if self.dest.exists():
            shutil.rmtree(self.dest)
        self.dest.mkdir(parents=True)
        for src in sorted(LIB.rglob("*")):
            if src.is_dir():
                continue
            rel = src.relative_to(LIB)
            if src.suffix == ".md":
                if rel.as_posix() == "builds/index.md":
                    continue  # merged into the generated index
                self.process_markdown(src, rel)
            else:
                (self.dest / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, self.dest / rel)

        cat = self.cat
        self.write("units/index.md", render.units_page(cat, self.guides))
        self.write("reference/gear.md", render.simple_table_page(cat, "Gear", "Every gear piece with price and sell value.", "gear.yaml", cat.gear, ["effect"]))
        self.write("reference/tiles.md", render.simple_table_page(cat, "Tiles", "Every tile with shape, price and sell value.", "tiles.yaml", cat.tiles, ["shape", "effect"]))
        self.write("reference/statuses.md", render.statuses_page(cat))
        self.write("seasons.md", render.seasons_page(cat))
        self.builds_index()

        if write_config:
            with BASE_CONFIG.open("rb") as fh:
                cfg = tomllib.load(fh)
            cfg["project"]["docs_dir"] = self.dest.name
            cfg["project"]["site_dir"] = SITE.name
            cfg["project"]["nav"] = self.nav()
            BUILD_CONFIG.write_text("# Generated by swg-build. Edit zensical.toml instead.\n" + tomli_w.dumps(cfg), encoding="utf-8")
        return self.problems
