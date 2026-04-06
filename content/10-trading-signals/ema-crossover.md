---
tags: [trading-signals, trend-following, moving-average]
---

# EMA crossover

A classic **trend-following** idea: when a faster exponential moving average (EMA) crosses above a slower EMA, it is often treated as bullish; a cross below as bearish. Commonly used on liquid NSE/BSE names and index futures when you want a simple, rules-based regime filter.

## Overview

You track two EMAs of price (usually close), for example **9/21** or **12/26**. The *signal* is the **crossing event**, not the absolute level of price.

## Signal definition

- **Long / risk-on bias**: fast EMA crosses **above** slow EMA.
- **Short / risk-off bias**: fast EMA crosses **below** slow EMA.

Some traders require the cross to happen **after** a minimum separation (filter chop) or only in the direction of a higher-timeframe trend.

## Parameters (typical)

| Parameter | Common starting points |
|-----------|-------------------------|
| Fast EMA | 9, 12 |
| Slow EMA | 21, 26, 50 |
| Timeframe | 5m–1D depending on hold period |

## How to interpret

Crossovers **lag** price; they shine in **trending** phases and whipsaw in **range-bound** markets. Pair with **ATR** or **ADX** if you want to avoid low-quality crosses in flat markets.

## Risks and limitations

Past behaviour does not guarantee future results. Slippage, gaps, and session-specific behaviour (open, Muhurat, circuit limits) matter on Indian markets. This note is **educational**, not investment advice.
