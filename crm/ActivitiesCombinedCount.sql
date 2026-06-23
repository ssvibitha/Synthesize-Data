-- Selects no.of meeting, calls, other tasks as a single query table
SELECT
    x.Activity_Link_ID AS ACTIVITY_LINK_ID,
    SUM(x.NumberOfCalls) AS NumberOfCalls,
    SUM(x.NumberOfOtherTasks) AS NumberOfOtherTasks,
    SUM(x.NumberOfMeetings) AS NumberOfMeetings
FROM
(
    /* Calls */
    SELECT
        c."Related To" AS Activity_Link_ID,
        COUNT(*) AS NumberOfCalls,
        0 AS NumberOfOtherTasks,
        0 AS NumberOfMeetings
    FROM Calls c
    GROUP BY c."Related To"

    UNION ALL

    SELECT
        c9."Lead ID" AS Activity_Link_ID,
        COUNT(*) AS NumberOfCalls,
        0,
        0
    FROM Calls_9000 c9
    GROUP BY c9."Lead ID"

    UNION ALL

    /* Other Tasks */
    SELECT
        t."Related To" AS Activity_Link_ID,
        0,
        COUNT(*) AS NumberOfOtherTasks,
        0
    FROM Tasks t
    WHERE t."Subject" NOT IN ('Call','Meeting')
    GROUP BY t."Related To"

    UNION ALL

    SELECT
        t9."Lead ID" AS Activity_Link_ID,
        0,
        COUNT(*) AS NumberOfOtherTasks,
        0
    FROM Tasks_9000 t9
    WHERE t9."Subject" NOT IN ('Call','Meeting')
    GROUP BY t9."Lead ID"

    UNION ALL

    /* Meetings */
    SELECT
        m."Related To" AS Activity_Link_ID,
        0,
        0,
        COUNT(*) AS NumberOfMeetings
    FROM Meetings m
    GROUP BY m."Related To"

    UNION ALL

    SELECT
        m9."Lead ID" AS Activity_Link_ID,
        0,
        0,
        COUNT(*) AS NumberOfMeetings
    FROM Meeting_9000 m9
    GROUP BY m9."Lead ID"

) x
GROUP BY x.Activity_Link_ID