-- Tasks_Count - Query Table
SELECT
		 "Related To" AS Activity_Link_ID,
		 COUNT(*) AS NumberOfOtherTasks
FROM  Tasks --Use CombinedTasks(tasks_10000) for 10k records
WHERE	 "Subject"  NOT IN ( 'Call'  , 'Meeting'  )
GROUP BY  "Related To" 
