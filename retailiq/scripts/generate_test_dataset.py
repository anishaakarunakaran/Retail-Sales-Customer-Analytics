import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(123)

N = 2000

FIRST_NAMES = [
    "Amit", "Priya", "Rahul", "Sneha", "Vikram", "Ananya", "Rohan", "Meera",
    "Arjun", "Deepa", "Kiran", "Pooja", "Sanjay", "Nisha", "Rajesh", "Kavita",
]
LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Reddy", "Nair", "Gupta", "Joshi",
    "Desai", "Iyer", "Mishra", "Tiwari", "Rao", "Mehta", "Chopra", "Verma",
]

REGIONS = ["East", "West", "South", "Central"]
REGION_STATES = {
    "East": ["Maharashtra", "Gujarat"],
    "West": ["Karnataka", "Kerala"],
    "South": ["Tamil Nadu", "Andhra Pradesh"],
    "Central": ["Madhya Pradesh", "Rajasthan"],
}
STATE_CITIES = {
    "Maharashtra": ["Mumbai", "Pune"],
    "Gujarat": ["Ahmedabad", "Surat"],
    "Karnataka": ["Bengaluru", "Mysuru"],
    "Kerala": ["Kochi", "Thiruvananthapuram"],
    "Tamil Nadu": ["Chennai", "Coimbatore"],
    "Andhra Pradesh": ["Hyderabad", "Visakhapatnam"],
    "Madhya Pradesh": ["Bhopal", "Indore"],
    "Rajasthan": ["Jaipur", "Jodhpur"],
}

CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Headphones", "Smartwatches"],
    "Clothing": ["T-Shirts", "Jeans", "Dresses", "Sneakers"],
    "Home & Garden": ["Lamps", "Plant Pots", "Cushions", "Cookware"],
    "Sports": ["Cricket Bats", "Yoga Mats", "Dumbbells", "Football"],
    "Books": ["Fiction", "Non-Fiction", "Comics", "Academic"],
    "Food & Beverage": ["Coffee", "Snacks", "Tea", "Chocolate"],
}

SUB_BRANDS = {
    "Smartphones": ["Samsung", "Apple", "OnePlus", "Xiaomi", "Realme"],
    "Laptops": ["Dell", "HP", "Lenovo", "Asus", "Acer"],
    "Headphones": ["Sony", "JBL", "Boat", "Sennheiser", "Bose"],
    "Smartwatches": ["Apple", "Samsung", "Fitbit", "Amazfit", "Garmin"],
    "T-Shirts": ["Levis", "H&M", "Zara", "Allen Solly", "Pepe Jeans"],
    "Jeans": ["Levis", "Wrangler", "Lee", "Pepe Jeans", "Spykar"],
    "Dresses": ["Zara", "H&M", "FabAlley", "Mango", "Only"],
    "Sneakers": ["Nike", "Adidas", "Puma", "Reebok", "Skechers"],
    "Lamps": ["Philips", "Havells", "Syska", "Wipro", "Orient"],
    "Plant Pots": ["Gardener", "Greenbase", "NurseryLive", "Leafy", "Ugaoo"],
    "Cushions": ["Wakefit", "Sleepwell", "Duroflex", "Kurlon", "Peps"],
    "Cookware": ["Prestige", "Pigeon", "Hawkins", "Borosil", "Milton"],
    "Cricket Bats": ["SS", "MRF", "SG", "GM", "Kookaburra"],
    "Yoga Mats": ["Boldfit", "Kobo", "Strauss", "Cosco", "YogaDesign"],
    "Dumbbells": ["Kobo", "Cosco", "Boldfit", "HealthGenie", "Strauss"],
    "Football": ["Adidas", "Nike", "Nivia", "Vector X", "Mikasa"],
    "Fiction": ["Penguin", "HarperCollins", "Random House", "Hachette", "Simon Schuster"],
    "Non-Fiction": ["Penguin", "HarperCollins", "Oxford", "Cambridge", "Pan Macmillan"],
    "Comics": ["Marvel", "DC", "Dark Horse", "Image", "IDW"],
    "Academic": ["Pearson", "McGraw Hill", "Cengage", "Wiley", "Springer"],
    "Coffee": ["Nescafe", "Blue Tokai", "Bru", "Starbucks", "Davidoff"],
    "Snacks": ["Haldiram", "Britannia", "Parle", "Lays", "Kurkure"],
    "Tea": ["Tata Tea", "Red Label", "Lipton", "Wagh Bakri", "24 Mantra"],
    "Chocolate": ["Cadbury", "Ferrero", "Nestle", "Amul", "Lindt"],
}

SUB_PRICE_RANGES = {
    "Smartphones": (150, 1200), "Laptops": (500, 2500), "Headphones": (30, 350),
    "Smartwatches": (80, 600), "T-Shirts": (15, 80), "Jeans": (30, 120),
    "Dresses": (25, 150), "Sneakers": (40, 200), "Lamps": (15, 120),
    "Plant Pots": (8, 60), "Cushions": (10, 70), "Cookware": (20, 200),
    "Cricket Bats": (30, 400), "Yoga Mats": (10, 80), "Dumbbells": (15, 150),
    "Football": (15, 100), "Fiction": (5, 35), "Non-Fiction": (8, 50),
    "Comics": (5, 25), "Academic": (10, 80), "Coffee": (5, 40),
    "Snacks": (2, 20), "Tea": (3, 25), "Chocolate": (2, 30),
}

SUB_MARGINS = {
    "Smartphones": 0.20, "Laptops": 0.22, "Headphones": 0.30, "Smartwatches": 0.25,
    "T-Shirts": 0.35, "Jeans": 0.32, "Dresses": 0.30, "Sneakers": 0.28,
    "Lamps": 0.25, "Plant Pots": 0.40, "Cushions": 0.35, "Cookware": 0.22,
    "Cricket Bats": 0.28, "Yoga Mats": 0.40, "Dumbbells": 0.25, "Football": 0.30,
    "Fiction": 0.45, "Non-Fiction": 0.42, "Comics": 0.40, "Academic": 0.38,
    "Coffee": 0.30, "Snacks": 0.25, "Tea": 0.28, "Chocolate": 0.22,
}

SEGMENTS = ["Consumer", "Corporate", "Home Office", "Small Business"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash", "UPI", "Net Banking", "Wallet"]
CHANNELS = ["Online", "Offline"]
STORE_TYPES = ["Flagship", "Standard", "Outlet"]

START_DATE = pd.Timestamp("2021-01-01")
END_DATE = pd.Timestamp("2024-12-31")

QUALITY_ISSUES = {
    "missing_values": 0,
    "duplicate_transaction_ids": 0,
    "invalid_dates": 0,
    "negative_quantities": 0,
    "zero_prices": 0,
    "invalid_categories": 0,
    "missing_customer_ids": 0,
    "inconsistent_states": 0,
    "extreme_outliers": 0,
    "high_discounts": 0,
    "incorrect_data_types": 0,
}

records = []
for i in range(N):
    cid = f"CUST{i+1:05d}"
    fn = RNG.choice(FIRST_NAMES)
    ln = RNG.choice(LAST_NAMES)
    age = int(np.clip(RNG.normal(38, 12), 18, 75))
    gender = RNG.choice(["Male", "Female"], p=[0.52, 0.48])
    region = RNG.choice(REGIONS)
    state = RNG.choice(REGION_STATES[region])
    city = RNG.choice(STATE_CITIES[state])
    segment = RNG.choice(SEGMENTS, p=[0.45, 0.25, 0.15, 0.15])

    cat = RNG.choice(list(CATEGORIES.keys()), p=[0.25, 0.25, 0.15, 0.12, 0.08, 0.15])
    sub = RNG.choice(CATEGORIES[cat])
    brand = RNG.choice(SUB_BRANDS[sub])
    price_range = SUB_PRICE_RANGES[sub]
    margin = SUB_MARGINS[sub]

    day_span = (END_DATE - START_DATE).days
    day_off = RNG.integers(0, day_span + 1)
    m = RNG.integers(1, 13)
    max_d = pd.Timestamp(2022, m, 1).days_in_month
    d = int(RNG.integers(1, max_d + 1))
    txn_date = pd.Timestamp(2022, m, d)

    price = round(float(RNG.uniform(price_range[0], price_range[1])), 2)
    qty = int(RNG.integers(1, 11))
    discount = float(RNG.choice([0, 5, 10, 15, 20], p=[0.55, 0.15, 0.15, 0.10, 0.05]))
    cost = round(price * (1 - margin) * float(RNG.uniform(0.9, 1.05)), 2)
    sales = round(price * qty * (1 - discount / 100), 2)
    profit = round(sales - cost * qty, 2)

    store_map = {"East": 101, "West": 201, "South": 301, "Central": 401}
    store_id = store_map[region]

    raw = RNG.exponential(1.5)
    rating = min(5, max(1, int(round(raw) + 1)))
    returned = 1 if RNG.random() < 0.05 else 0

    records.append({
        "transaction_id": f"TXN{i+1:06d}",
        "transaction_date": txn_date.strftime("%Y-%m-%d"),
        "customer_id": cid,
        "customer_name": f"{fn} {ln}",
        "customer_age": age,
        "customer_gender": gender,
        "customer_city": city,
        "customer_state": state,
        "customer_segment": segment,
        "product_id": f"PROD{i+1:05d}",
        "product_name": f"{brand} {sub} {i+1}",
        "category": cat,
        "subcategory": sub,
        "brand": brand,
        "unit_price": price,
        "quantity": qty,
        "discount_percent": discount,
        "sales_amount": sales,
        "cost_amount": cost * qty,
        "profit_amount": profit,
        "payment_method": RNG.choice(PAYMENT_METHODS, p=[0.25, 0.20, 0.15, 0.20, 0.10, 0.10]),
        "sales_channel": RNG.choice(CHANNELS, p=[0.45, 0.55]),
        "store_id": store_id,
        "store_type": RNG.choice(STORE_TYPES, p=[0.10, 0.60, 0.30]),
        "region": region,
        "customer_rating": rating,
        "returned": returned,
    })

df = pd.DataFrame(records)

issue_indices_missing_values = RNG.choice(N, size=30, replace=False)
missing_cols = ["customer_name", "customer_age", "customer_city", "customer_segment",
                "brand", "unit_price", "discount_percent", "payment_method",
                "sales_channel", "customer_rating"]
for idx in issue_indices_missing_values:
    col = RNG.choice(missing_cols)
    df.at[idx, col] = np.nan
QUALITY_ISSUES["missing_values"] = len(issue_indices_missing_values)

dup_indices = RNG.choice(N, size=15, replace=False)
dup_rows = df.iloc[dup_indices].copy()
df = pd.concat([df, dup_rows], ignore_index=True)
QUALITY_ISSUES["duplicate_transaction_ids"] = len(dup_indices)

invalid_date_indices = RNG.choice(len(df), size=10, replace=False)
bad_dates = ["2022-00-15", "2022-13-10", "2022-02-32", "2022-04-32",
             "2022-06-00", "2023-13-25", "2023-00-05", "2023-11-32",
             "2024-02-30", "2024-13-01"]
for i, idx in enumerate(invalid_date_indices):
    df.at[idx, "transaction_date"] = bad_dates[i]
QUALITY_ISSUES["invalid_dates"] = len(invalid_date_indices)

neg_qty_indices = RNG.choice(len(df), size=8, replace=False)
for idx in neg_qty_indices:
    df.at[idx, "quantity"] = -1 * int(RNG.integers(1, 5))
QUALITY_ISSUES["negative_quantities"] = len(neg_qty_indices)

zero_price_indices = RNG.choice(len(df), size=5, replace=False)
for idx in zero_price_indices:
    df.at[idx, "unit_price"] = 0
QUALITY_ISSUES["zero_prices"] = len(zero_price_indices)

bad_categories = ["Electrnics", "Cloting", "HomeGarden", "Sprts", "Boks",
                  "FoodBeverge", "ELECTRONICS", "clothing", "misc", "unknown"]
invalid_cat_indices = RNG.choice(len(df), size=10, replace=False)
for i, idx in enumerate(invalid_cat_indices):
    df.at[idx, "category"] = bad_categories[i]
QUALITY_ISSUES["invalid_categories"] = len(invalid_cat_indices)

missing_cid_indices = RNG.choice(len(df), size=5, replace=False)
for idx in missing_cid_indices:
    df.at[idx, "customer_id"] = np.nan
QUALITY_ISSUES["missing_customer_ids"] = len(missing_cid_indices)

bad_state_map = {
    "Maharashtra": "MH", "Karnataka": "Karnatka", "Tamil Nadu": "TN",
    "Gujarat": "Gujrat", "Kerala": "Kerla", "Rajasthan": "Rajsthan",
    "Madhya Pradesh": "MP", "Andhra Pradesh": "Andhra"
}
inconsistent_state_indices = RNG.choice(len(df), size=10, replace=False)
for idx in inconsistent_state_indices:
    orig = df.at[idx, "customer_state"]
    if orig in bad_state_map:
        df.at[idx, "customer_state"] = bad_state_map[orig]
QUALITY_ISSUES["inconsistent_states"] = len(inconsistent_state_indices)

outlier_indices = RNG.choice(len(df), size=5, replace=False)
for idx in outlier_indices:
    df.at[idx, "unit_price"] = float(RNG.choice([50000, 75000, 99999, 500000, 1000000]))
QUALITY_ISSUES["extreme_outliers"] = len(outlier_indices)

high_disc_indices = RNG.choice(len(df), size=10, replace=False)
for idx in high_disc_indices:
    df.at[idx, "discount_percent"] = float(RNG.choice([85, 90, 95, 99, 100, 82, 88, 92, 97, 81]))
QUALITY_ISSUES["high_discounts"] = len(high_disc_indices)

bad_type_indices = RNG.choice(len(df), size=10, replace=False)
bad_type_cols = ["unit_price", "quantity", "discount_percent", "sales_amount",
                 "cost_amount", "profit_amount", "customer_age", "customer_rating"]
bad_type_values = ["N/A", "null", "--", "None", "N/A", "null", "--", "None", "N/A", "null"]
for i, idx in enumerate(bad_type_indices):
    col = RNG.choice(bad_type_cols)
    df.at[idx, col] = bad_type_values[i]
QUALITY_ISSUES["incorrect_data_types"] = len(bad_type_indices)

df = df.sample(frac=1, random_state=42).reset_index(drop=True)

out_dir = Path(__file__).resolve().parent.parent / "demo-data"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "retail_sales_test.csv"
df.to_csv(out_path, index=False)

print(f"Generated {len(df)} rows with data quality issues -> {out_path.relative_to(Path(__file__).resolve().parent.parent)}")
print()
print("Data Quality Summary:")
print("-" * 45)
total_issues = 0
for issue_type, count in QUALITY_ISSUES.items():
    label = issue_type.replace("_", " ").title()
    print(f"  {label:<30} : {count}")
    total_issues += count
print("-" * 45)
print(f"  {'Total Issues':<30} : {total_issues}")
