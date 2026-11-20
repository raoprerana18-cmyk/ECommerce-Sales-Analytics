CREATE DATABASE ecommerce_analytics;
USE ecommerce_analytics;
SELECT DATABASE();
USE ecommerce_analytics;

SELECT COUNT(*) 
FROM customers;
SELECT *
FROM customers
LIMIT 5;
SELECT COUNT(*)
FROM orders;
DESCRIBE orders;
USE ecommerce_analytics;
SELECT DATABASE();
SHOW TABLES;
USE ecommerce_analytics;

SELECT COUNT(*) AS total_orders
FROM orders;
SELECT COUNT(*) AS missing_delivery_days
FROM orders
WHERE delivery_days IS NULL;
USE ecommerce_analytics;

SELECT COUNT(*) AS total_order_items
FROM order_items;
SELECT COUNT(*) AS total_customers FROM customers;

SELECT COUNT(*) AS total_products FROM products;

SELECT COUNT(*) AS total_orders FROM orders;

SELECT COUNT(*) AS total_order_items FROM order_items;
USE ecommerce_analytics;

SELECT 'customers' AS table_name, COUNT(*) AS total FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'returns', COUNT(*) FROM returns;
USE ecommerce_analytics;

DESCRIBE customers;

DESCRIBE products;

DESCRIBE orders;

DESCRIBE order_items;

DESCRIBE returns;
USE ecommerce_analytics;

SELECT
    c.customer_id,
    c.customer_name,
    c.country,
    o.order_id,
    o.order_date,
    o.order_total_usd,
    o.order_status
FROM customers c
INNER JOIN orders o
    ON c.customer_id = o.customer_id
LIMIT 10;
SELECT
    shipping_country,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(order_total_usd), 2) AS total_revenue
FROM orders
WHERE order_status = 'Delivered'
GROUP BY shipping_country
ORDER BY total_revenue DESC;
SELECT
    o.shipping_country,
    ROUND(SUM(oi.line_total_usd), 2) AS total_revenue,
    ROUND(SUM(oi.unit_cost_usd * oi.quantity), 2) AS total_cost,
    ROUND(SUM(oi.line_profit_usd), 2) AS total_profit
FROM orders o
INNER JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
GROUP BY o.shipping_country
ORDER BY total_profit DESC;
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total_usd), 2) AS total_revenue,
    ROUND(SUM(oi.line_profit_usd), 2) AS total_profit
FROM order_items oi
INNER JOIN products p
    ON oi.product_id = p.product_id
INNER JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_revenue DESC
LIMIT 10;

USE ecommerce_analytics;

WITH sales AS (
    SELECT
        p.category,
        SUM(oi.quantity) AS units_sold
    FROM order_items oi
    INNER JOIN products p
        ON oi.product_id = p.product_id
    INNER JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY p.category
),

returned AS (
    SELECT
        p.category,
        SUM(r.quantity_returned) AS units_returned
    FROM returns r
    INNER JOIN products p
        ON r.product_id = p.product_id
    INNER JOIN orders o
        ON r.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY p.category
)

SELECT
    s.category,
    s.units_sold,
    COALESCE(r.units_returned, 0) AS units_returned,
    ROUND(
        COALESCE(r.units_returned, 0) * 100.0
        / NULLIF(s.units_sold, 0), 2
    ) AS return_rate_percentage
FROM sales s
LEFT JOIN returned r
    ON s.category = r.category
ORDER BY return_rate_percentage DESC;
SELECT
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS latest_order_date,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
WHERE order_status = 'Delivered';
USE ecommerce_analytics;

SELECT
    customer_id,
    DATEDIFF(
        '2026-06-30',
        MAX(order_date)
    ) AS recency_days,
    COUNT(DISTINCT order_id) AS frequency,
    ROUND(SUM(order_total_usd), 2) AS monetary_value
FROM orders
WHERE order_status = 'Delivered'
GROUP BY customer_id
ORDER BY monetary_value DESC
LIMIT 20;

USE ecommerce_analytics;

WITH rfm AS (
    SELECT
        customer_id,
        DATEDIFF('2026-06-30', MAX(order_date)) AS recency,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(order_total_usd) AS monetary
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),

rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        ROUND(monetary, 2) AS monetary,

        6 - NTILE(5) OVER (
            ORDER BY recency ASC
        ) AS R_score,

        NTILE(5) OVER (
            ORDER BY frequency ASC
        ) AS F_score,

        NTILE(5) OVER (
            ORDER BY monetary ASC
        ) AS M_score

    FROM rfm
)

SELECT
    *,
    CONCAT(R_score, F_score, M_score) AS RFM_score
FROM rfm_scores
ORDER BY monetary DESC
LIMIT 20;

USE ecommerce_analytics;

WITH rfm AS (
    SELECT
        customer_id,
        DATEDIFF('2026-06-30', MAX(order_date)) AS recency,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(order_total_usd) AS monetary
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),

rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        ROUND(monetary, 2) AS monetary,

        6 - NTILE(5) OVER (
            ORDER BY recency ASC
        ) AS R_score,

        NTILE(5) OVER (
            ORDER BY frequency ASC
        ) AS F_score,

        NTILE(5) OVER (
            ORDER BY monetary ASC
        ) AS M_score

    FROM rfm
),

segments AS (
    SELECT *,
        CASE
            WHEN R_score >= 4 AND F_score >= 4 AND M_score >= 4
                THEN 'Champions'
            WHEN F_score >= 4 AND M_score >= 3
                THEN 'Loyal Customers'
            WHEN R_score >= 4 AND F_score BETWEEN 2 AND 3
                THEN 'Potential Loyalists'
            WHEN R_score <= 2 AND F_score >= 3
                THEN 'At Risk'
            WHEN R_score = 3 AND F_score >= 3
                THEN 'Needs Attention'
            ELSE 'Others'
        END AS customer_segment
    FROM rfm_scores
)

SELECT
    customer_segment,
    COUNT(*) AS total_customers
FROM segments
GROUP BY customer_segment
ORDER BY total_customers DESC;

USE ecommerce_analytics;

WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)

SELECT
    CASE
        WHEN total_orders = 1 THEN 'One-Time Customers'
        ELSE 'Repeat Customers'
    END AS customer_type,
    COUNT(*) AS total_customers
FROM customer_orders
GROUP BY customer_type;


USE ecommerce_analytics;

WITH customer_purchase_dates AS (
    SELECT DISTINCT
        customer_id,
        order_id,
        order_date
    FROM orders
    WHERE order_status = 'Delivered'
),

purchase_intervals AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS previous_order_date
    FROM customer_purchase_dates
)

SELECT
    ROUND(AVG(DATEDIFF(
        order_date,
        previous_order_date
    )), 2) AS average_days_between_purchases,

    MIN(DATEDIFF(
        order_date,
        previous_order_date
    )) AS minimum_days,

    MAX(DATEDIFF(
        order_date,
        previous_order_date
    )) AS maximum_days

FROM purchase_intervals
WHERE previous_order_date IS NOT NULL;
USE ecommerce_analytics;

WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)

SELECT
    DATE_FORMAT(first_order_date, '%Y-%m') AS cohort_month,
    COUNT(*) AS new_customers
FROM first_purchase
GROUP BY cohort_month
ORDER BY cohort_month;

USE ecommerce_analytics;

WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),

customer_activity AS (
    SELECT DISTINCT
        o.customer_id,
        DATE_FORMAT(fp.first_order_date, '%Y-%m') AS cohort_month,
        DATE_FORMAT(o.order_date, '%Y-%m') AS activity_month,
        TIMESTAMPDIFF(
            MONTH,
            DATE_FORMAT(fp.first_order_date, '%Y-%m-01'),
            DATE_FORMAT(o.order_date, '%Y-%m-01')
        ) AS month_number
    FROM orders o
    INNER JOIN first_purchase fp
        ON o.customer_id = fp.customer_id
    WHERE o.order_status = 'Delivered'
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(*) AS total_customers
    FROM first_purchase
    GROUP BY cohort_month
),

retention AS (
    SELECT
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM customer_activity
    GROUP BY cohort_month, month_number
)

SELECT
    r.cohort_month,
    r.month_number,
    r.active_customers,
    cs.total_customers,
    ROUND(
        r.active_customers * 100.0 / cs.total_customers,
        2
    ) AS retention_percentage
FROM retention r
INNER JOIN cohort_size cs
    ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.month_number;


USE ecommerce_analytics;

WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)

SELECT
    DATE_FORMAT(first_order_date, '%Y-%m') AS cohort_month,
    COUNT(*) AS new_customers
FROM first_purchase
GROUP BY cohort_month
ORDER BY cohort_month;




USE ecommerce_analytics;

SELECT
    customer_id,
    order_date,
    DATE_FORMAT(order_date, '%Y-%m') AS activity_month
FROM orders
WHERE order_status = 'Delivered'
ORDER BY customer_id, order_date
LIMIT 10;



USE ecommerce_analytics;

WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),

customer_activity AS (
    SELECT DISTINCT
        o.customer_id,
        DATE_FORMAT(fp.first_order_date, '%Y-%m') AS cohort_month,
        TIMESTAMPDIFF(
            MONTH,
            DATE_FORMAT(fp.first_order_date, '%Y-%m-01'),
            DATE_FORMAT(o.order_date, '%Y-%m-01')
        ) AS month_number
    FROM orders o
    INNER JOIN first_purchase fp
        ON o.customer_id = fp.customer_id
    WHERE o.order_status = 'Delivered'
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(*) AS total_customers
    FROM first_purchase
    GROUP BY cohort_month
),

retention AS (
    SELECT
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM customer_activity
    GROUP BY cohort_month, month_number
)

SELECT
    r.cohort_month,
    r.month_number,
    r.active_customers,
    cs.total_customers,
    ROUND(
        r.active_customers * 100.0 / cs.total_customers,
        2
    ) AS retention_percentage
FROM retention r
INNER JOIN cohort_size cs
    ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.month_number;





USE ecommerce_analytics;


WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),

customer_activity AS (
    SELECT DISTINCT
        o.customer_id,
        DATE_FORMAT(fp.first_order_date, '%Y-%m') AS cohort_month,
        TIMESTAMPDIFF(
            MONTH,
            DATE_FORMAT(fp.first_order_date, '%Y-%m-01'),
            DATE_FORMAT(o.order_date, '%Y-%m-01')
        ) AS month_number
    FROM orders o
    INNER JOIN first_purchase fp
        ON o.customer_id = fp.customer_id
    WHERE o.order_status = 'Delivered'
),

cohort_size AS (
    SELECT
        DATE_FORMAT(first_order_date, '%Y-%m') AS cohort_month,
        COUNT(*) AS total_customers
    FROM first_purchase
    GROUP BY DATE_FORMAT(first_order_date, '%Y-%m')
),

retention AS (
    SELECT
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM customer_activity
    GROUP BY cohort_month, month_number
)

SELECT
    r.cohort_month,
    r.month_number,
    r.active_customers,
    cs.total_customers,
    ROUND(
        r.active_customers * 100.0 / cs.total_customers,
        2
    ) AS retention_percentage
FROM retention r
INNER JOIN cohort_size cs
    ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.month_number;
