-- Using contacts_10000(CombinedContacts), tasks_10000, calls_10000, meeting_10000
-- For 10k records
SELECT
		 l."Id" AS Lead_ID,
		 l."Lead Source" AS Lead_Source,
		 l."Industry" AS Lead_Industry,
		 cm."Campaign Name" AS Campaign_Name,
		 cm."Member Status" AS Member_Status,
		 
			CASE
				 WHEN c."Contact Name"  IS NOT NULL THEN 1
				 ELSE 0
			 END AS Converted,
		 COALESCE(ac.NumberOfOtherTasks, 0) AS NumberOfOtherTasks,
		 COALESCE(ac.NumberOfCalls, 0) AS NumberOfCalls,
		 COALESCE(ac.NumberOfMeetings, 0) AS NumberOfMeetings
FROM  "Leads" l
LEFT JOIN "CombinedContacts" c ON REPLACE(c."Lead Id", 'zcrm_', '')  = l."Id" 
LEFT JOIN "Accounts" a ON c."Account Name"  = a."Account Name" 
LEFT JOIN "ActivitiesCombinedCount" ac ON REPLACE(ac.Lead_ID, 'zcrm_', '')  = 
		CASE
			 WHEN c."Contact Name"  IS NOT NULL THEN a."Id"
			 ELSE l."Id"
		 END 
LEFT JOIN "Campaign Members" cm ON REPLACE(cm."Lead ID", 'zcrm_', '')  = l."Id"  
