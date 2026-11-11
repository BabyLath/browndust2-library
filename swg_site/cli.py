"""Command-line entry points: swg-check, swg-serve, swg-build."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from . import catalog
from .generate import Generator
from .paths import BUILD_CONFIG, CONTENT, LIB, ROOT


def _report(problems) -> int:
    errors = [p for p in problems if p.level == "error"]
    warnings = [p for p in problems if p.level != "error"]
    for p in errors + warnings:
        print(p)
    if not problems:
        print("All good: catalogs, pages and boards check out.")
    else:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


def _guard(fn):
    """Turn a broken YAML file into one readable line instead of a traceback."""
    def run(*a, **k):
        try:
            return fn(*a, **k)
        except catalog.CatalogSyntaxError as ex:
            print(ex)
            sys.exit(1)
    return run


def _collect() -> list:
    cat = catalog.load()
    with tempfile.TemporaryDirectory() as tmp:
        return cat.problems + Generator(cat, Path(tmp) / "docs").run(write_config=False)


@_guard
def check_main():
    """Validate everything without building. Run this before you commit."""
    sys.exit(_report(_collect()))


def _generate() -> list:
    cat = catalog.load()
    return cat.problems + Generator(cat).run()


@_guard
def build_main():
    """Validate, generate, then build the production site into site/."""
    problems = _generate()
    if _report(problems):
        sys.exit("Build stopped. Fix the errors above.")
    subprocess.run(["zensical", "build", "--clean", "-f", str(BUILD_CONFIG)], cwd=ROOT, check=True)
    print("Built site/.")


def _snapshot() -> dict:
    return {p: p.stat().st_mtime for d in (LIB, CONTENT) for p in d.rglob("*") if p.is_file()}


@_guard
def serve_main():
    """Live preview. Edits in lib/ or content/ regenerate the site automatically."""
    _report(_generate())
    proc = subprocess.Popen(["zensical", "serve", "-f", str(BUILD_CONFIG), *sys.argv[1:]], cwd=ROOT)

    def watch():
        last = _snapshot()
        while proc.poll() is None:
            time.sleep(1)
            now = _snapshot()
            if now != last:
                last = now
                print("\nChange detected, regenerating…")
                try:
                    _report(_generate())
                except catalog.CatalogSyntaxError as ex:  # keep the preview alive on a bad edit
                    print(ex)
                except Exception as ex:
                    print(f"ERROR   {ex}")

    threading.Thread(target=watch, daemon=True).start()
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


@_guard
def new_unit_main():
    """Create lib/units/<id>.md from templates/unit.md, ready for the unit's effect and guide."""
    from .catalog import suggest
    from .paths import ROOT
    if len(sys.argv) != 2:
        sys.exit("Usage: uv run swg-new-unit <unit-id>    e.g. uv run swg-new-unit celia-the-curse")
    uid = sys.argv[1].strip()
    cat = catalog.load()
    if uid not in cat.units:
        sys.exit(f"'{uid}' isn't in content/units.yaml.{suggest(uid, cat.units)}")
    dest = LIB / "units" / f"{uid}.md"
    if dest.exists():
        sys.exit(f"{dest.relative_to(ROOT)} already exists. Edit it there.")
    text = (ROOT / "templates" / "unit.md").read_text(encoding="utf-8")
    text = text.replace("unit: celia-the-curse", f"unit: {uid}", 1)
    dest.write_text(text, encoding="utf-8")
    print(f"Created {dest.relative_to(ROOT)} for {cat.unit_label(uid)}.")
    print("Fill in ## Effect, delete the sections you don't need, then run uv run swg-serve to preview.")

