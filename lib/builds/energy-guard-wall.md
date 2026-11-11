---
title: Energy Guard wall
description: Soak End Game with cheap Energy Guard and let slow damage finish the fight.
tested: false
---

# Energy Guard wall

Stack [[Energy Guard]] so your side outlasts End Game, then win on damage that keeps ticking. End Game hits both sides equally, and if both reach 0 HP at the same moment you win.

!!! note "Theorycraft"
    Worked out from the gear and tile text on this site, not from a tested run. One thing to check in game: whether End Game damage hits Energy Guard first or goes straight to HP. If it skips Energy Guard, this build only helps against enemy attacks.

```board
name: Energy Guard core
season: s3
summary: Armor on Utility characters, plus Protection Tiles wherever a unit needs floor.
pieces:
  A: refithea-pure-white-blessing
  B: liberta-onsen-manager
  C: protection-tile
  D: protection-tile
  E: protection-tile
gear:
  A: [invulnerable-armor]
  B: [mercenary-armor]
roles:
  A: Wall
  B: Healer / Wall
details:
  A: 80 Energy Guard from Invulnerable Armor at battle start.
  B: Heals, plus 20 Energy Guard from Mercenary Armor.
  C: 15 Energy Guard each, the best value in the shop.
  D: 15 Energy Guard each, the best value in the shop.
  E: 15 Energy Guard each, the best value in the shop.
notes: Armor is roughly ten times better on a Utility character. Invulnerable Armor gives 80 Energy Guard there and 8 on anyone else.
```

## Where the Energy Guard comes from

| Source | Energy Guard | Tokens | Per token |
|---|---|---|---|
| Protection Tile | 15 | 2 | 7.5 |
| Invulnerable Armor on a Utility character | 80 | 15 | 5.3 |
| Mercenary Armor on a Utility character | 20 | 4 | 5.0 |
| Either armor on anyone else | 2 to 8 | 4 to 15 | about 0.5 |

**Protection Tiles are the best value in the shop.** At 2 tokens they're also the cheapest floor for a 1×1 unit, so they cost almost nothing you weren't going to spend anyway. Three of them is 45 Energy Guard for 6 tokens.

**Only put armor on Utility characters**, the ones tagged Support. Refithea (Pure White Blessing) and Liberta (Onsen Manager) both are, and Refithea costs only 4 tokens. The [Units](../units/index.md) table shows every unit's tags.

## How long you need to last

End Game starts at 20 seconds and ramps:

| Battle time | Damage each second | Total taken so far |
|---|---|---|
| 40s | 7 | 77 |
| 50s | 10 | 165 |
| 60s | 16 | 298 |
| 70s | 21 | 480 |
| 80s | 29 | 735 |

A full wall (Invulnerable Armor, Mercenary Armor and three Protection Tiles) is 145 Energy Guard. That's enough to cover End Game to about 48 seconds on its own, before enemy attacks. It buys time, but it won't win a fight that drags past a minute, so pair it with Poison or another damage source that doesn't need Stamina. The [End Game calculator](../tools/calculators.md#end-game-damage) shows any other timing.

## Pairs well with

- [Poison stack](poison-stack.md): the wall keeps you alive while Poison ticks.
- [Frost and Darkness lockdown](lockdown.md): fewer enemy hits means the Energy Guard lasts longer.
