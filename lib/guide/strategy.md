---
title: How to build a team
description: Pick a win condition, fit one attacker to the shared Stamina pool, gear by tag, and counter what View Formation shows.
order: 3
icon: lucide/lightbulb
---

# How to build a team

!!! tip "Quick start"
    1. **Pick one main attacker.** Every attacker draws from the same Stamina pool, so one well-fed attacker beats two starving ones.
    2. **Fill the rest with Support, Curse and Heal units.** They mostly act without spending Stamina.
    3. **Gear by tag.** Most gear does something different on an attacker than on everyone else. Read both halves before you buy.
    4. **Check View Formation every phase** and swap in a [[Cleanse+]] or [[Remove+]] unit when the enemy calls for one.

## The purpose of a team

There is no single best board. Each Phase puts a different enemy formation in front of you, it gets stronger every Phase, and the shop only offers four pieces at a time. A good team is the one that beats **this** enemy with **this** shop, and a run is a series of small adjustments, not one plan you force through.

That's why the first habit is the cheapest one: open **View Formation** before you spend anything.

## How do you win?

Every fight ends. After 20 seconds End Game damages both sides every second, and it ramps hard after 48. If both sides hit 0 HP at the same moment, you win. So a team needs an answer to one question: **how does the enemy reach 0 before you do?**

There are four answers:

- **Burst.** Kill before End Game gets expensive. At 40 seconds End Game has only dealt 77 damage in total.
- **Outlast.** Stack enough [[Energy Guard]] and healing that End Game and enemy hits run out your opponent first.
- **Tick.** [[Poison]] keeps dealing damage without spending Stamina, so it keeps working when your attacker can't.
- **Deny.** [[Frost]] and [[Darkness]] make the enemy act less and miss more, which stretches whatever plan you picked.

A board that has none of these is a pile of good units. It wins early Phases on raw stats and falls over around the middle of the Board.

## Types of teams

These are the four shapes most winning boards take. Each has a full write-up on the [Builds](../builds/index.md) page. All four are still theorycraft, worked out from item text rather than tested runs. The unit picks follow the [BD2 Tactical Compendium](https://botan14xd.github.io/BD2-Overview/content-packs/soul-wager/#strategy)'s October 22 update: Liatris, Rubia and Blade as damage dealers; Refithea, Celia, Levia, Liberta and Palette as supports and debuffers.

### Hypercarry

Everything goes into one attacker. Most damage bonuses in the shop are flat (+2 from a tile, +3 or +4 from a sword), so they're worth the most on the unit that attacks most often.

```board
name: Hypercarry
season: s3
summary: One attacker standing on three tiles, with a cheap support on armor.
pieces:
  A: rubia-thorn-of-the-desert
  B: refithea-pure-white-blessing
  C: attack-tile
  D: efficiency-tile
  E: acceleration-tile
gear:
  A: [knights-sword]
  B: [mercenary-armor]
roles:
  A: Main attacker
  B: Support
details:
  A: The cheapest of this season's strong damage dealers, leaving tokens for tiles.
  B: 20 Energy Guard from armor, since she's a Utility character.
  C: +2 DMG for the attacker standing inside.
  D: Stamina cost −2, so fewer of the attacker's actions get skipped.
  E: +10% Action Speed.
notes: A tile only affects characters inside it, so the attacker has to overlap all three. Check its footprint against the tile shapes before buying.
```

Weak point: a slow fight. If the enemy is still standing at 50 seconds, End Game is dealing 10 a second and you have no plan B. Full build: [One-attacker burst](../builds/stamina-burst.md).

### Stall

Win by being the last one standing. End Game hits both sides equally, so every point of Energy Guard you have and they don't is a point of lead.

```board
name: Stall
season: s3
summary: Armor on Utility characters, Protection Tiles under everything, and a Poison source to finish.
pieces:
  A: refithea-pure-white-blessing
  B: liberta-onsen-manager
  C: celia-the-curse
  D: protection-tile
  E: protection-tile
  F: protection-tile
gear:
  A: [invulnerable-armor]
  B: [mercenary-armor]
  C: [knights-necklace]
roles:
  A: Wall
  B: Healer / Wall
  C: Poison
details:
  A: 80 Energy Guard from Invulnerable Armor, ten times what anyone else gets from it.
  B: Heal tag, plus 20 Energy Guard from Mercenary Armor.
  C: Damage that doesn't need Stamina. Knight's Necklace adds Poison on a Curse character.
  D: 15 Energy Guard for 2 tokens, the best value in the shop.
notes: Check in game whether End Game damage hits Energy Guard first. If it goes straight to HP, this wall only protects against enemy attacks.
```

Weak point: Remove. An enemy that strips buffs can take your Energy Guard off before it does anything. Full build: [Energy Guard wall](../builds/energy-guard-wall.md).

### Poison

The current favourite. Stack Poison from several sources, bring one attacker for pressure and enough sustain to live while the stacks work. Each Poison stack deals 1 damage every 2 seconds, so 10 stacks is 5 damage a second for no Stamina at all.

```board
name: Poison
season: s3
summary: Three Poison sources plus a Curse Tile, around one attacker.
pieces:
  A: liatris-rodevs-star
  B: celia-the-curse
  C: refithea-pure-white-blessing
  D: curse-tile
gear:
  A: [mercenary-staff]
  B: [knights-necklace]
  C: [mercenary-sword]
roles:
  A: Poison / Attacker
  B: Poison / Debuffer
  C: Poison / Opener
details:
  A: Mercenary Staff gives each hit a 50% chance to add 1 Poison.
  B: 50% chance per cooldown to add Poison with Knight's Necklace.
  C: Mercenary Sword on a non-attacker applies 3 Poison at battle start.
  D: Put it under a unit with a short cooldown. 25% chance per cooldown to apply a random debuff.
notes: Mercenary Sword and Mercenary Staff have identical effects. Buy whichever the shop offers.
```

Weak point: [[Cleanse+]] units on the enemy side. Full build: [Poison stack](../builds/poison-stack.md).

### Lockdown

Make the enemy's attackers act less often and miss more, then win with whatever you were already doing. Lockdown is a layer, not a team on its own. It's at its best on top of a Stall or Poison board, where buying time is the whole point.

```board
name: Lockdown
season: s3
summary: Frost from a support at battle start, Darkness from the attacker's hits.
pieces:
  A: liatris-rodevs-star
  B: liberta-onsen-manager
gear:
  A: [heros-staff]
  B: [knights-staff]
roles:
  A: Darkness / Attacker
  B: Frost / Support
details:
  A: Each hit has a 50% chance to apply Darkness. Each stack is −5% enemy Accuracy.
  B: Knight's Staff on a non-attacker applies 4 Frost at battle start, −8% enemy Action Speed.
```

Weak point: it does no damage by itself. Full build: [Frost and Darkness lockdown](../builds/lockdown.md).

## What every team needs

### A Stamina budget

This is the one most losing boards get wrong. All attackers draw from **one shared Stamina pool**, and an action the pool can't cover is skipped with its cooldown restarted. Two expensive attackers don't add up to double damage. They take turns failing.

- Keep one main attacker. A second only works if both are cheap to run.
- Watch the Stamina estimate on the formation screen and compare it as you add pieces. It doesn't count Stamina-restoring effects, so the real number is usually a little better.
- An [Efficiency Tile](../reference/tiles.md#efficiency-tile) under the attacker cuts every action by 2 Stamina. On a fast attacker that's the cheapest damage increase in the shop.
- Damage that doesn't need Stamina, like Poison, Curse Tile debuffs and Strength on supports, is how a board scales past one attacker.

### An answer to the enemy board

View Formation shows you what you're up against. Two tags exist almost purely to counter it:

- **Against debuff-heavy enemies, bring [[Cleanse+]].** Refithea (Poolside Fairy) costs 4; Lisianne (Wandering Priest) costs 5 and also heals.
- **Against buff stackers and Energy Guard walls, bring [[Remove+]].** Eclipse (Dimension Witch) is 5 and also heals; Scheherazade (Lapis Witch) is 6 and also attacks.

You won't need either every Phase. Keep one in [Storage](board-shop.md#storage), where it costs nothing, and put it in when the enemy calls for it.

## Tags and teambuilding

**Pick units first, gear second.** Nearly every piece of gear checks the tag of the unit wearing it and does something different depending on the answer:

| Gear checks for | Gets the strong effect | Examples |
|---|---|---|
| Attacking Character | Units with Close-Range or Long-Range Attack | Swords, staffs |
| Utility Character | Units tagged [[Support+]] | Invulnerable Armor, Mercenary Armor |
| Curse Character | Units tagged [[Curse+]] | Knight's Necklace |

The gap is often huge. Invulnerable Armor is 80 Energy Guard on a Utility character and 8 on anyone else. So don't buy gear first and look for a body to put it on; buy the unit and then the gear that fits its tag.

Utility is the most common tag, on more than half the roster, so armor almost always has a good home. Some units carry two tags, like Liatris (Long-Range Attack and Utility). Which half of a piece of gear they get is worth checking in game before you build around it.

## Spending Soul Tokens

The shop is the other half of the game. You earn **16 tokens for a win and 10 for a loss**, and the decisions add up over a Board's Phases.

- **Spend early, reroll late.** Early Phases only roll low grades, so rerolling for a rare piece in Phase 1 buys odds that can't pay out.
- **Stop rerolling after four or five.** The cost starts at 1 and goes up by 1 every 4 rolls. The [reroll calculator](../tools/calculators.md#rerolls) shows the running total.
- **Reserve what you can't afford yet.** Tap the price tag and it survives the next refresh.
- **Losses aren't wasted.** A loss still pays 10, refreshes the shop and resets your reroll cost. With 5 lives, one early loss for a better shop can be the right trade.
- **Sell carefully.** Selling returns half the price rounded down, at least 2, and upgrades don't raise it. A Protection Tile sells for 1. Swapping pieces back and forth is expensive.
- **Grab discounts.** 10% of offers are half price. A discounted core piece is worth buying a Phase early.

## Building your units

### Building the attacker

#### Flat damage

[Attack Tile](../reference/tiles.md#attack-tile) (+2), Knight's Sword (+3 from battle start) and Hero's Sword (+4 when it lands an attack) all add flat damage per action. They're best on whoever acts most, which is your main attacker.

#### Speed and Stamina

[Acceleration Tile](../reference/tiles.md#acceleration-tile) adds 10% Action Speed, and God-King's Silver Arm adds 25% on a non-attacker. More speed means more actions, which means more Stamina spent, so pair speed with an Efficiency Tile.

#### On-hit effects

Hero's Staff, Knight's Staff and the Mercenary weapons add Darkness, Frost or Poison when the attacker lands a hit. They turn the attacker into a debuffer at the same time, which is how Poison and Lockdown boards fit around one attacker.

### Building supports

Supports use the **other** half of each item. Read gear text twice: the line for "Other Characters" is often the better one.

- Evil Dragon's Blade gives 3 [[Strength]] at battle start, adding damage to all your attackers.
- Knight's Sword and Hero's Sword give 3 and 4 random buffs.
- Mercenary Sword and Staff apply 3 Poison at battle start.
- Knight's Staff applies 4 Frost at battle start.
- Armor goes on Utility characters, every time.

## Choosing tiles

Tiles are the floor every unit needs. Since you have to buy floor anyway, the question is which tile gives the most for the shape you need.

#### Protection Tile

**Price** 2 · **Shape** 1×1 · **Best under** anything 1×1

15 [[Energy Guard]] at battle start. The best value in the shop and the cheapest floor there is. It only sells for 1, so it's a permanent purchase.

#### Efficiency Tile

**Price** 5 · **Shape** 1×3 · **Best under** your main attacker

Stamina cost −2. The core tile of any board with one attacker.

#### Attack Tile

**Price** 4 · **Shape** 4 squares, T-shaped · **Best under** your main attacker

+2 DMG to Attacking Characters inside. Does nothing for supports.

#### Curse Tile

**Price** 6 · **Shape** 4 squares, S-shaped · **Best under** units with short cooldowns

25% chance per cooldown to apply a random debuff. Strong on Poison boards; every debuff counts even when it isn't Poison.

#### Acceleration Tile

**Price** 3 · **Shape** 1×2 · **Best under** your attacker, if Stamina allows

+10% Action Speed at battle start.

#### Buff, Support and Vitality Tiles

Buff Tile (6) has a 25% chance per cooldown to give a random buff. Support Tile (5, 1×4) gives each character inside 1 random buff at battle start. Vitality Tile (4) gives each character inside 5 Max HP. All three are fine floor when the shop is dry, and none is worth rerolling for.

#### Basic Tile

**Price** 4 · **Shape** 2×2

No effect. Buy it only when it's the only tile that fits.

All tile shapes are drawn on the [Tiles](../reference/tiles.md) page.

## Common mistakes

- **Two big attackers.** They fight over Stamina and neither reaches its potential.
- **Gear on the wrong tag.** Armor on an attacker, a sword on a healer that only wanted the attack half.
- **No win condition.** Strong units with nothing that wins a long fight. You'll find out around the middle of the Board.
- **Ignoring View Formation.** The enemy board tells you whether you need Cleanse or Remove this Phase.
- **Rerolling in Phase 1.** Low-grade pools can't give you the piece you're rolling for.
- **Selling to fund a pivot.** Half price back, rounded down. Plan the board before you buy, and use Storage instead of selling.
