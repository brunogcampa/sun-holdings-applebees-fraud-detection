-- Prerrequisito: publicar discount_events_current con el notebook 02_publish_discount_events.
-- Un evento = un elemento de Discounts o ItemsSold[].Discounts.
-- Conservar los niveles separados al comparar importes; no son tickets únicos.

-- Catálogo, participación por nivel e importe medio por evento.
WITH catalog AS (
 SELECT discount_level, DiscountName, count(*) AS events,
 avg(Amount) AS mean_amount_signed, avg(abs(Amount)) AS mean_amount_magnitude
 FROM workspace.applebees_eda.discount_events_current
 GROUP BY discount_level, DiscountName
)
SELECT *, 100.0 * events / sum(events) OVER (PARTITION BY discount_level) AS pct_of_level_events
FROM catalog ORDER BY discount_level, events DESC;

-- Top 5 locations para CADA categoría: denominador = eventos de esa categoría y nivel.
WITH counts AS (
 SELECT discount_level, DiscountName, LocationId, count(*) AS events
 FROM workspace.applebees_eda.discount_events_current
 GROUP BY discount_level, DiscountName, LocationId
), ranked AS (
 SELECT *, 100.0 * events / sum(events) OVER (PARTITION BY discount_level, DiscountName)
 AS pct_of_category_events,
 row_number() OVER (PARTITION BY discount_level, DiscountName ORDER BY events DESC, LocationId) AS rank
 FROM counts
)
SELECT * FROM ranked WHERE rank <= 5
ORDER BY discount_level, DiscountName, rank;

-- Top 5 managers: agrupar por ID + location; mantener faltantes en el denominador.
WITH counts AS (
 SELECT ManagerId, LocationId, count(*) AS events
 FROM workspace.applebees_eda.discount_events_current GROUP BY ManagerId, LocationId
), total AS (SELECT count(*) AS events FROM workspace.applebees_eda.discount_events_current)
SELECT c.*, 100.0 * c.events / t.events AS pct_of_all_discount_events
FROM counts c CROSS JOIN total t WHERE c.ManagerId IS NOT NULL AND c.ManagerId > 0
ORDER BY c.events DESC, c.ManagerId, c.LocationId LIMIT 5;

-- Top 5 pares empleado + location. Porcentaje global y dentro de su location.
-- EmployeeId es quien figura en el evento; no afirmar que sea mesero sin validar su rol.
WITH counts AS (
 SELECT EmployeeId, LocationId, count(*) AS events
 FROM workspace.applebees_eda.discount_events_current GROUP BY EmployeeId, LocationId
), shares AS (
 SELECT *, 100.0 * events / sum(events) OVER () AS pct_of_all_discount_events,
 100.0 * events / sum(events) OVER (PARTITION BY LocationId) AS pct_of_location_discount_events
 FROM counts
)
SELECT * FROM shares WHERE EmployeeId IS NOT NULL AND EmployeeId > 0
ORDER BY events DESC, EmployeeId, LocationId LIMIT 5;
