# 5. Risk Management (India)

Risk for Indian algo books combines **classic trading risk** with **margin regime**, **INR** economics, and **operational** dependence on brokers and data vendors.

---

## 5.1 Risk dimensions (recap, India-accented)

| Dimension | Indian nuance |
|-----------|----------------|
| **Per-trade** | STT + slippage often larger than US for same notional in mid-caps |
| **Leverage** | F&O **SPAN** hikes in stress; **intraday** limits broker-specific |
| **Concentration** | Single-stock **circuit** can trap positions |
| **Liquidity** | **ADV** collapses outside top names |
| **Operational** | **API** outage at open is a **tail** event |

---

## 5.2 Position sizing in INR

### Notional vs risk

Size by **max loss per trade** in **INR**, not only “2% of account” if account mixes **cash + F&O**.

### F&O notional

**Lot** × **price** × **multiplier** (index) can be **large** vs margin—**gap** through stop is **non-linear** risk.

---

## 5.3 Drawdown controls

### Strategy-level

- **Daily max loss** → **flatten** and **lock** until human review
- **Max consecutive losses** → **reduce size** or **pause**

### Portfolio-level

- **Correlation** across **Bank Nifty** proxies can spike—**diversification** on paper vanishes in stress.

---

## 5.4 Stop-loss engineering

### Gaps

**Overnight gaps** on cash stocks can **skip** technical stop levels; **options** or **futures** hedges change payoff but add **basis** and **theta**.

### Circuit scenarios

If **sell-only** or **halt** states exist, **stops** may not **execute** as in continuous backtest—**scenario** testing required.

---

## 5.5 Margin shortfall and broker actions

### Peak margin awareness

Intraday **leverage** can **compress** if **peak** requirements rise; broker may **square-off** positions **automatically**.

### Algo response

- Subscribe to **margin utilization** where API exists
- **Throttle** new entries when **utilization** > threshold

---

## 5.6 Currency risk (for FPIs or INR-funded offshore)

If capital is **non-INR**, **P&L** in **USD** terms includes **FX** path—hedge policy belongs in **risk policy** doc.

---

## 5.7 Operational risk

### Checklist

- **Redundant** data feed or **stale-data halt**
- **Order idempotency** (retry safety)
- **Clock sync** (NTP) for **time-triggered** strategies
- **Secrets** rotation for API keys

---

## 5.8 Regulatory and surveillance risk

### Universe hygiene

Trading **ASM/GSM** names without understanding restrictions can cause **forced actions** or **higher margins**.

### Reporting

Maintain **logs** suitable for **broker** or **regulatory** inquiry—**retention** policy should be explicit.

---

## Summary

Indian risk management = **INR-native sizing** + **margin-aware** controls + **gap/circuit** honesty + **broker ops** resilience. Treat **surveillance lists** and **rule changes** as **first-class** risk factors.
