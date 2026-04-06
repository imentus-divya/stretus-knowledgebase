---
tags: [trading-signals, opening-range, breakout, intraday]
---

# Opening range breakout (ORB)

**Opening range breakout** defines a **high–low box** from the first **N minutes** of the session and trades a **breakout** beyond that range—often with volume confirmation. It is widely discussed for intraday NSE sessions (with caveats around the opening auction and volatility).

## Overview

ORB tries to capture **early imbalance** after the open. It works best when the day develops a **directional auction**; it fails on **two-sided chop**.

## Signal definition

- **Long**: price **closes above** the opening range high after the OR window ends (timing rules vary).
- **Short**: price **closes below** the opening range low.

Filters often include **max width** of the OR (avoid huge ranges) and **news avoidance**.

## Parameters (typical)

| Parameter | Common values |
|-----------|----------------|
| OR window | 15–30 minutes |
| Confirmation | 5m/15m close, volume spike |

## How to interpret

India’s open can be **volatile**; spreads and slippage matter. Consider **paper trading** and **small size** while learning.

## Risks and limitations

False breakouts are frequent. Educational content only—not investment advice.
