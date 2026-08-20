-- ============================================================
-- Retail Sales & Customer Analytics - Database Schema (SQLite)
-- Normalised relational model:
--   customers  -> orders      -> order_items
--   products   -> order_items
--   locations  -> customers
--   orders     -> payments
-- Foreign keys enforce referential integrity.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ---------- Dimension: Locations ----------
CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY,
    city        TEXT NOT NULL,
    state       TEXT NOT NULL,
    region      TEXT NOT NULL
);

-- ---------- Dimension: Customers ----------
CREATE TABLE IF NOT EXISTS customers (
    customer_id      INTEGER PRIMARY KEY,
    customer_name    TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    age              INTEGER,
    gender           TEXT,
    city             TEXT,
    state            TEXT,
    region           TEXT,      -- denormalised for reporting convenience
    location_id      INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations (location_id)
);

-- ---------- Dimension: Products ----------
CREATE TABLE IF NOT EXISTS products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    unit_price   REAL
);

-- ---------- Fact: Orders ----------
CREATE TABLE IF NOT EXISTS orders (
    order_id       INTEGER PRIMARY KEY,
    customer_id    INTEGER NOT NULL,
    order_date     TEXT NOT NULL,          -- ISO 'YYYY-MM-DD'
    payment_method TEXT,
    order_status   TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

-- ---------- Fact: Order Items (line level) ----------
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      INTEGER NOT NULL,
    product_id    INTEGER NOT NULL,
    quantity      INTEGER NOT NULL,
    unit_price    REAL NOT NULL,
    discount      REAL NOT NULL DEFAULT 0,
    sales         REAL NOT NULL,           -- revenue after discount
    cost          REAL NOT NULL,
    profit        REAL NOT NULL,
    profit_margin REAL,
    FOREIGN KEY (order_id)   REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

-- ---------- Fact: Payments ----------
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL,
    method     TEXT,
    amount     REAL,
    status     TEXT,
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

-- ---------- Indexes for query performance ----------
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date     ON orders (order_date);
CREATE INDEX IF NOT EXISTS idx_items_order     ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_items_product   ON order_items (product_id);