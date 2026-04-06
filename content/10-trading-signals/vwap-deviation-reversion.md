---
tags: [trading-signals, vwap, intraday, mean-reversion]
---

# VWAP deviation reversion

**VWAP** (volume-weighted average price) anchors intraday **fair value** for many traders. A common idea is **mean reversion** when price stretches **too far** from VWAP—often used for liquid NSE cash and derivatives with tight spreads.

## Overview

VWAP resets each session (typical implementation). Deviations can reflect **imbalance** (aggressive buying/selling) or **news**—context matters.

## Signal definition (conceptual)

- **Fade / reversion cue**: price trades **beyond** a deviation band from VWAP (e.g. σ-bands or fixed %), then shows **stalling** behaviour.
- **Trend / breakout cue**: price **holds** away from VWAP with **volume** support—some traders treat that as continuation rather than reversion.

## Parameters (typical)

| Idea | Example |
|------|---------|
| Band | ±1σ/±2σ around VWAP |
| Confirmation | candle pattern, volume spike, or time-of-day rules |

## How to interpret

VWAP strategies are sensitive to **auction dynamics** and **event risk** (results, policy). Avoid illiquid names where a few prints move price.

## Risks and limitations

Mean reversion fails in strong trend days. Educational only—not investment advice.
