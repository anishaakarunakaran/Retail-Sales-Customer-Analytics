import initSqlJs, { type Database } from 'sql.js';
import type { Transaction } from './types';

let db: Database | null = null;

export async function initDB(): Promise<Database> {
  if (db) return db;
  const SQL = await initSqlJs();
  db = new SQL.Database();
  createSchema(db);
  return db;
}

export function getDB(): Database | null { return db; }

function createSchema(database: Database): void {
  database.run(`CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT, transaction_date TEXT, customer_id TEXT, customer_name TEXT,
    customer_age INTEGER, customer_gender TEXT, customer_city TEXT, customer_state TEXT,
    customer_segment TEXT, product_id TEXT, product_name TEXT, category TEXT, subcategory TEXT,
    brand TEXT, unit_price REAL, quantity INTEGER, discount_percent REAL, sales_amount REAL,
    cost_amount REAL, profit_amount REAL, payment_method TEXT, sales_channel TEXT,
    store_id TEXT, store_type TEXT, region TEXT, customer_rating REAL, returned TEXT
  )`);
}

export function loadTransactionsToDB(data: Transaction[]): void {
  if (!db) return;
  const stmt = db.prepare(`INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`);
  data.forEach((r) => {
    stmt.run([r.transaction_id, r.transaction_date, r.customer_id, r.customer_name, r.customer_age, r.customer_gender, r.customer_city, r.customer_state, r.customer_segment, r.product_id, r.product_name, r.category, r.subcategory, r.brand, r.unit_price, r.quantity, r.discount_percent, r.sales_amount, r.cost_amount, r.profit_amount, r.payment_method, r.sales_channel, r.store_id, r.store_type, r.region, r.customer_rating, String(r.returned)]);
  });
  stmt.free();
}

export function runQuery(sql: string): { columns: string[]; rows: (string | number | null)[][] } {
  if (!db) return { columns: [], rows: [] };
  const results = db.exec(sql);
  if (results.length === 0) return { columns: [], rows: [] };
  return { columns: results[0].columns, rows: results[0].values };
}

export const PRESET_QUERIES = [
  { name: 'Total Revenue & Profit', sql: "SELECT SUM(sales_amount) as total_revenue, SUM(profit_amount) as total_profit, ROUND(SUM(profit_amount)*100.0/SUM(sales_amount),1) as margin_pct FROM transactions" },
  { name: 'Monthly Revenue', sql: "SELECT substr(transaction_date,1,7) as month, SUM(sales_amount) as revenue, COUNT(DISTINCT transaction_id) as orders FROM transactions GROUP BY month ORDER BY month" },
  { name: 'Top 10 Products', sql: "SELECT product_name, SUM(sales_amount) as revenue, SUM(profit_amount) as profit, COUNT(DISTINCT transaction_id) as orders FROM transactions GROUP BY product_name ORDER BY revenue DESC LIMIT 10" },
  { name: 'Revenue by Category', sql: "SELECT category, SUM(sales_amount) as revenue, SUM(profit_amount) as profit, ROUND(SUM(profit_amount)*100.0/SUM(sales_amount),1) as margin_pct FROM transactions GROUP BY category ORDER BY revenue DESC" },
  { name: 'Revenue by Region', sql: "SELECT region, SUM(sales_amount) as revenue, COUNT(DISTINCT customer_id) as customers FROM transactions GROUP BY region ORDER BY revenue DESC" },
  { name: 'Top 10 Customers', sql: "SELECT customer_name, customer_segment, SUM(sales_amount) as total_spent, COUNT(DISTINCT transaction_id) as orders FROM transactions GROUP BY customer_id ORDER BY total_spent DESC LIMIT 10" },
  { name: 'AOV by Segment', sql: "SELECT customer_segment, ROUND(AVG(sales_amount),2) as avg_order_value, COUNT(*) as transactions FROM transactions GROUP BY customer_segment ORDER BY avg_order_value DESC" },
  { name: 'Repeat Customers', sql: "SELECT customer_id, customer_name, COUNT(DISTINCT transaction_id) as order_count, SUM(sales_amount) as total_spent FROM transactions GROUP BY customer_id HAVING order_count > 1 ORDER BY total_spent DESC LIMIT 20" },
  { name: 'Profit Margin by Category', sql: "SELECT category, ROUND(AVG(profit_amount/sales_amount)*100,1) as avg_margin_pct, MIN(ROUND(profit_amount/sales_amount*100,1)) as min_margin, MAX(ROUND(profit_amount/sales_amount*100,1)) as max_margin FROM transactions WHERE sales_amount > 0 GROUP BY category" },
  { name: 'Sales by Channel', sql: "SELECT sales_channel, SUM(sales_amount) as revenue, COUNT(DISTINCT transaction_id) as orders, ROUND(AVG(sales_amount),2) as avg_order FROM transactions GROUP BY sales_channel" },
  { name: 'Discount Impact', sql: "SELECT CASE WHEN discount_percent = 0 THEN 'No Discount' WHEN discount_percent <= 10 THEN '1-10%' WHEN discount_percent <= 20 THEN '11-20%' WHEN discount_percent <= 30 THEN '21-30%' ELSE '30%+' END as discount_band, COUNT(*) as orders, ROUND(AVG(profit_amount/sales_amount)*100,1) as avg_margin FROM transactions WHERE sales_amount > 0 GROUP BY discount_band ORDER BY discount_band" },
  { name: 'Regional Customer Count', sql: "SELECT region, COUNT(DISTINCT customer_id) as customers, ROUND(SUM(sales_amount)/COUNT(DISTINCT customer_id),2) as revenue_per_customer FROM transactions GROUP BY region ORDER BY revenue_per_customer DESC" },
];
