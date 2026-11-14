---
# Build template. Copy to lib/builds/<build-name>.md (lower case, dashes for spaces).
title: Build name
# One line, shown in the Builds list and in search results.
description: What the build does, in one line.
# false = theorycraft, worked out from item text and not played yet.
# true  = you've cleared a board with it. The Builds list shows "Theorycraft" or "Tested".
tested: false
---

# Build name

<!-- Two or three sentences: the win condition, and why it beats the current season's boards.
These comments are hidden on the site. -->

What the build is trying to do, and why it works.

## Core

<!-- The team that makes the build, drawn as a team card: one column per member (role chip,
name, portrait or footprint, grade, price, note, gear), the tiles in a row underneath, and the
total in the header. Delete any line you don't need; only unit and tile are required.

  name, summary   title and one line under it
  context         optional, small text above the name
  season          the season it's written for
  members         the units, in the order they show on the card
    unit          unit id from content/units.yaml
    role          the chip above the unit, like "Poison / Attacker". Default: Attacker,
                  Support or Defender from the unit's tags
    archetype     chip colour: dps (red), support (green) or tank (blue). Default: from tags
    note          one short line under the unit
    gear          gear ids from content/gear.yaml
    at, turn      optional: where it stands on the 7x7 board, [row, column] counted from 1
                  at the top left (the top-left corner of the rectangle around the
                  footprint), and how many quarter turns clockwise it's rotated
  tiles           the tiles
    tile          tile id from content/tiles.yaml
    count         how many, if more than one
    note          one short line
    at, turn      optional, as above; for several copies, a list: at: [[1, 1], [5, 5]]
  notes           a tip at the bottom of the card
  total: false    hides the token total, for "pick one of these" lists

Give pieces an "at" and the card draws the board; units must stand on tiles. The easiest
way to get positions is the Board planner (Tools): lay out the board, press "Copy board
block" and paste it here. -->

```board
name: Build name
context: Optional context
season: s3
summary: One line under the name.
members:
  - unit: liatris-rodevs-star
    role: Main attacker
    note: Only attacker. Every token in gear goes here.
    gear: [knights-sword]
    at: [1, 1]
  - unit: celia-the-curse
    role: Poison / Debuffer
    note: On the Curse Tile, for extra debuffs.
    at: [4, 3]
tiles:
  - tile: basic-tile
    at: [1, 1]
  - tile: protection-tile
    note: 15 Energy Guard at battle start.
    at: [3, 1]
  - tile: curse-tile
    at: [4, 2]
notes: Optional tip shown at the bottom of the card.
```

## Shop plan

<!-- What to buy, phase by phase. Keep each cell short. -->

| Phases | Buy | Skip |
|---|---|---|
| 1 to 5 | Cheap tiles, the core debuffer | Rerolls |
| 6 to 10 | The damage dealer, first gear | Second attacker |
| 11 to 15 | Upgrades to the stopping points | Anything off-plan |

## Positioning

<!-- Footprints, which tiles go under which unit. Targeting ignores position, so this is
about fitting pieces and tile bonuses. -->

## Strengths and weaknesses

<!-- What it beats, what beats it, and how to tell from View Formation. -->

- **Beats:** boards that can't kill before 50 seconds.
- **Struggles against:** heavy Cleanse.

## Swap-ins

<!-- Units or gear that fill the same job when the shop doesn't offer the core piece. -->

## Pairs well with

<!-- Links to other builds this one mixes with, like [Poison stack](poison-stack.md). -->
