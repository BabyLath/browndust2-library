"""HTML snippets injected into generated Markdown pages.

All markup that repeats across pages lives here, so content files stay
plain Markdown + YAML.
"""
from __future__ import annotations

import datetime as dt
import html
import re

from .catalog import Catalog

e = html.escape
GRID = 7


# Relative paths in generated Markdown are resolved by Zensical against the SOURCE file's
# folder (reference/tiles.md lives in reference/), not the page URL (reference/tiles/).
# So a page in a subfolder reaches the site root with one "../" per folder level.

# ---------- shop math (mirrors lib/guide/board-shop.md) ----------
def sale_price(p: int) -> int:
    return -(-p // 2)  # ceil


def sell_price(p: int, pid: str = "") -> int:
    return 1 if pid == "protection-tile" else max(2, p // 2)


def fmt_date(d: dt.date) -> str:
    return f"{d:%b} {d.day}, {d.year}"


# ---------- small pieces ----------
def search_text(*parts: str) -> str:
    """Lower-case text for a data-search attribute, with [[Name]] shortcodes reduced to Name."""
    return re.sub(r"\[\[([^\[\]\n]+)\]\]", lambda m: m.group(1).strip().rstrip("+"), " ".join(p for p in parts if p)).lower()


def rich(text: str) -> str:
    """Multi-line description -> HTML. Each line is its own line; a blank line starts a new
    paragraph; a block of lines starting with "- " becomes a bullet list. A paragraph whose
    first line ends with ":" shows that line in bold, as a label for the lines under it. Single-line text
    comes out exactly as before."""
    text = str(text or "").strip()
    if "\n" not in text:
        return e(text)
    out = []
    for block in re.split(r"\n\s*\n", text):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if lines and all(ln.startswith("- ") for ln in lines):
            out.append('<ul class="swg-rich">' + "".join(f"<li>{e(ln[2:])}</li>" for ln in lines) + "</ul>")
        else:
            html_lines = [e(ln) for ln in lines]
            if len(lines) > 1 and lines[0].endswith(":"):
                html_lines[0] = f'<strong class="swg-rich__lead">{html_lines[0]}</strong>'
            out.append('<p class="swg-rich">' + "<br>".join(html_lines) + "</p>")
    return "".join(out)


def grade_badge(g: str) -> str:
    return f'<span class="swg-grade" data-grade="{e(g.lower())}">{e(g)}</span>' if g else ""


def slug(text: str) -> str:
    """"Close-Range Attack" -> "close-range-attack"; matches image file names and shortcode ids."""
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def tag_pills(tags) -> str:
    # Icon only; the tag name shows on hover. [[Tag]] is filled in by the shortcode pass,
    # which knows each page's path to the images (and falls back to the name with no icon).
    return "".join(f'<span class="swg-tag-icon">[[{e(t)}]]</span>' for t in tags or [])


def unit_link(cat: Catalog, uid: str, guides: set[str], prefix: str) -> str:
    label = e(cat.unit_label(uid))
    return f'<a href="{prefix}units/{uid}/">{label}</a>' if uid in guides else label


def join_and(items: list[str]) -> str:
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def upgrades_of(u: dict) -> list[int] | None:
    up = u.get("upgrades")
    return up if isinstance(up, list) and len(up) == 5 else None


# ---------- unit guide ----------
def _entry(x) -> tuple[str, str]:
    """A list entry in a guide's front matter: either an id, or {id: ..., note: ...}."""
    if isinstance(x, dict):
        return str(x.get("id", "")), str(x.get("note") or "")
    return str(x), ""


def _initials(name: str) -> str:
    words = [w for w in re.split(r"[\s-]+", re.sub(r"['’]s\b|['’]", "", name)) if w and w[0].isalnum()]
    return "".join(w[0] for w in words[:2]).upper() or "?"


def _fig(frame: str, caption: str, note: str = "", href: str = "", cls: str = "") -> str:
    """One item in a build column or recommendation list: a framed picture with a caption under it."""
    cap = caption + (f'<em class="swg-guide__flex-note">{e(note)}</em>' if note else "")
    inner = f'<span class="swg-guide__frame">{frame}</span><figcaption>{cap}</figcaption>'
    return f'<figure class="swg-guide__fig {cls}">' + (f'<a href="{href}">{inner}</a>' if href else inner) + "</figure>"


def gear_fig(cat: Catalog, gid: str, note: str, gear_images: dict, prefix: str) -> str:
    g = cat.gear[gid]
    pic = (f'<img src="{prefix}{gear_images[gid]}" alt="" loading="lazy">' if gid in gear_images
           else f'<span class="swg-guide__initials" aria-hidden="true">{e(_initials(g["name"]))}</span>')
    return _fig(pic, f'{e(g["name"])} <span class="swg-cost">{g["price"]}</span>', note, f"{prefix}reference/gear/#{gid}", "swg-guide__fig--gear")


def tile_fig(cat: Catalog, tid: str, note: str, prefix: str) -> str:
    t = cat.tiles[tid]
    return _fig(framed_shape(t.get("shape") or "", t["name"]), f'{e(t["name"])} <span class="swg-cost">{t["price"]}</span>',
                note, f"{prefix}reference/tiles/#{tid}", "swg-guide__fig--tile")


def unit_fig(cat: Catalog, uid: str, note: str, guides: set[str], prefix: str, portraits: dict | None = None) -> str:
    """A unit in Partner units or Works well with: its portrait if there is one, otherwise its footprint."""
    u = cat.units[uid]
    grade = (u.get("grade") or "").lower()
    pic = portraits.get(uid) if portraits else None
    frame = (f'<img src="{prefix}{pic}" alt="" loading="lazy" decoding="async">' if pic
             else framed_shape(u.get("shape") or "", cat.unit_label(uid)))
    return _fig(frame,
                f'{e(cat.unit_label(uid))} <span class="swg-cost">{u["price"]}</span>', note,
                f"{prefix}units/{uid}/" if uid in guides else "", f"swg-guide__fig--unit swg-guide__fig--{grade}" + (" swg-guide__fig--portrait" if pic else ""))


def framed_shape(shape: str, label: str) -> str:
    """Footprint for a framed square: one square of footprint is the same size in every frame,
    so a 1×1 unit looks small next to a 2×3 one, the way the pieces compare in game."""
    rows = parse_shape(shape)
    if not rows:
        return ""
    span = max(len(rows), len(rows[0]))
    pct = round(len(rows[0]) * 100 / max(4.6, span + .8), 1)
    return shape_svg(shape, label, 20, 4).replace('<svg class="swg-shape"', f'<svg class="swg-shape" style="width:{pct}%;height:auto"', 1)


def _ranks(value) -> list[dict]:
    if isinstance(value, dict):
        return [value]
    return [r for r in (value or []) if isinstance(r, dict)]


def unit_guide(cat: Catalog, uid: str, fm: dict, intro: str, sections: list[str], boards: list[str],
               guides: set[str], gear_images: dict, builds_meta: dict, prefix: str, portraits: dict | None = None) -> str:
    """Whole unit guide page body. Order: header, then a two-column
    summary (footprint and upgrade costs | ranks, stopping points, overview), then the author's own
    ## sections, example builds, recommendations, and example boards."""
    u = cat.units[uid]
    p = u["price"]
    label = cat.unit_label(uid)
    tagline = fm.get("tagline") or fm.get("summary")
    roles = fm.get("roles") or ([fm["role"]] if fm.get("role") else [])
    ranks = fm.get("ranks") or {}
    stops = fm.get("stopping_points") or []
    portraits = portraits or {}
    portrait = portraits.get(uid)

    # header
    chips = []
    if u.get("grade"):
        chips.append(f'<li>{grade_badge(u["grade"])}</li>')
    chips += [f'<li class="swg-guide__tag">[[{e(t)}+]]</li>' for t in u.get("tags") or []]
    chips += [f'<li class="swg-guide__role">{e(str(r).capitalize())}</li>' for r in roles]
    header = (f'<header class="swg-guide__header" markdown="1">\n\n# {label}\n\n'
              f'<div class="swg-guide__headmeta" markdown="0">'
              + (f'<p class="swg-guide__tagline">{e(str(tagline))}</p>' if tagline else "")
              + (f'<ul class="swg-guide__roles" aria-label="Grade, tags and roles">{"".join(chips)}</ul>' if chips else "")
              + f'<p class="swg-guide__price"><b>{p}</b> Soul Tokens · <b>{sale_price(p)}</b> on sale · sells for <b>{sell_price(p)}</b>'
              + f' · <a href="{prefix}units/">All units</a></p></div>\n\n</header>')

    # left column: footprint, where a portrait would be, and the upgrade costs
    up = upgrades_of(u)
    up_rows = ("".join(f"<tr><th>+{i + 1}</th><td>{n}</td></tr>" for i, n in enumerate(up))
               + f'<tr class="swg-guide__up-total"><th>To +5</th><td>{sum(up)}</td></tr>') if up else ""
    if portrait:
        # the unit's art, with the footprint moved to a small row under it
        top = (f'<div class="swg-guide__pic"><figure class="swg-guide__art"><img src="{prefix}{portrait}" alt="{e(label)}" width="168" height="200" decoding="async"></figure>'
               f'<figure class="swg-guide__footprint swg-guide__footprint--small"><span class="swg-guide__frame">{framed_shape(u.get("shape") or "", label)}</span>'
               f'<figcaption>Footprint</figcaption></figure></div>')
    else:
        top = (f'<figure class="swg-guide__footprint"><span class="swg-guide__frame">{framed_shape(u.get("shape") or "", label)}</span>'
               f'<figcaption>Footprint</figcaption></figure>')
    portrait = (f'<div class="swg-guide__portrait" markdown="0">{top}'
                + (f'<table class="swg-guide__upgrades"><caption>Upgrade cost</caption>{up_rows}</table>' if up_rows else "")
                + "</div>")

    # right column: ranks, stopping points, overview
    cards = ""
    for key, title in (("damage", "Damage rank"), ("support", "Support rank")):
        rs = _ranks(ranks.get(key))
        if not rs:
            continue
        lines = "".join(f'<p class="swg-guide__rank" data-tier="{e(str(r.get("tier", "?")))}">{e(str(r.get("tier", "?")))}'
                        + (f' <em>{e(str(r["note"]))}</em>' if r.get("note") else "") + "</p>" for r in rs)
        cards += f'<section class="swg-guide__rank-card"><h2>{title}</h2>{lines}</section>'
    stop_html = ""
    if stops:
        items = "".join(f"<li>+{int(n)}</li>" for n in stops)
        stop_html = (f'<section class="swg-guide__stops" id="stopping-points"><h2>Stopping points</h2>'
                     f'<ul class="swg-guide__stop-list">{items}</ul>'
                     + (f'<p class="swg-guide__stop-note">{e(str(fm["stopping_note"]))}</p>' if fm.get("stopping_note") else "")
                     + "</section>")
    right = ('<div class="swg-guide__main" markdown="1">\n\n'
             + (f'<div class="swg-guide__ranks" markdown="0">{cards}</div>\n\n' if cards else "")
             + (f'<div markdown="0">{stop_html}</div>\n\n' if stop_html else "")
             + f'<div class="swg-guide__prose" markdown="1">\n\n{intro.strip()}\n\n</div>\n\n</div>')
    bare = " swg-guide__summary--bare" if not (cards or stop_html or intro.strip()) else ""
    summary = f'<div class="swg-guide__summary{bare}" id="overview" markdown="1">\n\n{portrait}\n\n{right}\n\n</div>'

    out = [header, summary]

    # the author's own ## sections
    for sec in sections:
        out.append(f'<section class="swg-guide__section" markdown="1">\n\n{sec.strip()}\n\n</section>')

    # example builds from front matter
    for n, b in enumerate(fm.get("builds") or [], 1):
        cols, total = [], p
        tiles = [(_entry(x)) for x in b.get("tiles") or []]
        tiles = [(t, note) for t, note in tiles if t in cat.tiles]
        gear = [(g, note) for g, note in map(_entry, b.get("gear") or []) if g in cat.gear]
        partners = [(w, note) for w, note in map(_entry, b.get("with") or []) if w in cat.units]
        total += sum(cat.tiles[t]["price"] for t, _ in tiles) + sum(cat.gear[g]["price"] for g, _ in gear) \
            + sum(cat.units[w]["price"] for w, _ in partners)
        if tiles or b.get("tiles_note"):
            cols.append('<div class="swg-guide__col swg-guide__col--tiles"><h3>Tiles</h3><div class="swg-guide__figs">'
                        + "".join(tile_fig(cat, t, note, prefix) for t, note in tiles) + "</div>"
                        + (f'<p class="swg-guide__col-note">{e(str(b["tiles_note"]))}</p>' if b.get("tiles_note") else "")
                        + "</div>")
        if gear:
            cols.append('<div class="swg-guide__col"><h3>Gear</h3><div class="swg-guide__figs">'
                        + "".join(gear_fig(cat, g, note, gear_images, prefix) for g, note in gear) + "</div></div>")
        if partners:
            cols.append('<div class="swg-guide__col"><h3>Partner units</h3><div class="swg-guide__figs">'
                        + "".join(unit_fig(cat, w, note, guides, prefix, portraits) for w, note in partners) + "</div></div>")
        body = [f'<section class="swg-guide__section swg-guide__build" id="build-{n}" markdown="1">\n',
                f'<h2 class="swg-guide__label swg-guide__label--strong">{e(str(b.get("name", "Build")))}</h2>\n']
        if cols:
            body.append(f'<div class="swg-guide__build-grid swg-guide__build-grid--{len(cols)}" markdown="0">{"".join(cols)}</div>\n')
            body.append(f'<p class="swg-guide__build-total" markdown="0">With this unit: <b>{total}</b> Soul Tokens before upgrades.</p>\n')
        if b.get("note"):
            body.append(f'<div class="swg-guide__build-note" markdown="1">\n\n{str(b["note"]).strip()}\n\n</div>\n')
        body.append("</section>")
        out.append("\n".join(body))

    # recommendations: suggested builds and works well with
    groups = []
    sugg = [(b, note) for b, note in map(_entry, fm.get("suggested_builds") or []) if b in builds_meta]
    if sugg or fm.get("suggested_builds_note"):
        items = "".join(f'<li><a href="{prefix}builds/{b}/">{e(builds_meta[b])}</a>'
                        + (f'<em class="swg-guide__flex-note">{e(note)}</em>' if note else "") + "</li>" for b, note in sugg)
        groups.append('<div class="swg-guide__rec" id="suggested-builds"><div class="swg-guide__rec-label"><h2 class="swg-guide__label">Suggested builds</h2>'
                      + (f'<p class="swg-guide__section-note">{e(str(fm["suggested_builds_note"]))}</p>' if fm.get("suggested_builds_note") else "")
                      + "</div>" + (f'<ul class="swg-guide__rec-links">{items}</ul>' if items else "") + "</div>")
    wwith = [(w, note) for w, note in map(_entry, fm.get("works_well_with") or []) if w in cat.units]
    if wwith or fm.get("works_well_with_note"):
        groups.append('<div class="swg-guide__rec" id="works-well-with"><div class="swg-guide__rec-label"><h2 class="swg-guide__label">Works well with</h2>'
                      + (f'<p class="swg-guide__section-note">{e(str(fm["works_well_with_note"]))}</p>' if fm.get("works_well_with_note") else "")
                      + "</div>" + (f'<div class="swg-guide__rec-list">{"".join(unit_fig(cat, w, note, guides, prefix, portraits) for w, note in wwith)}</div>' if wwith else "")
                      + "</div>")
    if groups:
        out.append(f'<section class="swg-guide__section swg-guide__recs" id="recommendations" markdown="0">{"".join(groups)}</section>')

    # board fences written anywhere in the guide, gathered at the end
    if boards:
        out.append('<section class="swg-guide__section swg-guide__boards" id="example-boards" markdown="1">\n\n'
                   '<h2 class="swg-guide__label">Example boards</h2>\n\n' + "\n\n".join(b.strip() for b in boards) + "\n\n</section>")

    return '<div class="swg-guide" markdown="1">\n\n' + "\n\n".join(out) + "\n\n</div>\n"


# ---------- board fence ----------
def board(cat: Catalog, spec: dict, guides: set[str], prefix: str, portraits: dict | None = None) -> str:
    rows = [r.replace(" ", "") for r in str(spec.get("layout") or "").strip("\n").splitlines()]
    pieces: dict[str, str] = {str(k): str(v) for k, v in (spec.get("pieces") or {}).items()}
    gear: dict[str, list] = {str(k): (v if isinstance(v, list) else [v]) for k, v in (spec.get("gear") or {}).items()}
    roles: dict[str, str] = {str(k): str(v) for k, v in (spec.get("roles") or {}).items()}

    def kind_of(pid: str) -> str:
        return "unit" if pid in cat.units else "tile" if pid in cat.tiles else "?"

    floor = [r.replace(" ", "") for r in str(spec.get("floor") or "").strip("\n").splitlines()]
    if len(floor) != len(rows) or any(len(a) != len(b) for a, b in zip(floor, rows)):
        floor = []

    # palette index per unit letter so each unit gets a distinct hue
    unit_letters = [k for k, v in pieces.items() if kind_of(v) == "unit"]

    def edges(grid: list[str], r: int, c: int) -> str:
        """Border classes where the neighbouring cell belongs to a different piece."""
        ch, out = grid[r][c], []
        if r == 0 or grid[r - 1][c] != ch: out.append("e-t")
        if r == len(grid) - 1 or grid[r + 1][c] != ch: out.append("e-b")
        if c == 0 or grid[r][c - 1] != ch: out.append("e-l")
        if c == len(grid[r]) - 1 or grid[r][c + 1] != ch: out.append("e-r")
        return " ".join(out)

    seen: set[str] = set()

    def label(ch: str) -> str:
        if ch in seen:
            return ""
        seen.add(ch)
        return f"<b>{e(ch)}</b>"

    cells = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            f = floor[r][c] if floor else "."
            if ch == "." and f == ".":
                cells.append('<span class="swg-cell"></span>')
                continue
            if not floor:  # one layer: tiles and units side by side
                kind = kind_of(pieces.get(ch, ""))
                hue = unit_letters.index(ch) % 6 if ch in unit_letters else 0
                cells.append(f'<span class="swg-cell swg-cell--{kind} swg-hue-{hue} {edges(rows, r, c)}">{label(ch)}</span>')
                continue
            # two layers: the tile underneath, the unit standing on it
            inner = ""
            if ch != ".":
                hue = unit_letters.index(ch) % 6 if ch in unit_letters else 0
                inner = f'<span class="swg-cell__unit swg-cell--unit swg-hue-{hue} {edges(rows, r, c)}">{label(ch)}</span>'
            if f != ".":
                tl = label(f)
                cells.append(f'<span class="swg-cell swg-cell--tile swg-cell--floor {edges(floor, r, c)}">'
                             f'{tl.replace("<b>", "<i>").replace("</b>", "</i>") if tl else ""}{inner}</span>')
            else:
                cells.append(f'<span class="swg-cell swg-cell--floor">{inner}</span>')

    # ---- team card ----
    details: dict[str, str] = {str(k): str(v) for k, v in (spec.get("details") or {}).items()}
    total = 0
    members, floor_items = [], {}
    for letter, pid in pieces.items():
        kind = kind_of(pid)
        note = details.get(letter, "")
        if kind == "unit":
            u = cat.units[pid]
            gear_ids = [g for g in gear.get(letter, []) if g in cat.gear]
            price = u["price"] + sum(cat.gear[g]["price"] for g in gear_ids)
            total += price
            members.append((letter, pid, gear_ids, price, roles.get(letter, ""), note))
        elif kind == "tile":
            t = cat.tiles[pid]
            total += t["price"]
            # one row per tile type: three Protection Tiles show as "Protection Tile ×3"
            item = floor_items.setdefault(pid, {"pid": pid, "letters": [], "text": ""})
            item["letters"].append(letter)
            text = " ".join(x for x in (roles.get(letter, ""), note) if x)
            if text and text not in item["text"]:
                item["text"] = (item["text"] + " " + text).strip()

    def archetype(u: dict) -> tuple[str, str]:
        tags = u.get("tags") or []
        if any("Attack" in t for t in tags):
            return "dps", "Attacker"
        if "Defending" in tags:
            return "tank", "Defender"
        return "support", "Support"

    lis = []
    for letter, pid, gear_ids, price, role, note in members:
        u = cat.units[pid]
        arch, arch_label = archetype(u)
        hue = unit_letters.index(letter) % 6
        who = (f'<span class="swg-team__char">{e(u.get("character") or cat.unit_label(pid))}</span>'
               + (f'<span class="swg-team__costume">{e(u["costume"])}</span>' if u.get("costume") else ""))
        name = f'<a href="{prefix}units/{pid}/">{who}</a>' if pid in guides else who
        gear_html = "".join(
            f'<li class="swg-team__gear"><a href="{prefix}reference/gear/#{g}" title="{e(cat.gear[g]["name"])}">'
            f'<span class="swg-guide__initials" aria-hidden="true">{e(_initials(cat.gear[g]["name"]))}</span>'
            f'<span>{e(cat.gear[g]["name"])} <span class="swg-cost">{cat.gear[g]["price"]}</span></span></a></li>' for g in gear_ids)
        lis.append(
            f'<li class="swg-team__member swg-team__member--{arch}">'
            f'<p class="swg-team__role">{e(role) if role else arch_label}</p>'
            f'<div class="swg-team__unit">'
            f'<p class="swg-team__name"><span class="swg-key swg-cell--unit swg-hue-{hue}">{e(letter)}</span>'
            f'<span>{name}</span></p>'
            + (f'<span class="swg-team__frame swg-team__frame--portrait"><img src="{prefix}{portraits[pid]}" alt="" loading="lazy" decoding="async"></span>'
               if portraits and pid in portraits else
               f'<span class="swg-team__frame">{framed_shape(u.get("shape") or "", cat.unit_label(pid))}</span>')
            + f'<p class="swg-team__meta">{grade_badge(u.get("grade") or "")} <span class="swg-cost">{u["price"]}</span></p></div>'
            + (f'<div class="swg-team__context"><p class="swg-team__note">{e(note)}</p></div>' if note else "")
            + (f'<ul class="swg-team__gears" aria-label="Gear">{gear_html}</ul>' if gear_html else "")
            + "</li>")

    floor_html = ""
    if floor_items:
        rows_ = []
        for item in floor_items.values():
            t = cat.tiles[item["pid"]]
            n = len(item["letters"])
            rows_.append(f'<li><span class="swg-team__tile-shape">{shape_svg(t.get("shape") or "", t["name"], 6, 1)}</span>'
                         f'<span class="swg-team__tile-name"><a href="{prefix}reference/tiles/#{item["pid"]}">{e(t["name"])}</a>'
                         f'{f" ×{n}" if n > 1 else ""} <span class="swg-cost">{t["price"] * n}</span>'
                         + (f'<em>{e(item["text"])}</em>' if item["text"] else "") + "</span></li>")
        floor_html = f'<div class="swg-team__floor"><p class="swg-team__floor-label">Tiles</p><ul>{"".join(rows_)}</ul></div>'

    season = cat.season(str(spec.get("season", ""))) if spec.get("season") else None
    name_txt = e(str(spec.get("name", "Untitled build")))
    eyebrow = [e(str(spec["context"]))] if spec.get("context") else []
    if season: eyebrow.append(e(season["name"]))
    if spec.get("total") is not False:  # total: false for "pick one of these" lists
        eyebrow.append(f"{total} Soul Tokens" + ("" if rows else " before upgrades"))
    board_html = (f'<figure class="swg-team__board"><div class="swg-build__board" role="img" aria-label="7 by 7 board layout for {name_txt}">{"".join(cells)}</div></figure>'
                  if rows else "")
    return f"""
<section class="swg-team{' swg-team--board' if rows else ''}" aria-label="{name_txt}" markdown="0">
  <header class="swg-team__header">
    <div class="swg-team__intro">
      <p class="swg-team__eyebrow">{" · ".join(eyebrow)}</p>
      <p class="swg-team__title">{name_txt}</p>
      {f'<p class="swg-team__summary">{e(str(spec["summary"]))}</p>' if spec.get('summary') else ''}
    </div>
    {board_html}
  </header>
  {f'<ol class="swg-team__members swg-team__members--{min(len(lis), 4)}">{"".join(lis)}</ol>' if lis else ''}
  {floor_html}
  {f'<p class="swg-team__notes"><strong>Note:</strong> {e(str(spec["notes"]))}</p>' if spec.get('notes') else ''}
</section>
"""


# ---------- generated reference pages ----------
def _staleness(cat: Catalog, fname: str) -> str:
    ver = cat.verified.get(fname)
    cur = cat.current_season
    if ver == cur["id"]:
        return f'!!! success "Checked for {e(cur["name"])}"\n'
    vs = cat.season(ver or "")
    return (f'!!! warning "Not yet checked for {e(cur["name"])}"\n'
            f'    These values were last confirmed for {e(vs["name"]) if vs else "an earlier season"}. '
            f'{e(cur["name"])} changed costs on some pieces, so some prices below may be off.\n')


def _thumb(uid: str, portraits: dict) -> str:
    """Small portrait at the start of a Units table row. Rows without one keep an empty frame,
    so names still line up."""
    pic = portraits.get(uid)
    inner = f'<img src="../{pic}" alt="" loading="lazy" decoding="async">' if pic else ""
    return f'<span class="swg-thumb{"" if pic else " swg-thumb--empty"}" aria-hidden="true">{inner}</span>'


def units_page(cat: Catalog, guides: set[str], portraits: dict | None = None) -> str:
    portraits = portraits or {}
    has_grade = any(u.get("grade") for u in cat.units.values())
    has_tags = any(u.get("tags") for u in cat.units.values())
    has_up = any(upgrades_of(u) for u in cat.units.values())
    has_shape = any(parse_shape(u.get("shape") or "") for u in cat.units.values())
    rows = []
    for uid, u in sorted(cat.units.items(), key=lambda kv: (kv[1]["character"], kv[1]["costume"])):
        p = u["price"]
        unit_name = f'{u["character"]}, {u["costume"]}'
        has = uid in guides
        name = f'<a href="{uid}/">{e(u["costume"])}</a>' if has else e(u["costume"])
        rows.append(
            f'<tr data-search="{e(search_text(u["character"], u["costume"]))}" data-price="{p}" '
            f'data-grade="{e(u.get("grade") or "")}" data-tags="{e("|".join(u.get("tags") or []))}" data-guide="{int(has)}">'
            f'<td class="swg-unit-char">{_thumb(uid, portraits) if portraits else ""}{e(u["character"])}</td><td class="swg-unit-costume">{name}</td>'
            + (f'<td class="swg-fit swg-unit-shape">{shape_svg(u.get("shape") or "", unit_name, 10, 2) or "<span class=swg-missing>–</span>"}</td>' if has_shape else "")
            + (f'<td>{grade_badge(u.get("grade") or "")}</td>' if has_grade else "")
            + (f'<td>{tag_pills(u.get("tags"))}</td>' if has_tags else "")
            + _unit_price_cell(p, uid)
            + (_upgrade_cells(upgrades_of(u)) if has_up else "") + "</tr>")
    grades = "".join(f'<option>{e(g)}</option>' for g in cat.meta.get("grades", []))
    tags = "".join(f'<option>{e(t)}</option>' for t in cat.meta.get("tags", []))
    return f"""---
title: Units
description: Every unit piece in the Soul Wager Battle Shop with price, sale price and sell value.
icon: lucide/users
hide:
  - toc
---

# Units

{_staleness(cat, "units.yaml")}
Prices are in Soul Tokens. **On sale** is the 10%-chance half-price offer. **Sells for** is what you get back. **Upgrades** (switch it on above the table) lists the cost of each upgrade from +1 to +5, then their total; you can't upgrade past the level the unit has on your main roster. Names with a link have a full guide, including the unit's effect.

<div class="swg-filter" data-target="swg-units" markdown="0">
  <label>Search<input type="search" data-f="q" placeholder="Character or costume"></label>
  {f'<label>Grade<select data-f="grade"><option value="">Any</option>{grades}</select></label>' if has_grade else ''}
  {f'<label>Tag<select data-f="tag"><option value="">Any</option>{tags}</select></label>' if has_tags else ''}
  <label>Max price<input type="number" data-f="max" min="1" max="30" placeholder="Any"></label>
  <div class="swg-filter__opts">
    <label class="swg-check"><input type="checkbox" data-f="guide"> Has a guide</label>
    {'<label class="swg-check"><input type="checkbox" data-toggle="swg-show-up"> Show upgrade costs</label>' if has_up else ''}
    <output data-count aria-live="polite"></output>
  </div>
</div>

<div class="swg-table" markdown="0">
<table id="swg-units" class="swg-stack">
<thead><tr><th>Character</th><th>Costume</th>{'<th>Shape</th>' if has_shape else ''}{'<th>Grade</th>' if has_grade else ''}{'<th>Tags</th>' if has_tags else ''}<th class="num">Price <span class="swg-up__key">on sale, sells for</span></th>{_upgrade_head() if has_up else ''}</tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table>
</div>
"""


def parse_shape(shape: str) -> list[str] | None:
    """Text footprint -> padded rows. "##./.##" is two rows; "#" filled, "." empty. None if invalid."""
    rows = [r.strip() for r in str(shape).split("/") if r.strip()]
    if not rows or any(set(r) - {"#", "."} for r in rows) or "#" not in "".join(rows):
        return None
    width = max(len(r) for r in rows)
    return [r.ljust(width, ".") for r in rows]


def shape_svg(shape: str, label: str, cell: int = 20, gap: int = 4) -> str:
    """Footprint grid in the style of the in-game Codex: a black frame, filled squares
    light and empty squares dark, every square separated by the frame colour."""
    rows = parse_shape(shape)
    if not rows:
        return ""
    # cell and gap are px; the gap doubles as the frame width. Tiles use 20/4, unit rows 10/2.
    cols = len(rows[0])
    w = cols * cell + (cols + 1) * gap
    h = len(rows) * cell + (len(rows) + 1) * gap
    rects = "".join(
        f'<rect class="{"on" if ch == "#" else "off"}" x="{gap + c * (cell + gap)}" y="{gap + r * (cell + gap)}" '
        f'width="{cell}" height="{cell}"/>'
        for r, row in enumerate(rows) for c, ch in enumerate(row))
    return (f'<svg class="swg-shape" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{e(label)} footprint, {sum(r.count("#") for r in rows)} squares">'
            f'<rect class="frame" width="{w}" height="{h}"/>{rects}</svg>')


def _img(src: str, alt: str, cls: str) -> str:
    return f'<img class="{cls}" src="{e(src)}" alt="{e(alt)}" loading="lazy">'


def _price_cells(p: int, rid: str) -> str:
    return (f'<td class="num swg-price" data-label="Price">{p}</td>'
            f'<td class="num swg-price" data-label="On sale">{sale_price(p)}</td>'
            f'<td class="num swg-price" data-label="Sells for">{sell_price(p, rid)}</td>')


def _unit_price_cell(p: int, uid: str) -> str:
    """Units table: price in bold with the sale and sell values under it, in one column."""
    return (f'<td class="num swg-unit-price" data-label="Price"><b>{p}</b>'
            f'<span class="swg-price__sub">sale {sale_price(p)}, sells {sell_price(p, uid)}</span></td>')


def _upgrade_head() -> str:
    return '<th class="swg-up">Upgrades <span class="swg-up__key">+1 to +5, total</span></th>'


def _upgrade_cells(up) -> str:
    """One cell: the five upgrade costs in a row, then the total to reach +5."""
    if not up:
        return '<td class="swg-up swg-up--none" data-label="Upgrades">–</td>'
    steps = "".join(f'<span title="+{i}">{n}</span>' for i, n in enumerate(up, 1))
    return (f'<td class="swg-up" data-label="Upgrades"><span class="swg-up__steps" aria-label="+1 to +5: {", ".join(map(str, up))}">{steps}</span>'
            f'<span class="swg-up__total" title="Total to +5">{sum(up)}</span></td>')


def _table_page(cat: Catalog, title: str, desc: str, fname: str, head: str, rows: list[str], note: str = "",
                table_class: str = "", icon: str = "") -> str:
    return f"""---
title: {title}
description: {desc}
{f"icon: {icon}" if icon else ""}
---

# {title}

{_staleness(cat, fname)}
{note}
<div class="swg-table" markdown="0">
<table{f' class="{table_class}"' if table_class else ''}>
<thead><tr>{head}<th class="num">Price</th><th class="num">On sale</th><th class="num">Sells for</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table>
</div>
"""


def tiles_page(cat: Catalog, images: dict[str, str]) -> str:
    """Name, tile artwork, then footprint. images maps tile id -> image path from the site root."""
    has_effect = any(t.get("effect") for t in cat.tiles.values())
    rows = []
    for tid, t in sorted(cat.tiles.items(), key=lambda kv: kv[1]["name"]):
        art = (_img("../" + images[tid], t["name"], "swg-tile-img") if tid in images
               else '<span class="swg-missing">No image yet</span>')
        shape = shape_svg(t.get("shape") or "", t["name"]) or '<span class="swg-missing">Not set</span>'
        rows.append(f'<tr id="{tid}"><td class="swg-tile-name">{e(t["name"])}</td>'
                    f'<td class="swg-fit swg-tile-art">{art}</td><td class="swg-fit swg-tile-shape">{shape}</td>'
                    + (f'<td>{rich(t.get("effect") or "")}</td>' if has_effect else "")
                    + _price_cells(t["price"], tid) + "</tr>")
    head = '<th>Name</th><th>Tile</th><th>Shape</th>' + ("<th>Effect</th>" if has_effect else "")
    return _table_page(cat, "Tiles", "Every tile with its artwork, footprint, price and sell value.", "tiles.yaml", head, rows,
                       table_class="swg-stack", icon="lucide/grid-2x2")


def gear_page(cat: Catalog, images: dict[str, str]) -> str:
    has_effect = any(g.get("effect") for g in cat.gear.values())
    rows = []
    for gid, g in sorted(cat.gear.items(), key=lambda kv: kv[1]["name"]):
        icon = (_img("../" + images[gid], "", "swg-gear-icon") if gid in images
                else '<span class="swg-gear-icon swg-gear-icon--empty" aria-hidden="true"></span>')
        rows.append(f'<tr id="{gid}"><td class="swg-gear-name"><span class="swg-named">{icon}<span>{e(g["name"])}</span></span></td>'
                    + (f'<td class="swg-effect">{rich(g.get("effect") or "")}</td>' if has_effect else "")
                    + _price_cells(g["price"], gid) + "</tr>")
    head = "<th>Name</th>" + ("<th>Effect</th>" if has_effect else "")
    return _table_page(cat, "Gear", "Every gear piece with its icon, effects, price and sell value.", "gear.yaml", head, rows,
                       table_class="swg-stack", icon="lucide/shield")


def statuses_page(cat: Catalog, images: dict[str, str]) -> str:
    """images maps status id -> icon path from the site root."""
    def icon(sid: str) -> str:
        return (f'<img class="swg-status__icon" src="../{e(images[sid])}" alt="">' if sid in images
                else '<span class="swg-status__icon swg-status__icon--empty" aria-hidden="true"></span>')

    def block(kind: str) -> str:
        items = [(sid, st) for sid, st in cat.statuses.items() if st["kind"] == kind]
        return "\n".join(f'<div class="swg-status swg-status--{kind}"><dt>{icon(sid)}<span>{e(st["name"])}</span></dt>'
                         f'<dd>{rich(st["effect"])}</dd></div>' for sid, st in items)
    return f"""---
title: Buffs and debuffs
description: Every buff and debuff in the Soul Wager and what one stack does.
icon: lucide/flask-conical
---

# Buffs and debuffs

All values are per stack. Write `[[Name]]` in any description or guide to show a status's icon there, with its name on hover.

## Buffs

<dl class="swg-statuses" markdown="0">
{block("buff")}
</dl>

## Debuffs

<dl class="swg-statuses" markdown="0">
{block("debuff")}
</dl>
"""


def seasons_page(cat: Catalog) -> str:
    parts = []
    for s in reversed(cat.seasons):
        if s.get("end"):
            span = f'{fmt_date(s["start"])} to {fmt_date(s["end"])}'
        elif s.get("expected_end"):
            span = f'{fmt_date(s["start"])} to about {fmt_date(s["expected_end"])}'
        else:
            span = f'From {fmt_date(s["start"])}'
        boards = "".join(f'<li>Board {b["number"]}: {e(b["name"])}' + (f' ({b["phases"]} phases)' if b.get("phases") else "") + "</li>"
                         for b in s["boards"]) or "<li>No boards recorded yet.</li>"
        changes = "".join(f"<li>{e(c)}</li>" for c in s["changes"])
        sources = " ".join(f'<a href="{e(u)}">source {i}</a>' for i, u in enumerate(s["sources"], 1))
        if s is cat.current_season:
            span += ", in progress"
        parts.append(f"""<section class="swg-season" markdown="0">
  <header><h2 id="{s['id']}">{e(s['name'])}</h2><p>{span}</p></header>
  <div class="swg-season__cols">
    <div><h3>Boards</h3><ul>{boards}</ul></div>
    <div><h3>What changed</h3><ul>{changes}</ul>{f'<p class="swg-sources">{sources}</p>' if sources else ''}</div>
  </div>
</section>""")
    return f"""---
title: Seasons
description: Every Soul Wager season, its boards and its balance changes.
icon: lucide/calendar-days
---

# Seasons

Each season runs about eight weeks. Runs lock for settlement at 15:00 UTC on the last day.

{chr(10).join(parts)}
"""


def season_card(cat: Catalog, prefix: str = "", strategy_link: bool = True) -> str:
    """Current-season block (home page, current season strategy). JS fills in the live countdown."""
    s = cat.current_season
    end = s.get("end") or s.get("expected_end")
    approx = "" if s.get("end") else "about "
    changes = "".join(f"<li>{e(c)}</li>" for c in s["changes"][:4])
    return f"""<section class="swg-now" markdown="0" data-season-start="{s['start'].isoformat()}" data-season-end="{end.isoformat() if end else ''}" data-approx="{1 if approx else 0}">
  <div class="swg-now__head">
    <h2>{e(s['name'])} is running</h2>
    <p class="swg-now__dates">Started {fmt_date(s['start'])}{f", ends {approx}{fmt_date(end)}" if end else ""}.</p>
    <p class="swg-now__countdown" data-countdown></p>
  </div>
  <div class="swg-now__changes"><h3>What changed</h3><ul>{changes}</ul><a href="{prefix}seasons/#{s['id']}">Full season notes</a>{f' · <a href="{prefix}guide/current-season/">Current season strategy</a>' if strategy_link else ''}</div>
</section>"""


# ---------- board planner ----------
def planner(cat: Catalog, guides: set[str], plain) -> str:
    """Mount point and data for the board planner (lib/javascripts/planner.js)."""
    import json
    data = {
        "grid": GRID,
        "season": cat.current_season["name"],
        "seasonId": cat.current_season["id"],
        "units": [{"id": uid, "name": cat.unit_label(uid), "price": u["price"], "grade": u.get("grade") or "",
                   "tags": u.get("tags") or [], "shape": u.get("shape") or "#", "guide": uid in guides}
                  for uid, u in cat.units.items() if u.get("shape") and parse_shape(u["shape"])],
        "tiles": [{"id": tid, "name": t["name"], "price": t["price"], "shape": t.get("shape") or "#",
                   "effect": plain(str(t.get("effect") or "")).strip()}
                  for tid, t in cat.tiles.items() if t.get("shape") and parse_shape(t["shape"])],
        "gear": [{"id": gid, "name": g["name"], "price": g["price"],
                  "effect": plain(str(g.get("effect") or "")).strip()} for gid, g in cat.gear.items()],
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<div id="swg-planner" class="swg-planner" markdown="0"><p class="swg-planner__nojs">The planner needs JavaScript.</p></div>\n'
            f'<script type="application/json" id="swg-planner-data">{blob}</script>')
