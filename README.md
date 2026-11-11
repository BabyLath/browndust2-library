# Soul Wager Guide

A fan guide for **The Soul Wager** in Brown Dust 2: unit prices, builds, season notes and calculators.

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

`swg-check` prints the file and line of every problem and suggests the closest id when you mistype one:

```
ERROR   lib/builds/poison-stack.md:10  piece A: 'celia-the-cures' isn't a unit or tile. Did you mean 'celia-the-curse'?
WARNING content/units.yaml:9  verified_for is 's2' but the current season is 's3'. Recheck prices, then set verified_for: s3.
```

Errors stop the build. Warnings don't, but they show up on the site too (the Units page shows a "not yet checked" notice until `verified_for` matches the current season).

Never edit `generated-docs/`, `site/` or `.zensical.generated.toml`. They're rebuilt every time.

## Deploying to GitHub Pages

1. Push this folder to `github.com/babylath/soul-wager-guide` (or change `site_url` and `repo_url` in `zensical.toml`).
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Every push to `main` runs `.github/workflows/deploy.yml`, which builds and publishes. Pull requests run `check.yml` instead, so a broken id can't reach `main`.

## Where things live

| You want to change | Edit |
|---|---|
| Unit prices, grades, tags | `content/units.yaml` (one unit per line) |
| Gear and tiles | `content/gear.yaml`, `content/tiles.yaml` |
| Buffs and debuffs | `content/statuses.yaml` |
| Seasons, boards, balance notes | `content/seasons.yaml` |
| Allowed grades, tags, roles, ratings | `content/meta.yaml` |
| Guide pages | `lib/guide/*.md` |
| A unit guide | `lib/units/<unit-id>.md` (copy `templates/unit.md`) |
| A build | `lib/builds/<name>.md` (copy `templates/build.md`) |
| Home page | `lib/index.md` |
| Colours and fonts | top of `lib/styles/extra.css`, and `font` in `zensical.toml` |
| Site name, links, footer | `zensical.toml` |
| Hover definitions for terms | `includes/abbreviations.md` |
| Site changelog | `lib/changelog.md` |

The sidebar builds itself from these folders. Guide pages sort by `order:` in their front matter.

## Every new season

This is the routine that keeps the data current.

1. Add the season to the end of `content/seasons.yaml` with its `start`, an `expected_end`, and a `changes` line per balance note. Link the official notice under `sources`.
2. Set the previous season's `end`.
3. Update changed prices, add new units to `content/units.yaml`, and add any new grade to `content/meta.yaml`.
4. Once every price is checked, set `verified_for:` to the new season id in `units.yaml`, `gear.yaml` and `tiles.yaml`. The warnings and the site notice go away.
5. Add a line to `lib/changelog.md`.
6. `uv run swg-check`, then commit.

The home page countdown is worked out in the visitor's browser from the season dates, so it stays right between deploys. Only the dates themselves need a rebuild.

## Writing a unit guide

```
cp templates/unit.md lib/units/levia-overheat.md
```

The file name must equal the unit id. Fill in the front matter (`role`, `rating`, `summary`, `works_well_with`, all optional) and write the body in plain Markdown. The title, price, sale price, sell value, grade and tags come from the catalog, so you never type them twice. Every `## Heading` becomes a section and an entry in the page's table of contents.

## Writing a build

Builds use a `board` fence. It draws a 7×7 diagram from a text layout, lists each piece with its price, and totals the cost from the catalog:

````
```board
name: Poison stack
season: s3
layout: |
  AA.BB..
  AA.BB..
  CCCC...
  .......
  .......
  .......
  .......
pieces:
  A: liatris-rodevs-star
  B: celia-the-curse
  C: curse-tile
gear:
  A: [knights-sword]
notes: Optional tip.
```
````

- `layout` is 7 rows of 7 characters. `.` is an empty square, any other character is a piece. Leave `layout` out to show just the piece list.
- `pieces` maps each character to a unit or tile id.
- `gear` maps a unit's character to a list of gear ids.
- Put the fence at the start of a line, not inside a list or quote.

## Contributing

- **Found wrong data?** Open an issue with the "Data correction" form. A screenshot of the in-game shop or Codex is the fastest way to get it fixed.
- **Collaborators:** small fixes can go straight through GitHub's edit button (the pencil on every page links to the source file). For anything bigger, clone, run `swg-serve`, edit, run `swg-check`, commit, push.
- **Everyone else:** fork, branch, make the change, open a pull request. The Check workflow runs on it automatically.

## Credits and licences

- Mechanics, prices and the buff/debuff list are adapted from the [BD2 Tactical Compendium Soul Wager page](https://botan14xd.github.io/BD2-Overview/content-packs/soul-wager/) by BotAn, licensed CC BY 4.0. Keep the credit in the site footer.
- Season notes come from official notices, linked from each season on the Seasons page.
- Site structure and tooling were modelled on [Mythag Library](https://github.com/mythaglibrary/website).
- Brown Dust 2 is a trademark of NEOWIZ and GAMFS N. This fan site is not affiliated with or endorsed by them.
