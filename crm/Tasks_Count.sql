-- Tasks_Count - Query Table

SELECT "Related To" AS Activity_Link_ID, COUNT(*) AS NumberOfTasks 
FROM Tasks 
GROUP BY "Related To"