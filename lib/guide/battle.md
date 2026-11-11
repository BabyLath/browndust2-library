---
title: Battle and End Game
description: Targeting, cooldowns, shared Stamina, unit tags and End Game damage.
order: 2
icon: lucide/swords
---

# Battle and End Game

Combat runs on its own until one side hits 0 HP. If both sides hit 0 at the same moment, **you win**.

## Targeting doesn't care about position

Every unit hits the whole enemy field. Where you put your damage dealer on the grid changes nothing about its damage. Placement only matters for tile bonuses and fitting pieces together.

## Cooldowns and triggers

Most units act each time their cooldown finishes. Some have no cooldown and react to something instead:

| Trigger | Example |
|---|---|
| Enemy attacks | Seir, Demon's Daughter |
| Ally acts | Eclipse, Dream Bride |
| A condition is met | Refithea, Poolside Fairy |
| Battle starts | Jayden, Beautiful Girl Devotee |

## Stamina

All attackers share **one Stamina pool**. If the pool can't cover an action, that unit skips it and its cooldown restarts. This is the most common reason a strong-looking board loses: two expensive attackers starve each other.

The formation screen shows an estimate of average Stamina use. It ignores Stamina-restoring effects.

| Rating | Average Stamina use |
|---|---|
| Very Low | 0 to 4.9 |
| Low | 5 to 9.9 |
| Medium | 10 to 14.9 |
| High | 15 to 19.9 |
| Very High | 20 and up |

## Unit tags

| Tag | What it does |
|---|---|
| [[Close-Range Attack+]] | Melee hit every cooldown |
| [[Long-Range Attack+]] | Ranged hit every cooldown |
| [[Defending+]] | Reacts when the enemy attacks |
| [[Support+]] | Buffs allies |
| [[Heal+]] | Restores HP |
| [[Curse+]] | Debuffs the enemy |
| [[Cleanse+]] | Removes your debuffs |
| [[Remove+]] | Strips enemy buffs |

Attackers have four stats worth reading: damage range (rolled per action), Stamina cost, Accuracy and cooldown.

The full list is on [Buffs and debuffs](../reference/statuses.md).

## End Game

After **20 seconds**, both sides start taking damage every second. It ramps slowly, then fast:

- From 20 to 48 seconds, damage per second is `floor(t / 3) - 6`, so it climbs by 1 every 3 seconds up to 10.
- From 48 seconds on, damage per second is `ceil(1.11 ^ (floor(t / 3) + 6))`, roughly 11% more every 3 seconds.

At one minute, both sides take 16 damage a second. Builds that rely on slow stacking need enough sustain to outlast this, or enough burst to end the fight before it matters. The [End Game calculator](../tools/calculators.md#end-game-damage) shows the numbers for any second.
