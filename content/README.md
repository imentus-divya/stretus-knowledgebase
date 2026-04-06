# India Algo Trading Knowledge Base

Structured markdown chapters for an **Indian equities / derivatives** algo platform. Inspired by the layout of `knowledge-base/` in this repo (foundations → instruments → concepts → strategy → risk → reference), but **India-specific**: venues, regulation, settlement, taxes, and operational realities.

**Disclaimer:** Rules, margins, charges, and circulars change. Treat this as **educational scaffolding**—verify against current **SEBI**, **NSE**, **BSE**, and **NSCCL** / **ICCL** disclosures before production or compliance decisions.

## Files (slugs for your own server or docs)

| Slug (suggested) | File |
|------------------|------|
| `00-india-toc` | `00-table-of-contents-india.md` |
| `01-indian-market-foundations` | `01-indian-market-foundations.md` |
| `02-indian-instruments-mechanics` | `02-indian-instruments-mechanics.md` |
| `03-core-concepts-india` | `03-core-trading-concepts-india.md` |
| `04-strategy-design-algo-india` | `04-strategy-design-algo-india.md` |
| `05-risk-management-india` | `05-risk-management-india.md` |
| `06-data-execution-india` | `06-data-and-execution-india.md` |
| `09-glossary-india` | `09-glossary-india.md` |

## Using with a Mangrove-style server

Point `DocumentLoader` at this folder (or merge these files into your main `knowledge-base/` after review). Search and cross-reference will work the same way if your indexer reads markdown from a directory.

## What is not duplicated here

- **Indicator math** (RSI, MACD, etc.) is largely **market-agnostic**; reuse standard references or your existing `06-indicators`-style doc and add an “India context” section (session gaps, rupee ticks, lot sizes).
- **Signal catalogs** should be **your** platform’s registry names, not Mangrove’s.
