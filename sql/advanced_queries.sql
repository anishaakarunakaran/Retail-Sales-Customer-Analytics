-- ============================================================
-- Retail Sales & Customer Analytics - Advanced Queries
-- Window functions (rank, running totals, lag/lead), CTEs,
-- subqueries and date functions for deeper insight.
-- ============================================================

-- A1. Rank products by revenue WITHIN each category (ROW_NUMBER / DENSE_RANK)
WITH product_rev AS (
    SELECT p.category, p.product_id, p.product_name,
           SUM(oi.sales) AS revenue,
           SUM(oi.profit) AS profit
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_id
)
SELECT category, product_name, ROUND(revenue, 2) AS revenue,
       RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS cat_rank
FROM product_rev
ORDER BY category, cat_rank;

-- A2. Running total of monthly revenue (cumulative 2021-2024)
WITH monthly AS (
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.sales) AS revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY month
)
SELECT month, ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS running_total
FROM monthly
ORDER BY month;

-- A3. Top 2 customers by spend in each region
WITH customer_spend AS (
    SELECT c.region, c.customer_id, c.customer_name,
           SUM(oi.sales) AS spend
    FROM order_items oi
    JOIN orders o    ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
)
SELECT region, customer_name, ROUND(spend, 2) AS spend
FROM (
    SELECT region, customer_name, spend,
           ROW_NUMBER() OVER (PARTITION BY region ORDER BY spend DESC) AS rn
    FROM customer_spend
)
WHERE rn <= 2
ORDER BY region, spend DESC;

-- A4. First and last purchase per customer + days between (LAG/LEAD)
WITH purchases AS (
    SELECT o.customer_id, o.order_date
    FROM orders o
    WHERE o.order_status = 'Completed'
)
SELECT customer_id,
       MIN(order_date) AS first_purchase,
       MAX(order_date) AS last_purchase,
       COUNT(*) AS total_orders,
       CAST(AVG(order_days) AS INTEGER) AS avg_gap_days
FROM (
    SELECT customer_id, order_date,
           julianday(order_date) - julianday(
               LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)
           ) AS order_days
    FROM purchases
)
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY avg_gap_days;

-- A5. RFM-style segmentation in SQL: Recency / Frequency / Monetary scores
WITH rfm AS (
    SELECT c.customer_id,
           CAST(julianday('2024-12-31') - julianday(MAX(o.order_date)) AS INTEGER) AS recency_days,
           COUNT(DISTINCT o.order_id) AS frequency,
           SUM(oi.sales) AS monetary
    FROM customers c
    JOIN orders o      ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id
)
SELECT customer_id,
       CASE
         WHEN recency_days <= 60 THEN 5
         WHEN recency_days <= 120 THEN 4
         WHEN recency_days <= 240 THEN 3
         WHEN recency_days <= 365 THEN 2
         ELSE 1 END AS recency_score,
       CASE
         WHEN frequency >= 40 THEN 5
         WHEN frequency >= 25 THEN 4
         WHEN frequency >= 12 THEN 3
         WHEN frequency >= 6  THEN 2
         ELSE 1 END AS frequency_score,
       CASE
         WHEN monetary >= 80000 THEN 5
         WHEN monetary >= 30000 THEN 4
         WHEN monetary >= 12000 THEN 3
         WHEN monetary >= 4000  THEN 2
         ELSE 1 END AS monetary_score
FROM rfm
ORDER BY recency_score DESC, frequency_score DESC, monetary_score DESC;

-- A6. Discount effect: margin by discount band (CASE)
SELECT
    CASE
        WHEN discount = 0            THEN 'No discount'
        WHEN discount < 0.10         THEN '0-10%'
        WHEN discount < 0.20         THEN '10-20%'
        WHEN discount < 0.30         THEN '20-30%'
        ELSE                              '30%+'
    END AS discount_band,
    COUNT(*) AS lines,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(SUM(profit)/SUM(sales), 4) AS margin
FROM order_items
GROUP BY discount_band
ORDER BY margin DESC;

-- A7. Weekly sales pattern (weekday share of revenue)
SELECT
    CASE CAST(strftime('%w', order_date) AS INTEGER)
        WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday' ELSE 'Saturday'
    END AS day_of_week,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(sales) * 100.0 / (SELECT SUM(sales) FROM order_items), 2) AS pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY day_of_week
ORDER BY pct DESC;

-- A8. Contribution of top 20% of products to revenue (Pareto check)
WITH product_rev AS (
    SELECT product_id, SUM(sales) AS revenue
    FROM order_items GROUP BY product_id
),
ranked AS (
    SELECT product_id, revenue,
           SUM(revenue) OVER (ORDER BY revenue DESC) AS cum_rev,
           SUM(revenue) OVER () AS total_rev,
           ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rn,
           COUNT(*) OVER () AS n_products
    FROM product_rev
)
SELECT ROUND(SUM(revenue), 2) AS top20_revenue,
       (SELECT total_rev FROM ranked LIMIT 1) AS total_revenue,
       ROUND(SUM(revenue) * 100.0 / (SELECT total_rev FROM ranked LIMIT 1), 2) AS share_pct,
       MAX(rn) AS products_included
FROM ranked WHERE rn <= ROUND(0.2 * (SELECT n_products FROM ranked LIMIT 1));