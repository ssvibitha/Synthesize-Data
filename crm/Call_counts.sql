SELECT
		 "Related To" AS Activity_Link_ID,
		 COUNT(*) AS NumberOfCalls
FROM  Calls  --Use CombinedCalls(calls_10000) for 10k records
GROUP BY  "Related To" 