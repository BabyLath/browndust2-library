---
title: How to build a team
description: Pick a win condition, fit one attacker to the shared Stamina pool, gear by tag, and counter what View Formation shows.
order: 3
icon: lucide/lightbulb
---

# How to build a team

!!! tip "Quick start"
    1. **Check if your planned strategy works.** The current strategy last season might not work for the current one, so check if your strategy counters the current formation and not you getting countered instead.
    2. **Pick one Main type of Damage.** It is generally better to pick a single type of damage to not spread yourself too thin and instead, take upgrades that improves your selected type of damage.
    3. **Pick one main attacker.** Every attacker draws from the same Stamina pool, so one well-fed attacker beats two starving ones.
    4. **Fill the rest with Support, Curse and Heal units.** They mostly act without spending Stamina.
    5. **Gear by tag.** Most gear does something different on an attacker than on everyone else. Read both halves before you buy.
    6. **Check View Formation every phase** and swap in a [[Cleanse]] or [[Remove]] unit when the enemy calls for one.

## The purpose of a team

There is no single best board. Each Phase puts a different enemy formation in front of you, it gets stronger every Phase, and the shop only offers four pieces at a time. A good team is the one that beats **this** enemy with **this** shop, and a run is a series of small adjustments, not one plan you force through.

That's why the first habit is the cheapest one: open **View Formation** before you spend anything.

## How do you win?

Every fight ends. After 20 seconds End Game damages both sides every second, and it ramps hard after 48. If both sides hit 0 HP at the same moment, you win. So a team needs an answer to one question: **how does the enemy reach 0 before you do?**

These four are example answers:

- **Burst.** Kill before End Game gets expensive. At 40 seconds End Game has only dealt 77 damage in total.
- **Outlast.** Stack enough [[Energy Guard]] and healing that End Game and enemy hits run out your opponent first.
- **Tick.** [[Poison]] keeps dealing damage without spending Stamina, so it keeps working when your attacker can't.
- **Deny.** Debuffs such as [[Frost]] and [[Darkness]] make the enemy act less and miss more, which stretches whatever plan you picked.

A board that has none of these is a pile of good units. It wins early Phases on raw stats and falls over around the middle of the Board.

## Types of teams

### Hypercarry

Everything goes into one attacker. The rest supports them.

```board
name: Hypercarry
summary: Ingrid hypercarry while the rest enables her.
members:
  - unit: ingrid-kardis-bullet
    role: Main attacker
    note: Cheap attacker that attacks an additional time with no Stamina cost.
  - unit: arines-priest-of-vitality
    role: Support
    note: Cheap DMG dealt buffer upon battle start
  - unit: lathel-homunculus
    role: Support
    note: Great DMG dealt buffer at battle start.

```

Weak point: a slow fight. If the enemy is still standing at 50 seconds, End Game is dealing 10 a second and you have no plan B. Full build: [One-attacker burst](../builds/ingrid-hypercarry.md).

### Stun

Win by stunning the enemy formation, leaving them unable to act.

```board
name: Stun
summary: Stun the enemy with Layla with your Bernie(s) & Samay(s) doing damage.
members:
  - unit: layla-anvil-of-creation
    role: Main Stun Source
    note: 45% chance to stun the opponent for 0.5s.
  - unit: bernie-righteous-raider-girl
    role: DPS
    note: Attacks immediately when the opponent is stunned.
  - unit: samay-kind-liberator
    role: Poison DPS
    note: Extra DPS to be added to the team when found.

notes: Make sure to have enough stamina for layla to attack & only have one source of stun on the board.
```

Weak point: [[Counter+]], [[Laceration+]], [[Darkness+]] & [[Frost+]]

### Poison

The current favourite. Stack Poison from several sources, bring one attacker for pressure and enough sustain to live while the stacks work. Each Poison stack deals 1 damage every 2 seconds, so 10 stacks is 5 damage a second for no Stamina at all.

```board
name: Poison
summary: Spam enough Poison till the enemy cannot sustain it any longer.
members:
  - unit: nebris-labyrinth-gatekeeper
    role: Poison / Attacker
    note: Poison Multiplier per hit
  - unit: celia-the-curse
    role: Poison applicator
    note: Usually your first and cheap poison applicator
tiles:
  - tile: curse-tile
    note: Put it under a unit with a short cooldown. 25% chance per cooldown to apply a random debuff.
notes: Mercenary Sword and Mercenary Staff have identical effects. Buy whichever the shop offers.
```

Weak point: [[Cleanse+]] units on the enemy side. Full build: [Poison stack](../builds/poison-stack.md).

### Lockdown

Make the enemy's attackers act less often and miss more, then win with whatever you were already doing. Lockdown is a layer, not a team on its own. It's at its best on top of a Stall or Poison board, where buying time is the whole point.

```board
name: Lockdown
summary: Frost from a support at battle start, Darkness from the attacker's hits.
members:
  - unit: wiggle-bomb-in-the-hoodie
    role: Darkness / Attacker
    note: Each hit has a 50% chance to apply Darkness. Each stack is −5% enemy Accuracy.
    gear: [heros-staff]
  - unit: cynthia-warmth-within-the-severe-cold
    role: Frost / Support
    note: Knight's Staff on a non-attacker applies 4 Frost at battle start, −8% enemy Action Speed.
    gear: [knights-staff]
```

Weak point: it does no damage by itself

### Counter

Make the enemy basically kill theirself by stacking [[Counter+]] & [[Energy-Guard+]]

```board
name: Counter
summary: Stack Counter and Enery Guard while enemy kills theirself
members:
  - unit: sylvia-sword-queen
    role: Attacker / Counter applicator
    note: Gain 1 [[Counter]] for every 3 attacks landed
  - unit: sylvia-desert-flower
    role: Defender
    note: 40% chance to reduce damage taken and gain 1 [[Counter]]
```

## What every team needs

### A Stamina budget

This is the one most losing boards get wrong. All attackers draw from **one shared Stamina pool**, and an action the pool can't cover is skipped with its cooldown restarted. Two expensive attackers don't add up to double damage. They take turns failing.

- Keep one main attacker. A second only works if both are cheap to run.
- Watch the Stamina estimate on the formation screen and compare it as you add pieces. It doesn't count Stamina-restoring effects, so the real number is usually a little better.
- An [Efficiency Tile](../reference/tiles.md#efficiency-tile) under the attacker cuts every action by 2 Stamina. On a fast attacker that's the cheapest damage increase in the shop.
- Damage that doesn't need Stamina, like Poison, Curse Tile debuffs and Strength on supports, is how a board scales past one attacker.

### An answer to the enemy board

View Formation shows you what you're up against. Two tags exist almost purely to counter it:

- **Against debuff-heavy enemies, bring [[Cleanse]].** Refithea (Poolside Fairy) costs 4; Lisianne (Wandering Priest) costs 5 and also heals.
- **Against buff stackers and Energy Guard walls, bring [[Remove]].** Eclipse (Dimension Witch) is 5 and also heals; Scheherazade (Lapis Witch) is 6 and also attacks.

You won't need either every Phase. Keep one in [Storage](board-shop.md#storage), where it costs nothing, and put it in when the enemy calls for it.

## Tags and teambuilding

**Pick units first, gear second.** Nearly every piece of gear checks the tag of the unit wearing it and does something different depending on the answer:

| Gear checks for | Gets the strong effect | Examples |
|---|---|---|
| Attacking Character | Units with Close-Range or Long-Range Attack | Swords, staffs |
| Utility Character | Units tagged [[Support+]] | Invulnerable Armor, Mercenary Armor |
| Curse Character | Units tagged [[Curse+]] | Knight's Necklace |

The gap is often huge. Invulnerable Armor is 80 Energy Guard on a Utility character and 8 on anyone else. So don't buy gear first and look for a body to put it on; buy the unit and then the gear that fits its tag.

Utility is the most common tag, on more than half the roster, so armor almost always has a good home. Some units carry two tags, like Liatris ([[long-range-attack]] and [[support]]). Which half of a piece of gear they get is worth checking in game before you build around it.

## Spending Soul Tokens

The shop is the other half of the game. You earn **16 tokens for a win and 10 for a loss**, and the decisions add up over a Board's Phases.

- **Spend early, reroll late.** Early Phases only roll low grades, so rerolling for a rare piece in Phase 1 buys odds that can't pay out.
- **Stop rerolling after four or five.** The cost starts at 1 and goes up by 1 every 4 rolls. The [reroll calculator](../tools/calculators.md#rerolls) shows the running total.
- **Reserve what you can't afford yet.** Tap the price tag and it survives the next refresh.
- **Losses aren't wasted.** A loss still pays 10, refreshes the shop and resets your reroll cost. With 5 lives, one early loss for a better shop can be the right trade.
- **Sell carefully.** Selling returns half the price rounded down, at least 2, and upgrades don't raise it. A Protection Tile sells for 1. Swapping pieces back and forth is expensive.
- **Grab discounts.** 10% of offers are half price. A discounted core piece is worth buying a Phase early.

## Common mistakes

- **Two big attackers.** They fight over Stamina and neither reaches its potential.
- **Gear on the wrong tag.** Armor on an attacker, a sword on a healer that only wanted the attack half.
- **No win condition.** Strong units with nothing that wins a long fight. You'll find out around the middle of the Board.
- **Ignoring View Formation.** The enemy board tells you whether you need Cleanse or Remove this Phase.
- **Rerolling in Phase 1.** Low-grade pools can't give you the piece you're rolling for.
- **Selling to fund a pivot.** Half price back, rounded down. Plan the board before you buy, and use Storage instead of selling.
