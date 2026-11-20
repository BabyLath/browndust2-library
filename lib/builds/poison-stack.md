---
title: Poison stack
description: Stack Poison and other debuffs, heal enough to outlast End Game.
tested: true
---

# Poison stack

Pile debuffs, Poison above all, onto the enemy while enough sustain keeps you alive for the stacks to finish the fight. This is the approach the BD2 Tactical Compendium recommends.

```board
name: Damage dealers
summary: Running two is enough, three or more at once usually drains the shared Stamina pool so make sure to have a stamina battery if running more thant two.
total: false
members:
  - unit: nebris-labyrinth-gatekeeper
  - unit: nebris-laid-back-lifeguard
  - unit: gray-mist-man
```

```board
name: Supports and debuffers
summary: Fill the rest of the board from these as the shop offers them.
total: false
members:
  - unit: celia-the-curse
  - unit: palette-shattered-dream
  - unit: levia-overheat
  - unit: liberta-onsen-manager
notes: Watch the Stamina meter at the top of the formation screen. Every attacker draws from one pool.
```

## Why it works

Each [[Poison]] stack deals 1 damage every 2 seconds, so 10 stacks is 5 damage a second that costs no Stamina. By 60 seconds End Game hits both sides for 16 a second, so the stacks need to be in place well before then, leaving the opponent with more tick damage.

The strategy is great against enemy formations that stops you from doing attacks, usually from debuffs and/or [[Counter]], it is also great for long fights as you stack more Poison on the opponent.
