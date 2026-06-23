-- Selects no.of meeting, calls, other tasks as a single query table
-- For 10k records 

SELECT
		 c."Lead_ID" as "Lead_ID",
		 c."NumberOfCalls" as "NumberOfCalls",
		 m."NumberOfMeetings" as "NumberOfMeetings",
		 o."NumberOfOtherTasks" as "NumberOfOtherTasks"
FROM  "Call_counts" c
LEFT JOIN "Meeting_counts" m ON m."Lead_ID"  = c."Lead_ID" 
LEFT JOIN "OtherTask_counts" o ON o."Lead_ID"  = c."Lead_ID"  
