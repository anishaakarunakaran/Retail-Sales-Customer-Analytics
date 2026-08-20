"""
Retail Sales & Customer Analytics - Exploratory Data Analysis + Statistics
==========================================================================
Phase 3 (EDA) and Phase 4 (Statistical Analysis).

Reads data/cleaned/retail_sales_clean.csv, produces:
  * KPI summary + all analysis tables
  * Charts saved to visuals/
  * results JSON (reports/analysis_results.json) used by the business report
  * Plain-text findings log (reports/eda_findings.md)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

CLEAN = Path("data/cleaned/retail_sales_clean.csv")
OUT = Path("reports/analysis_results.json")
VIS = Path("visuals")
FINDINGS = Path("reports/eda_findings.md")

plt.rcParams.update({
    "figure.dpi": 140, "font.size": 9,
    "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.autolayout": True,
})

findings: list[str] = []


def note(s: str) -> None:
    findings.append(s)
    print(">>", s)


def save_fig(fig, name: str) -> None:
    fig.savefig(VIS / name, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def load() -> pd.DataFrame:
    df = pd.read_csv(CLEAN, parse_dates=["Order_Date"])
    df["Order_Month"] = df["Order_Date"].dt.month
    df["Order_Year"] = df["Order_Date"].dt.year
    df["Order_YM"] = df["Order_Date"].dt.to_period("M")
    return df


# ---------------------------------------------------------------------------
# 1. Global KPIs
# ---------------------------------------------------------------------------
def kpis(df: pd.DataFrame) -> dict:
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order_ID"].nunique()
    total_customers = df["Customer_ID"].nunique()
    total_qty = df["Quantity"].sum()
    aov = total_sales / total_orders
    margin = total_profit / total_sales
    k = {
        "total_sales": round(float(total_sales), 2),
        "total_profit": round(float(total_profit), 2),
        "total_orders": int(total_orders),
        "total_customers": int(total_customers),
        "total_quantity": int(total_qty),
        "avg_order_value": round(float(aov), 2),
        "avg_order_lines": round(float(len(df) / total_orders), 2),
        "overall_profit_margin": round(float(margin), 4),
        "avg_discount": round(float(df["Discount"].mean()), 4),
        "date_range": [str(df["Order_Date"].min().date()), str(df["Order_Date"].max().date())],
    }
    note(f"KPI: Revenue ${total_sales:,.0f} | Profit ${total_profit:,.0f} "
         f"| Margin {margin:.1%} | Orders {total_orders:,} | Customers {total_customers:,} | AOV ${aov:,.2f}")
    return k


# ---------------------------------------------------------------------------
# 2. Time series
# ---------------------------------------------------------------------------
def time_analysis(df: pd.DataFrame) -> dict:
    monthly = df.groupby(df["Order_Date"].dt.to_period("M")).agg(
        sales=("Sales", "sum"), profit=("Profit", "sum"),
        orders=("Order_ID", "nunique"), qty=("Quantity", "sum"))
    monthly.index = monthly.index.astype(str)

    yearly = df.groupby("Order_Year").agg(
        sales=("Sales", "sum"), profit=("Profit", "sum"),
        orders=("Order_ID", "nunique"))
    yearly["yoy_growth"] = yearly["sales"].pct_change().round(4)
    cagr = (yearly["sales"].iloc[-1] / yearly["sales"].iloc[0]) ** (1 / 3) - 1
    note(f"Revenue growth 2021->2024: {yearly['sales'].iloc[-1]/yearly['sales'].iloc[0]-1:.1%} "
         f"(CAGR {cagr:.1%})")
    for y, row in yearly.iterrows():
        note(f"  {y}: ${row['sales']:,.0f} profit ${row['profit']:,.0f} "
             f"({row['yoy_growth']:+.1%} yoy)" if not pd.isna(row["yoy_growth"]) else f"  {y}: base year")

    # Seasonality: total sales by calendar month (aggregated across years)
    seas = df.assign(cm=df["Order_Date"].dt.month).groupby("cm")["Sales"].sum()
    peak = seas.idxmax()
    n_years = df["Order_Year"].nunique()
    note(f"Peak demand month: {pd.Timestamp(2020, int(peak), 1).strftime('%B')} "
         f"(avg ${seas.max()/n_years:,.0f}/year vs annual month average ${seas.mean()/n_years:,.0f})")
    trough = seas.idxmin()
    note(f"Lowest demand month: {pd.Timestamp(2020, int(trough), 1).strftime('%B')} "
         f"({seas.max()/seas.min():.1f}x the trough)")

    dow = df.assign(dow=df["Order_Date"].dt.day_name()).groupby("dow")["Sales"].sum()
    dow = dow.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    note(f"Weekend share of sales: {(dow.loc[['Saturday','Sunday']].sum()/dow.sum()):.1%}")

    # Charts
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(range(len(monthly)), monthly["sales"], color="#1f77b4")
    ax.set_xticks(range(0, len(monthly), 6))
    ax.set_xticklabels(monthly.index[::6], rotation=45)
    ax.set_title("Monthly Revenue Trend (2021-2024)")
    ax.set_ylabel("Revenue ($)")
    save_fig(fig, "monthly_revenue_trend.png")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(monthly.index, monthly["profit"], color="#2ca02c", width=0.8)
    ax.set_xticks(range(0, len(monthly), 6))
    ax.set_xticklabels(monthly.index[::6], rotation=45)
    ax.set_title("Monthly Profit Trend")
    ax.set_ylabel("Profit ($)")
    save_fig(fig, "monthly_profit_trend.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(seas.index, seas.values / 1e6, color="#ff7f0e")
    ax.set_xticks(seas.index)
    ax.set_xticklabels([pd.Timestamp(2020, int(m), 1).strftime("%b") for m in seas.index])
    ax.set_title("Seasonality: Total Sales by Calendar Month ($M)")
    ax.set_ylabel("Revenue ($M)")
    save_fig(fig, "seasonality.png")

    return {"monthly": monthly.reset_index().to_dict("records"),
            "yearly": yearly.reset_index().to_dict("records"),
            "seasonality": seas.round(0).to_dict(),
            "dow_sales": dow.round(0).to_dict()}


# ---------------------------------------------------------------------------
# 3. Products
# ---------------------------------------------------------------------------
def product_analysis(df: pd.DataFrame) -> dict:
    prod = df.groupby(["Product_ID", "Product_Name", "Category", "Sub_Category"]).agg(
        sales=("Sales", "sum"), profit=("Profit", "sum"), qty=("Quantity", "sum"),
        orders=("Order_ID", "nunique")).reset_index()
    prod["margin"] = prod["profit"] / prod["sales"]

    top10_sales = prod.nlargest(10, "sales")
    top10_profit = prod.nlargest(10, "profit")
    low_margin = prod[prod["sales"] > prod["sales"].quantile(0.75)].nsmallest(10, "margin")

    cat = df.groupby("Category").agg(
        sales=("Sales", "sum"), profit=("Profit", "sum"), qty=("Quantity", "sum"),
        orders=("Order_ID", "nunique")).sort_values("sales", ascending=False)
    cat["margin"] = cat["profit"] / cat["sales"]
    cat["sales_share"] = cat["sales"] / cat["sales"].sum()
    note(f"Category revenue share: " + ", ".join(f"{c} {s:.0%}" for c, s in cat["sales_share"].items()))
    note(f"Category margin: " + ", ".join(f"{c} {m:.1%}" for c, m in cat["margin"].items()))

    sub = df.groupby("Sub_Category").agg(
        sales=("Sales", "sum"), profit=("Profit", "sum"), qty=("Quantity", "sum"),
        orders=("Order_ID", "nunique")).sort_values("sales", ascending=False)
    sub["margin"] = sub["profit"] / sub["sales"]

    top_product = top10_sales.iloc[0]
    note(f"Top product by revenue: {top_product['Product_Name']} "
         f"(${top_product['sales']:,.0f}, margin {top_product['margin']:.1%})")
    note(f"Top product by profit: {top10_profit.iloc[0]['Product_Name']} "
         f"(${top10_profit.iloc[0]['profit']:,.0f})")

    # Charts
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(cat.index, cat["sales"], color="#1f77b4")
    ax.set_title("Revenue by Category")
    ax.set_ylabel("Revenue ($)")
    save_fig(fig, "revenue_by_category.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(top10_sales["Product_Name"][::-1], top10_sales["sales"][::-1], color="#1f77b4")
    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("Revenue ($)")
    save_fig(fig, "top10_products.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(sub.head(12).index, sub.head(12)["sales"], color="#2ca02c")
    ax.set_xticklabels(sub.head(12).index, rotation=45, ha="right")
    ax.set_title("Revenue by Sub-Category (Top 12)")
    ax.set_ylabel("Revenue ($)")
    save_fig(fig, "revenue_by_subcategory.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(cat.index, cat["margin"], color="#9467bd")
    ax.axhline(margin_global := df["Profit"].sum() / df["Sales"].sum(), color="red", ls="--", lw=1)
    ax.text(len(cat) - 0.4, margin_global, f" overall {margin_global:.1%}", color="red")
    ax.set_title("Profit Margin by Category")
    ax.set_ylabel("Margin")
    save_fig(fig, "category_margin.png")

    return {"top10_sales": top10_sales.to_dict("records"),
            "top10_profit": top10_profit.to_dict("records"),
            "low_margin_high_volume": low_margin.to_dict("records"),
            "category": cat.reset_index().to_dict("records"),
            "subcategory": sub.reset_index().to_dict("records")}


# ---------------------------------------------------------------------------
# 4. Customers
# ---------------------------------------------------------------------------
def customer_analysis(df: pd.DataFrame) -> dict:
    cust = df.groupby("Customer_ID").agg(
        sales=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order_ID", "nunique"),
        qty=("Quantity", "sum"),
        first_order=("Order_Date", "min"), last_order=("Order_Date", "max"),
        segment=("Customer_Segment", "first"), age=("Age", "first"),
        region=("Region", "first")).reset_index()
    cust["aov"] = cust["sales"] / cust["orders"]

    one_time = int((cust["orders"] == 1).sum())
    note(f"Customers: {len(cust):,} | one-time buyers {(one_time/len(cust)):.0%} "
         f"| repeat buyers {(1-one_time/len(cust)):.0%}")

    # New vs returning customers per year (by first order year)
    cust["first_year"] = cust["first_order"].dt.year
    new_per_year = cust.groupby("first_year").size()
    note(f"New customers by year: " + ", ".join(f"{y}: {n}" for y, n in new_per_year.items()))

    # Customer lifetime value tiers
    q75 = cust["sales"].quantile(0.75)
    q50 = cust["sales"].quantile(0.50)
    tier = np.where(cust["sales"] >= q75, "High-value",
                    np.where(cust["sales"] >= q50, "Mid-value", "Low-value"))
    cust["value_tier"] = tier
    tier_stats = cust.groupby("value_tier").agg(
        customers=("Customer_ID", "nunique"), sales=("sales", "sum"),
        avg_spend=("sales", "mean"), avg_orders=("orders", "mean"))
    note(f"High-value customers (top 25% by spend) contribute "
         f"{(cust[cust['value_tier']=='High-value']['sales'].sum()/cust['sales'].sum()):.0%} of revenue "
         f"from {tier_stats.loc['High-value','customers']:,} customers")

    seg = cust.groupby("segment").agg(
        customers=("Customer_ID", "nunique"), sales=("sales", "sum"),
        avg_spend=("sales", "mean"), avg_orders=("orders", "mean"),
        avg_aov=("aov", "mean")).round(2)
    note(f"Segment AOV: " + ", ".join(f"{c}: ${a:,.0f}" for c, a in seg["avg_aov"].items()))

    # age vs spending
    age_spend = cust[["age", "sales"]].dropna()
    r_age, p_age = stats.pearsonr(age_spend["age"], age_spend["sales"])
    note(f"Correlation age vs customer spend: r={r_age:.3f}, p={p_age:.4f} "
         f"({'significant' if p_age<0.05 else 'not significant'})")

    # Charts
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(seg.index, seg["avg_spend"], color="#d62728")
    ax.set_title("Average Customer Spend by Segment")
    ax.set_ylabel("Avg spend ($)")
    ax.set_xticklabels(seg.index, rotation=20, ha="right")
    save_fig(fig, "segment_avg_spend.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    tier_order = ["Low-value", "Mid-value", "High-value"]
    ax.bar(tier_order, tier_stats.loc[tier_order, "sales"], color="#17becf")
    ax.set_title("Revenue by Customer Value Tier")
    ax.set_ylabel("Revenue ($)")
    save_fig(fig, "value_tier_revenue.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(new_per_year.index.astype(str), new_per_year.values, color="#8c564b")
    ax.set_title("New Customers by Year")
    ax.set_ylabel("Customers")
    save_fig(fig, "new_customers_by_year.png")

    return {"customers": int(len(cust)),
            "one_time_buyers": int(one_time),
            "repeat_buyers": int(len(cust) - one_time),
            "new_per_year": new_per_year.to_dict(),
            "tiers": tier_stats.reset_index().to_dict("records"),
            "segment": seg.reset_index().to_dict("records"),
            "age_spend_corr": {"r": round(float(r_age), 4), "p": round(float(p_age), 4)}}


# ---------------------------------------------------------------------------
# 5. Geography
# ---------------------------------------------------------------------------
def geo_analysis(df: pd.DataFrame) -> dict:
    reg = df.groupby("Region").agg(sales=("Sales", "sum"), profit=("Profit", "sum"),
                                   orders=("Order_ID", "nunique")).sort_values("sales", ascending=False)
    reg["margin"] = reg["profit"] / reg["sales"]
    reg["share"] = reg["sales"] / reg["sales"].sum()
    note(f"Region revenue share: " + ", ".join(f"{r}: {s:.0%}" for r, s in reg["share"].items()))
    note(f"Region margin: " + ", ".join(f"{r}: {m:.1%}" for r, m in reg["margin"].items()))

    st = df.groupby("State").agg(sales=("Sales", "sum"), profit=("Profit", "sum"),
                                 orders=("Order_ID", "nunique")).sort_values("sales", ascending=False)
    st["margin"] = st["profit"] / st["sales"]
    city = df.groupby("City").agg(sales=("Sales", "sum"), profit=("Profit", "sum"),
                                  orders=("Order_ID", "nunique")).sort_values("sales", ascending=False)
    city["margin"] = city["profit"] / city["sales"]

    best = reg.index[0]
    worst = reg.index[-1]
    note(f"Best region: {best} (${reg.loc[best,'sales']:,.0f}, margin {reg.loc[best,'margin']:.1%})")
    note(f"Weakest region: {worst} (${reg.loc[worst,'sales']:,.0f}, margin {reg.loc[worst,'margin']:.1%})")
    top_state = st.index[0]
    note(f"Top state: {top_state} (${st.loc[top_state,'sales']:,.0f})")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(reg.index, reg["sales"], color="#1f77b4")
    ax.set_title("Revenue by Region")
    ax.set_ylabel("Revenue ($)")
    save_fig(fig, "revenue_by_region.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(st.head(10).index[::-1], st.head(10)["sales"][::-1], color="#2ca02c")
    ax.set_title("Revenue by State (Top 10)")
    ax.set_xlabel("Revenue ($)")
    save_fig(fig, "revenue_by_state.png")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(reg.index, reg["margin"], color="#9467bd")
    ax.set_title("Profit Margin by Region")
    ax.set_ylabel("Margin")
    save_fig(fig, "region_margin.png")

    return {"region": reg.reset_index().to_dict("records"),
            "state": st.head(15).reset_index().to_dict("records"),
            "city": city.head(15).reset_index().to_dict("records")}


# ---------------------------------------------------------------------------
# 6. Discounts
# ---------------------------------------------------------------------------
def discount_analysis(df: pd.DataFrame) -> dict:
    band = df.groupby("Discount_Band", observed=True).agg(
        lines=("Sales", "size"), sales=("Sales", "sum"), profit=("Profit", "sum"),
        qty=("Quantity", "sum")).reset_index()
    band["margin"] = band["profit"] / band["sales"]
    band["avg_line_value"] = band["sales"] / band["lines"]
    note(f"Margin by discount band: " + ", ".join(f"{b}: {m:.1%}" for b, m in
                                                  band.set_index("Discount_Band")["margin"].items()))
    note(f"Discount bands >20% carry only {band.loc[band['Discount_Band'].isin(['20-30%','30%+']),'sales'].sum()/df['Sales'].sum():.1%} of revenue "
         f"but drag margin down to {band.loc[band['Discount_Band'].isin(['20-30%','30%+']),'margin'].mean():.1%}")

    # Correlations (line level)
    r_s, p_s = stats.pearsonr(df["Discount"], df["Sales"])
    r_p, p_p = stats.pearsonr(df["Discount"], df["Profit"])
    r_q, p_q = stats.pearsonr(df["Discount"], df["Quantity"])
    note(f"Discount vs Sales: r={r_s:.3f} (p={p_s:.2e})")
    note(f"Discount vs Profit: r={r_p:.3f} (p={p_p:.2e})")
    note(f"Discount vs Quantity: r={r_q:.3f} (p={p_q:.2e})")
    r_units, p_units = stats.pearsonr(df["Discount"], df["Quantity"] * df["Unit_Price"])
    note(f"Discount vs Basket Value (qty*price): r={r_units:.3f} (p={p_units:.2e})")

    fig, ax = plt.subplots(figsize=(7, 3.5))
    x = np.arange(len(band))
    ax.bar(x - 0.15, band["sales"] / 1e6, width=0.3, color="#1f77b4", label="Revenue ($M)")
    ax2 = ax.twinx()
    ax2.plot(x, band["margin"], color="#d62728", marker="o", label="Margin")
    ax.set_xticks(x); ax.set_xticklabels(band["Discount_Band"])
    ax.set_title("Revenue and Margin by Discount Band")
    ax.set_ylabel("Revenue ($M)"); ax2.set_ylabel("Profit margin")
    save_fig(fig, "discount_band_analysis.png")

    return {"bands": band.round(4).to_dict("records"),
            "corr_discount_sales": {"r": round(float(r_s), 4), "p": float(p_s)},
            "corr_discount_profit": {"r": round(float(r_p), 4), "p": float(p_p)},
            "corr_discount_qty": {"r": round(float(r_q), 4), "p": float(p_q)}}


# ---------------------------------------------------------------------------
# 7. Statistics - hypothesis tests
# ---------------------------------------------------------------------------
def statistical_analysis(df: pd.DataFrame) -> dict:
    results = {}

    # ---- T-test 1: profit margin, discounted vs non-discounted lines
    no_disc = df[df["Discount"] == 0]["Profit_Margin"]
    disc = df[df["Discount"] > 0]["Profit_Margin"]
    t1, p1 = stats.ttest_ind(disc, no_disc, equal_var=False)
    results["ttest_discount_margin"] = {
        "group_means": {"no_discount": round(float(no_disc.mean()), 4),
                        "discounted": round(float(disc.mean()), 4)},
        "t": round(float(t1), 4), "p": float(p1),
        "h0": "Mean profit margin is equal for discounted and non-discounted lines",
        "h1": "Mean profit margin differs (discounted lines are less profitable)",
        "decision": "Reject H0" if p1 < 0.05 else "Fail to reject H0",
    }
    note(f"T-test (Welch): margin discounted vs not -> t={t1:.2f}, p={p1:.2e}")

    # ---- T-test 2: average order value, high vs low value customers
    cust = df.groupby("Customer_ID").agg(sales=("Sales", "sum"), orders=("Order_ID", "nunique")).reset_index()
    cust["aov"] = cust["sales"] / cust["orders"]
    high = cust[cust["sales"] >= cust["sales"].quantile(0.75)]["aov"]
    low = cust[cust["sales"] < cust["sales"].quantile(0.25)]["aov"]
    t2, p2 = stats.ttest_ind(high, low, equal_var=False)
    results["ttest_aov_tiers"] = {
        "high_tier_mean_aov": round(float(high.mean()), 2),
        "low_tier_mean_aov": round(float(low.mean()), 2),
        "t": round(float(t2), 4), "p": float(p2),
        "h0": "Mean AOV is equal for high- and low-value customers",
        "h1": "Mean AOV differs between tiers",
        "decision": "Reject H0" if p2 < 0.05 else "Fail to reject H0",
    }
    note(f"T-test AOV high vs low tier -> t={t2:.2f}, p={p2:.2e}")

    # ---- ANOVA: profit margin by category
    cat_groups = [g["Profit_Margin"].values for _, g in df.groupby("Category")]
    f_cat, p_cat = stats.f_oneway(*cat_groups)
    cat_means = df.groupby("Category")["Profit_Margin"].mean().round(4)
    results["anova_category_margin"] = {
        "group_means": cat_means.to_dict(),
        "F": round(float(f_cat), 4), "p": float(p_cat),
        "h0": "Mean profit margin is equal across all categories",
        "h1": "At least one category has a different mean margin",
        "decision": "Reject H0" if p_cat < 0.05 else "Fail to reject H0",
    }
    note(f"ANOVA margin by category -> F={f_cat:.2f}, p={p_cat:.2e}")

    # ---- ANOVA: average spend by segment
    seg_spend = cust.merge(df[["Customer_ID", "Customer_Segment"]].drop_duplicates(),
                           on="Customer_ID")
    seg_groups = [g.values for _, g in seg_spend.groupby("Customer_Segment")["sales"]]
    f_seg, p_seg = stats.f_oneway(*seg_groups)
    results["anova_segment_spend"] = {
        "F": round(float(f_seg), 4), "p": float(p_seg),
        "h0": "Mean customer spend is equal across segments",
        "h1": "At least one segment spends differently",
        "decision": "Reject H0" if p_seg < 0.05 else "Fail to reject H0",
    }
    note(f"ANOVA spend by segment -> F={f_seg:.2f}, p={p_seg:.2e}")

    # ---- Correlation heatmap
    corr_cols = ["Sales", "Profit", "Quantity", "Unit_Price", "Discount", "Profit_Margin"]
    corr = df[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr_cols))); ax.set_yticks(range(len(corr_cols)))
    ax.set_xticklabels(corr_cols, rotation=45, ha="right"); ax.set_yticklabels(corr_cols)
    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                    color="white" if abs(corr.iloc[i, j]) > 0.6 else "black", fontsize=8)
    ax.set_title("Correlation Matrix of Sales Metrics")
    save_fig(fig, "correlation_heatmap.png")

    results["correlation_matrix"] = corr.round(3).to_dict()
    return results


def main() -> None:
    VIS.mkdir(exist_ok=True)
    df = load()
    results = {}
    results["kpis"] = kpis(df)
    results["time"] = time_analysis(df)
    results["products"] = product_analysis(df)
    results["customers"] = customer_analysis(df)
    results["geo"] = geo_analysis(df)
    results["discounts"] = discount_analysis(df)
    results["stats"] = statistical_analysis(df)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    FINDINGS.parent.mkdir(exist_ok=True)
    FINDINGS.write_text("\n".join(f"- {f}" for f in findings), encoding="utf-8")
    print(f"\nSaved results -> {OUT}")
    print(f"Saved {len(list(VIS.glob('*.png')))} charts -> {VIS}")


if __name__ == "__main__":
    main()