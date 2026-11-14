---
title: One-attacker burst
description: Build one damage dealer up with flat damage, speed and Stamina savings and win before End Game ramps.
tested: false
---

# One-attacker burst

Put everything into a single attacker and end the fight before End Game gets expensive. Most of the gear and tiles that add damage are flat bonuses, so they pay off most on the unit that hits most often.

!!! note "Theorycraft"
    Worked out from the gear and tile text on this site, not from a tested run. Update it once you've tried it.

```board
name: Burst core
season: s3
summary: One attacker standing on Attack, Efficiency and Acceleration Tiles, with damage gear.
members:
  - unit: rubia-thorn-of-the-desert
    role: Main attacker
    note: Stands on all three tiles. Knight's Sword adds +3 DMG from battle start.
    gear: [knights-sword]
tiles:
  - tile: attack-tile
    note: +2 DMG to Attacking characters inside.
  - tile: efficiency-tile
    note: Stamina cost −2 per action.
  - tile: acceleration-tile
    note: +10% Action Speed at battle start.
notes: A tile only affects characters located inside it, so the attacker has to stand on all three. Check its footprint against the tile shapes before buying.
```

## What each piece adds

| Piece | Tokens | Effect on the attacker |
|---|---|---|
| Attack Tile | 4 | +2 DMG |
| Efficiency Tile | 5 | Stamina cost −2 |
| Acceleration Tile | 3 | +10% Action Speed |
| Knight's Sword | 6 | +3 DMG from battle start |
| Hero's Sword | 9 | +4 DMG each time it lands an attack |
| Evil Dragon's Blade | 15 | +1 DMG each time it lands an attack |

**Efficiency Tile is the quiet key piece.** Every attacker shares one Stamina pool, and an attack the pool can't afford is skipped. Cutting the cost by 2 per action means more of the attacker's hits actually happen, which matters more as its speed goes up.

**Choosing a sword:**
- Knight's Sword is a flat +3 from the start. It's the cheap, reliable pick for short fights.
- Hero's Sword and Evil Dragon's Blade trigger when the attacker lands an attack. If that bonus stacks with every hit, it gets stronger the longer the fight goes. Check in game whether it stacks or stays at one bonus.

**Supports carry gear too.** Evil Dragon's Blade on a non-attacker gives 3 [[Strength]] at battle start, and each stack adds 1 DMG to attacking characters. Hero's Sword and Knight's Sword on a non-attacker give 4 and 3 random buffs instead.

## Picking the attacker

Liatris (Rodev's Star), Rubia (Thorn of the Desert) and Blade (Apostle) have been the strongest damage dealers this season, according to the BD2 Tactical Compendium. Rubia is the cheapest at 6 tokens, which leaves the most for tiles and gear. Run one, not two: a second attacker splits the Stamina pool and the flat bonuses.

## When it falls short

If the fight is still going at 50 seconds, End Game is dealing 10 a second to both sides and climbing. Against enemies with heavy defence, mix in the [Energy Guard wall](energy-guard-wall.md) or switch to [Poison stack](poison-stack.md).
