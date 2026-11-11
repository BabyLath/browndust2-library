"""Turn lib/ + content/ into generated-docs/ that Zensical can build.

Steps:
  1. Copy lib/ (styles, scripts, images, Markdown) into generated-docs/.
  2. Expand ```board fences into HTML board diagrams.
  3. Give unit guides (lib/units/<id>.md) their title and header card from the catalog.
  4. Write catalog-driven pages: units, gear, tiles, buffs/debuffs, seasons, builds index.
  5. Write the Zensical config with a generated nav.
"""
from __future__ import annotations

import datetime as dt
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import tomli_w
import yaml

from . import render
from .render import e
from .catalog import Catalog, Problem, suggest
from .paths import BASE_CONFIG, BUILD_CONFIG, GENERATED, LIB, SITE

IMAGE_EXTS = (".png", ".webp", ".avif", ".jpg", ".jpeg", ".svg")

SYMBOL_RE = re.compile(r"\[\[([^\[\]\n]+)\]\]")
CODE_RE = re.compile(r"(^```.*?^```[ \t]*$|`[^`\n]+`)", re.M | re.S)

FENCE_RE = re.compile(r"^```board[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)


def split_front_matter(text: str) -> tuple[dict, str, int]:
    """Return (front matter, body, number of lines the front matter used)."""
    m = FM_RE.match(text)
    if not m:
        return {}, text, 0
    return (yaml.safe_load(m.group(1)) or {}), text[m.end():], m.group(0).count("\n")


HEADING_RE = re.compile(r"^#{2,3}\s+\S", re.M)
FENCED_RE = re.compile(r"^```.*?^```", re.M | re.S)


def auto_hide_toc(fm: dict, body: str) -> dict:
    """Hide the right-hand "On this page" column on pages with fewer than two section
    headings, so the content gets the full width. A page that sets `hide:` itself is left alone."""
    if "hide" in fm:
        return fm
    if len(HEADING_RE.findall(FENCED_RE.sub("", body))) < 2:
        fm = {**fm, "hide": ["toc"]}
    return fm


def dump_front_matter(fm: dict) -> str:
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n"


def git_dates(root: Path) -> dict[str, dt.date]:
    """Path (relative to the repo) -> date of the last commit that touched it.
    Files with uncommitted changes count as edited today, so a local preview matches what you'll publish.
    Empty when git or the history isn't available; pages then just don't show a date."""
    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout
    try:
        top = Path(git("rev-parse", "--show-toplevel").strip())
        log = git("log", "--format=@%cs", "--name-only", "--", ".")
        status = git("status", "--porcelain", "--", ".")
    except (OSError, subprocess.CalledProcessError):
        return {}
    dates: dict[str, dt.date] = {}
    current = None
    for line in log.splitlines():
        if line.startswith("@"):
            current = dt.date.fromisoformat(line[1:])
        elif line and current:
            key = (top / line).resolve().relative_to(root.resolve()).as_posix() if (top / line).resolve().is_relative_to(root.resolve()) else None
            if key and key not in dates:  # log is newest first
                dates[key] = current
    today = dt.date.today()
    for line in status.splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        full = (top / path).resolve()
        if full.is_relative_to(root.resolve()):
            dates[full.relative_to(root.resolve()).as_posix()] = today
    return dates


def _line(path: Path, needle: str) -> int | None:
    try:
        for i, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if needle in ln:
                return i
    except OSError:
        pass
    return None


class Generator:
    def __init__(self, cat: Catalog, dest: Path = GENERATED):
        self.cat = cat
        self.edited = git_dates(LIB.parent)
        self.dest = dest
        self.problems: list[Problem] = []
        self.guides = {p.stem for p in (LIB / "units").glob("*.md") if p.stem != "index"}
        self.tile_images = self.find_images("tiles", cat.tiles)
        tpath = Path(__file__).resolve().parent.parent / "content" / "tiles.yaml"
        upath = tpath.with_name("units.yaml")
        for uid, u in cat.units.items():
            if u.get("shape") and not render.parse_shape(u["shape"]):
                self.err(upath, None, f"'{uid}': shape \"{u['shape']}\" isn't valid. Use # for a square, . for a gap and / between rows, like \".#./###/###/.#.\".")
        for tid, t in cat.tiles.items():
            if t.get("shape") and not render.parse_shape(t["shape"]):
                self.err(tpath, None, f"'{tid}': shape \"{t['shape']}\" isn't valid. Use # for a square, . for a gap and / between rows, like \"##./.##\".")
        self.gear_images = self.find_images("gear", cat.gear)
        self.portraits = self.find_portraits()
        self.status_images = self.find_images("statuses", cat.statuses)
        self.tags = {render.slug(t): {"name": t} for t in cat.meta.get("tags", [])}
        self.tag_images = self.find_images("tags", self.tags)
        # [[Name]] or [[id]] -> (kind, id), matched without regard to case
        self.symbols: dict[str, tuple[str, str]] = {}
        for kind, pool in (("status", cat.statuses), ("tag", self.tags)):
            for rid, row in pool.items():
                for k in (rid, row["name"]):
                    if k.lower() in self.symbols and self.symbols[k.lower()] != (kind, rid):
                        self.err(LIB.parent / "content" / "meta.yaml", None, f"'{row['name']}' is both a tag and a status; [[{row['name']}]] can't tell them apart.")
                    self.symbols[k.lower()] = (kind, rid)
        self.pages: dict[str, dict] = {}  # rel path -> front matter (for nav)

    # ---------- images ----------
    def find_images(self, folder: str, pool: dict[str, dict]) -> dict[str, str]:
        """Map ids to images in lib/images/<folder>/<id>.<ext>. An `image:` field in the catalog
        overrides the file name. Reports missing images and files that match no id."""
        base = LIB / "images" / folder
        files = {p.stem: p for p in base.glob("*") if p.suffix.lower() in IMAGE_EXTS} if base.exists() else {}
        found: dict[str, str] = {}
        for rid, row in pool.items():
            if row.get("image"):
                path = base / str(row["image"])
                if path.exists():
                    found[rid] = f"images/{folder}/{path.name}"
                else:
                    self.err(base, None, f"'{rid}' sets image: {row['image']} but lib/images/{folder}/{row['image']} doesn't exist.")
            elif rid in files:
                found[rid] = f"images/{folder}/{files[rid].name}"
        used = {Path(v).stem for v in found.values()}
        for stem, path in sorted(files.items()):
            if stem not in used:
                self.err(path, None, f"image doesn't match any {folder} id.{suggest(stem, pool)} Rename it to the id.", "warning")
        missing = sorted(set(pool) - set(found))
        if missing:
            self.err(base, None, f"{len(missing)} of {len(pool)} have no image yet: {', '.join(missing)}.", "warning")
        return found

    def find_portraits(self) -> dict[str, str]:
        """Unit guide portraits: lib/images/portraits/<unit-id>.avif. Only units with a guide
        need one, so only those are reported as missing."""
        base = LIB / "images" / "portraits"
        found: dict[str, str] = {}
        if base.exists():
            rank = {".avif": 0, ".webp": 1, ".png": 2, ".jpg": 3, ".jpeg": 3}
            for p in sorted(base.iterdir(), key=lambda p: rank.get(p.suffix.lower(), 9)):
                if p.suffix.lower() not in rank or p.name.startswith("."):
                    continue
                if p.stem not in self.cat.units:
                    self.err(p, None, f"portrait doesn't match any unit id.{suggest(p.stem, self.cat.units)} Rename it to the unit id.", "warning")
                elif p.stem not in found:
                    found[p.stem] = f"images/portraits/{p.name}"
        missing = sorted(self.guides - set(found))
        if missing:
            self.err(base, None, f"{len(missing)} unit guide(s) have no portrait yet: {', '.join(missing)}. "
                     f"Add lib/images/portraits/<unit-id>.avif; until then the guide shows the footprint.", "warning")
        return found

    # ---------- [[Name]] icon shortcodes ----------
    def symbol_html(self, kind: str, rid: str, prefix: str, with_name: bool = False) -> str:
        """[[Name]]: icon only, name on hover. [[Name+]]: icon followed by the name.
        Without an icon yet, both show the name."""
        pool, images = (self.cat.statuses, self.status_images) if kind == "status" else (self.tags, self.tag_images)
        name = e(pool[rid]["name"])
        if rid not in images:
            if with_name:  # the name is already showing, so no hover hint
                return f'<span class="swg-sym--plain">{name}</span>'
            return f'<abbr class="swg-sym swg-sym--text" title="{name}">{name}</abbr>'
        img = f'<img class="swg-sym__img" src="{prefix}{images[rid]}" alt="{"" if with_name else name}">'
        if with_name:
            return f'<span class="swg-sym swg-sym--named">{img}<span>{name}</span></span>'
        return f'<abbr class="swg-sym" title="{name}">{img}</abbr>'

    def symbolize(self, text: str, rel: str, where: Path) -> str:
        """Replace [[Name]] outside code with the status icon (or its name until an icon exists)."""
        prefix = "../" * rel.count("/")  # relative to the source file's folder, see render.py

        def swap(m: re.Match) -> str:
            raw = m.group(1).strip()
            with_name = raw.endswith("+")
            key = raw.rstrip("+").strip().lower()
            hit = self.symbols.get(key) or self.symbols.get(render.slug(key))
            if not hit:
                names = [st["name"] for st in self.cat.statuses.values()] + [t["name"] for t in self.tags.values()]
                self.err(where, None, f"[[{m.group(1)}]] isn't a known buff, debuff or tag.{suggest(raw.rstrip('+'), names)} "
                         "Add statuses to content/statuses.yaml and tags to content/meta.yaml.")
                return m.group(0)
            return self.symbol_html(*hit, prefix, with_name)

        parts = CODE_RE.split(text)
        return "".join(p if i % 2 else SYMBOL_RE.sub(swap, p) for i, p in enumerate(parts))

    def plain(self, text: str) -> str:
        """[[Name]] -> Name, for front matter fields like description."""
        return SYMBOL_RE.sub(lambda m: m.group(1).strip().rstrip("+").strip(), str(text))

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
            return render.board(self.cat, spec, self.guides, prefix, self.portraits)
        return FENCE_RE.sub(repl, body)

    def validate_board(self, path: Path, line: int, spec: dict):
        cat = self.cat
        rows = [r.replace(" ", "") for r in str(spec.get("layout") or "").strip("\n").splitlines()]
        if rows and len(rows) != render.GRID or any(len(r) != render.GRID for r in rows):
            self.err(path, line, f"board layout must be {render.GRID} rows of {render.GRID} characters (use . for empty squares).")
        floor = [r.replace(" ", "") for r in str(spec.get("floor") or "").strip("\n").splitlines()]
        if floor and (len(floor) != render.GRID or any(len(r) != render.GRID for r in floor)):
            self.err(path, line, f"board floor must be {render.GRID} rows of {render.GRID} characters (use . for empty squares).")
            floor = []
        pieces = {str(k): v for k, v in (spec.get("pieces") or {}).items()}
        used = {ch for r in rows + floor for ch in r if ch != "."}
        if floor and rows and len(rows) == render.GRID:
            for r in range(render.GRID):
                for c in range(render.GRID):
                    u, f = rows[r][c], floor[r][c]
                    if u != "." and pieces.get(u) in cat.tiles:
                        self.err(path, line, f"'{u}' is a tile; with a floor, tiles go in floor and units in layout.")
                        return
                    if f != "." and pieces.get(f) in cat.units:
                        self.err(path, line, f"'{f}' is a unit; with a floor, units go in layout, not floor.")
                        return
                    if u != "." and f == ".":
                        self.err(path, line, f"unit '{u}' stands on an empty square (row {r + 1}, column {c + 1}); every unit square needs a tile under it.", "warning")
                        break
        for ch in sorted(used - pieces.keys()):
            self.err(path, line, f"layout uses '{ch}' but pieces doesn't say what it is.")
        for ch in sorted(pieces.keys() - used if rows else []):
            self.err(path, line, f"piece '{ch}' isn't placed in the layout or floor.", "warning")
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
        known = ["name", "context", "season", "summary", "floor", "layout", "pieces", "gear", "roles", "details", "notes", "total"]
        for k in spec:
            if k not in known:
                self.err(path, line, f"board block has an unknown key '{k}'.{suggest(str(k), known)}", "warning")
        for key in ("roles", "details"):
            for ch in (spec.get(key) or {}):
                if str(ch) not in pieces:
                    self.err(path, line, f"{key} mentions '{ch}', which isn't one of the pieces.")

    # ---------- pages ----------
    def process_markdown(self, src: Path, rel: Path):
        text = src.read_text(encoding="utf-8")
        fm, body, fm_lines = split_front_matter(text)
        prefix = "../" * (len(rel.parts) - 1)  # site root, relative to the source file's folder

        if rel.parts[0] == "units" and rel.name != "index.md":
            body = self.unit_guide(src, fm, body)
            fm = {"title": self.cat.unit_label(fm["unit"]) if fm.get("unit") in self.cat.units else rel.stem,
                  "description": fm.get("tagline") or fm.get("summary") or "", **{k: v for k, v in fm.items() if k in ("order",)}}
        else:
            for k in ("title", "description"):
                if not fm.get(k):
                    self.err(src, 1, f"front matter needs '{k}'.")

        body = self.expand_boards(src, body, fm_lines, prefix)
        body = body.replace("<!-- swg:season -->", render.season_card(self.cat, prefix, rel.as_posix() != "guide/current-season.md"))
        body = self.season_notice(src, fm, body)
        extra_sources = []
        if "<!-- swg:planner -->" in body:
            body = body.replace("<!-- swg:planner -->", render.planner(self.cat, self.guides, self.plain))
            extra_sources += [LIB.parent / "content" / n for n in ("units.yaml", "tiles.yaml", "gear.yaml")]
        if "<!-- swg:rewards -->" in body:
            body = body.replace("<!-- swg:rewards -->", self.rewards_block())
            extra_sources.append(LIB.parent / "content" / "rewards.yaml")
        self.pages[rel.as_posix()] = fm
        out = self.dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        fm = auto_hide_toc(fm, body)
        if fm.get("description"):
            fm["description"] = self.plain(fm["description"])
        if rel.as_posix() not in ("index.md", "changelog.md"):
            body = body.rstrip() + self.updated_line(src, *extra_sources)
        body = self.symbolize(body, rel.as_posix(), src)
        self.pages[rel.as_posix()] = fm
        out.write_text(dump_front_matter(fm) + body, encoding="utf-8")

    def rewards_block(self) -> str:
        """Tables for content/rewards.yaml: chips per Board clear, the shop, and whether clears cover the shop."""
        path = LIB.parent / "content" / "rewards.yaml"
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as ex:
            self.err(path, None, f"can't be read ({ex}).")
            return ""

        def num(row: dict, key: str, label: str, missing: list) -> int | None:
            v = row.get(key)
            if v is None or str(v).strip() in ("", "?"):
                missing.append(f"{label} {key}")
                return None
            if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                self.err(path, _line(path, label), f"'{label}': {key} should be a whole number, not '{v}'.")
                return None
            return v

        def cell(v) -> str:
            return f"{v:,}" if isinstance(v, int) else '<span class="swg-unknown" title="Not recorded yet">?</span>'

        missing: list[str] = []
        clears = data.get("clears") or []
        shop = data.get("shop") or []
        out = []

        earned = [num(c, "chips", str(c.get("board", "?")), missing) for c in clears]
        if clears:
            rows = "".join(f"<tr><td>{e(str(c.get('board', '')))}</td><td class=\"num\">{cell(v)}</td></tr>" for c, v in zip(clears, earned))
            known = None if None in earned else sum(earned)
            out.append('## Alea Chips per Board\n\n<div class="swg-table" markdown="0"><table>'
                       '<thead><tr><th>Board</th><th class="num">Alea Chips</th></tr></thead>'
                       f'<tbody>{rows}</tbody><tfoot><tr><th>Every Board</th><th class="num">{cell(known)}</th></tr></tfoot></table></div>')

        costs = []
        if shop:
            rows = []
            for it in shop:
                name = str(it.get("item", "?"))
                price = num(it, "price", name, missing)
                limit = it.get("limit")
                unlimited = str(limit).strip().lower() == "unlimited"
                if unlimited:
                    limit = None
                elif limit is None or str(limit).strip() in ("", "?"):
                    missing.append(f"{name} limit")
                    limit = None
                elif isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
                    self.err(path, _line(path, name), f"'{name}': limit should be a whole number, unlimited, or blank if you don't know yet.")
                    limit = None
                total = price * limit if price is not None and limit is not None else None
                if not unlimited:
                    costs.append(total)
                note = f'<span class="swg-up__key">{e(str(it["note"]))}</span>' if it.get("note") else ""
                rows.append(f"<tr><td>{e(name)}{note}</td><td class=\"num\">{cell(price)}</td>"
                            f"<td class=\"num\">{cell(limit) if not unlimited else 'No limit'}</td><td class=\"num\">{cell(total) if not unlimited else '–'}</td></tr>")
            all_cost = None if (None in costs or not costs) else sum(costs)
            out.append('## The shop\n\n<div class="swg-table" markdown="0"><table>'
                       '<thead><tr><th>Item</th><th class="num">Price</th><th class="num">Limit</th><th class="num">To buy all</th></tr></thead>'
                       f'<tbody>{"".join(rows)}</tbody><tfoot><tr><th colspan="3">Everything with a limit</th><th class="num">{cell(all_cost)}</th></tr></tfoot></table></div>')
            known = None if (not clears or None in earned) else sum(earned)
            if known is not None and all_cost is not None:
                diff = known - all_cost
                verdict = (f"Clearing every Board gives <b>{known:,}</b> Alea Chips and the limited items cost <b>{all_cost:,}</b>, "
                           + (f"so you have <b>{diff:,}</b> left over for unlimited items." if diff >= 0 else f"so you're <b>{-diff:,}</b> short. Skip the lowest-value items."))
                out.append(f'<p class="swg-rewards-sum" markdown="0">{verdict}</p>')

        if missing:
            self.err(path, None, f"{len(missing)} value(s) not recorded yet, like {missing[0]}. The page shows ? for them.", "warning")
            out.append('<p class="swg-updated__note" markdown="0"><span class="swg-unknown">?</span> means not recorded yet. '
                       'Seen the number in game? Add it to <code>content/rewards.yaml</code>.</p>')
        return "\n\n".join(out)

    def updated_line(self, *sources: Path) -> str:
        """'Last updated' line from the newest of the given source files, flagged if it predates the current season."""
        dates = [self.edited.get(p.resolve().relative_to(LIB.parent.resolve()).as_posix()) for p in sources]
        dates = [d for d in dates if d]
        if not dates:
            return ""
        d = max(dates)
        season = next((x for x in reversed(self.cat.seasons) if x["start"] <= d), None)
        now = self.cat.current_season
        old = f' <span class="swg-updated__old">Before {e(now["name"])} started.</span>' if d < now["start"] else ""
        when = f' <span class="swg-updated__season">({e(season["name"])})</span>' if season and not old else ""
        return f'\n\n<p class="swg-updated" markdown="0">Last updated <time datetime="{d.isoformat()}">{render.fmt_date(d)}</time>{when}.{old}</p>\n'

    def season_notice(self, src: Path, fm: dict, body: str) -> str:
        """Pages with `season:` in front matter are about one season. Warn (and tell readers) once it's over."""
        sid = fm.get("season")
        if not sid:
            return body
        written = self.cat.season(str(sid))
        if not written:
            self.err(src, 1, f"unknown season '{sid}'.{suggest(str(sid), [x['id'] for x in self.cat.seasons])}")
            return body
        now = self.cat.current_season
        if written["id"] == now["id"]:
            return body
        self.err(src, 1, f"written for {written['name']}, but the current season is {now['name']}. "
                 f"Update the page, then set season: {now['id']}.", "warning")
        note = (f'!!! warning "Out of date"\n    This page was written for {written["name"]}. '
                f'{now["name"]} has started, so some of it may no longer apply.\n\n')
        # put the notice right after the page's # heading
        m = re.search(r"^# .*\n", body, re.M)
        return body[:m.end()] + "\n" + note + body[m.end():] if m else note + body

    def unit_guide(self, src: Path, fm: dict, body: str) -> str:
        cat = self.cat
        uid = fm.get("unit")
        if uid != src.stem:
            self.err(src, 2, f"unit: '{uid}' should match the file name '{src.stem}'.")
        if not self.check_id(src, 2, "unit", uid, cat.units):
            return body
        roles_ok = cat.meta.get("roles", [])
        for r in (fm.get("roles") or ([fm["role"]] if fm.get("role") else [])):
            if r not in roles_ok:
                self.err(src, None, f"unknown role '{r}'.{suggest(r, roles_ok)} Use any of: {', '.join(roles_ok)}.")
        tiers = [str(t) for t in cat.meta.get("ratings", [])]
        for key, r in (fm.get("ranks") or {}).items():
            if key not in ("damage", "support"):
                self.err(src, None, f"ranks: '{key}' should be damage or support.")
            elif not isinstance(r, dict) or str(r.get("tier")) not in tiers:
                self.err(src, None, f"ranks.{key}.tier should be one of {', '.join(tiers)}.")
        for n in fm.get("stopping_points") or []:
            if not (isinstance(n, int) and 0 <= n <= 5):
                self.err(src, None, f"stopping_points should be upgrade levels from 0 to 5, like [0, 3, 5]. Got {n!r}.")
        ids = lambda xs: [render._entry(x)[0] for x in xs or []]
        for b in fm.get("builds") or []:
            for gid in ids(b.get("gear")):
                self.check_id(src, None, "gear", gid, cat.gear)
            for tid in ids(b.get("tiles")):
                self.check_id(src, None, "tile", tid, cat.tiles)
            for wid in ids(b.get("with")):
                self.check_id(src, None, "unit", wid, cat.units)
        for w in ids(fm.get("works_well_with")):
            self.check_id(src, None, "unit", w, cat.units)
        builds_meta = self.builds_meta()
        for bid in ids(fm.get("suggested_builds")):
            if bid not in builds_meta:
                self.err(src, None, f"suggested_builds: no build page lib/builds/{bid}.md.{suggest(bid, list(builds_meta))}")
        template = (LIB.parent / "templates" / "unit.md").read_text(encoding="utf-8")
        tfm, template_body, _ = split_front_matter(template)
        leftovers = [ln.strip() for ln in template_body.splitlines()
                     if len(ln.strip()) > 25 and not ln.startswith(("<!--", "#")) and ln.strip() in body]
        for k in ("tagline", "ranks", "stopping_points", "stopping_note", "builds", "works_well_with", "works_well_with_note"):
            if fm.get(k) and fm.get(k) == tfm.get(k) and uid != tfm.get("unit"):
                leftovers.insert(0, f"{k} (the template's example)")
            elif k in ("tagline", "stopping_note", "works_well_with_note", "ranks", "builds") and fm.get(k) and fm.get(k) == tfm.get(k):
                leftovers.insert(0, f"{k} (the template's example)")
        if leftovers:
            more = f" and {len(leftovers) - 1} more" if len(leftovers) > 1 else ""
            self.err(src, None, f"still has template text: \"{leftovers[0][:60]}\"{more}. Replace it or delete that part before publishing.", "warning")
        # Split the body: text before the first ## is the overview,
        # each ## starts a full-width section, and board blocks are gathered into "Example boards".
        boards: list[str] = []
        def pull(m):
            boards.append(m.group(0))
            return ""
        body = FENCE_RE.sub(pull, body)
        parts, current, in_code = [], [], False
        for line in body.splitlines():
            if line.lstrip().startswith(("```", "~~~")):
                in_code = not in_code
            if line.startswith("## ") and not in_code:
                parts.append("\n".join(current))
                current = []
            current.append(line)
        parts.append("\n".join(current))
        intro, sections = parts[0], [p for p in parts[1:] if p.strip()]
        prefix = "../"
        return render.unit_guide(cat, uid, fm, intro, sections, boards, self.guides, self.gear_images, builds_meta, prefix, self.portraits)

    def builds_meta(self) -> dict[str, str]:
        """Build page slug -> title, for unit guides' suggested_builds."""
        if not hasattr(self, "_builds_meta"):
            self._builds_meta = {}
            for p in sorted((LIB / "builds").glob("*.md")):
                if p.name != "index.md":
                    fm, _, _ = split_front_matter(p.read_text(encoding="utf-8"))
                    self._builds_meta[p.stem] = str(fm.get("title") or p.stem)
        return self._builds_meta

    def write(self, rel: str, text: str):
        path = self.dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        fm, body, _ = split_front_matter(text)
        fm = auto_hide_toc(fm, body)
        if fm.get("description"):
            fm["description"] = self.plain(fm["description"])
        source = {"reference/tiles.md": "tiles.yaml", "reference/gear.md": "gear.yaml", "reference/statuses.md": "statuses.yaml",
                  "units/index.md": "units.yaml", "seasons.md": "seasons.yaml"}.get(rel)
        where = (LIB.parent / "content" / source) if source else (LIB / rel)
        if source:
            body = body.rstrip() + self.updated_line(where)
        elif rel == "builds/index.md":
            body = body.rstrip() + self.updated_line(*sorted((LIB / "builds").glob("*.md")))
        body = self.symbolize(body, rel, where)
        path.write_text(dump_front_matter(fm) + body, encoding="utf-8")
        self.pages[rel] = fm

    def builds_index(self):
        builds = sorted(p for p in (LIB / "builds").glob("*.md") if p.name != "index.md")
        items = []
        for p in builds:
            fm, _, _ = split_front_matter(p.read_text(encoding="utf-8"))
            # tested: true -> "Tested"; false or missing -> "Theorycraft".
            # (Not "status": the theme uses that name for its own page markers.)
            tested = fm.get("tested", False)
            if not isinstance(tested, bool):
                self.err(p, None, f"tested should be true or false, not '{tested}'.")
            label = ('<span class="swg-status-label swg-status-label--tested">Tested</span> ' if tested is True
                     else '<span class="swg-status-label">Theorycraft</span> ')
            items.append(f"- {label}[{fm.get('title', p.stem)}]({p.stem}.md): {fm.get('description', '')}")
        intro = ""
        if (LIB / "builds" / "index.md").exists():
            _, intro, _ = split_front_matter((LIB / "builds" / "index.md").read_text(encoding="utf-8"))
        self.write("builds/index.md", "---\ntitle: Builds\ndescription: Board layouts that clear the current season.\nicon: lucide/layout-grid\n---\n\n"
                   + (intro.strip() or "# Builds") + "\n\n" + ("\n".join(items) or "No builds yet. Copy templates/build.md into lib/builds/.") + "\n")

    # ---------- nav ----------
    def nav(self) -> list:
        def title(rel): return self.pages.get(rel, {}).get("title", Path(rel).stem)
        def section(folder: str, fold: str | None = None) -> list:
            """Index page first, then the folder's pages. With `fold`, the pages go into a
            collapsible group of that name (closed unless you're on one of its pages), so long
            lists like unit guides don't fill the sidebar."""
            files = [r for r in self.pages if r.startswith(folder + "/") and r.count("/") == 1 and not r.endswith("index.md")]
            files.sort(key=lambda r: (self.pages[r].get("order", 999), title(r)))
            head = [f"{folder}/index.md"] if f"{folder}/index.md" in self.pages else []
            items = [{title(r): r} for r in files]
            if fold and items:
                items = [{f"{fold} ({len(items)})": items}]
            return head + items
        # Units and Builds sit inside the Guide section so the theme draws them as collapsible
        # items (icon, label linking to the list page, separate arrow button).
        # Section headings themselves can't collapse.
        return [
            {"Home": "index.md"},
            {"Guide": section("guide") + [{"Units": section("units")}, {"Builds": section("builds")}]},
            {"Reference": ["reference/gear.md", "reference/tiles.md", "reference/statuses.md", "seasons.md"]},
            {"Tools": section("tools")},
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
        self.write("units/index.md", render.units_page(cat, self.guides, self.portraits))
        self.write("reference/gear.md", render.gear_page(cat, self.gear_images))
        self.write("reference/tiles.md", render.tiles_page(cat, self.tile_images))
        self.write("reference/statuses.md", render.statuses_page(cat, self.status_images))
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
