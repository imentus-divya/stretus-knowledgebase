# India Algo Trading Knowledge Base — Table of Contents

Index for systematic and algorithmic trading on **Indian stock markets** (primarily **NSE** / **BSE** cash equity and **NSE F&O**). Use this TOC to navigate slugs in your own API or documentation site.

---

## How to use this knowledge base

- **New to Indian markets:** Read **1 → 2 → 6** first (structure, products, data/execution).
- **Building strategies:** Read **3 → 4** (concepts, design), then **5** (risk).
- **Compliance / ops:** Emphasize **1**, **2**, and **6**; cross-check SEBI/NSE circulars.

---

# 1. Indian Market Foundations

**File:** `01-indian-market-foundations.md`  
**Slug:** `01-indian-market-foundations`

SEBI’s role, exchange ecosystem (NSE, BSE), market phases, circuit filters, surveillance, and what “algo trading” means in the Indian regulatory sense.

**Tags:** sebi, nse, bse, circuit-limit, algo-trading, surveillance

---

# 2. Indian Instruments & Mechanics

**File:** `02-indian-instruments-mechanics.md`  
**Slug:** `02-indian-instruments-mechanics`

Cash equity, rolling settlement **T+1**, **F&O** (futures & options), contract specs, **margin** and **SPAN**, **STT** and common charges, **currency** and **commodity** (brief), **SLB** overview.

**Tags:** t1-settlement, futures, options, span, stt, margin, nse-fo

---

# 3. Core Trading Concepts (India Context)

**File:** `03-core-trading-concepts-india.md`  
**Slug:** `03-core-trading-concepts-india`

Indices (**Nifty**, **Bank Nifty**, etc.), sector structure, session behaviour, gaps, impact of **pre-open** / **call auction**, retail vs institutional flow, common retail patterns adapted to Indian session length and tick structure.

**Tags:** nifty, bank-nifty, pre-open, session, liquidity

---

# 4. Strategy Design & Algo Development (India)

**File:** `04-strategy-design-algo-india.md`  
**Slug:** `04-strategy-design-algo-india`

From idea to deployment: bar construction, timezone (**IST**), corporate actions, survivorship, backtest realism (costs, gaps, halts), paper trading, **SEBI** expectations around algos and controls at broker level.

**Tags:** backtest, ist, corporate-actions, algo-controls, paper-trading

---

# 5. Risk Management (India)

**File:** `05-risk-management-india.md`  
**Slug:** `05-risk-management-india`

MTM, margin shortfall, **peak margin** concepts, position limits, single-stock concentration, **F&O** leverage risk, currency risk for foreign participants, operational risk (broker API, colocation).

**Tags:** mtm, peak-margin, leverage, concentration, operational-risk

---

# 6. Data & Execution (India)

**File:** `06-data-and-execution-india.md`  
**Slug:** `06-data-and-execution-india`

Data vendors vs exchange feeds, **ISIN** / **symbol** mapping, adjustments (splits, bonuses, dividends), auction days, **Muhurat** and special sessions, order types on Indian OMS, **co-location** at high level.

**Tags:** isin, tick-data, corporate-actions, colocation, order-types

---

# 9. Glossary (India)

**File:** `09-glossary-india.md`  
**Slug:** `09-glossary-india`

Abbreviations and terms: SEBI, NSCCL, VIX India, ASM/GSM, ASM long-term, etc.

**Tags:** glossary, definitions, abbreviations

---

## Suggested reading order

1. Foundations → Instruments → Data & Execution  
2. Core concepts → Strategy design  
3. Risk management (parallel to strategy iteration)  
4. Glossary as lookup

---

## Relationship to the original `knowledge-base/`

The parent repo’s chapters (e.g. generic microstructure, options Greeks, backtesting philosophy) **complement** this set. This India KB **does not replace** universal quant content—it **anchors** it to **Indian regulation, calendars, and microstructure**.
