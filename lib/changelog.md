---
title: Changelog
description: What changed on this site.
icon: lucide/history
---

# Changelog

Newest first. Add a line here whenever you update data or pages.

## November 9, 2026

- New unit guide layout: a large header with tagline and roles, footprint and upgrade costs in the left column, tier-coloured rank boxes, stopping points, full-width sections, example builds in Tiles, Gear and Partner units columns, Suggested builds, Works well with, and Example boards.
- Board blocks are drawn as team cards: a role chip, footprint, grade, price, note and gear for each unit, with the tiles listed underneath. New fields: `context` and `details`.
- New unit and build templates to match.
- Removed the repository link from the page header and the edit button from pages.
- Unit portraits from `lib/images/portraits/<unit-id>.avif`: on the unit's guide (footprint moves below it), as a thumbnail in the Units table, in Partner units and Works well with, and on board cards.

## November 8, 2026

- Sidebar has a Tools section with the Board planner and Calculators.
- Board planner: drag pieces from the list onto the board and drag placed pieces to move them, with mouse or touch.
- New tool: Board planner. Place tiles, units and gear on the 7×7 board, see the cost against your Soul Tokens, share the plan as a link or copy it as a board block.
- Board blocks can draw units standing on tiles with a separate `floor:` layer.
- Every page shows when it was last updated, flagged if that was before the current season.
- "Your first run" quick start on the Guide's front page.
- Alea Chip shop page: the two currencies explained, tables for chips per Board and shop prices (to be filled in), and what to buy first.
- New page: Current season strategy. The team, what to buy first, a shop cheat sheet and counters for Season 3, without the theory. Linked from the season box on the home page.
- Pages can set `season:` in front matter. Once a newer season starts, the check warns and the page shows an "Out of date" notice.
- Strategy page rewritten as "How to build a team": win conditions, four team types with example boards, Stamina, counters, gear by tag, spending, tiles and common mistakes.
- Board blocks can label each piece's role (`roles:`) and show a total without a layout (`total: true`).

## November 6, 2026

- Units: grades, tags, footprints and upgrade costs filled in for all 133 units, including the new Helena (B-Rank Idol).
- Grades use the seven Codex grades, each with its own badge colour.
- Units table: price, sale and sell values share one column, and upgrade costs fit in one column when switched on.
- Energy Guard wall and lockdown builds now use Support-tagged units where the gear needs one.
- Unit prices checked for Season 3.
- Every page has a sidebar icon.
- New unit guide format: tagline, damage and support ranks, upgrade stopping points, example builds and pairings. New build template with a shop plan and strengths and weaknesses.
- Builds list shows whether each build is tested or theorycraft.

## November 5, 2026

- Tiles: new artwork and footprint columns, effects and shapes for all nine tiles, checked for Season 3.
- Buffs and debuffs get icons, and `[[Name]]` shows a status icon inside any text. Added Energy Guard.
- Gear icons sit beside their names.
- Short pages drop the empty "On this page" column and use the full width.
- Unit tags get icons, shown on tag labels and with `[[Tag]]` or `[[Tag+]]` in any text.
- Units: upgrade costs for +1 to +5 replace the effect column. Effects move to each unit's own page.
- Search on phones now hides rows that don't match.
- Units get a footprint Shape column. Upgrade costs are hidden behind a "Show upgrade costs" switch, and the table has roomier rows.
- New builds: Energy Guard wall, One-attacker burst, Frost and Darkness lockdown. Poison stack gains a gear and tiles section. All marked Theorycraft until tested.

## November 4, 2026

- Renamed the site to BrownDust II Library.
- Light mode uses warm paper and dark ink; dark mode moved to a neutral charcoal.
- Dropped coloured stripes, tinted cards, pill badges and hover motion. Sections are separated by rules.
- Fonts are now bundled with the site.

## November 2, 2026

- Moved the site to Zensical with YAML catalogs and a validation step.
- Added the Seasons page covering Trial Seasons 1 to 3.
- Added unit guides for the three units with Season 3 fixes.
- Unit prices still reflect the BD2 Tactical Compendium table. Season 3 cost changes aren't in yet.
