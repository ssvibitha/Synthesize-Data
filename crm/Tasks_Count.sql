-- Tasks_Count - Query Table

SELECT "Related To" AS Activity_Link_ID, COUNT(*) AS NumberOfTasks 
FROM Tasks --Use CombinedTasks(tasks_10000) for 10k records
GROUP BY "Related To"