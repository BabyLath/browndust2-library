---
title: Current season strategy
description: Just tell me what to run. The team, what to buy, and what to skip this season.
order: 0
icon: lucide/target
# The season this page is written for. When a new season starts, swg-check warns and the
# page shows an "Out of date" notice until you update it and change this to the new id.
season: s3
---

# Current season strategy

!!! tip "TL;DR"
    - **Run Poison.** One attacker, everyone else stacking [[Poison]], a healer to stay alive.
    - **Your attacker:** Liatris (Rodev's Star) or Rubia (Thorn of the Desert). Whichever shows up first.
    - **Your core:** Celia (The Curse) with Knight's Necklace. Buy her the moment you see her.
    - **Floor:** Protection Tiles. 2 tokens each.
    - **Don't reroll in early Phases.** Save it for the end of the Board.
    - **Before the season ends, spend every Alea Chip.** Leftovers are wiped.

No theory, just what to do for this season. If you want to know *why*, read [How to build a team](strategy.md).

## The team

This is the finished board you're building toward. You won't have it in Phase 1; pick the pieces up as the shop offers them, in the order under [What to buy first](#what-to-buy-first).

```board
name: Season 3 Poison
season: s3
summary: One attacker, three Poison sources, one healer.
pieces:
  A: liatris-rodevs-star
  B: celia-the-curse
  C: refithea-pure-white-blessing
  D: liberta-onsen-manager
  E: curse-tile
  F: protection-tile
  G: protection-tile
gear:
  A: [mercenary-staff]
  B: [knights-necklace]
  C: [mercenary-sword]
  D: [mercenary-armor]
roles:
  A: Poison / Attacker
  B: Core / Debuffer
  C: Poison / Opener
  D: Healer
details:
  A: Your only attacker. Swap in Rubia if she shows up first; same gear.
  B: Poison on half her cooldowns. Buy her on sight.
  C: 3 Poison the moment the battle starts.
  D: Heals, plus 20 Energy Guard from the armor.
  E: Put it under Celia. Extra random debuffs.
  F: Cheap floor with 15 Energy Guard. Use them under any 1×1 unit.
notes: Mercenary Sword and Mercenary Staff do the same thing. Buy whichever the shop has and give the first one to your attacker.
```

## What to buy first

Celia, Refithea, Liatris and Rubia are Basic or Rare grade, so they can show up from Phase 1. Buy in this order:

1. **Celia, The Curse** (4). Your core. Buy on sight.
2. **Liatris or Rubia** (6). Whichever comes first. Don't buy both.
3. **Knight's Necklace** (5). Goes on Celia, nobody else.
4. **Mercenary Staff or Sword** (4). First one on your attacker, second on Refithea.
5. **Protection Tiles** (2). Whenever you need floor.
6. **Refithea, Pure White Blessing** (4) and **Liberta, Onsen Manager** (6).
7. **Curse Tile** (6). Under Celia.
8. **Upgrades**, once the board above is complete.

**Can't afford it?** Tap the price tag to reserve it. It stays through the next shop refresh.

## Shop cheat sheet

| You see | Do this |
|---|---|
| Celia, The Curse | Buy. Always. |
| Liatris or Rubia, and you have no attacker | Buy |
| A second attacker | Skip. Two attackers fight over Stamina. |
| Knight's Necklace, Mercenary Staff, Mercenary Sword | Buy until everyone on the team has one |
| Protection Tile | Buy if you need floor |
| Levia (Overheat) or Palette (Shattered Dream) | Good backups if Celia never shows up. Levia also attacks, so she counts as a second attacker. |
| Blade (Apostle) | Strong, but 12 tokens and Mythical grade, so late. Only if you have no attacker yet. |
| Anything half price | Buy it a Phase early if it's on the list |
| Armor (Invulnerable or Mercenary) | Only for Refithea or Liberta |
| Expensive gear not on this page | Skip |

## Phase by phase

| When | Do |
|---|---|
| **Early Phases** | Shops only roll low grades. Buy Celia, Liatris or Rubia, Refithea and Protection Tiles. **No rerolls.** |
| **Middle Phases** | Add the Poison gear and Liberta. Check View Formation before every battle. |
| **Late Phases** | All grades show up. Fill gaps, upgrade your attacker and Celia, and reroll up to 4 times if you're missing a core piece. |
| **Lost a battle?** | Not a disaster. You still get 10 tokens, the shop refreshes and rerolls reset to 1. You have 5 lives per Board. |

## If the enemy has…

Open **View Formation** before every battle. If you see one of these, change one piece:

| Enemy board | Fix |
|---|---|
| Lots of debuffs on you | Add a [[Cleanse+]] unit. Refithea (Poolside Fairy) costs 4. |
| Lots of buffs or Energy Guard | Add a [[Remove+]] unit. Eclipse (Dimension Witch) costs 5 and heals. |
| [[Cleanse+]] units | Your Poison gets wiped. Add the [Lockdown](../builds/lockdown.md) gear so they act less. |
| Fights that drag past a minute | Add more Protection Tiles. End Game is hitting 16 a second by then. |

Keep your counter unit in **Storage** between battles. Storage is free.

## Don't

- Don't run two attackers.
- Don't put armor on your attacker. It's ten times better on Refithea or Liberta.
- Don't reroll in early Phases. Those shops can't roll what you're looking for.
- Don't sell to change plans. You only get half back.

## Before the season ends

<!-- swg:season -->

Runs lock at **15:00 UTC** on the last day. The countdown above is in your own time zone.

- **Spend every Alea Chip.** Leftover chips are wiped at the end of the season. Buy everything in the [Alea Chip shop](rewards.md), contracts included.
- **Finish your runs before the lock.** Dates are on the Seasons page.

!!! note "Where this comes from"
    The unit picks follow the [BD2 Tactical Compendium](https://botan14xd.github.io/BD2-Overview/content-packs/soul-wager/#strategy) as of October 22: stack Poison with moderate sustain. The gear and order are worked out from item text on this site and haven't been tested in a full run yet. Last checked November 8, 2026.
