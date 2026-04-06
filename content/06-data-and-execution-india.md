# 6. Data & Execution (India)

Building blocks for **clean signals** and **reliable fills** on Indian venues.

---

## 6.1 Security master

### Minimum fields

- **Exchange**, **symbol**, **series** (EQ/BE/etc.), **ISIN**
- **Lot size** (F&O), **tick size**, **instrument type**
- **Listing / delisting** dates, **suspension** flags where available

### Why it breaks algos

**Corporate actions** and **reclassifications** without master updates → wrong **quantities**, wrong **options** chains.

---

## 6.2 Price and corporate actions

### Adjustments

Choose one:

- **Adjusted** historical prices (splits/bonus) for **continuous** technical signals
- **Unadjusted** + **corporate action** event table for **accurate PnL** simulation

### Dividends

**Cash dividend** ex-dates drop spot; **total return** series needed for **some** factor designs.

---

## 6.3 Data vendors vs direct feeds

### Vendors

Convenience, **cleaning**, **survivorship-bias-aware** universes (premium products).

### Exchange / colocation feeds

Lower latency, higher **engineering** burden; **co-lo** is regulated and **contractual**.

### Algo starter path

**Vendor EOD** + **broker intraday** for execution; upgrade when **latency** becomes the bottleneck.

---

## 6.4 Bar construction pitfalls

### Auction trades

Mis-typing **auction** vs **continuous** trades **distorts** OHLC.

### Out-of-sequence

Handle **trade corrections** and **cancelled** trades per vendor spec.

---

## 6.5 Order types (conceptual)

Indian brokers/exchanges support variants of:

- **Limit**, **market**, **SL**, **SL-M**, **iceberg** (where available)
- **Day** vs **IOC** semantics

Map **your abstract order** model to **broker OMS** explicitly—**partial fills** and **modify** behaviour differ.

---

## 6.6 Special sessions

### Muhurat trading

**Short** **Diwali** session—**liquidity** and **spread** differ; many strategies should **opt out**.

### Other special sessions

Verify **circulars** for **joint holidays**, **restricted** sessions, or **mock** sessions.

---

## 6.7 Backtesting data quality

### Checks

- **Null** bars vs **halt**
- **Volume** spikes on **splits** if unadjusted
- **Symbol changes** and **name changes** (same ISIN)

---

## 6.8 Logging for forensics

Log **signal snapshot**, **risk checks**, **order request**, **ack**, **fill**, **reject reason**, **margin snapshot** (if available). Indian dispute and **audit** scenarios reward **structured** logs.

---

## Summary

India data/execution = **strong security master** + **explicit adjustment policy** + **broker order mapping** + **special session** handling. This layer is as important as **alpha code**.
