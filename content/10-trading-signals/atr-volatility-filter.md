---
tags: [trading-signals, atr, volatility, risk]
---

# ATR volatility filter

**Average True Range (ATR)** estimates **how much** an instrument typically moves. Many traders use ATR as a **filter** (trade only when volatility is in-range) or to **size positions** and set **stops**—directly relevant to risk management on Indian cash and F&O.

## Overview

ATR is **not directional**—it measures **movement scale**. Higher ATR → larger typical swings; lower ATR → quieter tape.

## Signal definition (as risk tooling)

- **Position sizing**: risk per trade / ATR → smaller size when volatility is high (common approach).
- **Stop placement**: stop distance as **k × ATR** (k chosen by style).
- **Regime filter**: skip strategies that assume quiet markets when ATR spikes (event windows).

## Parameters (typical)

| Parameter | Common values |
|-----------|----------------|
| ATR period | 14 |
| Multiplier k | 1.5–3 for stops (example) |

## How to interpret

ATR changes with **corporate events**, **index moves**, and **liquidity**. Always align stops with **exchange limits** and your broker’s margin rules.

## Risks and limitations

ATR-based sizing reduces blow-up risk but does not guarantee returns. Not investment advice.
