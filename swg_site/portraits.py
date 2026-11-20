"""swg-portraits: trim, resize and centre unit portraits, animated AVIFs included.

    uv run swg-portraits                    fit every portrait in lib/images/portraits/
    uv run swg-portraits <folder>           bring in images from another folder (file names = unit ids)
    uv run swg-portraits --dry-run          list what would change without changing anything

Each image is cropped to the box around everything visible in any of its frames (one box for
the whole animation, so it doesn't wobble), scaled so its longer side is 128 px, and centred
on a transparent 128x128 square. The result is saved as lib/images/portraits/<unit-id>.avif
with every frame and its timing. Images already in that shape are left alone, so running it
again changes nothing. Before a file is replaced, the original is copied to
.cache/portrait-originals/ (not published, not committed).
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence

from . import catalog
from .catalog import suggest
from .paths import LIB, ROOT

SIZE = 128
PORTRAITS = LIB / "images" / "portraits"
BACKUP = ROOT / ".cache" / "portrait-originals"
EXTS = [".avif", ".webp", ".png", ".gif", ".jpg", ".jpeg"]  # preferred first when one id has several
ALPHA_MIN = 8      # alpha at or below this counts as empty: compression leaves faint specks
BG_TOLERANCE = 12  # for images without transparency: how close to the corner colour counts as background


def read_frames(path: Path) -> tuple[list[Image.Image], list[int]]:
    """Every frame as RGBA, and how long each one shows (ms)."""
    with Image.open(path) as im:
        frames, durations = [], []
        for fr in ImageSequence.Iterator(im):
            frames.append(fr.convert("RGBA"))
            durations.append(int(fr.info.get("duration") or im.info.get("duration") or 100))
    return frames, durations


def content_box(frames: list[Image.Image]) -> tuple[int, int, int, int] | None:
    """The smallest box holding everything visible in any frame. For images with no
    transparency, the background is whatever colour the top-left corner is."""
    box = None
    opaque = all(f.getchannel("A").getextrema()[0] == 255 for f in frames)
    for f in frames:
        if opaque:
            rgb = f.convert("RGB")
            bg = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
            diff = ImageChops.difference(rgb, bg).convert("L").point(lambda v: 255 if v > BG_TOLERANCE else 0)
            b = diff.getbbox()
        else:
            b = f.getchannel("A").point(lambda v: 255 if v > ALPHA_MIN else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    return box


def plan_fit(size: tuple[int, int], box: tuple[int, int, int, int], target: int = SIZE):
    """(scaled width, scaled height, left, top) for the content box on the target square."""
    w, h = box[2] - box[0], box[3] - box[1]
    k = target / max(w, h)
    nw, nh = max(1, round(w * k)), max(1, round(h * k))
    return nw, nh, (target - nw) // 2, (target - nh) // 2


def already_fitted(size, box, target: int = SIZE) -> bool:
    nw, nh, left, top = plan_fit(size, box, target)
    # a pixel or two of slack: re-encoding can fade the outermost row of a fitted image
    return (tuple(size) == (target, target) and abs((box[2] - box[0]) - nw) <= 2 and abs((box[3] - box[1]) - nh) <= 2
            and abs(box[0] - left) <= 2 and abs(box[1] - top) <= 2)


def fit(frames: list[Image.Image], box, target: int = SIZE) -> list[Image.Image]:
    nw, nh, left, top = plan_fit(frames[0].size, box, target)
    out = []
    for f in frames:
        part = f.crop(box)
        if part.size != (nw, nh):
            # resize with premultiplied alpha, or edges pick up a dark fringe
            part = part.convert("RGBa").resize((nw, nh), Image.LANCZOS).convert("RGBA")
        canvas = Image.new("RGBA", (target, target), (0, 0, 0, 0))
        canvas.alpha_composite(part, (left, top))
        out.append(canvas)
    return out


def save_avif(frames: list[Image.Image], durations: list[int], dest: Path):
    tmp = dest.with_name(dest.stem + ".tmp.avif")
    if len(frames) > 1:
        frames[0].save(tmp, format="AVIF", save_all=True, append_images=frames[1:], duration=durations, quality=85, speed=4)
    else:
        frames[0].save(tmp, format="AVIF", quality=85, speed=4)
    tmp.replace(dest)


def _show(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def back_up(path: Path) -> Path:
    folder = BACKUP
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / path.name
    if dest.exists():
        dest = folder / f"{path.stem}.{time.strftime('%Y%m%d-%H%M%S')}{path.suffix}"
    shutil.copy2(path, dest)
    return dest


def run(src: Path, out: Path = PORTRAITS, dry: bool = False, units=None) -> int:
    """Fit every image in src into out. Returns the number of problems."""
    units = units if units is not None else catalog.load().units
    files: dict[str, Path] = {}
    problems = 0
    for p in sorted(src.iterdir(), key=lambda p: (p.stem, EXTS.index(p.suffix.lower()) if p.suffix.lower() in EXTS else 99)):
        if p.name.startswith(".") or p.is_dir() or p.name.endswith(".tmp.avif"):
            continue
        if p.suffix.lower() not in EXTS:
            print(f"  skipped   {p.name}: not an image this can read ({', '.join(EXTS)})")
            continue
        if p.stem not in units:
            print(f"  skipped   {p.name}: '{p.stem}' isn't a unit id in content/units.yaml.{suggest(p.stem, units)}")
            problems += 1
            continue
        if p.stem in files:
            print(f"  skipped   {p.name}: {files[p.stem].name} is used for {p.stem} instead")
            continue
        files[p.stem] = p
    done = same = saved = 0
    for uid, p in files.items():
        dest = out / f"{uid}.avif"
        try:
            frames, durations = read_frames(p)
        except Exception as ex:
            print(f"  failed    {p.name}: couldn't read it ({ex})")
            problems += 1
            continue
        box = content_box(frames)
        if not box:
            print(f"  skipped   {p.name}: every frame is empty")
            problems += 1
            continue
        anim = f", {len(frames)} frames" if len(frames) > 1 else ""
        if p == dest and already_fitted(frames[0].size, box):
            same += 1
            print(f"  ok        {p.name}: already {SIZE}×{SIZE} and centred{anim}")
            continue
        nw, nh, _, _ = plan_fit(frames[0].size, box)
        what = (f"{frames[0].width}×{frames[0].height}, content {box[2] - box[0]}×{box[3] - box[1]} "
                f"→ {nw}×{nh} centred on {SIZE}×{SIZE}{anim}")
        if dry:
            print(f"  would fit {p.name}: {what}")
            done += 1
            continue
        for old in {dest, p} if p.parent.resolve() == out.resolve() else {dest}:
            if old.exists():
                back_up(old)
                saved += 1
        save_avif(fit(frames, box), durations, dest)
        if p.parent.resolve() == out.resolve() and p != dest:
            p.unlink()  # e.g. celia.png became celia.avif; the original is in the backup folder
        print(f"  fitted    {p.name} → {_show(dest)}: {what}")
        done += 1
    verb = "would fit" if dry else "fitted"
    print(f"\n{done} {verb}, {same} already fine" + (f", {problems} problem(s)" if problems else "") + ".")
    if saved:
        print(f"The {saved} original(s) it replaced are in {_show(BACKUP)}/, in case you want one back.")
    return problems


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if flags - {"--dry-run"} or len(args) > 1:
        sys.exit(__doc__)
    src = Path(args[0]).expanduser() if args else PORTRAITS
    if not src.is_dir():
        sys.exit(f"No folder at {src}.")
    PORTRAITS.mkdir(parents=True, exist_ok=True)
    print(f"Portraits from {_show(src)} → {_show(PORTRAITS)}/ ({SIZE}×{SIZE}, centred)\n")
    sys.exit(1 if run(src, PORTRAITS, "--dry-run" in flags) else 0)
