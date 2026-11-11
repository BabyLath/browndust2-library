"""HTML snippets injected into generated Markdown pages.

All markup that repeats across pages lives here, so content files stay
plain Markdown + YAML.
"""
from __future__ import annotations

import datetime as dt
import html

from .catalog import Catalog

e = html.escape
GRID = 7


# ---------- shop math (mirrors lib/guide/board-shop.md) ----------
def sale_price(p: int) -> int:
    return -(-p // 2)  # ceil


def sell_price(p: int, pid: str = "") -> int:
    return 1 if pid == "protection-tile" else max(2, p // 2)


def fmt_date(d: dt.date) -> str:
    return f"{d:%b} {d.day}, {d.year}"


# ---------- small pieces ----------
def grade_badge(g: str) -> str:
    return f'<span class="swg-grade" data-grade="{e(g.lower())}">{e(g)}</span>' if g else ""


def tag_pills(tags) -> str:
    return "".join(f'<span class="swg-tag">{e(t)}</span>' for t in tags or [])


def unit_link(cat: Catalog, uid: str, guides: set[str], prefix: str) -> str:
    label = e(cat.unit_label(uid))
    return f'<a href="{prefix}units/{uid}/">{label}</a>' if uid in guides else label


# ---------- unit guide header ----------
def unit_card(cat: Catalog, uid: str, fm: dict, guides: set[str]) -> str:
    u = cat.units[uid]
    p = u["price"]
    rating = fm.get("rating")
    role = fm.get("role")
    wwith = fm.get("works_well_with") or []
    chips = "".join(f"<li>{unit_link(cat, w, guides, '../../')}</li>" for w in wwith if w in cat.units)
    return f"""
<div class="swg-unit-card" markdown="0">
  <div class="swg-unit-card__main">
    <p class="swg-unit-card__meta">{grade_badge(u.get('grade') or '')}{f'<span class="swg-role">{e(role)}</span>' if role else ''}{tag_pills(u.get('tags'))}</p>
    {f'<p class="swg-unit-card__summary">{e(fm["summary"])}</p>' if fm.get('summary') else ''}
  </div>
  <dl class="swg-unit-card__stats">
    {f'<div class="swg-rating" data-rating="{e(str(rating))}"><dt>Rating</dt><dd>{e(str(rating))}</dd></div>' if rating else ''}
    <div><dt>Price</dt><dd>{p}</dd></div>
    <div><dt>On sale</dt><dd>{sale_price(p)}</dd></div>
    <div><dt>Sells for</dt><dd>{sell_price(p)}</dd></div>
  </dl>
  {f'<div class="swg-unit-card__pairs"><p>Works well with</p><ul>{chips}</ul></div>' if chips else ''}
</div>
"""


# ---------- board fence ----------
def board(cat: Catalog, spec: dict, guides: set[str], prefix: str) -> str:
    rows = [r.replace(" ", "") for r in str(spec.get("layout") or "").strip("\n").splitlines()]
    pieces: dict[str, str] = {str(k): str(v) for k, v in (spec.get("pieces") or {}).items()}
    gear: dict[str, list] = {str(k): (v if isinstance(v, list) else [v]) for k, v in (spec.get("gear") or {}).items()}

    def kind_of(pid: str) -> str:
        return "unit" if pid in cat.units else "tile" if pid in cat.tiles else "?"

    # palette index per unit letter so each unit gets a distinct hue
    unit_letters = [k for k, v in pieces.items() if kind_of(v) == "unit"]
    seen: set[str] = set()
    cells = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == ".":
                cells.append('<span class="swg-cell"></span>')
                continue
            pid = pieces.get(ch, "")
            kind = kind_of(pid)
            hue = unit_letters.index(ch) % 6 if ch in unit_letters else 0
            # draw borders only where the neighbouring cell is a different piece
            edges = []
            if r == 0 or rows[r - 1][c] != ch: edges.append("t")
            if r == len(rows) - 1 or rows[r + 1][c] != ch: edges.append("b")
            if c == 0 or row[c - 1] != ch: edges.append("l")
            if c == len(row) - 1 or row[c + 1] != ch: edges.append("r")
            label = ""
            if ch not in seen:
                seen.add(ch)
                label = f'<b>{e(ch)}</b>'
            cells.append(f'<span class="swg-cell swg-cell--{kind} swg-hue-{hue} {" ".join("e-" + x for x in edges)}">{label}</span>')

    total = 0
    legend = []
    for letter, pid in pieces.items():
        kind = kind_of(pid)
        if kind == "unit":
            u = cat.units[pid]
            name, price = unit_link(cat, pid, guides, prefix), u["price"]
        elif kind == "tile":
            name, price = e(cat.tiles[pid]["name"]), cat.tiles[pid]["price"]
        else:
            continue
        total += price
        gtxt = ""
        for gid in gear.get(letter, []):
            if gid in cat.gear:
                total += cat.gear[gid]["price"]
                gtxt += f'<span class="swg-gear">{e(cat.gear[gid]["name"])} <i>{cat.gear[gid]["price"]}</i></span>'
        hue = unit_letters.index(letter) % 6 if letter in unit_letters else 0
        legend.append(f'<li class="swg-legend--{kind}"><span class="swg-key swg-cell--{kind} swg-hue-{hue}">{e(letter)}</span>'
                      f'<span class="swg-legend__name">{name}{gtxt}</span><span class="swg-legend__price">{price}</span></li>')

    season = cat.season(str(spec.get("season", ""))) if spec.get("season") else None
    head = f'<p class="swg-build__title">{e(str(spec.get("name", "Untitled build")))}</p>'
    sub = []
    if season: sub.append(e(season["name"]))
    if rows:
        sub.append(f"{total} tokens on the board")
    board_html = (f'<div class="swg-build__board" role="img" aria-label="7 by 7 board layout for {e(str(spec.get("name", "build")))}">{"".join(cells)}</div>'
                  if rows else "")
    return f"""
<figure class="swg-build{'' if rows else ' swg-build--list'}" markdown="0">
  {board_html}
  <figcaption>
    {head}
    {f'<p class="swg-build__sub">{" / ".join(sub)}</p>' if sub else ''}
    {f'<p>{e(str(spec["summary"]))}</p>' if spec.get('summary') else ''}
    <ul class="swg-legend">{''.join(legend)}</ul>
    {f'<p class="swg-build__notes">{e(str(spec["notes"]))}</p>' if spec.get('notes') else ''}
  </figcaption>
</figure>
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


def units_page(cat: Catalog, guides: set[str]) -> str:
    has_grade = any(u.get("grade") for u in cat.units.values())
    has_tags = any(u.get("tags") for u in cat.units.values())
    rows = []
    for uid, u in sorted(cat.units.items(), key=lambda kv: (kv[1]["character"], kv[1]["costume"])):
        p = u["price"]
        has = uid in guides
        name = f'<a href="{uid}/">{e(u["costume"])}</a>' if has else e(u["costume"])
        rows.append(
            f'<tr data-search="{e((u["character"] + " " + u["costume"]).lower())}" data-price="{p}" '
            f'data-grade="{e(u.get("grade") or "")}" data-tags="{e("|".join(u.get("tags") or []))}" data-guide="{int(has)}">'
            f'<td>{e(u["character"])}</td><td>{name}</td>'
            + (f'<td>{grade_badge(u.get("grade") or "")}</td>' if has_grade else "")
            + (f'<td>{tag_pills(u.get("tags"))}</td>' if has_tags else "") +
            f'<td class="num">{p}</td><td class="num">{sale_price(p)}</td><td class="num">{sell_price(p)}</td></tr>')
    grades = "".join(f'<option>{e(g)}</option>' for g in cat.meta.get("grades", []))
    tags = "".join(f'<option>{e(t)}</option>' for t in cat.meta.get("tags", []))
    return f"""---
title: Units
description: Every unit piece in the Soul Wager Battle Shop with price, sale price and sell value.
hide:
  - toc
---

# Units

{_staleness(cat, "units.yaml")}
Prices are in Soul Tokens. **On sale** is the 10%-chance half-price offer. **Sells for** is what you get back. Names with a link have a full guide.

<div class="swg-filter" data-target="swg-units" markdown="0">
  <label>Search<input type="search" data-f="q" placeholder="Character or costume"></label>
  {f'<label>Grade<select data-f="grade"><option value="">Any</option>{grades}</select></label>' if has_grade else ''}
  {f'<label>Tag<select data-f="tag"><option value="">Any</option>{tags}</select></label>' if has_tags else ''}
  <label>Max price<input type="number" data-f="max" min="1" max="30" placeholder="Any"></label>
  <label class="swg-check"><input type="checkbox" data-f="guide"> Has a guide</label>
  <output data-count></output>
</div>

<div class="swg-table" markdown="0">
<table id="swg-units">
<thead><tr><th>Character</th><th>Costume</th>{'<th>Grade</th>' if has_grade else ''}{'<th>Tags</th>' if has_tags else ''}<th class="num">Price</th><th class="num">On sale</th><th class="num">Sells for</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table>
</div>
"""


def simple_table_page(cat: Catalog, title: str, desc: str, fname: str, rows: dict, cols: list[str]) -> str:
    head = "".join(f"<th>{c.title()}</th>" for c in cols)
    body = []
    for rid, r in sorted(rows.items(), key=lambda kv: kv[1]["name"]):
        p = r["price"]
        extra = "".join(f"<td>{e(str(r.get(c) or '—'))}</td>" for c in cols)
        body.append(f'<tr data-search="{e(r["name"].lower())}" data-price="{p}"><td>{e(r["name"])}</td>{extra}'
                    f'<td class="num">{p}</td><td class="num">{sale_price(p)}</td><td class="num">{sell_price(p, rid)}</td></tr>')
    return f"""---
title: {title}
description: {desc}
---

# {title}

{_staleness(cat, fname)}
<div class="swg-table" markdown="0">
<table>
<thead><tr><th>Name</th>{head}<th class="num">Price</th><th class="num">On sale</th><th class="num">Sells for</th></tr></thead>
<tbody>
{chr(10).join(body)}
</tbody></table>
</div>
"""


def statuses_page(cat: Catalog) -> str:
    def block(kind: str) -> str:
        items = [s for s in cat.statuses.values() if s["kind"] == kind]
        return "\n".join(f'<div class="swg-status swg-status--{kind}"><dt>{e(s["name"])}</dt><dd>{e(s["effect"])}</dd></div>' for s in items)
    return f"""---
title: Buffs and debuffs
description: Every buff and debuff in the Soul Wager and what one stack does.
---

# Buffs and debuffs

All values are per stack.

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
        current = ' swg-season--current' if s is cat.current_season else ""
        parts.append(f"""<section class="swg-season{current}" markdown="0">
  <header><h2 id="{s['id']}">{e(s['name'])}</h2><p>{span}</p></header>
  <div class="swg-season__cols">
    <div><h3>Boards</h3><ul>{boards}</ul></div>
    <div><h3>What changed</h3><ul>{changes}</ul>{f'<p class="swg-sources">{sources}</p>' if sources else ''}</div>
  </div>
</section>""")
    return f"""---
title: Seasons
description: Every Soul Wager season, its boards and its balance changes.
---

# Seasons

Each season runs about eight weeks. Runs lock for settlement at 15:00 UTC on the last day.

{chr(10).join(parts)}
"""


def season_card(cat: Catalog) -> str:
    """Current-season block for the home page. JS fills in the live countdown."""
    s = cat.current_season
    end = s.get("end") or s.get("expected_end")
    approx = "" if s.get("end") else "about "
    changes = "".join(f"<li>{e(c)}</li>" for c in s["changes"][:4])
    return f"""<section class="swg-now" markdown="0" data-season-start="{s['start'].isoformat()}" data-season-end="{end.isoformat() if end else ''}" data-approx="{1 if approx else 0}">
  <div class="swg-now__head">
    <p class="swg-now__label">Current season</p>
    <h2>{e(s['name'])}</h2>
    <p class="swg-now__dates">Started {fmt_date(s['start'])}{f", ends {approx}{fmt_date(end)}" if end else ""}</p>
    <p class="swg-now__countdown" data-countdown></p>
  </div>
  <div class="swg-now__changes"><p>What changed</p><ul>{changes}</ul><a href="seasons/#{s['id']}">Full season notes</a></div>
</section>"""
