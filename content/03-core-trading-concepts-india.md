# 3. Core Trading Concepts (India Context)

Universal technical and microstructure ideas still apply; this chapter highlights **how Indian session structure, indices, and flow** change day-to-day trading.

---

## 3.1 Major indices and benchmarks

### Nifty 50

Broad **large-cap** benchmark; futures and options are among the most liquid derivatives globally by contract count.

### Bank Nifty (and financials)

**Banking** concentration; **higher beta** and **event risk** around RBI policy, earnings seasons, and macro prints.

### Sectoral and thematic indices

**IT**, **Pharma**, **Metal**, **Midcap**, **Smallcap** indices help structure **rotation** and **pairs** ideas—liquidity varies sharply vs Nifty.

### Practical note

Index **weights** and **rebalancing** create **predictable flows**; your data pipeline should ingest **rebalance announcements**.

---

## 3.2 Session shape and volatility

### Intraday rhythm

- **Opening** period often has **wider spreads** and **auction-imprinted** opens.
- **Mid-session** can be **quieter** in many names; **closing** hour sees **institutional** balancing.

### Bar construction

Decide explicitly:

- **Time bars** (e.g. 5-minute **IST**)
- **Session boundaries** (exclude pre-open or model separately)
- **Auction prints** as separate event types vs first continuous trade

---

## 3.3 Tick size, lot size, and price granularity

### Tick size

Exchanges specify **minimum price increments**; they can change with **price bands** or **corporate actions**.

### Lot size

**F&O** **lot sizes** are **periodically revised**—stale lot sizes break **position sizing** and **P&L** options math.

---

## 3.4 Corporate action seasonality

### Earnings

**Heavy clustering** in **quarterly** windows; **gap risk** on announcement days is **larger** than on “random” days for many mid-caps.

### Dividends and splits

**Ex-dates** affect **spot** series; your **total return** vs **price return** choice matters for **momentum** and **carry** style signals.

---

## 3.5 Retail vs institutional footprint (conceptual)

### Observations (not laws of nature)

- **Retail** flow can dominate **options** OI in certain underlyings.
- **Institutions** may trade **index** and **single-stock** futures for **beta** adjustments.

### Algo design

- **Microcap** strategies face **different adversarial selection** than **Nifty** scalping.
- **Capacity** is a function of **ADV** and **impact**, not only signal strength.

---

## 3.6 Currency and macro sensitivity

### USDINR and crude (indirect)

Many **large caps** have **FX** or **commodity** exposure; **macro** days move **correlations** across the book.

### RBI and policy

**Rate decisions** and **liquidity** operations affect **banks** and **rate-sensitive** sectors first, then broader risk appetite.

---

## 3.7 Calendar effects (India-specific)

### Holidays

**Exchange holidays** differ from US/Europe; **joint holidays** with banking system matter for **settlement** and **MF flows**.

### Budget and event risk

**Union Budget** and major **policy** events can create **gap** and **volatility regime** shifts—**risk-off** logic belongs in execution layer.

---

## Summary

India context = **index ecosystem**, **IST session shape**, **lot/tick hygiene**, **earnings and macro calendar**, and **capacity realism**. Layer universal TA/quant concepts on top of this **local** structure.
