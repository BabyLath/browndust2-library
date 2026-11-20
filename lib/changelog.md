---
title: Changelog
description: What changed on this site.
icon: lucide/history
---

# Changelog

Newest first. Add a line here whenever you update data or pages.

## November 15, 2026

- New command `uv run swg-new-season` starts the next season in one step and keeps last season's strategy page under Reference → Past season strategies.
- Lists (the Units table and the planner's piece list) show still portraits; animations play on guide pages, team cards and the planner board. Visitors who've turned on "reduce motion" on their device see still portraits everywhere.

## November 14, 2026

- New command `uv run swg-portraits`: trims, resizes and centres unit portraits to 128×128 AVIF, keeping animations. Portraits now show whole, never cropped, everywhere they appear.
- Board planner on phones: the list of units and tiles is a drawer along the bottom of the screen, so the board stays in view while you drag. It tucks itself away while you place a piece.
- New page-not-found page with the main pages and a "Maybe you meant" guess for old or mistyped links.
- Optional visitor stats with GoatCounter (off until you add a code in `zensical.toml`).
- Every deploy now checks every link and image and runs browser tests of the planner and tables first; a failure stops the deploy instead of breaking the live site.
- Unit guides: Suggested builds fills itself. It lists every team card on the site with that unit, grouped by page, and each card name links straight to the card. The `suggested_builds` field is gone.
- **Add to planner** on unit guides and in every Units table row. It puts the unit in the planner's To place tray without leaving the page; an open planner tab picks it up straight away.
- Board planner: **Saved boards**, to keep several boards in your browser and switch between them.
- Board planner: **Save image** downloads a picture of the board with portraits, total and gear.
- Board planner: Undo now also brings back the board's name and budget, and a plan link pasted into the address bar while the planner is open loads it.
- Gear and Tiles pages: search (names and effects), max price and sorting, like the Units table.
- Board planner: Copy link, Copy board block and Save image show "✓ Copied" or "✓ Saved" on the button, with a note beside the buttons.
- Board planner: Undo and Redo buttons, plus Ctrl+Z, Ctrl+Shift+Z and Ctrl+Y. Every change to the pieces can be stepped back, and opening a shared link keeps your own board one Undo away.
- Team cards have an **Open in planner** link. Pieces without a board position wait in a To place tray above the planner board.
- Link previews: pasting a page into Discord, Reddit or X shows the site card, or the unit's portrait and tagline for unit guides.
- Units table: click a column header to sort by it, or use the Sort menu, which also works on phones.
- The home page's browser tab shows just the site name.

## November 12, 2026

- Removed the season check notices ("Checked for…", "Not yet checked…", "Out of date") and the season flag on Last updated dates.
- Removed the "Has a guide" filter from the Units table.
- Board planner shows unit portraits on the board, in the unit list, in the piece details and in the list of placed pieces.
- Bigger portraits in the Units table.
- Board planner pieces look like the home page board: raised, rounded tiles with units standing on them, and selected pieces lift.
- Board planner: moving a tile with units on it now carries the units along, plus any other tiles those units stand on.
- Board planner chibis are all one size and stand on a single square of the unit's footprint: the middle one where there is one, otherwise the first.
- Board planner: drag a piece from the board onto the list to remove it, with Undo. Copy link now always includes the plan, even after scrolling the page.
- Board planner: no more letters on the pieces. The list of placed pieces shows each unit's colour and each tile's shape instead.
- Board blocks use a list format: `members` (unit, role, note, gear) and `tiles` (tile, count, note), with optional `at` and `turn` for board positions. No more letter maps. Every board on the site was converted, and the Board planner exports the new format.

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
