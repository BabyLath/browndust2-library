# How BrownDust II Library is put together

Read this before changing anything in `swg_site/` or `overrides/`. For day-to-day editing, the README is enough.

## Pipeline

```
content/*.yaml ─┐
                ├─► swg_site.generate ─► generated-docs/ ─► zensical build ─► site/
lib/**         ─┘          │
                           └─► .zensical.generated.toml (zensical.toml + nav + paths)
```

1. `catalog.load()` reads every YAML file and checks ids, types and vocabularies.
2. `Generator.run()` copies `lib/` into `generated-docs/` and, on the way:
   - expands ` ```board ` fences into HTML diagrams (`render.board`);
   - lays out each `lib/units/<id>.md` guide with its header, summary and generated sections (`render.unit_guide`);
   - replaces `<!-- swg:season -->` on any page with the current-season block;
   - writes the catalog pages: `units/index.md`, `reference/*.md`, `seasons.md`, `builds/index.md`.
3. The nav is generated from folders and front matter, merged into a copy of `zensical.toml`, and handed to `zensical build`.

`swg-check` runs steps 1 and 2 into a temporary folder and reports problems without building.

## Design decisions

**One source of truth.** A unit's name and price live only in `content/units.yaml`. Guides, builds and tables look them up, so a price change is one edit.

**Content files stay free of markup.** Shared HTML lives in `swg_site/render.py` and styles in `lib/styles/extra.css`. Guide authors write Markdown and YAML only.

**Validation over conventions.** Ids, grades, tags, roles, ratings, seasons and board layouts are all checked, with file and line numbers and a closest-match suggestion. A typo fails the PR check instead of silently rendering wrong.

**Calculators and the countdown run in the browser.** They're plain JS in `lib/javascripts/site.js` with no dependencies. The shop maths is duplicated in `render.py` (for tables) and `site.js` (for calculators); keep them in sync.

## Gotchas

- HTML blocks that contain Markdown need `markdown="1"`; blocks that shouldn't be parsed use `markdown="0"`.
- Fences must start at column 0.
- Instant navigation is off, so scripts run on every page load. If you turn it on, `site.js` already subscribes to `document$`.
