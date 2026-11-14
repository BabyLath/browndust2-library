---
title: Frost and Darkness lockdown
description: Slow and blind the enemy's attackers so fewer of their hits happen and land.
tested: false
---

# Frost and Darkness lockdown

Instead of out-damaging the enemy, make them hit less often and miss more. [[Frost]] slows every enemy character and [[Darkness]] lowers their accuracy, so together they cut the damage coming at you.

!!! note "Theorycraft"
    Worked out from the gear and status text on this site, not from a tested run. Update it once you've tried it.

```board
name: Lockdown gear
season: s3
summary: Frost from a support at battle start, Darkness and more Frost from the attacker's hits.
members:
  - unit: liatris-rodevs-star
    role: Darkness / Attacker
    note: 50% chance per hit to apply 1 Darkness (−5% enemy Accuracy each).
    gear: [heros-staff]
  - unit: liberta-onsen-manager
    role: Frost / Support
    note: 4 Frost at battle start (−8% enemy Action Speed).
    gear: [knights-staff]
notes: Knight's Staff does different things depending on who holds it. On a support it applies 4 Frost at battle start; on an attacker it applies 1 Frost on half its hits.
```

## The numbers

| Source | Tokens | What it applies |
|---|---|---|
| Knight's Staff on a non-attacker | 6 | 4 Frost at battle start: enemy Action Speed −8% |
| Knight's Staff on an attacker | 6 | 50% chance per hit: 1 Frost (−2% Action Speed) |
| Hero's Staff on an attacker | 9 | 50% chance per hit: 1 Darkness (−5% Accuracy) |

Darkness is the stronger stack: each one takes 5% off enemy accuracy, against 2% speed for Frost. Ten Darkness stacks take 50% off enemy accuracy.

## Counter-pick: when the enemy uses Darkness

Check **View Formation** before every phase. If the enemy applies Darkness to you, **Peerless Javelin** (15) on your attacker adds 200% Accuracy Rate and 20% Crit Rate at battle start, which overrides a lot of Darkness. On a support it gives 5 [[Focus]] instead, adding 25% accuracy to every character.

## Pairs well with

- [Energy Guard wall](energy-guard-wall.md): the shield lasts much longer when half the enemy's hits miss.
- [Poison stack](poison-stack.md): Poison doesn't need to hit, so slowing the enemy only buys it more time.
