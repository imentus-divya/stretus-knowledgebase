# 4. Strategy Design & Algo Development (India)

From **research** to **live** for Indian markets: data choices, backtesting discipline, and **operational** requirements.

---

## 4.1 Define the edge and the universe

### Universe filters

- **Minimum daily turnover** (INR) or **ADV** shares
- **Exclude** ASM/GSM stages your broker forbids
- **F&O** availability if strategy needs **hedge** or **short** via derivatives

### Edge types

- **Cross-sectional** (rank stocks daily)
- **Time-series** (signals on single name or index)
- **Event** (earnings drift, index rebalance)

Document **holding period**, **rebalance frequency**, and **capacity** in **INR** terms.

---

## 4.2 Bar data and timezone

### IST everywhere

Store timestamps in **UTC** or **IST** consistently; label **session** explicitly. Mixed timezone bugs corrupt **session open/close** logic.

### Corporate time

**Splits/bonus** adjust historical prices or use **total return** indices for **benchmark** comparison—be explicit in code.

---

## 4.3 Backtesting: India-specific realism

### Costs

- **STT** + **exchange/SEBI/GST/brokerage** + **slippage**
- **F&O**: include **bid-ask** on entry/exit where you do not assume mid

### Halts and limits

- Model **no-fill** on **circuit** or **halt**
- Avoid **look-ahead** through **surveillance lists** (use **point-in-time** flags if you simulate them)

### Survivorship

Universes like “current Nifty 50” **ex post** inflate backtests. Use **historical constituents** or accept **bias disclosure**.

---

## 4.4 Walk-forward and out-of-sample

### Why it matters

Indian markets **regime-shift** with **policy**, **margin rules**, and **participation**. **Single-window** fit overstates robustness.

### Practice

- **Train** parameters on older windows; **validate** on forward windows
- Track **degradation** after major rule changes (e.g. margin, STT tweaks)

---

## 4.5 Paper trading and shadow mode

### Paper

Use **broker paper** or **exchange-simulated** feeds where available; match **order types** and **latency** assumptions to production.

### Shadow

Run **live data** with **disabled sends** to compare **signal** vs **sim fill**—catches **clock skew** and **master data** bugs.

---

## 4.6 Algo governance (conceptual checklist)

Work with your **compliance** and **broker**; typical themes include:

- **Unique algo identifier** per strategy
- **Change control** (versioned releases)
- **Kill switch** and **max loss** per day/strategy
- **Audit logs** (decision → order → fill)

---

## 4.7 Execution algorithms

### Slicing

**TWAP/VWAP/Iceberg** behaviour depends on **broker OMS**; Indian **tick sizes** and **queues** favour **patient** execution on illiquid names.

### Market vs limit

- **Market** / **marketable limit** for urgency
- **Limit** for cost; risk **non-fill** in fast markets

---

## 4.8 From research notebook to production

### Minimum promotion criteria

- **Deterministic** builds (pinned dependencies)
- **Config-driven** parameters (no magic numbers in prod)
- **Health checks** on data freshness (late feed = **flat** or **halt** trading)
- **Monitoring**: PnL, drawdown, order reject rate, latency

---

## Summary

Indian algo design = **correct universe + IST data + honest costs + point-in-time surveillance + governance**. Without these, “sharp” backtests rarely survive contact with **NSE reality**.
