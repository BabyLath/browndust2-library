---
title: Build name
description: One line shown in the builds list and search results.
---

# Build name

What the build is trying to do, in two or three sentences.

```board
name: Build name
season: s3                 # a season id from content/seasons.yaml
summary: One line under the diagram.
# Optional. 7 rows of 7 characters. "." is empty; any other character is a piece.
# Units and tiles use their own letters. Leave layout out to show just the piece list.
layout: |
  AA.BB..
  AA.BB..
  .......
  CCCC...
  .......
  .......
  .......
pieces:
  A: liatris-rodevs-star   # unit or tile id
  B: celia-the-curse
  C: curse-tile
gear:                       # optional: unit letter -> gear ids
  A: [knights-sword]
notes: Optional tip shown under the piece list.
```

## How to play it

Shop priorities by phase, what to reroll for, when to sell.
