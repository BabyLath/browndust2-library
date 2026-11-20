"""swg-new-season: start the next Soul Wager season in one step.

    uv run swg-new-season              asks for the new season's name and dates, with defaults
    uv run swg-new-season --dry-run    shows what it would change, changes nothing
    uv run swg-new-season --yes        takes every default without asking

What it does:
  1. content/seasons.yaml: gives the season that's ending its `end` date and adds the new season
     after it (id, name, start, expected_end; empty boards, changes and sources to fill in).
  2. Copies lib/guide/current-season.md to lib/archive/<old id>-strategy.md, titled after the old
     season, with a note saying it's archived, links fixed for the new folder, and the live
     season card and countdown replaced by the dates the season ran. The Seasons page links it, and the sidebar lists it under
     Reference > Past season strategies.
  3. Adds a line to lib/changelog.md.
Then it checks the catalogs; if anything is wrong it puts every file back as it was.
"""
from __future__ import annotations

import argparse
import datetime as dt
import posixpath
import re
import sys
from pathlib import Path

import yaml

from .paths import CONTENT, LIB, ROOT

SEASON_DAYS = 56  # seasons have run about eight weeks


def bump(text: str, sep: str = "") -> str:
    """"s3" -> "s4", "Trial Season 3" -> "Trial Season 4"; no number at the end -> add " 2"."""
    m = re.match(r"^(.*?)(\d+)$", text)
    return f"{m.group(1)}{int(m.group(2)) + 1}" if m else f"{text}{sep}2"


def as_date(v) -> dt.date:
    return v if isinstance(v, dt.date) else dt.date.fromisoformat(str(v))


def long_date(d: dt.date) -> str:
    return f"{d:%B} {d.day}, {d.year}"


def defaults(seasons: list[dict], today: dt.date) -> dict:
    last = seasons[-1]
    prev_end = as_date(last.get("end") or last.get("expected_end") or today - dt.timedelta(days=1))
    start = prev_end + dt.timedelta(days=1)
    return {"id": bump(str(last["id"]), "-"), "name": bump(str(last["name"]), " "), "previous_end": prev_end,
            "start": start, "expected_end": start + dt.timedelta(days=SEASON_DAYS - 1)}


# ---------- the edits, as pure text functions so they're easy to test ----------
def edit_seasons(text: str, last: dict, new: dict, previous_end: dt.date) -> str:
    """Set the last season's end and append the new season, keeping the file's comments."""
    start = text.rfind(f"- id: {last['id']}")
    if start < 0:
        raise ValueError(f"couldn't find '- id: {last['id']}' in seasons.yaml")
    head, block = text[:start], text[start:]
    indent = re.search(r"\n(\s+)name:", block).group(1)
    if not last.get("end"):
        if re.search(r"^\s+expected_end:.*$", block, re.M):
            block = re.sub(r"^(\s+)expected_end:.*$", rf"\g<1>end: {previous_end.isoformat()}", block, count=1, flags=re.M)
        else:
            block = re.sub(r"^(\s+start:.*)$", rf"\1\n{indent}end: {previous_end.isoformat()}", block, count=1, flags=re.M)
    lead = indent[:-2] if len(indent) >= 2 else ""
    entry = (f"\n{lead}- id: {new['id']}\n{indent}name: {new['name']}\n{indent}start: {new['start'].isoformat()}\n"
             f"{indent}expected_end: {new['expected_end'].isoformat()}\n{indent}boards: []\n{indent}changes: []\n{indent}sources: []\n")
    return head + block.rstrip("\n") + "\n" + entry


def relink(body: str, src_dir: str, dest_dir: str) -> str:
    """Rewrite relative Markdown links so they still point at the same pages from dest_dir."""
    def fix(m: re.Match) -> str:
        target = m.group(2)
        if re.match(r"^(\w+:|#|/)", target):
            return m.group(0)
        path, _, frag = target.partition("#")
        new = posixpath.relpath(posixpath.normpath(posixpath.join(src_dir, path)), dest_dir)
        return m.group(1) + new + (f"#{frag}" if frag else "")
    return re.sub(r"(\]\()([^)\s]+)", fix, body)


def archive_page(text: str, season: dict, end: dt.date, order: int) -> str:
    """The current-season page, as a dated archive page for `season`."""
    m = re.match(r"\A---\n(.*?)\n---\n?", text, re.S)
    body = text[m.end():] if m else text
    name = season["name"]
    # the live season card and countdown only make sense while the season is on: swap the card
    # for the dates it ran, and drop lines that talk about the countdown
    ran = f"{name} ran from {long_date(as_date(season['start']))} to {long_date(end)}."
    body = body.replace("<!-- swg:season -->", ran)
    body = "\n".join(line for line in body.split("\n") if "countdown" not in line.lower())
    body = relink(body, "guide", "archive")
    note = (f'!!! note "Archived from {name}"\n'
            f"    This is the strategy this site recommended during {name} ({long_date(as_date(season['start']))} to "
            f"{long_date(end)}), kept as it was. Units, prices and boards may have changed since. "
            f"For the season that's on now, see [Current season strategy](../guide/current-season.md).\n")
    body, n = re.subn(r"(?m)^# .*$", f"# {name} strategy\n\n{note}", body, count=1)
    if not n:
        body = f"# {name} strategy\n\n{note}\n{body}"
    fm = {"title": f"{name} strategy", "description": f"What this site recommended running in {name}.",
          "order": order, "icon": "lucide/archive"}
    body = re.sub(r"\n{3,}", "\n\n", body.lstrip("\n").rstrip())
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n" + body + "\n"


def add_changelog(text: str, line: str, today: dt.date) -> str:
    heading = f"## {long_date(today)}"
    if heading + "\n" in text:
        i = text.index(heading + "\n") + len(heading) + 1
        rest = text[i:].lstrip("\n")
        return text[:i] + "\n" + line + "\n" + rest
    i = text.find("\n## ")
    i = len(text) if i < 0 else i + 1
    return text[:i] + f"{heading}\n\n{line}\n\n" + text[i:]


# ---------- the command ----------
def rollover(answers: dict, *, content: Path = CONTENT, lib: Path = LIB, today: dt.date | None = None,
             dry: bool = False, validate: bool = True, out=print) -> int:
    today = today or dt.date.today()
    seasons_file, page = content / "seasons.yaml", lib / "guide" / "current-season.md"
    changelog = lib / "changelog.md"
    text = seasons_file.read_text(encoding="utf-8")
    seasons = (yaml.safe_load(text) or {}).get("seasons") or []
    if not seasons:
        out("content/seasons.yaml has no seasons to follow on from.")
        return 1
    last = seasons[-1]
    d = {**defaults(seasons, today), **{k: v for k, v in answers.items() if v is not None}}
    if d["id"] in {str(s["id"]) for s in seasons}:
        out(f"There's already a season with the id '{d['id']}'.")
        return 1
    if d["start"] <= as_date(last["start"]):
        out(f"The new season has to start after {last['name']} did ({as_date(last['start'])}).")
        return 1
    if d["expected_end"] <= d["start"]:
        out("The expected end has to be after the start.")
        return 1
    end = as_date(last["end"]) if last.get("end") else d["previous_end"]
    archive = lib / "archive" / f"{last['id']}-strategy.md"

    new_files: dict[Path, str] = {
        seasons_file: edit_seasons(text, last, d, end),
        changelog: add_changelog(changelog.read_text(encoding="utf-8"),
                                 f"- {d['name']} started {long_date(d['start'])}. What we recommended in {last['name']} "
                                 f"is kept at [{last['name']} strategy](archive/{last['id']}-strategy.md).", today),
    }
    if page.exists():
        if archive.exists():
            out(f"{archive.relative_to(lib.parent)} already exists; leaving it as it is.")
        else:
            new_files[archive] = archive_page(page.read_text(encoding="utf-8"), last, end, order=-len(seasons))

    def show(p: Path) -> str:
        return str(p.relative_to(lib.parent)) if p.is_relative_to(lib.parent) else str(p)
    out(f"{last['name']} ends {long_date(end)}; {d['name']} ({d['id']}) runs {long_date(d['start'])} "
        f"to about {long_date(d['expected_end'])}.\n")
    for p in new_files:
        out(("  would " if dry else "  ") + ("write  " if not p.exists() else "update ") + show(p))
    if dry:
        out("\nDry run: nothing was changed.")
        return 0
    before = {p: (p.read_text(encoding="utf-8") if p.exists() else None) for p in new_files}
    for p, t in new_files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8")
    if validate:
        from . import catalog
        try:
            cat = catalog.load()
            errors = [x for x in cat.problems if x.level == "error"]
        except Exception as ex:  # a broken seasons.yaml
            errors = [ex]
        if errors:
            for p, t in before.items():
                if t is None:
                    p.unlink()
                else:
                    p.write_text(t, encoding="utf-8")
            out("\nSomething didn't check out, so every file was put back as it was:")
            for x in errors:
                out(f"  {x}")
            return 1
    out(f"""
Done. Still to do by hand:
  1. content/seasons.yaml: fill in {d['name']}'s changes and sources, and boards as you confirm them.
  2. Update changed prices and add new units in content/units.yaml.
  3. Rewrite lib/guide/current-season.md for {d['name']}. The old version is saved as {show(archive)}.
  4. uv run swg-check, then commit.""")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="swg-new-season", description=__doc__.split("\n\n")[0])
    ap.add_argument("--id"); ap.add_argument("--name")
    ap.add_argument("--start", type=dt.date.fromisoformat, metavar="YYYY-MM-DD")
    ap.add_argument("--previous-end", type=dt.date.fromisoformat, metavar="YYYY-MM-DD",
                    help="last day of the season that's ending, if seasons.yaml doesn't have it yet")
    ap.add_argument("--expected-end", type=dt.date.fromisoformat, metavar="YYYY-MM-DD")
    ap.add_argument("--yes", action="store_true", help="take every default without asking")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    seasons = (yaml.safe_load((CONTENT / "seasons.yaml").read_text(encoding="utf-8")) or {}).get("seasons") or []
    if not seasons:
        sys.exit("content/seasons.yaml has no seasons yet.")
    last = seasons[-1]
    answers = {"id": a.id, "name": a.name, "start": a.start, "previous_end": a.previous_end, "expected_end": a.expected_end}
    if not a.yes and sys.stdin.isatty():
        d = defaults(seasons, dt.date.today())
        print("Press Enter to keep the suggestion in [brackets].\n")

        def ask(key, label, conv=str):
            if answers[key] is not None:
                return
            while True:
                got = input(f"{label} [{d[key]}]: ").strip()
                if not got:
                    return
                try:
                    answers[key] = conv(got)
                    d[key] = answers[key]
                    if key == "previous_end" and answers["start"] is None:
                        d["start"] = answers[key] + dt.timedelta(days=1)
                    if key in ("previous_end", "start") and answers["expected_end"] is None:
                        d["expected_end"] = d["start"] + dt.timedelta(days=SEASON_DAYS - 1)
                    return
                except ValueError:
                    print("  Use YYYY-MM-DD, like 2026-12-16.")
        if not last.get("end"):
            ask("previous_end", f"Last day of {last['name']}", dt.date.fromisoformat)
        ask("name", "New season's name")
        ask("id", "Its id (used in board blocks as season:)")
        ask("start", "First day", dt.date.fromisoformat)
        ask("expected_end", "Expected last day", dt.date.fromisoformat)
        print()
    sys.exit(rollover(answers, dry=a.dry_run))
