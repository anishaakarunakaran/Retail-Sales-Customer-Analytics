"""
Retail Sales & Customer Analytics - Build SQLite Database
=========================================================
Populates the relational schema (sql/schema.sql) from the cleaned
flat data (data/cleaned/retail_sales_clean.csv) into
retail.db with normalized tables: locations, customers, products,
orders, order_items, payments.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

CLEAN = Path("data/cleaned/retail_sales_clean.csv")
DB = Path("data/retail.db")


def build() -> None:
    df = pd.read_csv(CLEAN, parse_dates=["Order_Date"])
    df["Order_Date"] = df["Order_Date"].dt.strftime("%Y-%m-%d")

    if DB.exists():
        DB.unlink()

    con = sqlite3.connect(DB)
    con.executescript(Path("sql/schema.sql").read_text(encoding="utf-8"))

    # locations: unique city/state/region combos
    locs = df[["City", "State", "Region"]].drop_duplicates().reset_index(drop=True)
    locs.index = locs.index + 1
    locs["location_id"] = locs.index
    con.executemany(
        "INSERT INTO locations (location_id, city, state, region) VALUES (?,?,?,?)",
        locs[["location_id", "City", "State", "Region"]].values.tolist())
    loc_map = {r["City"]: int(r["location_id"]) for r in locs.to_dict("records")}

    # customers
    cust = df[["Customer_ID", "Customer_Name", "Customer_Segment", "Age", "Gender",
               "City", "State", "Region"]]
    cust = cust.drop_duplicates("Customer_ID")
    cust["location_id"] = cust["City"].map(loc_map)
    con.executemany(
        "INSERT INTO customers (customer_id, customer_name, customer_segment, age, gender, "
        "city, state, region, location_id) VALUES (?,?,?,?,?,?,?,?,?)",
        cust[["Customer_ID", "Customer_Name", "Customer_Segment", "Age", "Gender",
              "City", "State", "Region", "location_id"]].values.tolist())

    # products
    prod = df[["Product_ID", "Product_Name", "Category", "Sub_Category", "Unit_Price"]]
    prod = prod.drop_duplicates("Product_ID")
    con.executemany(
        "INSERT INTO products (product_id, product_name, category, sub_category, unit_price) "
        "VALUES (?,?,?,?,?)",
        prod[["Product_ID", "Product_Name", "Category", "Sub_Category", "Unit_Price"]]
        .values.tolist())

    # orders
    ords = df[["Order_ID", "Customer_ID", "Order_Date", "Payment_Method", "Order_Status"]]
    ords = ords.drop_duplicates("Order_ID")
    con.executemany(
        "INSERT INTO orders (order_id, customer_id, order_date, payment_method, order_status) "
        "VALUES (?,?,?,?,?)",
        ords.values.tolist())

    # order_items
    items = df[["Order_ID", "Product_ID", "Quantity", "Unit_Price", "Discount",
                "Sales", "Cost", "Profit", "Profit_Margin"]]
    con.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount, "
        "sales, cost, profit, profit_margin) VALUES (?,?,?,?,?,?,?,?,?)",
        items.values.tolist())

    # payments (one per order)
    pay = df[["Order_ID", "Payment_Method", "Sales", "Order_Status"]].drop_duplicates("Order_ID")
    con.executemany(
        "INSERT INTO payments (order_id, method, amount, status) VALUES (?,?,?,?)",
        pay.values.tolist())

    con.commit()
    con.close()
    print(f"Built {DB} -> orders={len(ords):,} | order_items={len(items):,} | "
          f"customers={len(cust):,} | products={len(prod)} | locations={len(locs)}")


if __name__ == "__main__":
    build()