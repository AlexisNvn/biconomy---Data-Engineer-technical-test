--- Houly number of events per Bundler (Bar chart)
SELECT *
FROM crosstab(
    $$
    SELECT
	  date_trunc('hour', block_timestamp) AS date,
	  b.entity_name as category,
	  COUNT(*) AS value
	FROM
	  user_operation_events u
	LEFT JOIN bundlers b on b.address = u.from_address 
	where b.entity_name is not NULL
	GROUP BY
	  date, category
	ORDER BY
	  date, category
    $$,
    $$
    SELECT DISTINCT entity_name as category FROM bundlers ORDER BY entity_name
    $$
) as ct (
	date TIMESTAMP,
	"Alchemy" INT,
	"Biconomy" INT,
	"Candide" INT,
	"Etherspot" INT,
	"Particle" INT,
	"Pimlico" INT,
	"Pimlicoalireza" INT,
	"Stackup" INT,
	"Unipass" INT,
	"ZeroDev" INT
);

--- Overall number of events per Bundler (pie chart)
SELECT
  b.entity_name as category,
  COUNT(*) AS value
FROM
  user_operation_events u
LEFT JOIN bundlers b on b.address = u.from_address 
where b.entity_name is not NULL
GROUP BY
  category
ORDER BY
  category













