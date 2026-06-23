-- CombinedTasks_Count - Query Table
-- For 10k records
--Combining tasks(crm data - for 1k records) and tasks_9000

SELECT
    x.Activity_Link_ID AS Activity_Link_ID,
    SUM(x.NumberOfOtherTasks) AS NumberOfOtherTasks
FROM
(
    SELECT
        t."Related To" AS Activity_Link_ID,
        COUNT(*) AS NumberOfOtherTasks
    FROM Tasks t
    WHERE t."Subject" NOT IN ('Call', 'Meeting')
    GROUP BY t."Related To"

    UNION ALL

    SELECT
        t9."Lead ID" AS Activity_Link_ID,
        COUNT(*) AS NumberOfOtherTasks
    FROM Tasks_9000 t9
    WHERE t9."Subject" NOT IN ('Call', 'Meeting')
    GROUP BY t9."Lead ID"
) x
GROUP BY x.Activity_Link_ID