SELECT
		 "Lead ID" AS Lead_ID,
		 COUNT(*) AS NumberOfMeetings
FROM  CombinedMeeting -- AKA meeting_1000
GROUP BY  "Lead ID" 
