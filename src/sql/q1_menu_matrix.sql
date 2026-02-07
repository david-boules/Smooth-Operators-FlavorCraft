-- Q1: Menu Engineering Matrix (Profit vs Popularity) BY LOCATION
-- REMOVED "HAVING COUNT > 5" so small stores show data

WITH order_locations AS (
    SELECT DISTINCT 
        CAST(payment_for_id AS VARCHAR) AS order_id, 
        CAST(place_id AS VARCHAR) AS store_id        
    FROM fct_payments
    WHERE payment_for_type = 'order' 
      AND place_id IS NOT NULL
)

SELECT 
    COALESCE(ol.store_id, 'Unknown') AS store_name,
    COALESCE(s.title, 'Other') AS section_name,       
    m.title AS menu_item_name,     
    
    COUNT(f.id) AS total_sold,
    AVG(f.price) AS avg_price,
    
    -- Profit Logic
    COALESCE(
        AVG(f.price) - AVG(CASE WHEN f.cost > 0 AND f.cost < f.price THEN f.cost ELSE NULL END),
        AVG(f.price) * 0.70 
    ) AS estimated_profit_per_item

FROM fct_order_items f
JOIN dim_menu_items m ON f.item_id = m.id
LEFT JOIN dim_sections s ON m.section_id = s.id
LEFT JOIN order_locations ol ON CAST(f.order_id AS VARCHAR) = ol.order_id

GROUP BY ol.store_id, s.title, m.title
-- REMOVED HAVING CLAUSE HERE to allow small data
ORDER BY store_name, section_name, total_sold DESC;