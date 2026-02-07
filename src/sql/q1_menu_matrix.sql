SELECT 
    s.title AS section_name,       
    m.title AS menu_item_name,     
    
    COUNT(f.id) AS total_sold,
    
    AVG(f.price) AS avg_price,
    
    -- Filter out invalid costs (0 or equal to price)
    AVG(CASE 
        WHEN f.cost > 0 AND f.cost < f.price THEN f.cost 
        ELSE NULL 
    END) AS avg_estimated_cost,
    
    -- Profit Calc: Use a valid cost if available, else default to 70% margin
    COALESCE(
        AVG(f.price) - AVG(CASE WHEN f.cost > 0 AND f.cost < f.price THEN f.cost ELSE NULL END),
        AVG(f.price) * 0.70 
    ) AS estimated_profit_per_item

FROM fct_order_items f
JOIN dim_menu_items m ON f.item_id = m.id
LEFT JOIN dim_sections s ON m.section_id = s.id
GROUP BY s.title, m.title
HAVING COUNT(f.id) > 5
ORDER BY section_name, total_sold DESC;