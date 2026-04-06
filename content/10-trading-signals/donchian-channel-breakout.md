---
tags: [trading-signals, donchian, breakout, trend]
---

# Donchian channel breakout

**Donchian channels** plot the highest high and lowest low over **N** periods. A classic **breakout** signal is a close above the **upper** channel (long) or below the **lower** channel (short)—popular in systematic trend strategies and adaptable to Indian futures with proper sizing.

## Overview

Donchian breakouts are **simple and transparent**: you trade **new highs/lows** in a window. The trade-off is **whipsaws** when markets range.

## Signal definition

- **Long breakout**: price **closes above** the prior N-bar **highest high** (implementation-specific).
- **Short breakout**: price **closes below** the prior N-bar **lowest low**.

Filters often include **time stops**, **ATR stops**, or **volume**.

## Parameters (typical)

| Parameter | Common values |
|-----------|----------------|
| Lookback N | 20 (Turtle-style), 55, etc. |

## How to interpret

Works best when **trend persistence** exists. In India, watch **gap risk** and **overnight** exposure on derivatives.

## Risks and limitations

Breakout systems can have long losing streaks in chop. Not investment advice.
