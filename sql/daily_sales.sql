SELECT 
    DATE(order_date) AS sale_day,
    SUM(total_amount) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
GROUP BY sale_day
ORDER BY sale_day DESC;