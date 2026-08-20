-- ============================================================
-- Retail Sales & Customer Analytics - Business Analysis Queries
-- Answers the 12 core business questions with SELECT, WHERE,
-- GROUP BY, HAVING, ORDER BY, JOINs, CASE, subqueries and CTEs.
-- ============================================================

-- Q1. What is total revenue (and profit)?
SELECT ROUND(SUM(sales), 2)  AS total_revenue,
       ROUND(SUM(profit), 2) AS total_profit,
       ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
FROM order_items;

-- Q2. Top 10 products by revenue
SELECT p.product_name, p.category,
       ROUND(SUM(oi.sales), 2) AS revenue,
       ROUND(SUM(oi.profit), 2) AS profit,
       ROUND(SUM(oi.profit) / SUM(oi.sales), 4) AS margin
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;

-- Q3. Which categories generate the highest profit?
SELECT p.category,
       ROUND(SUM(oi.sales), 2)        AS revenue,
       ROUND(SUM(oi.profit), 2)       AS profit,
       ROUND(SUM(oi.profit)/SUM(oi.sales), 4) AS margin,
       COUNT(DISTINCT oi.order_id)    AS orders
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY profit DESC;

-- Q4. Which customers have spent the most?
SELECT c.customer_id, c.customer_name, c.customer_segment, c.region,
       ROUND(SUM(oi.sales), 2) AS total_spend,
       COUNT(DISTINCT oi.order_id) AS orders
FROM order_items oi
JOIN orders o     ON oi.order_id = o.order_id
JOIN customers c  ON o.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY total_spend DESC
LIMIT 10;

-- Q5. What is monthly revenue?
SELECT strftime('%Y-%m', o.order_date) AS month,
       ROUND(SUM(oi.sales), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY month
ORDER BY month;

-- Q6. Month-over-month revenue growth (window function)
WITH monthly AS (
    SELECT strftime('%Y-%m', order_date) AS month,
           SUM(sales) AS revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY month
)
SELECT month,
       revenue,
       revenue - LAG(revenue) OVER (ORDER BY month)              AS change_abs,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month) * 100, 2)      AS growth_pct
FROM monthly
ORDER BY month;

-- Q7. Which customers have made more than 5 purchases?
SELECT c.customer_id, c.customer_name, c.customer_segment,
       COUNT(DISTINCT oi.order_id) AS order_count,
       ROUND(SUM(oi.sales), 2)     AS total_spend
FROM order_items oi
JOIN orders o    ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id
HAVING COUNT(DISTINCT oi.order_id) > 5
ORDER BY order_count DESC;

-- Q8. What is the average order value (AOV)?
SELECT ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM order_items;

-- Q9. Which regions have the highest profit margin?
SELECT c.region,
       ROUND(SUM(oi.sales), 2) AS revenue,
       ROUND(SUM(oi.profit), 2) AS profit,
       ROUND(SUM(oi.profit)/SUM(oi.sales), 4) AS margin
FROM order_items oi
JOIN orders o    ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY margin DESC;

-- Q10. Products with high sales but low profit (revenue > $1.5M, margin < 15%)
SELECT p.product_name, p.category,
       ROUND(SUM(oi.sales), 2)  AS revenue,
       ROUND(SUM(oi.profit), 2) AS profit,
       ROUND(SUM(oi.profit)/SUM(oi.sales), 4) AS margin
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
HAVING SUM(oi.sales) > 1500000 AND SUM(oi.profit)/SUM(oi.sales) < 0.15
ORDER BY revenue DESC;

-- Q11. Customers who have not purchased recently (no order in last 90 days)
SELECT c.customer_id, c.customer_name, c.customer_segment,
       MAX(o.order_date) AS last_order_date,
       CAST(julianday('2024-12-31') - julianday(MAX(o.order_date)) AS INTEGER) AS days_since_last
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
HAVING MAX(o.order_date) IS NULL
    OR julianday('2024-12-31') - julianday(MAX(o.order_date)) > 90
ORDER BY days_since_last DESC;

-- Q12. What percentage of revenue comes from the top 10 customers?
WITH customer_revenue AS (
    SELECT c.customer_id,
           SUM(oi.sales) AS spend
    FROM order_items oi
    JOIN orders o    ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
),
totals AS (
    SELECT SUM(sales) AS total_revenue FROM order_items
)
SELECT ROUND(SUM(spend), 2) AS top10_revenue,
       (SELECT total_revenue FROM totals) AS total_revenue,
       ROUND(SUM(spend) * 100.0 / (SELECT total_revenue FROM totals), 2) AS top10_pct
FROM (SELECT spend FROM customer_revenue ORDER BY spend DESC LIMIT 10);

-- Q13. Segment behaviour: AOV and margin by customer segment
SELECT c.customer_segment,
       COUNT(DISTINCT oi.order_id) AS orders,
       ROUND(SUM(oi.sales)/COUNT(DISTINCT oi.order_id), 2) AS aov,
       ROUND(SUM(oi.sales), 2) AS revenue,
       ROUND(SUM(oi.profit)/SUM(oi.sales), 4) AS margin
FROM order_items oi
JOIN orders o    ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY revenue DESC;