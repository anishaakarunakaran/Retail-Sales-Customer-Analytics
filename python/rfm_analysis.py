"""
Retail Sales & Customer Analytics - RFM Analysis
================================================
Phase 5 (Customer Analytics).

Computes Recency / Frequency / Monetary per customer on Completed orders,
scores 1-5 by quintile, and assigns business segments:

  Champions            - recent, frequent, high spend
  Loyal Customers      - strong frequency and spend
  Potential Loyalists  - recent but lower frequency/spend
  New Customers        - very recent, first purchase(s)
  At Risk              - was active, going quiet
  Hibernating          - low activity, medium recency
  Lost                 - old, low frequency (incl. one-time buyers long ago)
  Can't Lose           - big spenders who stopped buying

Outputs:
  reports/rfm_results.json        - segment summary tables
  reports/rfm_segments.csv        - segment-level metrics (for Power BI)
  data/cleaned/customer_rfm.csv   - customer-level RFM scores + segment
  visuals/rfm_segments.png        - segment chart
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CLEAN = Path("data/cleaned/retail_sales_clean.csv")
CUST_RFM = Path("data/cleaned/customer_rfm.csv")
OUT = Path("reports/rfm_results.json")
SEG_CSV = Path("reports/rfm_segments.csv")

plt.rcParams.update({
    "figure.dpi": 140, "font.size": 9,
    "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
})

REFERENCE_DATE = pd.Timestamp("2024-12-31")


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    cust = df.groupby("Customer_ID").agg(
        last_order=("Order_Date", "max"),
        first_order=("Order_Date", "min"),
        orders=("Order_ID", "nunique"),
        monetary=("Sales", "sum"),
        profit=("Profit", "sum"),
        segment=("Customer_Segment", "first"),
        region=("Region", "first"),
    ).reset_index()
    cust["recency_days"] = (REFERENCE_DATE - cust["last_order"]).dt.days
    cust["recency_weeks"] = cust["recency_days"] // 7

    # Scores 1..5 (higher = better); Recency is inverted (fewer days = 5)
    def score_series(s, reverse=False):
        qs = s.quantile([0.2, 0.4, 0.6, 0.8]).values
        bins = [-np.inf, *qs, np.inf]
        labels = [1, 2, 3, 4, 5] if not reverse else [5, 4, 3, 2, 1]
        return pd.cut(s, bins=bins, labels=labels, include_lowest=True).astype(int)

    cust["R"] = score_series(cust["recency_days"], reverse=True)
    cust["F"] = score_series(cust["orders"])
    cust["M"] = score_series(cust["monetary"])
    cust["RFM_Score"] = cust["R"] * 100 + cust["F"] * 10 + cust["M"]
    return cust


def assign_segment(r: pd.Series) -> str:
    R, F, M, n_orders = r["R"], r["F"], r["M"], r["orders"]
    if R >= 4 and F >= 4 and M >= 4:
        return "Champions"
    if R >= 3 and F >= 4 and M >= 4:
        return "Loyal Customers"
    if R >= 4 and n_orders <= 2:
        return "New Customers"
    if R >= 4 and (F >= 3 or M >= 3):
        return "Potential Loyalists"
    if R >= 4:
        return "Promising"
    if R <= 2 and F >= 4 and M >= 4:
        return "Can't Lose"
    if R <= 2 and F >= 3 and M >= 3:
        return "At Risk"
    if R <= 2:
        return "Lost"
    if F <= 2 and M <= 2:
        return "Hibernating"
    return "Promising"


def summarize(cust: pd.DataFrame) -> pd.DataFrame:
    seg = cust.groupby("Segment").agg(
        customers=("Customer_ID", "nunique"),
        revenue=("monetary", "sum"),
        profit=("profit", "sum"),
        avg_spend=("monetary", "mean"),
        avg_orders=("orders", "mean"),
        avg_recency_weeks=("recency_weeks", "mean"),
        avg_aov=("monetary", lambda s: cust.loc[s.index, "monetary"].sum()
                 / max(cust.loc[s.index, "orders"].sum(), 1)),
    ).round(2)
    seg["revenue_share"] = seg["revenue"] / seg["revenue"].sum()
    seg["margin"] = seg["profit"] / seg["revenue"]
    return seg


def main() -> None:
    df = pd.read_csv(CLEAN, parse_dates=["Order_Date"])
    cust = build_rfm(df)
    cust["Segment"] = cust.apply(assign_segment, axis=1)

    seg = summarize(cust)
    order = ["Champions", "Loyal Customers", "Potential Loyalists", "New Customers",
             "Promising", "Hibernating", "At Risk", "Can't Lose", "Lost"]
    seg = seg.reindex([s for s in order if s in seg.index])

    # Customer-level export for Power BI
    cust.to_csv(CUST_RFM, index=False)
    seg.reset_index().to_csv(SEG_CSV, index=False)

    # Findings
    for s in seg.index:
        row = seg.loc[s]
        print(f"{s:<18} n={int(row['customers']):>4} rev=${row['revenue']/1e6:>6.1f}M "
              f"({row['revenue_share']:>5.1%}) avg_spend=${row['avg_spend']:>8,.0f} "
              f"avg_orders={row['avg_orders']:.1f} avg_recency={row['avg_recency_weeks']:.0f}w")

    # Chart
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axes[0]
    ax.bar(seg.index, seg["customers"], color="#1f77b4")
    ax.set_title("Customers per RFM Segment")
    ax.set_ylabel("Customers")
    ax.tick_params(axis="x", rotation=45)
    ax = axes[1]
    ax.bar(seg.index, seg["revenue"] / 1e6, color="#2ca02c")
    ax.set_title("Revenue per RFM Segment ($M)")
    ax.set_ylabel("Revenue ($M)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig("visuals/rfm_segments.png", bbox_inches="tight")

    # Merge segment info back onto customer-level for Power BI
    cust.to_csv(CUST_RFM, index=False)

    results = {
        "reference_date": str(REFERENCE_DATE.date()),
        "segments": seg.reset_index().to_dict("records"),
        "customer_level": cust.head(50).to_dict("records"),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved -> {OUT}, {SEG_CSV}, {CUST_RFM}, visuals/rfm_segments.png")


if __name__ == "__main__":
    main()