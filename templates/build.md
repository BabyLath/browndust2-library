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

<!-- The pieces that make the build, drawn as a team card:
one column per unit (role chip, name, footprint, grade, price, note, gear), the tiles in a
row underneath, and the total in the header.

  context   optional, small text above the name (a mode or progression stage)
  floor     optional, 7 rows of 7: where the tiles go. "." is empty, a letter per piece.
  layout    optional, 7 rows of 7: where the units stand. With floor, units stand on tiles.
            Either one draws the 7x7 board in the card's header. The Board planner
            (Tools) writes both for you: lay out the board and press "Copy board block".
  pieces    each letter's unit or tile id
  gear      a unit's letter -> gear ids
  roles     a unit's letter -> the short chip above it (default: Attacker, Support or
            Defender, from its tags). Chip colour follows the tags too.
  details   any letter -> one short note under that unit or tile
  notes     a tip at the bottom of the card
  total     false hides the token total, for "pick one of these" lists -->

```board
name: Build name
context: Optional context
season: s3
summary: One line under the name.
floor: |
  AA.....
  AA.....
  P......
  .CC....
  CC.....
  .......
  .......
layout: |
  D......
  DD.....
  D......
  .EE....
  .......
  .......
  .......
pieces:
  A: basic-tile
  P: protection-tile
  C: curse-tile
  D: liatris-rodevs-star
  E: celia-the-curse
gear:
  D: [knights-sword]
roles:
  D: Main attacker
  E: Poison / Debuffer
details:
  D: Only attacker. Every token in gear goes here.
  E: On the Curse Tile, for extra debuffs.
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
