-- Query table that includes details like
-- lead_id, lead_source, lead_industry, campaign_name, member_status in campaign, 
-- no.of calls,tasks,activities per lead

SELECT
		 l."Id" AS Lead_ID,
		 l."Lead Source" AS Lead_Source,
		 l."Industry" AS Lead_Industry,
		 cm."Campaign Name" AS Campaign_Name,
		 cm."Member Status" AS Member_Status,
		 
			CASE
				 WHEN c."Last Name"  IS NOT NULL THEN 1
				 ELSE 0
			 END AS Converted,
		 COALESCE(tc.NumberOfTasks, 0) AS NumberOfTasks,
		 COALESCE(cc.NumberOfCalls, 0) AS NumberOfCalls,
		 COALESCE(mc.NumberOfMeetings, 0) AS NumberOfMeetings
FROM  Leads l
LEFT JOIN Contacts c ON l."Last Name"  = c."Last Name" 
LEFT JOIN Accounts a ON c."Account Name"  = a."Account Name" 
LEFT JOIN Task_counts tc ON tc.Activity_Link_ID  = 
		CASE
			 WHEN c."Last Name"  IS NOT NULL THEN a."Id"
			 ELSE l."Id"
		 END 
LEFT JOIN Call_counts cc ON cc.Activity_Link_ID  = 
		CASE
			 WHEN c."Last Name"  IS NOT NULL THEN a."Id"
			 ELSE l."Id"
		 END 
LEFT JOIN Meeting_counts mc ON mc.Activity_Link_ID  = 
		CASE
			 WHEN c."Last Name"  IS NOT NULL THEN a."Id"
			 ELSE l."Id"
		 END 
LEFT JOIN "Campaign Members - Leads" cm ON cm."Lead Id"  = l."Id"  

