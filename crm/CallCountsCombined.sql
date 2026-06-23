--Combining Calls(crm data - for 1k records) and calls_9000

SELECT
		 x.Activity_Link_ID AS Activity_Link_ID,
		 SUM(x.NumberOfCalls) AS NumberOfCalls
FROM (	SELECT
			 c."Related To" AS Activity_Link_ID,
			 COUNT(*) AS NumberOfCalls
	FROM  Calls c 
	GROUP BY  c."Related To" 
	UNION ALL
 	SELECT
			 c9."Lead ID" AS Activity_Link_ID,
			 COUNT(*) AS NumberOfCalls
	FROM  Calls_9000 c9 
	GROUP BY  c9."Lead ID" 
 
) x 
GROUP BY  x.Activity_Link_ID 
