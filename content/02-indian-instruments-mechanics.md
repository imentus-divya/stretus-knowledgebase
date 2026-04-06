# 2. Indian Instruments & Market Mechanics

How **cash equity**, **derivatives**, **settlement**, **taxes**, and **margins** work for Indian algo strategies.

---

## 2.1 Cash equity (spot segment)

### Definition

Buying/selling shares for **delivery** or **intraday square-off** in the **cash** segment. **Intraday** must be closed same day per broker product rules; **delivery** goes to settlement.

### Settlement: T+1 (rolling)

India has moved to **T+1 rolling settlement** for equities (verify current SEBI/exchange notices for any segment-specific timing). **Funds and securities** settle on defined cycles; your **backtest** PnL timing should align with **when you assume fills settle**, not only trade date.

### ISIN and symbols

- **ISIN** identifies the security globally; exchanges use **symbol** + series (e.g. **EQ**).
- Algo systems need a **security master** mapping **broker symbol ↔ ISIN ↔ exchange token**.

---

## 2.2 Equity derivatives (F&O)

### Futures

- **Contract multiplier** = **lot size × index points** (index) or **lot size × price** (stock fut).
- **Expiry**: monthly (and weekly for major indices on NSE—verify current contract calendar).
- **Mark-to-market (MTM)** daily until close or roll.

### Options

- **European-style** index options are standard for many Indian index products (verify contract specs).
- **Margins** are portfolio-based in practice via **SPAN** + **exposure** + **additional** margins.

### Rolling positions

- **Roll** near expiry to next month: model **spread slippage** and **liquidity** at roll window.

---

## 2.3 SPAN margin (conceptual)

### Definition

**SPAN** (Standard Portfolio Analysis of Risk) is a **scenario-based** margining system used for **F&O**. Clearing computes **initial** and **exposure** requirements using **position** and **volatility** assumptions.

### Algo implications

- **Backtests** that ignore margin changes **overstate** capacity.
- **Stress** your book under **margin hike** scenarios (events, volatility spikes).

---

## 2.4 STT, charges, and realistic backtests

### Securities Transaction Tax (STT)

**STT** applies to **cash** and **derivatives** at rates defined by law; rates differ by **instrument** and **side** (buy/sell, option exercise, etc.). Always use **current** finance act schedules.

### Other costs

- **Exchange** transaction charges, **SEBI** fees, **GST** on brokerage and charges, **stamp duty** (state-dependent for some legs).
- **Brokerage** is negotiable; **slippage** is often larger than all fees for small-cap strategies.

### Backtest rule of thumb

Use a **round-trip cost model** (bps + fixed per order) + **slippage model** scaled by **ADV** and **spread**.

---

## 2.5 Currency derivatives (brief)

NSE/BSE offer **currency futures and options** (USDINR, etc.). Useful for **hedging** or **FX strategies**; separate margin and holiday calendars from equity.

---

## 2.6 Commodity derivatives (brief)

**MCX**, **NCDEX**, etc., are **separate** ecosystems (different regulator history merged under SEBI). If your platform is **equity-only**, document that scope clearly.

---

## 2.7 Securities Lending & Borrowing (SLB)

### Concept

**SLB** allows **borrowed** stock for **short delivery** / arbitrage; retail access varies by broker.

### Algo note

**Short cash** restrictions mean many retail algos use **F&O** for directional **short** exposure instead of borrowed stock.

---

## 2.8 Peak margin and intraday leverage (conceptual)

SEBI has evolved rules on **upfront margin** and **peak margin** reporting for clients. Brokers enforce **collection** and **shortfall** penalties.

### Algo implications

- **Leverage** in UI may not equal **regulatory margin** at all times.
- Systems should read **broker margin API** where available, not hard-code “5× intraday.”

---

## Summary

Indian mechanics = **T+1 cash**, **F&O with SPAN**, **STT-heavy cost stack**, and **broker-enforced margins**. Algo PnL without these layers is **fiction**.
