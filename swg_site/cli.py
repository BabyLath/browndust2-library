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


def _collect() -> list:
    cat = catalog.load()
    with tempfile.TemporaryDirectory() as tmp:
        return cat.problems + Generator(cat, Path(tmp) / "docs").run(write_config=False)


def check_main():
    """Validate everything without building. Run this before you commit."""
    sys.exit(_report(_collect()))


def _generate() -> list:
    cat = catalog.load()
    return cat.problems + Generator(cat).run()


def build_main():
    """Validate, generate, then build the production site into site/."""
    problems = _generate()
    if _report(problems):
        sys.exit("Build stopped. Fix the errors above.")
    subprocess.run(["zensical", "build", "--clean", "-f", str(BUILD_CONFIG)], cwd=ROOT, check=True)
    print("Built site/.")


def _snapshot() -> dict:
    return {p: p.stat().st_mtime for d in (LIB, CONTENT) for p in d.rglob("*") if p.is_file()}


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
                except Exception as ex:  # keep the preview alive on a bad edit
                    print(f"ERROR   {ex}")

    threading.Thread(target=watch, daemon=True).start()
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
