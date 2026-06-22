SELECT
		 "Related To" AS Activity_Link_ID,
		 COUNT(*) AS NumberOfCalls
FROM  Calls 
GROUP BY  "Related To" 
