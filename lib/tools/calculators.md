---
title: Calculators
description: Reroll cost, discount and sell value, and End Game damage at any second.
---

# Calculators

## Rerolls

The first four rerolls in a phase cost 1 token each, then the cost goes up by 1 every four rolls.

<div class="swg-calc" data-calc="reroll" markdown="0">
  <label>Rerolls this phase <input type="number" min="0" max="40" value="4" data-in="n"></label>
  <p class="swg-calc__out" data-out></p>
</div>

## Discount and sell value

<div class="swg-calc" data-calc="price" markdown="0">
  <label>Shop price <input type="number" min="1" max="30" value="5" data-in="p"></label>
  <label class="swg-check"><input type="checkbox" data-in="prot"> Protection Tile</label>
  <p class="swg-calc__out" data-out></p>
</div>

## End Game damage

Starts at 20 seconds. Climbs by 1 every 3 seconds until 48 seconds, then about 11% every 3 seconds.

<div class="swg-calc" data-calc="endgame" markdown="0">
  <label>Battle time, seconds <input type="range" min="0" max="90" value="60" data-in="t"> <output data-t>60</output></label>
  <p class="swg-calc__out" data-out></p>
  <div class="swg-spark" data-spark aria-hidden="true"></div>
</div>
