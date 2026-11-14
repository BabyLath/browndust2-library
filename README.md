# BrownDust II Library

Fan guides and data for Brown Dust 2. It currently covers **The Soul Wager**: unit prices, builds, season notes and calculators.

Built with [Zensical](https://zensical.org). Content is Markdown in `lib/` and YAML catalogs in `content/`. A small Python package (`swg_site/`) validates everything, turns catalogs into pages, and runs the build.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then in this folder:

```
uv sync --locked
```

## Commands

| Command | What it does |
|---|---|
| `uv run swg-serve` | Live preview at http://localhost:8000. Saving a file in `lib/` or `content/` updates the page. |
| `uv run swg-check` | Validates catalogs, pages and board fences. Run it before you commit. |
| `uv run swg-build` | Production build into `site/`. Stops if `swg-check` finds errors. |
| `uv run swg-new-unit <id>` | Creates `lib/units/<id>.md` from the template, ready for the unit's effect and guide. |

`swg-check` prints the file and line of every problem and suggests the closest id when you mistype one:

```
ERROR   lib/builds/poison-stack.md:10  piece A: 'celia-the-cures' isn't a unit or tile. Did you mean 'celia-the-curse'?
WARNING lib/images/portraits  2 unit guide(s) have no portrait yet: dalvi-summer-vacation, justia-blood-glutton.
```

Errors stop the build. Warnings don't; they point out things worth filling in.

Never edit `generated-docs/`, `site/` or `.zensical.generated.toml`. They're rebuilt every time.

## Deploying to GitHub Pages

1. Create the repo `github.com/babylath/browndust2-library` and push this folder to it. The site will be at `https://babylath.github.io/browndust2-library/`. If you pick a different repo name, update `site_url`, `repo_url`, `repo_name` and the social link in `zensical.toml`, and the issue link in `lib/index.md`.
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Every push to `main` runs `.github/workflows/deploy.yml`, which builds and publishes. Pull requests run `check.yml` instead, so a broken id can't reach `main`.

## Where things live

| You want to change | Edit |
|---|---|
| Unit prices, grades, tags, upgrade costs | `content/units.yaml` |
| A unit's effect | `## Effect` on its page, `lib/units/<unit-id>.md` |
| Gear and tiles | `content/gear.yaml`, `content/tiles.yaml` |
| Buffs and debuffs | `content/statuses.yaml` |
| Seasons, boards, balance notes | `content/seasons.yaml` |
| Allowed grades, tags, roles, ratings | `content/meta.yaml` |
| Guide pages | `lib/guide/*.md` |
| A unit guide | `lib/units/<unit-id>.md` (copy `templates/unit.md`) |
| A build | `lib/builds/<name>.md` (copy `templates/build.md`) |
| Home page | `lib/index.md` |
| Colours and fonts | top of `lib/styles/extra.css`. Font files live in `lib/fonts/` (self-hosted, so previews and the live site always match) |
| Site name, links, footer | `zensical.toml` |
| A page's sidebar icon | `icon: lucide/<name>` in its front matter; names from [lucide.dev](https://lucide.dev/icons) |
| Current season strategy | `lib/guide/current-season.md`. Rewrite it each season |
| Alea Chip rewards and shop prices | `content/rewards.yaml`. Blank values show as ? on the page and the check lists them |
| Board planner | Nothing to edit. It reads units, tiles and gear from `content/` on every build |
| Hover definitions for terms | `includes/abbreviations.md` |
| Buff and debuff icons | `lib/images/statuses/<status-id>.png` |
| Unit tag icons | `lib/images/tags/<tag>.png`, e.g. `close-range-attack.png` |
| Tile pictures | `lib/images/tiles/<tile-id>.png` (footprints come from `shape` in `content/tiles.yaml`) |
| Gear icons | `lib/images/gear/<gear-id>.png` |
| Unit portraits | `lib/images/portraits/<unit-id>.avif`, 168×200 or any image with that shape. Used on the unit's guide, as a thumbnail in the Units table, in Partner units and Works well with on other guides, on board cards, and in the Board planner. PNG or AVIF with a transparent background looks best on the planner board |
| Site changelog | `lib/changelog.md` |

The sidebar builds itself from these folders. Guide pages sort by `order:` in their front matter.

The right-hand "On this page" column only appears on pages with two or more `##` headings; on shorter pages it's hidden so tables get the full width. To control it yourself, set `hide: [toc]` (always hide) or `hide: []` (always show) in a page's front matter.

## Every new season

This is the routine that keeps the data current.

1. Add the season to the end of `content/seasons.yaml` with its `start`, an `expected_end`, and a `changes` line per balance note. Link the official notice under `sources`.
2. Set the previous season's `end`.
3. Update changed prices, add new units to `content/units.yaml`, and add any new grade to `content/meta.yaml`.
4. Rewrite `lib/guide/current-season.md` for the new season.
5. Add a line to `lib/changelog.md`.
6. `uv run swg-check`, then commit.

The home page countdown is worked out in the visitor's browser from the season dates, so it stays right between deploys. Only the dates themselves need a rebuild.

## Tile and gear images

Drop a picture into the matching folder and name it after the id in the catalog:

```
lib/images/tiles/curse-tile.png     -> Tile column on the Tiles page
lib/images/gear/knights-sword.png   -> icon beside the name on the Gear page
```

PNG, WebP, AVIF, JPG and SVG all work. Transparent PNGs look best. Gear icons are shown at 32×32 px, tile pictures at 56 px tall. To use a different file name, add `image: my-file.png` to that row in `content/tiles.yaml` or `content/gear.yaml`.

Each tile's `shape` field draws its footprint in the Shape column, styled like the in-game Codex: a black frame with filled squares in white and empty ones dark. Rows are split by `/`, `#` is a filled square and `.` an empty one. `"##/##"` is 2×2, `"####"` is 1×4, `"##/#."` is an L, `"##./.##"` is a Z. `swg-check` rejects anything else.

`swg-check` warns about items still missing a picture, and about files whose name doesn't match any id (with the closest id it can find).

## Multi-line descriptions

The `effect` of a tile, gear piece or status can span several lines. `gear.yaml` is already written in block style, so you only need to type under `effect: |`. Unit effects live on each unit's own page instead; see "Writing a unit guide". Write that entry in block style instead of the one-line `{ ... }` form, and put `|` after `effect:`:

```yaml
  - id: knights-sword
    name: "Knight's Sword"
    price: 6
    effect: |
      Equip on an Attacking Character.
      Close-range: +2 DMG.
      Long-range: +1 DMG.

      - Stacks with [[Strength]].
      - Cannot be equipped twice.
```

Each line shows as its own line, a blank line starts a new paragraph, and lines starting with `- ` become a bullet list. Indent every line of the text by the same amount, deeper than `effect:`. Other entries can stay on one line; both styles mix freely in the same file.

## Status and tag icons in text

Write a buff, debuff or unit tag as `[[Name]]` (or its id, `[[energy-guard]]`) anywhere: tile and gear effects, unit summaries, season notes, build notes or guide pages. It turns into that icon, and hovering shows its name. Add `+` to show the name beside the icon: `[[Curse+]]`. That's how the tag table on the Battle page is written. Until the status has an icon, its name appears in place with a dotted underline, so the sentence still reads.

```yaml
effect: "Upon Battle Start: Gain 15 [[Energy Guard]]."
```

Status icons live in `lib/images/statuses/<id>.png` and also show on the Buffs and debuffs page. Tag icons live in `lib/images/tags/<tag>.png`, named after the tag in lower case with dashes: `curse.png`, `close-range-attack.png`. They show on the Units table and unit guides as icons only, with the tag name on hover. A tag with no icon yet shows its name instead. To add a new status, add a row to `content/statuses.yaml`. `swg-check` rejects any `[[Name]]` it doesn't recognise and suggests the closest one. Text inside backticks is left alone, so you can still write about the syntax.

## Grades and tags

`grade` is one of the seven Codex grades in `content/meta.yaml`: Basic, Rare, Ancient, Heroic, Legendary, Mythical, Unique. Each gets its own badge colour (gray, green, blue, purple, red-orange, yellow, and a light-blue shimmer for Unique), set under "grade badges" in `lib/styles/extra.css`.

`tags` can be written as names or ids: `[Close-Range Attack, Curse]` and `[close-range-attack, curse]` both work. `utility` is accepted as another name for **Support**, since gear text calls those characters "Utility"; add more under `tag_aliases` in `content/meta.yaml`.

## Unit footprints

Each unit has a `shape`, written like a tile's: rows split by `/`, `#` for a filled square, `.` for an empty one. Copy it from the unit's Codex card.

```yaml
    shape: ".#./###/###/.#."
```

The Units table draws it in a Shape column (shown once any unit has one), and the unit's guide page draws it beside the upgrade costs.

## Upgrade costs

Each unit in `content/units.yaml` has an `upgrades` list: the cost of +1, +2, +3, +4 and +5, in that order.

```yaml
    upgrades: [2, 3, 4, 5, 6]
```

On the Units table they're hidden until a reader ticks **Show upgrade costs** (the choice is remembered in their browser); then they appear as five columns plus a **To +5** total. The unit's guide page always shows them in a small table. Leave it as `[]` until you know all five; `swg-check` rejects a list that isn't exactly five whole numbers.

## Writing a unit guide

```
uv run swg-new-unit levia-overheat
```

That creates `lib/units/levia-overheat.md` from `templates/unit.md`. A guide page reads from top to bottom:

1. **Header:** name, an italic tagline, then grade, tags and roles on one line, and the price.
2. **Summary:** the footprint and upgrade costs on the left. On the right are the rank boxes, stopping points and your overview (the text before the first `##`).
3. **Your sections:** every `##` heading becomes a full-width section, such as Effect, How to Play and Teambuilding.
4. **Example builds:** one section per build, with Tiles, Gear and Partner units columns.
5. **Suggested builds** and **Works well with.**
6. **Example boards:** any `board` block you write in the guide is moved here.

| Front matter | Shows as |
|---|---|
| `tagline` | Italic line under the name, also used in search results |
| `roles` | Debuffer, Support… after the grade and tags |
| `ranks.damage` / `ranks.support` | Rank boxes: a tier letter (S to F) coloured by tier, with a short note. A list gives several ranks in one box |
| `stopping_points`, `stopping_note` | Upgrade levels worth stopping at, like +0 · +3 · +5 |
| `builds` | Example build sections: `tiles`, `tiles_note`, `gear`, `with` (partner units) and `note` |
| `suggested_builds`, `suggested_builds_note` | Links to build pages, by file name in `lib/builds/` |
| `works_well_with`, `works_well_with_note` | Partner units with their footprint and grade |

Any entry in `tiles`, `gear`, `with`, `suggested_builds` or `works_well_with` can be an id or `{ id: …, note: … }`. The note shows under it in small italics.

Grade, tags, footprint, upgrade costs and price come from `content/units.yaml`. In the text, each line shows as its own line, `**bold**` marks condition lines and `[[Poison]]` shows an icon. Gear without an image in `lib/images/gear/` shows its initials until you add one.

**Portrait:** put the unit's art at `lib/images/portraits/<unit-id>.avif`, for example `lib/images/portraits/celia-the-curse.avif`. It fills the top of the left column, cropped from the top to a 168×200 shape, with the footprint moved to a small row under it. Until a guide has a portrait, the footprint takes its place, and `swg-check` lists the guides still missing one. AVIF keeps the file small; WebP, PNG and JPG also work if you have those instead.

Every field is optional, so a guide can start with just a tagline and grow. `swg-check` warns if the page still contains the template's example text or values.

## Writing a build

Copy `templates/build.md` to `lib/builds/<name>.md`. It lays out the sections a build page should cover: Core (the board), Shop plan by phase, Positioning, Strengths and weaknesses, Swap-ins and Pairs well with. Set `tested: true` once you've cleared a board with it; until then the Builds list labels it **Theorycraft**.

Boards are written as `board` blocks and drawn as team cards. The header holds the name, season, total cost and the 7×7 board. Below it is one column per unit with a role chip, name, footprint, grade, price, a note and its gear. On phones each unit becomes a row. The tiles are listed underneath.

````
```board
name: Poison stack
context: Optional, small text above the name
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
notes: Optional tip at the bottom of the card.
```
````

- **`members`** lists the units in the order they appear on the card. Only `unit` is required:
  - `role`: the chip above the unit, like `Poison / Attacker`. Without it the chip says Attacker, Support or Defender, based on the unit's tags.
  - `archetype`: the chip's colour, `dps` (red), `support` (green) or `tank` (blue). Without it the colour also follows the tags.
  - `note`: a short line under the unit.
  - `gear`: a list of gear ids.
- **`tiles`** lists the tiles. Only `tile` is required. Add `count` for several copies and `note` for a short line.
- **`at` and `turn`** are optional on any member or tile. `at` is the position on the 7×7 board as `[row, column]`, counted from 1 at the top left; it's the top-left corner of the rectangle around the piece's footprint after turning, which can be an empty corner for shapes like the Curse Tile. `turn` is how many quarter turns clockwise the piece is rotated. Several copies of a tile take a list: `at: [[1, 5], [7, 7]]`. If pieces have positions, the card draws the board in its header, and every unit needs tiles under it. Pieces without `at` are still listed, just not drawn.
- **Getting positions:** the easiest way is the [Board planner](https://babylath.github.io/browndust2-library/tools/planner/). Lay out the board, press **Copy board block** and paste it in; it writes `at` and `turn` for you.
- **`total: false`** hides the token total, for "pick one of these" lists.
- Put the block at the start of a line, not inside a list or quote.

`swg-check` reports mistakes with the piece's name: unknown ids (with a suggestion), misspelled keys, pieces that overlap or run off the board, and units standing on empty squares. The card shows a small letter next to each unit's name to match it to the board drawing. Those letters are assigned automatically; you never write them.

## Contributing

- **Found wrong data?** Open an issue with the "Data correction" form. A screenshot of the in-game shop or Codex is the fastest way to get it fixed.
- **Collaborators:** small fixes can be made directly in the file on GitHub. For anything bigger, clone, run `swg-serve`, edit, run `swg-check`, commit, push.
- **Everyone else:** fork, branch, make the change, open a pull request. The Check workflow runs on it automatically.

## Credits and licences

- Mechanics, prices and the buff/debuff list are adapted from the [BD2 Tactical Compendium Soul Wager page](https://botan14xd.github.io/BD2-Overview/content-packs/soul-wager/) by BotAn, licensed CC BY 4.0. Keep the credit in the site footer.
- Season notes come from official notices, linked from each season on the Seasons page.
- Brown Dust 2 is a trademark of NEOWIZ and GAMFS N. This fan site is not affiliated with or endorsed by them.

## Last updated dates

Every page except Home and the Changelog ends with "Last updated", taken from the last commit that changed its source file (for the Units, Gear, Tiles and Seasons pages, the YAML file). Files you've changed but not committed show today's date in a local preview. Outside a git repository the line is left out.

