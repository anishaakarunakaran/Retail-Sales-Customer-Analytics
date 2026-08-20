# Retail Sales & Customer Analytics — Management Report

**Prepared by:** Data Analyst
**Period covered:** 1 Jan 2021 – 31 Dec 2024
**Scope:** 108,045 completed order lines | 33,209 orders | 1,648 active customers
**Data:** cleaned retail transactions (see `data/cleaned/retail_sales_clean.csv`)

---

## 1. Executive Summary

The business delivered **$68.9M revenue** and **$16.4M profit** (23.8% margin)
over four years, growing **+22.1%** (CAGR 6.9%). Demand is strongly seasonal:
**December is the peak month at 2.4x July.**

Three strategic issues require management attention:

1. **Revenue growth is decelerating** while **new customer acquisition has
   collapsed** (1,312 new customers in 2021 → 66 in 2024). The company is
   over-reliant on an existing base.
2. **Revenue is dangerously concentrated** — the top 25% of customers drive
   **74%** of revenue, and Champions + Loyal customers (33% of customers) drive
   **80%**.
3. **Blanket discounting is destroying profit.** Lines with 30%+ discounts are
   loss-making (−8.2% margin, −$305K in 2024 alone) yet produce **no measurable
   volume lift** (r = 0.004).

The recommendations below are prioritised by financial impact and are each
traceable to evidence in this report.

## 2. Sales Performance

| Metric | Value |
|---|---|
| Total revenue | $68,905,247 |
| Total profit | $16,396,834 |
| Profit margin | 23.8% |
| Total orders | 33,209 |
| Average order value | $2,074.90 |
| Units sold | 324,562 |

**Yearly progression**

| Year | Revenue | YoY | Profit |
|---|---|---|---|
| 2021 | $15.59M | — | $3.69M |
| 2022 | $16.39M | +5.1% | $3.96M |
| 2023 | $17.88M | +9.1% | $4.24M |
| 2024 | $19.04M | +6.5% | $4.51M |

**FINDING → EVIDENCE → IMPACT → RECOMMENDATION**
- **Finding:** Growth is positive but volatile and slowing (YoY 5.1% → 9.1% → 6.5%).
- **Evidence:** yearly table above; CAGR 6.9% with late-period deceleration.
- **Impact:** extrapolating current trajectory, growth will continue to cool.
- **Recommendation:** treat customer retention and reactivation — not new-site
  traffic alone — as the primary growth lever.

## 3. Customer Insights

- 1,648 active customers; **9% are one-time buyers**, 91% repeat.
- **High-value customers (top 25% by spend, n=412) contribute 74% of revenue.**
- Segment AOV: Corporate **$2,558** > Small Business **$2,240** > Home Office
  **$1,618** > Consumer **$1,221**.
- **New customers by year:** 2021: 1,312 → 2022: 185 → 2023: 85 → 2024: 66.
- Customer **age does not predict spend** (r = 0.001, p = 0.95); segment and
  behaviour do — the difference in spend across segments is statistically
  significant (ANOVA F = 137.4, p < 0.001).

**FINDING → EVIDENCE → IMPACT → RECOMMENDATION**
- **Finding:** Acquisition funnel is drying up while value concentrates in a few
  hundred accounts.
- **Evidence:** new-customer counts above; 74% revenue from 412 customers.
- **Impact:** churn of even a few Champions directly moves quarterly revenue.
- **Recommendation:** launch a **Champion retention programme**, a **win-back
  campaign** for At-Risk and Can't-Lose customers (worth $4.0M), and a
  structured B2B outreach to Corporate/Small Business, the highest-AOV segments.

## 4. Product Insights

| Category | Revenue | Share | Margin |
|---|---|---|---|
| Technology | $26.2M | 38% | **12.4%** |
| Furniture | $24.4M | 35% | 29.6% |
| Home & Lifestyle | $11.6M | 17% | **35.5%** |
| Office Supplies | $6.8M | 10% | 27.1% |

- Top product by revenue: **CoreX Computer 3 — $3.89M** at only **7.3% margin**.
- Most profitable product: **Oakline Chair 2 — $563K profit**.
- The top 20% of products generate **54.6%** of revenue (Pareto effect).
- **High-sales / low-profit products** are concentrated in Technology:
  CoreX Computer 3 (7.3%), CoreX Phone 2 (7.7%), CoreX Phone 6 (7.7%),
  CoreX Computer 4 (7.9%).

**FINDING → EVIDENCE → IMPACT → RECOMMENDATION**
- **Finding:** Technology drives volume but carries a third of the company's
  average margin (12.4% vs 23.8%).
- **Evidence:** category table; 5 of the top 10 revenue products sit at 7–9% margin.
- **Impact:** every extra Technology dollar adds far less profit than a
  Home & Lifestyle or Furniture dollar.
- **Recommendation:** renegotiate Technology cost prices, bundle tech with
  high-margin categories (H&L 35.5%), and shift promotion spend away from
  low-margin flagships.

## 5. Regional Insights

| Region | Revenue | Share | Margin |
|---|---|---|---|
| West | $19.9M | 29% | 23.5% |
| East | $19.4M | 28% | 23.8% |
| South | $17.7M | 26% | 23.9% |
| Central | $11.9M | 17% | **24.0%** |

- Top state: **California — $9.6M**.
- Margins are healthy everywhere (23.5–24.0%); the gap is in **revenue**.

**FINDING → EVIDENCE → IMPACT → RECOMMENDATION**
- **Finding:** Central is the weakest revenue region (17%) despite the best
  margin (24.0%).
- **Evidence:** regional table.
- **Impact:** Central is an under-penetrated, high-quality market.
- **Recommendation:** expand assortment, logistics and marketing in Central
  states (IL, OH, MI, TX) before chasing price in mature West/East markets.

## 6. Profitability Analysis

- Overall margin **23.8%**; margins differ significantly across categories
  (ANOVA F = 9,119, p < 0.001).
- Margin by discount band:

| Discount band | Revenue | Margin |
|---|---|---|
| No discount | $24.0M | **32.1%** |
| 0–10% | $16.7M | 28.7% |
| 10–20% | $16.7M | 20.5% |
| 20–30% | $7.7M | 9.9% |
| **30%+** | **$3.7M** | **−8.2%** |

- Bands above 20% carry 16.6% of revenue but drag average margin to **0.8%**.

**FINDING → EVIDENCE → IMPACT → RECOMMENDATION**
- **Finding:** discount depth correlates strongly with margin collapse
  (r = −0.75 between discount and margin) and 30%+ discounts lose money.
- **Evidence:** band table; 30%+ band gross loss of $305K.
- **Impact:** discounting above ~15% transfers revenue from profit to the
  customer with no volume gain.
- **Recommendation:** cap discounts at 15% by policy; reserve deeper discounts
  for seasonal clearance of specific slow-moving SKUs, never across the catalogue.

## 7. Statistical Findings

| Test | H0 | Result | Decision |
|---|---|---|---|
| Discounted vs non-discounted margin (Welch t-test) | equal margins | t = −186.2, p < 0.001 | **Reject H0** — discounts cut margin (38.4% → 25.3%) |
| High vs low tier AOV (Welch t-test) | equal AOV | t = 24.6, p < 0.001 | **Reject H0** — tiers differ ($2,352 vs $1,087) |
| Margin by category (ANOVA) | equal margins | F = 9,119, p < 0.001 | **Reject H0** — category mix matters |
| Spend by segment (ANOVA) | equal spend | F = 137.4, p < 0.001 | **Reject H0** — segment drives value |
| Discount vs quantity (Pearson) | no relationship | r = 0.004, p = 0.19 | **Not significant** — discounts do not lift volume |
| Age vs customer spend (Pearson) | no relationship | r = 0.001, p = 0.95 | **Not significant** — age is not a value driver |

## 8. Key Business Problems

1. **Acquisition collapse** — new customers fell ~95% from 2021 to 2024.
2. **Customer concentration** — 33% of customers produce 80% of revenue; a few
   lost accounts would be material.
3. **Discount leakage** — deep discounts cost profit without driving sales.
4. **Margin mix shift** — fast-growing Technology is the thinnest-margin category.
5. **Seasonal capacity** — December demand is 2.4x July; the supply chain and
   marketing must peak-time differently.
6. **Silent churn** — 536 Lost customers ($3.0M) and 123 At-Risk/Can't-Lose
   customers ($4.0M) are recoverable value sitting untapped.

## 9. Recommendations (priority order)

| # | Action | Target | Expected lever |
|---|---|---|---|
| 1 | Kill 30%+ blanket discounts; cap at 15% | All categories | Protect margin (recovers ~$305K loss band + margin upside) |
| 2 | Champion retention programme | Champions + Loyal (542 customers) | Protect 80% of revenue |
| 3 | Win-back campaign | At Risk + Can't Lose (123 customers) | Recover $4.0M at risk |
| 4 | B2B programme (volume pricing) | Corporate, Small Business | Grow highest-AOV segments |
| 5 | Cross-sell high-margin Home & Lifestyle with Technology | All | Improve category margin mix |
| 6 | Expand Central region | IL, OH, MI, TX | Grow under-penetrated high-margin market |
| 7 | Seasonal campaign calendar | Nov–Dec, Aug–Sep peaks | Capture peak demand; avoid Jan–Feb blanket offers |
| 8 | One-time-buyer activation | 9% of customers (146) + 536 Lost | Convert first purchase into loyalty |

## 10. Limitations

- Dataset is synthetic (realistic but not actual company transactions); numeric
  results are internally valid but not external benchmarks.
- RFM reference date is fixed at 31 Dec 2024; recency-based segments should be
  re-computed with fresh data.
- Line-level correlations are inflated by the large sample size (N > 100K);
  statistical significance must be read alongside effect sizes.
- No marketing-cost, channel, or price-elasticity data — ROI of campaigns can
  only be estimated, not proven.
- Age/spend and behavioural tests assume Completed orders only.

## 11. Future Improvements

- Add a live date filter and refresh pipeline so RFM and dashboard update
  monthly (e.g., Power BI auto-refresh / scheduled job).
- Add marketing cost and channel data to enable true ROI and CLV modelling.
- Model customer lifetime value (predictive RFM / survival analysis) to rank
  customers by expected future value.
- Price-elasticity experiment design to replace blanket discounts with
  data-driven promo decisions.
- Forecast demand (seasonal decomposition + time-series model) to drive
  inventory purchasing for peak months.

---
*Every figure above is computed from the project's dataset — see
`reports/analysis_results.json`, `reports/rfm_results.json` and
`reports/sql_analysis_results.md` for the underlying calculations.*