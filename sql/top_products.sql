SELECT 
    product_id,
    product_name,
    SUM(quantity) AS total_quantity_sold,
    SUM(total_amount) AS total_revenue
FROM orders
GROUP BY product_id, product_name
ORDER BY total_revenue DESC
LIMIT 10;