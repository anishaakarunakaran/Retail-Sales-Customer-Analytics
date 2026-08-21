import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)

N = 32000

FIRST_NAMES = [
    "Amit", "Priya", "Rahul", "Sneha", "Vikram", "Ananya", "Rohan", "Meera",
    "Arjun", "Deepa", "Kiran", "Pooja", "Sanjay", "Nisha", "Rajesh", "Kavita",
    "Manish", "Shreya", "Arun", "Divya", "Nitin", "Sunita", "Gaurav", "Ritu",
    "Pradeep", "Swati", "Mohan", "Geeta", "Suresh", "Anita"
]
LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Reddy", "Nair", "Gupta", "Joshi",
    "Desai", "Iyer", "Mishra", "Tiwari", "Rao", "Mehta", "Chopra", "Verma",
    "Kapoor", "Saxena", "Malhotra", "Aggarwal"
]

REGIONS = ["East", "West", "South", "Central"]
REGION_STATES = {
    "East": ["Maharashtra", "Gujarat"],
    "West": ["Karnataka", "Kerala"],
    "South": ["Tamil Nadu", "Andhra Pradesh"],
    "Central": ["Madhya Pradesh", "Rajasthan"],
}
STATE_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubli"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Andhra Pradesh": ["Hyderabad", "Visakhapatnam", "Vijayawada"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
}

CATEGORIES = {
    "Electronics": {
        "subcategories": {
            "Smartphones": {
                "brands": ["Samsung", "Apple", "OnePlus", "Xiaomi", "Realme"],
                "price_range": (150, 1200),
                "cost_margin": 0.20,
            },
            "Laptops": {
                "brands": ["Dell", "HP", "Lenovo", "Asus", "Acer"],
                "price_range": (500, 2500),
                "cost_margin": 0.22,
            },
            "Headphones": {
                "brands": ["Sony", "JBL", "Boat", "Sennheiser", "Bose"],
                "price_range": (30, 350),
                "cost_margin": 0.30,
            },
            "Smartwatches": {
                "brands": ["Apple", "Samsung", "Fitbit", "Amazfit", "Garmin"],
                "price_range": (80, 600),
                "cost_margin": 0.25,
            },
        }
    },
    "Clothing": {
        "subcategories": {
            "T-Shirts": {
                "brands": ["Levis", "H&M", "Zara", "Allen Solly", "Pepe Jeans"],
                "price_range": (15, 80),
                "cost_margin": 0.35,
            },
            "Jeans": {
                "brands": ["Levis", "Wrangler", "Lee", "Pepe Jeans", "Spykar"],
                "price_range": (30, 120),
                "cost_margin": 0.32,
            },
            "Dresses": {
                "brands": ["Zara", "H&M", "FabAlley", "Mango", "Only"],
                "price_range": (25, 150),
                "cost_margin": 0.30,
            },
            "Sneakers": {
                "brands": ["Nike", "Adidas", "Puma", "Reebok", "Skechers"],
                "price_range": (40, 200),
                "cost_margin": 0.28,
            },
        }
    },
    "Home & Garden": {
        "subcategories": {
            "Lamps": {
                "brands": ["Philips", "Havells", "Syska", "Wipro", "Orient"],
                "price_range": (15, 120),
                "cost_margin": 0.25,
            },
            "Plant Pots": {
                "brands": ["Gardener", "Greenbase", "NurseryLive", "Leafy", "Ugaoo"],
                "price_range": (8, 60),
                "cost_margin": 0.40,
            },
            "Cushions": {
                "brands": ["Wakefit", "Sleepwell", "Duroflex", "Kurlon", "Peps"],
                "price_range": (10, 70),
                "cost_margin": 0.35,
            },
            "Cookware": {
                "brands": ["Prestige", "Pigeon", "Hawkins", "Borosil", "Milton"],
                "price_range": (20, 200),
                "cost_margin": 0.22,
            },
        }
    },
    "Sports": {
        "subcategories": {
            "Cricket Bats": {
                "brands": ["SS", "MRF", "SG", "GM", "Kookaburra"],
                "price_range": (30, 400),
                "cost_margin": 0.28,
            },
            "Yoga Mats": {
                "brands": ["Boldfit", "Kobo", "Strauss", "Cosco", "YogaDesign"],
                "price_range": (10, 80),
                "cost_margin": 0.40,
            },
            "Dumbbells": {
                "brands": ["Kobo", "Cosco", "Boldfit", "HealthGenie", "Strauss"],
                "price_range": (15, 150),
                "cost_margin": 0.25,
            },
            "Football": {
                "brands": ["Adidas", "Nike", "Nivia", "Vector X", "Mikasa"],
                "price_range": (15, 100),
                "cost_margin": 0.30,
            },
        }
    },
    "Books": {
        "subcategories": {
            "Fiction": {
                "brands": ["Penguin", "HarperCollins", "Random House", "Hachette", "Simon Schuster"],
                "price_range": (5, 35),
                "cost_margin": 0.45,
            },
            "Non-Fiction": {
                "brands": ["Penguin", "HarperCollins", "Oxford", "Cambridge", "Pan Macmillan"],
                "price_range": (8, 50),
                "cost_margin": 0.42,
            },
            "Comics": {
                "brands": ["Marvel", "DC", "Dark Horse", "Image", "IDW"],
                "price_range": (5, 25),
                "cost_margin": 0.40,
            },
            "Academic": {
                "brands": ["Pearson", "McGraw Hill", "Cengage", "Wiley", "Springer"],
                "price_range": (10, 80),
                "cost_margin": 0.38,
            },
        }
    },
    "Food & Beverage": {
        "subcategories": {
            "Coffee": {
                "brands": ["Nescafe", "Blue Tokai", "Bru", "Starbucks", "Davidoff"],
                "price_range": (5, 40),
                "cost_margin": 0.30,
            },
            "Snacks": {
                "brands": ["Haldiram", "Britannia", "Parle", "Lays", "Kurkure"],
                "price_range": (2, 20),
                "cost_margin": 0.25,
            },
            "Tea": {
                "brands": ["Tata Tea", "Red Label", "Lipton", "Wagh Bakri", "24 Mantra"],
                "price_range": (3, 25),
                "cost_margin": 0.28,
            },
            "Chocolate": {
                "brands": ["Cadbury", "Ferrero", "Nestle", "Amul", "Lindt"],
                "price_range": (2, 30),
                "cost_margin": 0.22,
            },
        }
    },
}

SEGMENTS = ["Consumer", "Corporate", "Home Office", "Small Business"]
SEGMENT_WEIGHTS = [0.45, 0.25, 0.15, 0.15]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash", "UPI", "Net Banking", "Wallet"]
PAYMENT_WEIGHTS = [0.25, 0.20, 0.15, 0.20, 0.10, 0.10]
CHANNELS = ["Online", "Offline"]
CHANNEL_WEIGHTS = [0.45, 0.55]
STORE_TYPES = ["Flagship", "Standard", "Outlet"]
STORE_WEIGHTS = [0.10, 0.60, 0.30]

START_DATE = pd.Timestamp("2021-01-01")
END_DATE = pd.Timestamp("2024-12-31")

CUSTOMERS = []
for i in range(300):
    cid = f"CUST{i+1:05d}"
    fn = RNG.choice(FIRST_NAMES)
    ln = RNG.choice(LAST_NAMES)
    age = int(np.clip(RNG.normal(38, 12), 18, 75))
    gender = RNG.choice(["Male", "Female"], p=[0.52, 0.48])
    region = RNG.choice(REGIONS)
    state = RNG.choice(REGION_STATES[region])
    city = RNG.choice(STATE_CITIES[state])
    segment = RNG.choice(SEGMENTS, p=SEGMENT_WEIGHTS)
    CUSTOMERS.append({
        "customer_id": cid,
        "customer_name": f"{fn} {ln}",
        "customer_age": age,
        "customer_gender": gender,
        "customer_city": city,
        "customer_state": state,
        "customer_segment": segment,
    })

customer_lookup = {c["customer_id"]: c for c in CUSTOMERS}

category_list = list(CATEGORIES.keys())
category_weights = [0.25, 0.25, 0.15, 0.12, 0.08, 0.15]

all_subcategories = []
all_brands = []
category_for_sub = []
subcategory_for_brand = []
for cat, data in CATEGORIES.items():
    for sub, sub_data in data["subcategories"].items():
        all_subcategories.append(sub)
        category_for_sub.append(cat)
        for brand in sub_data["brands"]:
            all_brands.append(brand)
            subcategory_for_brand.append(sub)

sub_cat_map = dict(zip(all_subcategories, category_for_sub))
sub_brand_map = {}
for cat, data in CATEGORIES.items():
    for sub, sub_data in data["subcategories"].items():
        sub_brand_map[sub] = sub_data["brands"]


def get_price_range(subcategory, brand):
    for cat, data in CATEGORIES.items():
        for sub, sub_data in data["subcategories"].items():
            if sub == subcategory:
                return sub_data["price_range"]
    return (10, 100)


def get_cost_margin(subcategory):
    for cat, data in CATEGORIES.items():
        for sub, sub_data in data["subcategories"].items():
            if sub == subcategory:
                return sub_data["cost_margin"]
    return 0.30


def generate_dates(n):
    day_span = (END_DATE - START_DATE).days
    day_offsets = RNG.integers(0, day_span + 1, size=n)
    base = pd.to_datetime(START_DATE) + pd.to_timedelta(day_offsets, unit="D")
    month_probs = np.array([0.06, 0.06, 0.07, 0.07, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.10, 0.15])
    month_probs = month_probs / month_probs.sum()
    month_indices = RNG.choice(12, size=n, p=month_probs)
    dates = []
    for i in range(n):
        m = month_indices[i] + 1
        yr = base[i].year
        max_day = pd.Timestamp(yr, m, 1).days_in_month
        d = int(np.clip(base[i].day, 1, max_day))
        dates.append(pd.Timestamp(yr, m, d))
    return pd.DatetimeIndex(dates)


def get_store_id(region):
    store_map = {
        "East": RNG.choice([101, 102, 103, 104]),
        "West": RNG.choice([201, 202, 203, 204]),
        "South": RNG.choice([301, 302, 303, 304]),
        "Central": RNG.choice([401, 402, 403, 404]),
    }
    return store_map[region]


def generate_rating(rng, size):
    raw = rng.exponential(1.5, size=size)
    clipped = np.clip(np.round(raw) + 1, 1, 5).astype(int)
    return clipped


dates = generate_dates(N)
customer_indices = RNG.integers(0, 300, size=N)

transaction_ids = [f"TXN{i+1:06d}" for i in range(N)]
sel_customers = [CUSTOMERS[idx] for idx in customer_indices]
customer_ids = [c["customer_id"] for c in sel_customers]
customer_names = [c["customer_name"] for c in sel_customers]
customer_ages = [c["customer_age"] for c in sel_customers]
customer_genders = [c["customer_gender"] for c in sel_customers]
customer_cities = [c["customer_city"] for c in sel_customers]
customer_states = [c["customer_state"] for c in sel_customers]
customer_segments = [c["customer_segment"] for c in sel_customers]
customer_regions = []
for state in customer_states:
    for reg, states in REGION_STATES.items():
        if state in states:
            customer_regions.append(reg)
            break

selected_categories = RNG.choice(category_list, size=N, p=category_weights)
subcategories = []
brands = []
for cat in selected_categories:
    subs = CATEGORIES[cat]["subcategories"]
    sub = RNG.choice(list(subs.keys()))
    subcategories.append(sub)
    brand = RNG.choice(subs[sub]["brands"])
    brands.append(brand)

unit_prices = []
cost_amounts = []
for i in range(N):
    cat = selected_categories[i]
    sub = subcategories[i]
    price_range = CATEGORIES[cat]["subcategories"][sub]["price_range"]
    margin = CATEGORIES[cat]["subcategories"][sub]["cost_margin"]
    price = round(float(RNG.uniform(price_range[0], price_range[1])), 2)
    unit_prices.append(price)
    cost = round(price * (1 - margin) * float(RNG.uniform(0.9, 1.05)), 2)
    cost_amounts.append(cost)

quantities = RNG.integers(1, 11, size=N)
discount_pcts = np.zeros(N)
for i in range(N):
    if RNG.random() < 0.40:
        discount_pcts[i] = round(float(RNG.choice([5, 10, 15, 20, 25, 30], p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05])), 1)
    else:
        discount_pcts[i] = 0.0

unit_prices_arr = np.array(unit_prices)
cost_amounts_arr = np.array(cost_amounts)
quantities_arr = quantities.astype(float)
discount_arr = discount_pcts

sales_amounts = np.round(unit_prices_arr * quantities_arr * (1 - discount_arr / 100), 2)
profit_amounts = np.round(sales_amounts - cost_amounts_arr * quantities_arr, 2)

payment_methods = RNG.choice(PAYMENT_METHODS, size=N, p=PAYMENT_WEIGHTS)
sales_channels = RNG.choice(CHANNELS, size=N, p=CHANNEL_WEIGHTS)
store_types = RNG.choice(STORE_TYPES, size=N, p=STORE_WEIGHTS)
store_ids = [get_store_id(reg) for reg in customer_regions]
ratings = generate_rating(RNG, N)
returned = (RNG.random(N) < 0.05).astype(int)

df = pd.DataFrame({
    "transaction_id": transaction_ids,
    "transaction_date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
    "customer_id": customer_ids,
    "customer_name": customer_names,
    "customer_age": customer_ages,
    "customer_gender": customer_genders,
    "customer_city": customer_cities,
    "customer_state": customer_states,
    "customer_segment": customer_segments,
    "product_id": [f"PROD{i+1:05d}" for i in range(N)],
    "product_name": [f"{brands[i]} {subcategories[i]} {i+1}" for i in range(N)],
    "category": selected_categories,
    "subcategory": subcategories,
    "brand": brands,
    "unit_price": unit_prices,
    "quantity": quantities,
    "discount_percent": discount_pcts,
    "sales_amount": sales_amounts,
    "cost_amount": np.round(cost_amounts_arr * quantities_arr, 2),
    "profit_amount": profit_amounts,
    "payment_method": payment_methods,
    "sales_channel": sales_channels,
    "store_id": store_ids,
    "store_type": store_types,
    "region": customer_regions,
    "customer_rating": ratings,
    "returned": returned,
})

out_dir = Path(__file__).resolve().parent.parent / "demo-data"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "retail_sales_demo.csv"
df.to_csv(out_path, index=False)

print(f"Generated {len(df)} rows -> {out_path.relative_to(Path(__file__).resolve().parent.parent)}")
