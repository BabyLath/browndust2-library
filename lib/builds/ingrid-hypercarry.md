---
title: Ingrid Hypercarry Burst
description: Solo Ingrid, surrounded by Arines's & Lathels
tested: true
---

# One-attacker burst

Put everything into a single attacker and end the fight before End Game gets expensive. Most of the gear and tiles that add damage are flat bonuses, so they pay off most on the unit that hits most often.

```board
name: Burst core
summary: One attacker VS the world
members:
  - unit: ingrid-kardis-bullet
    role: Main attacker
    note: Stands on all boost tiles. Knight's Sword adds +3 DMG from battle start.
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

```board
name: Supports
summary: Fill the rest of the board from these as the shop offers them.
total: false
members:
  - unit: lathel-homunculus
  - unit: arines-priest-of-vitality
  - unit: samay-kind-student
notes: Make sure that the supports' [[Allied-Character]] is touching atleast 1 tile of Ingrid.
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

**Choosing a sword:**
- Knight's Sword is a flat +3 from the start. It's the cheap, reliable pick for short fights.
- Hero's Sword and Evil Dragon's Blade are good & triggers when the attacker lands an attack. If that bonus stacks with every hit, it gets stronger the longer the fight goes. Unfortunately these are expensive and rare.

**Supports surrounds Ingrid.** Since most of the damage we get is from the first few seconds of the round, surrounding Ingrid with many Arines & Homumculus Lathel gives her enough damage to defeat the opponent before they start to ramp up.

## When it falls short

If the fight is still going after the buffs disappear & End Game is dealing 10 a second to both sides and climbing. You are **Cooked.** Against enemies with heavy defence, find another strategy like: [Poison stack](poison-stack.md).
