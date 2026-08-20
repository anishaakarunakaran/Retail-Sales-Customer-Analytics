"""
Retail Sales & Customer Analytics - Synthetic Data Generator
============================================================
Creates a realistic, internally-consistent retail transaction dataset
(2021-2024) with engineered customer behaviours, seasonality, regional
variation, price bands and discount-driven profit erosion.

Design principles:
  * Deterministic (seeded) -> fully reproducible.
  * Referential integrity between customers, products, orders and locations.
  * Deliberate, realistic data-quality issues injected into the RAW file
    (missing values, duplicates, typos, invalid dates) so Phase 1-2 of the
    project has genuine work to do.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# 1. PRODUCT CATALOGUE
# ---------------------------------------------------------------------------
# (sub_category, min_price, max_price, base_margin, weight_in_orders)
CATALOGUE = {
    "Office Supplies": [
        ("Binders", 8, 90, 0.38, 2.0),
        ("Paper", 4, 60, 0.40, 2.2),
        ("Pens & Writing", 1, 45, 0.45, 2.0),
        ("Office Equipment", 30, 320, 0.30, 1.2),
        ("Storage & Organization", 10, 180, 0.35, 1.1),
    ],
    "Technology": [
        ("Phones", 150, 1400, 0.24, 1.0),
        ("Computers", 400, 2600, 0.22, 0.8),
        ("Accessories", 20, 260, 0.38, 1.6),
        ("Peripherals", 15, 220, 0.35, 1.4),
        ("Software", 10, 320, 0.55, 1.0),
    ],
    "Furniture": [
        ("Chairs", 80, 950, 0.38, 1.2),
        ("Tables", 120, 1200, 0.35, 0.9),
        ("Bookcases", 90, 750, 0.36, 0.8),
        ("Office Desks", 150, 1400, 0.34, 0.8),
        ("Storage Furniture", 60, 600, 0.37, 0.8),
    ],
    "Home & Lifestyle": [
        ("Appliances", 40, 850, 0.32, 1.2),
        ("Kitchenware", 10, 320, 0.42, 1.5),
        ("Lighting", 12, 240, 0.40, 1.2),
        ("Home Decor", 5, 180, 0.45, 1.6),
        ("Cleaning Supplies", 5, 120, 0.44, 1.4),
    ],
}

CATEGORY_MARGIN_SHIFT = {
    "Office Supplies": 0.00,
    "Technology": -0.06,   # tech is squeezed
    "Furniture": 0.02,
    "Home & Lifestyle": 0.04,
}

BRANDS = {
    "Technology": ["NovaTech", "CoreX", "PixelWave", "VoltLink", "Apex"],
    "Furniture": ["Oakline", "ComfortPro", "UrbanDesk", "Hearth"],
    "Office Supplies": ["StapleCo", "ClearPoint", "EverWrite", "InkWell"],
    "Home & Lifestyle": ["Lumina", "HomeEase", "BrightLeaf", "FreshHome"],
}


def build_products() -> pd.DataFrame:
    rows = []
    pid = 1
    for category, subs in CATALOGUE.items():
        brand = RNG.choice(BRANDS[category])
        for sub_cat, lo, hi, margin, w in subs:
            n_items = RNG.integers(4, 7)          # products per sub-category
            for i in range(1, n_items + 1):
                price = float(np.round(RNG.uniform(lo, hi), 2))
                base_margin = margin + CATEGORY_MARGIN_SHIFT[category]
                base_margin = float(np.clip(base_margin, 0.18, 0.55))
                name = f"{brand} {sub_cat.rstrip('s')} {i}"
                rows.append({
                    "product_id": pid,
                    "product_name": name,
                    "category": category,
                    "sub_category": sub_cat,
                    "unit_price": price,
                    "unit_cost": float(np.round(price * (1 - base_margin), 2)),
                    "base_margin": base_margin,
                    "catalog_weight": w,
                })
                pid += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. LOCATIONS  (Region -> State -> City)
# ---------------------------------------------------------------------------
REGIONS = {
    "East": {
        "New York": ["New York", "Buffalo"],
        "Pennsylvania": ["Philadelphia", "Pittsburgh"],
        "Massachusetts": ["Boston"],
        "Virginia": ["Richmond"],
    },
    "West": {
        "California": ["Los Angeles", "San Francisco", "San Diego"],
        "Washington": ["Seattle"],
        "Colorado": ["Denver"],
        "Arizona": ["Phoenix"],
    },
    "Central": {
        "Illinois": ["Chicago"],
        "Ohio": ["Columbus", "Cleveland"],
        "Michigan": ["Detroit"],
        "Texas": ["Dallas", "Houston"],
    },
    "South": {
        "Florida": ["Miami", "Orlando"],
        "Georgia": ["Atlanta", "Savannah"],
        "North Carolina": ["Charlotte"],
        "Texas": ["Austin"],
    },
}

# Regional demand strength -> drives "which regions perform best" insight
REGION_WEIGHT = {"West": 1.25, "East": 1.10, "South": 0.95, "Central": 0.75}
REGION_MARGIN_SHIFT = {"West": 0.01, "East": 0.005, "South": -0.02, "Central": -0.035}


def build_locations() -> pd.DataFrame:
    rows, lid = [], 1
    for region, states in REGIONS.items():
        for state, cities in states.items():
            for city in cities:
                rows.append({
                    "location_id": lid,
                    "city": city,
                    "state": state,
                    "region": region,
                })
                lid += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. CUSTOMERS
# ---------------------------------------------------------------------------
FIRST_NAMES = {
    "East": ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
             "Linda", "David", "Elizabeth", "William", "Susan", "Sarah", "Karen"],
    "West": ["Michael", "Ashley", "Christopher", "Jessica", "Matthew", "Emily",
             "Joshua", "Amanda", "Daniel", "Melissa", "Andrew", "Stephanie"],
    "Central": ["Robert", "Barbara", "Brian", "Laura", "Kevin", "Michelle",
                "Jason", "Kimberly", "Jeffrey", "Angela", "Scott", "Amy"],
    "South": ["William", "Tiffany", "Charles", "Brittany", "Thomas", "Sandra",
              "Justin", "Rebecca", "Anthony", "Sharon", "Brandon", "Nicole"],
}
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
              "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
              "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
              "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
              "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King"]

SEGMENT_MIX = {"Consumer": 0.40, "Corporate": 0.25, "Home Office": 0.20, "Small Business": 0.15}

# Segment behaviour: order_rate (annual purchase propensity), basket size, price sensitivity
SEGMENT_BEHAVIOUR = {
    "Consumer":       {"order_rate": 0.40, "basket": (1, 3),   "price_sens": 0.10},
    "Corporate":      {"order_rate": 1.40, "basket": (2, 6),   "price_sens": 0.04},
    "Home Office":    {"order_rate": 0.70, "basket": (1, 4),   "price_sens": 0.08},
    "Small Business": {"order_rate": 1.00, "basket": (2, 5),   "price_sens": 0.06},
}


def build_customers(loc_df: pd.DataFrame) -> pd.DataFrame:
    n = 1800
    segments = RNG.choice(list(SEGMENT_MIX), size=n, p=list(SEGMENT_MIX.values()))
    cities = loc_df.sample(n=n, replace=True,
                           weights=loc_df["region"].map(REGION_WEIGHT).values,
                           random_state=RNG).reset_index(drop=True)

    rows = []
    for i, (seg, loc) in enumerate(zip(segments, cities.itertuples()), start=1):
        region = loc.region
        age_lo, age_hi = {
            "Consumer": (18, 68), "Corporate": (24, 60),
            "Home Office": (22, 65), "Small Business": (25, 62),
        }[seg]
        age = int(np.clip(RNG.normal((age_lo + age_hi) / 2, 11), age_lo, age_hi))
        gender = RNG.choice(["Male", "Female"], p=[0.49, 0.51])
        first = RNG.choice(FIRST_NAMES[region])
        last = RNG.choice(LAST_NAMES)
        rows.append({
            "customer_id": i,
            "customer_name": f"{first} {last}",
            "customer_segment": seg,
            "age": age,
            "gender": gender,
            "city": loc.city,
            "state": loc.state,
            "region": region,
            "location_id": loc.location_id,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. ORDERS + ORDER LINES
# ---------------------------------------------------------------------------
DATE_START = pd.Timestamp("2021-01-01")
DATE_END = pd.Timestamp("2024-12-31")

# Monthly seasonality (index 0 = January)
MONTH_WEIGHT = [0.80, 0.85, 0.95, 0.90, 1.00, 1.05,
                0.70, 1.20, 1.25, 1.05, 1.60, 1.75]
# Annual growth trend (2021 -> 2024) so growth analysis is meaningful
YEAR_GROWTH = {2021: 1.00, 2022: 1.07, 2023: 1.15, 2024: 1.24}
# Weekend uplift for consumers (home shopping)
WEEKEND_UPLIFT = {"Consumer": 1.45, "Home Office": 1.25,
                  "Corporate": 0.75, "Small Business": 0.85}

DISCOUNT_BANDS = [(0.00, 0.00, 0.32),   # no discount
                  (0.00, 0.10, 0.22),   # light
                  (0.10, 0.20, 0.24),   # medium
                  (0.20, 0.30, 0.14),   # heavy
                  (0.30, 0.45, 0.08)]   # deep - erodes margin


def pick_discount(seg: str) -> float:
    price_sens = SEGMENT_BEHAVIOUR[seg]["price_sens"]
    weights = [w * (1 + price_sens * 2 if i in (1, 2) else 1) for i, (_, _, w) in enumerate(DISCOUNT_BANDS)]
    weights = np.array(weights) / np.sum(weights)
    lo, hi, _ = DISCOUNT_BANDS[RNG.choice(len(DISCOUNT_BANDS), p=weights)]
    return float(np.round(RNG.uniform(lo, hi), 4))


def generate_orders(customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    n_days = (DATE_END - DATE_START).days + 1

    # Per-customer lifetime order count drawn from a Poisson model
    # -> produces a realistic long tail (many low-frequency buyers,
    #    a few heavy buyers) instead of every customer repeating.
    # Two-mode design: ~30% "light" shoppers (sporadic, often 1-2 orders),
    # the rest regular/repeat; a gamma multiplier adds right-skew; 8% are
    # heavy hitters who drive a large share of volume.
    rate = customers["customer_segment"].map(
        lambda s: SEGMENT_BEHAVIOUR[s]["order_rate"]).values
    ORDER_SCALE = 8.0  # boosts volume toward ~100k line items
    light = RNG.random(len(customers)) < 0.30
    mult = RNG.gamma(1.5, 0.67, size=len(customers))          # mean ~1, right-skew
    lam = rate * 4 * 0.92 * ORDER_SCALE * mult
    lam = np.where(light, lam * 0.15, lam)
    heavy = (RNG.random(len(customers)) < 0.08) & ~light
    lam = np.where(heavy, lam * RNG.uniform(1.8, 3.2, len(customers)), lam)
    order_counts = RNG.poisson(lam).astype(int)
    total_orders = int(order_counts.sum())
    cust_ids = np.repeat(customers["customer_id"].values, order_counts)

    # Draw dates (seasonal + year-growth + weekend-aware)
    day_weights = []
    for i in range(n_days):
        d = DATE_START + pd.Timedelta(days=i)
        w = MONTH_WEIGHT[d.month - 1] * YEAR_GROWTH[d.year]
        day_weights.append(w)
    day_weights = np.array(day_weights)
    day_weights = day_weights / day_weights.sum()
    order_days = RNG.choice(np.arange(n_days), size=total_orders, p=day_weights)
    order_dates = [DATE_START + pd.Timedelta(days=int(d)) for d in order_days]

    # Line items
    lines = []
    order_id = 10000
    for cust_id, date in zip(cust_ids, order_dates):
        seg = customers.loc[customers["customer_id"] == cust_id, "customer_segment"].iloc[0]
        lo, hi = SEGMENT_BEHAVIOUR[seg]["basket"]
        n_lines = int(RNG.integers(lo, hi + 1))
        status = RNG.choice(["Completed", "Completed", "Completed", "Cancelled",
                             "Returned", "Pending"],
                            p=[0.84, 0.06, 0.03, 0.03, 0.025, 0.015])
        payment = RNG.choice(["Card", "UPI", "Net Banking", "COD", "Wallet"],
                             p=[0.35, 0.25, 0.20, 0.12, 0.08])
        for _ in range(n_lines):
            prod = products.sample(1, weights=products["catalog_weight"], random_state=RNG).iloc[0]
            qty = int(RNG.integers(1, 6))
            discount = pick_discount(seg)
            unit_price = prod.unit_price
            unit_cost = prod.unit_cost
            line_sales = round(qty * unit_price * (1 - discount), 2)
            line_cost = round(qty * unit_cost, 2)
            line_profit = round(line_sales - line_cost, 2)
            line_margin = round(line_profit / line_sales, 4) if line_sales else 0.0
            lines.append({
                "Order_ID": order_id,
                "Order_Date": date,
                "Customer_ID": cust_id,
                "Product_ID": prod.product_id,
                "Product_Name": prod.product_name,
                "Category": prod.category,
                "Sub_Category": prod.sub_category,
                "Quantity": qty,
                "Unit_Price": unit_price,
                "Discount": discount,
                "Sales": line_sales,
                "Cost": line_cost,
                "Profit": line_profit,
                "Profit_Margin": line_margin,
            })
        order_id += 1

    df = pd.DataFrame(lines)
    # Merge customer attributes
    df = df.merge(customers[["customer_id", "customer_name", "customer_segment",
                             "age", "gender", "city", "state", "region"]],
                  left_on="Customer_ID", right_on="customer_id", how="left")
    df.drop(columns="customer_id", inplace=True)
    df.rename(columns={"customer_name": "Customer_Name",
                       "customer_segment": "Customer_Segment",
                       "age": "Age", "gender": "Gender",
                       "city": "City", "state": "State", "region": "Region"},
              inplace=True)
    df["Payment_Method"] = np.nan  # filled below per-order
    df["Order_Status"] = np.nan

    # Payment + status are order-level: propagate by Order_ID
    order_meta = pd.DataFrame({
        "Order_ID": [int(i) for i in np.unique(lines and [l["Order_ID"] for l in lines])]})
    # rebuild properly
    order_ids = df["Order_ID"].unique()
    meta = pd.DataFrame({
        "Order_ID": order_ids,
        "Payment_Method": RNG.choice(["Card", "UPI", "Net Banking", "COD", "Wallet"],
                                     size=len(order_ids), p=[0.35, 0.25, 0.20, 0.12, 0.08]),
        "Order_Status": RNG.choice(["Completed", "Completed", "Completed", "Cancelled",
                                    "Returned", "Pending"],
                                   size=len(order_ids), p=[0.84, 0.06, 0.03, 0.03, 0.025, 0.015]),
    })
    df = df.drop(columns=["Payment_Method", "Order_Status"]).merge(meta, on="Order_ID")

    # Order date -> cast to string for raw export
    df["Order_Date"] = df["Order_Date"].dt.strftime("%Y-%m-%d")
    cols = ["Order_ID", "Order_Date", "Customer_ID", "Product_ID", "Product_Name",
            "Category", "Sub_Category", "Quantity", "Unit_Price", "Discount",
            "Sales", "Cost", "Profit", "Profit_Margin", "Customer_Name",
            "Customer_Segment", "Age", "Gender", "City", "State", "Region",
            "Payment_Method", "Order_Status"]
    return df[cols]


# ---------------------------------------------------------------------------
# 5. INJECT REALISTIC DATA-QUALITY ISSUES (raw file only)
# ---------------------------------------------------------------------------
def inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)

    # a) Missing Age (~1.6%)
    age_missing = RNG.random(n) < 0.016
    df.loc[age_missing, "Age"] = np.nan

    # b) Missing City (~0.9%)
    city_missing = RNG.random(n) < 0.009
    df.loc[city_missing, "City"] = np.nan

    # c) Missing Discount (~1.2%)
    disc_missing = RNG.random(n) < 0.012
    df.loc[disc_missing, "Discount"] = "-"        # string -> forces type cleaning

    # d) Duplicate rows (~0.3%)
    dup_idx = RNG.choice(n, size=int(n * 0.003), replace=False)
    dups = df.iloc[dup_idx].copy()
    df = pd.concat([df, dups], ignore_index=True)

    # e) Category casing typos (~0.6%)
    for _ in range(int(n * 0.006)):
        i = RNG.integers(0, len(df))
        df.loc[i, "Category"] = df.loc[i, "Category"].lower()

    # f) Invalid dates (~0.2%) - e.g. impossible day/month
    bad_dates = RNG.random(len(df)) < 0.002
    df.loc[bad_dates, "Order_Date"] = RNG.choice(["2021/02/30", "2023-13-01", "2022-00-15"], size=bad_dates.sum())

    # g) Extreme Unit_Price typos (~0.15%) - one extra digit or negative
    price_bad = RNG.random(len(df)) < 0.0015
    df.loc[price_bad, "Unit_Price"] = df.loc[price_bad, "Unit_Price"] * 10
    neg_price = RNG.random(len(df)) < 0.0005
    df.loc[neg_price, "Unit_Price"] = -df.loc[neg_price, "Unit_Price"].abs()

    # h) Negative Quantity (~0.1%)
    neg_qty = RNG.random(len(df)) < 0.001
    df.loc[neg_qty, "Quantity"] = -df.loc[neg_qty, "Quantity"]

    return df


def main() -> None:
    products = build_products()
    locations = build_locations()
    customers = build_customers(locations)
    sales = generate_orders(customers, products)
    raw = inject_quality_issues(sales)

    out = "data/raw/raw_retail_sales.csv"
    raw.to_csv(out, index=False)
    print(f"Saved {len(raw):,} rows x {raw.shape[1]} cols -> {out}")
    print(f"Customers: {customers.shape[0]:,} | Products: {products.shape[0]} | "
          f"Locations: {locations.shape[0]}")
    print("Sample:")
    print(raw.head(3).to_string())


if __name__ == "__main__":
    main()