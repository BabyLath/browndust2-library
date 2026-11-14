---
title: Poison stack
description: Stack Poison and other debuffs, heal enough to outlast End Game.
tested: false
---

# Poison stack

Pile debuffs, Poison above all, onto the enemy while enough sustain keeps you alive for the stacks to finish the fight. This is the approach the BD2 Tactical Compendium recommends.

```board
name: Damage dealers (pick one)
season: s3
summary: All three have performed well. Running two at once usually drains the shared Stamina pool.
total: false
members:
  - unit: liatris-rodevs-star
  - unit: rubia-thorn-of-the-desert
  - unit: blade-apostle
```

```board
name: Supports and debuffers
season: s3
summary: Fill the rest of the board from these as the shop offers them.
total: false
members:
  - unit: celia-the-curse
  - unit: refithea-pure-white-blessing
  - unit: levia-overheat
  - unit: liberta-onsen-manager
  - unit: palette-shattered-dream
notes: Watch the Stamina meter at the top of the formation screen. Every attacker draws from one pool.
```

## Why it works

Position doesn't affect targeting, so the layout only needs to fit the pieces and any tile bonuses. What matters is Stamina: one attacker with debuffers around it spends the pool on hits, while Poison ticks for free.

Each [[Poison]] stack deals 1 damage every 2 seconds, so 10 stacks is 5 damage a second that costs no Stamina. By 60 seconds End Game hits both sides for 16 a second, so the stacks need to be in place well before then.

## Gear and tiles

!!! note "Theorycraft"
    This section is worked out from the gear and tile text on this site, not from a tested run. Update it once you've tried it.

```board
name: Poison gear
season: s3
summary: Cheap gear that adds Poison on its own, on top of what the units apply.
members:
  - unit: celia-the-curse
    role: Poison / Debuffer
    note: Knight's Necklace on a Curse character, 50% chance per cooldown to add Poison.
    gear: [knights-necklace]
  - unit: liatris-rodevs-star
    role: Poison / Attacker
    note: Mercenary Staff, 50% chance per hit to add Poison.
    gear: [mercenary-staff]
  - unit: refithea-pure-white-blessing
    role: Poison / Opener
    note: Mercenary Sword on a non-attacker, 3 Poison at battle start.
    gear: [mercenary-sword]
tiles:
  - tile: curse-tile
    note: 25% chance per cooldown to apply a random debuff to the unit standing on it.
notes: Mercenary Staff and Mercenary Sword have identical effects, so buy whichever the shop offers. Knight's Necklace only adds Poison on a Curse character; on anyone else it gives SP instead.
```

- **Knight's Necklace** (5) on a Curse character: every cooldown has a 50% chance to apply 1 Poison.
- **Mercenary Staff or Sword** (4 each) on your attacker: 50% chance per hit to apply 1 Poison. On anyone else: 3 Poison at battle start.
- **Curse Tile** (6) under a unit with a short cooldown: 25% chance per cooldown to apply a random debuff. It isn't always Poison, but every debuff helps.

Source: [BD2 Tactical Compendium, Strategy](https://botan14xd.github.io/BD2-Overview/content-packs/soul-wager/#strategy), October 22 update.
