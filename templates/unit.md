---
# Unit guide template.
# Create a page with:  uv run swg-new-unit <unit-id>
# (or copy this file to lib/units/<unit-id>.md; the file name must equal the unit id).
#
# The page title, grade, tags, footprint, upgrade costs and price all come from
# content/units.yaml, so don't repeat them here. Every field below except `unit`
# is optional: delete any you don't know yet and that part of the page disappears.
#
# Page order: header (name, tagline, grade, tags, roles, price) → summary
# (footprint and upgrade costs on the left; ranks, stopping points and your overview
# on the right) → your ## sections → example builds → suggested builds and
# works well with → example boards.
unit: celia-the-curse

# One line under the name, in italics. Also used in search results and link previews.
tagline: Cheap Curse support that fits almost any debuff board.

# Shown after the grade and tags. Any of: attacker, support, debuffer, healer, defender, utility.
roles: [debuffer, support]

# Rank boxes for damage and support. tier is S, A, B, C, D or F;
# note is a few words. For more than one rank in a box, use a list:
#   damage: [{ tier: D, note: Early game }, { tier: B, note: Fully upgraded }]
ranks:
  damage:  { tier: C, note: Chip damage only }
  support: { tier: A, note: Poison on a budget }

# Upgrade levels worth stopping at (0 to 5), and an optional note under them.
stopping_points: [0, 3, 5]
stopping_note: +3 is where the Poison chance gets reliable.

# Example builds. Each becomes its own section with three columns: Tiles, Gear and
# Partner units (ids from content/), drawn with their footprints or icons and prices,
# plus the total. Any entry can carry a short note shown under it:
#   gear: [knights-necklace, { id: mercenary-staff, note: Any staff }]
builds:
  - name: Poison support
    tiles: [curse-tile]
    tiles_note: Or any tile that fits
    gear: [{ id: knights-necklace, note: Curse only }]
    with: [{ id: liatris-rodevs-star, note: Or Rubia }]
    note: The default. Put her on the Curse Tile and let Liatris do the hitting.
  - name: Budget filler
    gear: [mercenary-staff]
    note: When the shop gives you nothing better, she still adds 3 Poison at battle start.

# Build pages this unit belongs in (file names in lib/builds/, without .md).
# Entries can carry a note.
suggested_builds: [{ id: poison-stack, note: Her best board }]

# Units that pair well, drawn with their footprint and grade. Entries can carry a note.
works_well_with: [liatris-rodevs-star, { id: rubia-thorn-of-the-desert, note: Cheaper }, refithea-pure-white-blessing]
works_well_with_note: Anything that applies Poison.
---

<!-- Overview: text before the first ## heading appears next to the footprint, under the
ranks. Two or three sentences on what the unit is for. These comments are hidden on the site. -->

A 4-token Curse unit that turns any gear into Poison. Buy her early and build around one real damage dealer.

## Effect

<!-- Copy the unit's effect from its Codex card. Each line shows as its own line;
use **bold** for condition lines, "- " for bullets, and [[Poison]] for status icons. -->

**Every Cooldown:**
Apply 1 [[Poison]] to the opponent.

## How to Play

<!-- Every ## heading becomes its own full-width section. Use ### for subsections. -->

Put her on a Curse Tile and stop thinking about her. She does her job from any position.

## Teambuilding

She belongs in debuff boards next to one real damage dealer. She isn't worth a slot in a burst board, where every token should go into the attacker.

<!--
Optional sections, add any you need:
  ## Placement       footprint tips, tile bonuses, which tiles she wants under her
  ## Upgrades        what changes at each stopping point
  ## Counters        what beats her and what to do about it
  ## Season notes    changes from balance patches, newest first

Example boards: a ```board block anywhere on this page is moved to an "Example boards"
section at the end. See templates/build.md for the fields.
-->
