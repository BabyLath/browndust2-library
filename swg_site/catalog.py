"""Loading and validating the YAML catalogs in content/.

Everything else (pages, fences, guides) looks things up through `Catalog`,
so a unit's name or price lives in exactly one place.
"""
from __future__ import annotations

import datetime as dt
import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .paths import CONTENT

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class Problem:
    file: Path
    line: int | None
    message: str
    level: str = "error"  # or "warning"

    def __str__(self) -> str:
        where = f"{self.file.relative_to(CONTENT.parent)}" + (f":{self.line}" if self.line else "")
        return f"{self.level.upper():7} {where}  {self.message}"


def suggest(value: str, choices) -> str:
    match = difflib.get_close_matches(value, list(choices), n=1, cutoff=0.6)
    return f" Did you mean '{match[0]}'?" if match else ""


def _line_of(path: Path, needle: str) -> int | None:
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if needle in line:
            return i
    return None


class CatalogSyntaxError(Exception):
    """A YAML file in content/ can't be read. str() is a one-line, human-readable report."""


def _load(name: str) -> tuple[Path, dict]:
    path = CONTENT / name
    try:
        with path.open(encoding="utf-8") as fh:
            return path, (yaml.safe_load(fh) or {})
    except yaml.YAMLError as ex:
        mark = getattr(ex, "problem_mark", None)
        line = f":{mark.line + 1}" if mark else ""
        hint = ("Check the indentation around that line: every line of a multi-line effect must be "
                "indented the same amount, deeper than 'effect: |', using spaces not tabs.")
        raise CatalogSyntaxError(f"ERROR   content/{name}{line}  can't be read ({getattr(ex, 'problem', ex)}). {hint}") from None


@dataclass
class Catalog:
    meta: dict
    units: dict[str, dict]
    gear: dict[str, dict]
    tiles: dict[str, dict]
    statuses: dict[str, dict]
    seasons: list[dict]
    verified: dict[str, str] = field(default_factory=dict)  # catalog -> season id
    problems: list[Problem] = field(default_factory=list)

    @property
    def current_season(self) -> dict:
        return self.seasons[-1]

    def season(self, sid: str) -> dict | None:
        return next((s for s in self.seasons if s["id"] == sid), None)

    def unit_label(self, uid: str) -> str:
        u = self.units[uid]
        return f"{u['character']}, {u['costume']}"

    def piece(self, kind: str, pid: str) -> dict | None:
        return {"unit": self.units, "gear": self.gear, "tile": self.tiles}[kind].get(pid)


def load() -> Catalog:
    problems: list[Problem] = []

    def index(name: str, key: str, required: dict[str, type]) -> tuple[dict[str, dict], str | None]:
        path, data = _load(name)
        rows = data.get(key) or []
        out: dict[str, dict] = {}
        for row in rows:
            rid = str(row.get("id", ""))
            line = _line_of(path, f"id: {rid}") if rid else None
            if not ID_RE.match(rid):
                problems.append(Problem(path, line, f"id '{rid}' must be lowercase words joined by dashes."))
                continue
            if rid in out:
                problems.append(Problem(path, line, f"id '{rid}' is used twice."))
            for fname, ftype in required.items():
                if fname not in row:
                    problems.append(Problem(path, line, f"'{rid}' is missing '{fname}'."))
                elif not isinstance(row[fname], ftype):
                    problems.append(Problem(path, line, f"'{rid}': '{fname}' should be {ftype.__name__}, got {row[fname]!r}."))
            out[rid] = row
        return out, data.get("verified_for")

    _, meta = _load("meta.yaml")
    units, uv = index("units.yaml", "units", {"character": str, "costume": str, "price": int})
    gear, gv = index("gear.yaml", "gear", {"name": str, "price": int})
    tiles, tv = index("tiles.yaml", "tiles", {"name": str, "price": int})
    statuses, _ = index("statuses.yaml", "statuses", {"name": str, "kind": str, "effect": str})

    # vocabularies
    upath = CONTENT / "units.yaml"
    grades, tags = set(meta.get("grades", [])), set(meta.get("tags", []))

    def key(text) -> str:  # "Close-Range Attack", "close-range-attack" and "close range attack" all match
        return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")

    grade_by_key = {key(g): g for g in grades}
    tag_by_key = {key(t): t for t in tags}
    for alias, target in (meta.get("tag_aliases") or {}).items():
        if target in tags:
            tag_by_key[key(alias)] = target
        else:
            problems.append(Problem(CONTENT / "meta.yaml", None, f"tag_aliases: '{alias}' points to '{target}', which isn't in tags."))
    for uid, u in units.items():
        line = _line_of(upath, f"id: {uid}")
        g = u.get("grade") or ""
        if g:
            if key(g) in grade_by_key:
                u["grade"] = grade_by_key[key(g)]          # store the display name
            else:
                problems.append(Problem(upath, line, f"'{uid}': unknown grade '{g}'.{suggest(g, grades)} Add it to meta.yaml if it's new."))
        normalised = []
        for t in u.get("tags") or []:
            if key(t) in tag_by_key:
                normalised.append(tag_by_key[key(t)])
            else:
                problems.append(Problem(upath, line, f"'{uid}': unknown tag '{t}'.{suggest(key(t), tag_by_key)}"))
        u["tags"] = list(dict.fromkeys(normalised))       # display names, duplicates removed
    for uid, u in units.items():
        up = u.get("upgrades")
        if up in (None, []):
            continue
        if not (isinstance(up, list) and len(up) == 5 and all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in up)):
            problems.append(Problem(upath, _line_of(upath, f"id: {uid}"),
                f"'{uid}': upgrades should be five whole numbers for +1 to +5, like [2, 3, 4, 5, 6], or []. Got {up!r}."))
        if "effect" in u:
            problems.append(Problem(upath, _line_of(upath, f"id: {uid}"),
                f"'{uid}': effects now go on the unit's page, lib/units/{uid}.md, under '## Effect'.", level="warning"))
    spath = CONTENT / "statuses.yaml"
    for sid, s in statuses.items():
        if s.get("kind") not in ("buff", "debuff"):
            problems.append(Problem(spath, _line_of(spath, f"id: {sid}"), f"'{sid}': kind must be buff or debuff."))

    # seasons
    sepath, sdata = _load("seasons.yaml")
    seasons = sdata.get("seasons") or []
    if not seasons:
        problems.append(Problem(sepath, None, "Add at least one season."))
    for s in seasons:
        line = _line_of(sepath, f"id: {s.get('id')}")
        for k in ("id", "name", "start"):
            if k not in s:
                problems.append(Problem(sepath, line, f"season is missing '{k}'."))
        for k in ("start", "end", "expected_end"):
            if k in s and not isinstance(s[k], dt.date):
                problems.append(Problem(sepath, line, f"'{s.get('id')}': {k} must be a date like 2026-12-15."))
        s.setdefault("boards", [])
        s.setdefault("changes", [])
        s.setdefault("sources", [])

    cat = Catalog(meta, units, gear, tiles, statuses, seasons,
                  verified={"units.yaml": uv, "gear.yaml": gv, "tiles.yaml": tv}, problems=problems)

    # staleness: the reason this check exists
    if seasons:
        cur = cat.current_season["id"]
        for fname, ver in cat.verified.items():
            if ver != cur:
                problems.append(Problem(CONTENT / fname, _line_of(CONTENT / fname, "verified_for: "),
                    f"verified_for is '{ver}' but the current season is '{cur}'. Recheck prices, then set verified_for: {cur}.",
                    level="warning"))
    return cat
