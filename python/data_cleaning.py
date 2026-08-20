"""
Retail Sales & Customer Analytics - Data Cleaning Pipeline
==========================================================
Phase 1 (Data Understanding) + Phase 2 (Data Cleaning) + Feature Engineering.

Reads data/raw/raw_retail_sales.csv, runs a documented cleaning pipeline,
and writes data/cleaned/retail_sales_clean.csv plus a cleaning report
(reports/cleaning_report.json + md).

Cleaning decisions (each is justified in the report):
  1. Parse dates; drop 146 rows with impossible dates (month 00/13).
  2. Drop rows with negative Quantity (invalid transaction lines).
  3. Recompute Unit_Price for typos (e.g. 10x errors, negatives) using the
     identity  Sales = Quantity * Unit_Price * (1 - Discount).
  4. Derive missing Discount from Sales/Unit_Price/Quantity instead of guessing.
  5. Remove exact duplicate rows.
  6. Standardise Category casing.
  7. Impute missing Age with segment median; missing City with state mode.
  8. Keep only Completed orders for revenue analytics (Cancelled/Returned/
     Pending do not generate revenue) - business rule, documented.
  9. Feature engineering: Order_Year, Order_Month, Order_Day, Day_Of_Week,
     Age_Group, Discount_Band.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/raw_retail_sales.csv")
CLEAN = Path("data/cleaned/retail_sales_clean.csv")
REPORT = Path("reports/cleaning_report.json")

REPORT_MD = """# Data Cleaning Report

{body}

## Cleaning decisions (with rationale)

| # | Issue | Action | Rationale |
|---|-------|--------|-----------|
| 1 | Invalid order dates (month 00/13) | Rows dropped | Impossible dates cannot be repaired reliably; 0.13% of data |
| 2 | Negative quantity | Rows dropped | Invalid transaction lines |
| 3 | Unit price typos (10x, negative) | Recalculated | Unit_Price = Sales / (Qty * (1-Discount)) |
| 4 | Missing discount ('-') | Derived from Sales/Unit_Price | Discount = 1 - Sales/(Qty*Unit_Price) |
| 5 | Exact duplicate rows | Dropped | Duplicates bias counts |
| 6 | Category casing (e.g. 'technology') | Standardised to Title Case | Inconsistent values break GROUP BY |
| 7 | Missing Age | Imputed with segment median | Age differs by segment (Corporate older, Consumer younger) |
| 8 | Missing City | Imputed with state mode | City belongs to a known state |
| 9 | Non-Completed orders | Excluded from analysis set | Cancelled/Returned/Pending produce no revenue |
"""


def phase1_understanding(df: pd.DataFrame) -> dict:
    """Phase 1 - capture data quality baseline before cleaning."""
    report = {
        "raw_shape": [int(df.shape[0]), int(df.shape[1])],
        "data_types": {c: str(t) for c, t in df.dtypes.items()},
        "missing_values": {c: int(v) for c, v in df.isna().sum().items() if v > 0},
        "missing_pct": {c: round(float(v / len(df) * 100), 2)
                        for c, v in df.isna().sum().items() if v > 0},
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_counts": {c: int(df[c].nunique()) for c in df.columns},
        "negative_quantity": int((df["Quantity"] < 0).sum()),
        "negative_unit_price": int((df["Unit_Price"] < 0).sum()),
        "invalid_dates": int(df["Order_Date"].astype(str).str[5:7].isin(["00", "13"]).sum()),
        "order_status_counts": df["Order_Status"].value_counts().to_dict(),
        "descriptive_stats": df[["Quantity", "Unit_Price", "Discount", "Sales",
                                 "Profit", "Profit_Margin"]].describe().round(2).to_dict(),
    }
    return report


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Phase 2 - cleaning pipeline. Returns cleaned (Completed-only) frame."""
    log: dict[str, int] = {}

    # 1. Order_Date parsing + invalid date removal
    df = df.copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    n_bad_dates = int(df["Order_Date"].isna().sum())
    df = df.dropna(subset=["Order_Date"])
    log["invalid_dates_dropped"] = n_bad_dates

    # 2. Negative Quantity
    n_neg_qty = int((df["Quantity"] < 0).sum())
    df = df[df["Quantity"] >= 0]
    log["negative_quantity_dropped"] = n_neg_qty

    # 3. Fix Unit_Price typos: derive from Sales = Qty * Price * (1-Discount)
    #    First make Discount numeric where possible.
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce")
    n_disc_missing = int(df["Discount"].isna().sum())

    # For lines with a valid discount, expected price must match recorded.
    has_disc = df["Discount"].notna()
    expected_price = np.where(
        has_disc,
        df["Sales"] / np.maximum(df["Quantity"] * (1 - df["Discount"]), 1e-9),
        np.nan,
    )
    inconsistent = has_disc & (np.abs(df["Unit_Price"] - expected_price)
                               > 0.01 * expected_price)
    n_price_fixed = int(inconsistent.sum())
    df.loc[inconsistent, "Unit_Price"] = np.round(expected_price[inconsistent], 2)
    # Negative unit prices that survived -> derive or drop
    neg_price = df["Unit_Price"] <= 0
    df.loc[neg_price, "Unit_Price"] = np.where(
        has_disc[neg_price], np.round(expected_price[neg_price], 2), np.nan)
    n_neg_price = int((df["Unit_Price"] <= 0).sum())
    df = df[df["Unit_Price"] > 0]
    log["unit_price_recalculated"] = n_price_fixed + n_neg_price

    # 4. Derive missing Discount from the price identity (clamped 0..0.9)
    missing_disc = df["Discount"].isna()
    derived = 1 - df["Sales"] / (df["Quantity"] * df["Unit_Price"])
    df.loc[missing_disc, "Discount"] = np.clip(derived[missing_disc], 0, 0.9)
    log["discount_derived"] = n_disc_missing

    # 4b. Reconciliation check: Sales must equal Qty*Price*(1-Discount).
    #     A tiny number of lines combine a price typo AND a missing discount
    #     (both unknowable from each other) -> exclude as unreconcilable.
    resid = np.abs(df["Sales"] - df["Quantity"] * df["Unit_Price"] * (1 - df["Discount"]))
    n_unrec = int((resid > 0.05).sum())
    df = df[resid <= 0.05]
    log["unreconcilable_lines_dropped"] = n_unrec

    # 5. Duplicates
    n_dups = int(df.duplicated().sum())
    df = df.drop_duplicates()
    log["duplicates_dropped"] = n_dups

    # 6. Category casing
    df["Category"] = df["Category"].str.strip().str.title()
    df["Sub_Category"] = df["Sub_Category"].str.strip().str.title()
    df["Payment_Method"] = df["Payment_Method"].str.strip()
    df["Order_Status"] = df["Order_Status"].str.strip().str.title()

    # 7. Impute missing Age (segment median) and City (state mode)
    log["age_imputed"] = int(df["Age"].isna().sum())
    log["city_imputed"] = int(df["City"].isna().sum())
    df["Age"] = df.groupby("Customer_Segment")["Age"].transform(
        lambda s: s.fillna(s.median()))
    df["City"] = df.groupby("State")["City"].transform(
        lambda s: s.fillna(s.mode().iloc[0] if len(s.mode()) else "Unknown"))

    # 8. Business rule - Completed orders only for revenue analytics
    status_counts = df["Order_Status"].value_counts().to_dict()
    df = df[df["Order_Status"] == "Completed"]
    log["non_completed_excluded"] = int(df.shape[0])  # patched below

    # 9. Feature engineering
    df["Order_Year"] = df["Order_Date"].dt.year
    df["Order_Month"] = df["Order_Date"].dt.month
    df["Order_Day"] = df["Order_Date"].dt.day
    df["Day_Of_Week"] = df["Order_Date"].dt.day_name()

    bins = [0, 25, 35, 45, 55, 65, 100]
    labels = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)

    df["Discount_Band"] = pd.cut(
        df["Discount"], bins=[-0.001, 0.001, 0.10, 0.20, 0.30, 1.0],
        labels=["No Discount", "0-10%", "10-20%", "20-30%", "30%+"],
        include_lowest=True)

    df["Revenue"] = df["Sales"]
    return df, status_counts, log


def main() -> None:
    df = pd.read_csv(RAW)
    understanding = phase1_understanding(df)
    clean_df, status_counts, log = clean(df)

    # Patch excluded count (was overwritten in the loop)
    total_after_valid = understanding["raw_shape"][0] - understanding["invalid_dates"] \
        - understanding["negative_quantity"] - understanding["duplicate_rows"]
    excluded = int(status_counts.get("Cancelled", 0) + status_counts.get("Returned", 0)
                   + status_counts.get("Pending", 0))
    log["non_completed_excluded"] = excluded
    log["rows_remaining"] = int(len(clean_df))

    # Column order
    cols = ["Order_ID", "Order_Date", "Customer_ID", "Product_ID", "Product_Name",
            "Category", "Sub_Category", "Quantity", "Unit_Price", "Discount",
            "Sales", "Cost", "Profit", "Profit_Margin", "Revenue",
            "Customer_Name", "Customer_Segment", "Age", "Age_Group", "Gender",
            "City", "State", "Region", "Payment_Method", "Order_Status",
            "Order_Year", "Order_Month", "Order_Day", "Day_Of_Week", "Discount_Band"]
    clean_df = clean_df[cols]

    CLEAN.parent.mkdir(exist_ok=True)
    clean_df.to_csv(CLEAN, index=False)

    report = {
        "phase1": understanding,
        "phase2_actions": log,
        "cleaned_shape": [int(len(clean_df)), int(clean_df.shape[1])],
        "cleaned_totals": {
            "total_sales": round(float(clean_df["Sales"].sum()), 2),
            "total_orders": int(clean_df["Order_ID"].nunique()),
            "total_customers": int(clean_df["Customer_ID"].nunique()),
            "total_profit": round(float(clean_df["Profit"].sum()), 2),
        },
    }
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, default=str))

    # Human-readable report
    md = REPORT_MD.format(body="")
    md += f"""
## Baseline (Phase 1)
- Rows x columns: {understanding['raw_shape']}
- Duplicates: {understanding['duplicate_rows']}
- Invalid dates: {understanding['invalid_dates']}
- Negative quantities: {understanding['negative_quantity']}
- Negative unit prices: {understanding['negative_unit_price']}
- Missing values: {json.dumps(understanding['missing_pct'], indent=2)}

## Cleaning actions (Phase 2)
{json.dumps(log, indent=2)}

## After cleaning
- Cleaned rows: {len(clean_df):,} (Completed orders only)
- Total sales: $ {clean_df['Sales'].sum():,.0f}
- Total profit: $ {clean_df['Profit'].sum():,.0f}
- Total orders: {clean_df['Order_ID'].nunique():,}
- Total customers: {clean_df['Customer_ID'].nunique():,}
"""
    Path("reports/data_cleaning_report.md").write_text(md, encoding="utf-8")
    print(f"Cleaned {len(clean_df):,} rows -> {CLEAN}")
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()