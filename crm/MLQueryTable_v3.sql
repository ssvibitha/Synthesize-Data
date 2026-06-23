-- Query table accomodating 10,000 leads and combined data of contacts, activities 
-- due to limited crm storage
-- includes details like lead_id, lead_source, lead_industry, campaign_name, 
-- member_status in campaign, no.of calls,tasks,activities per lead

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
		 COALESCE(tc.NumberOfOtherTasks, 0) AS NumberOfOtherTasks,
		 COALESCE(cc.NumberOfCalls, 0) AS NumberOfCalls,
		 COALESCE(mc.NumberOfMeetings, 0) AS NumberOfMeetings
FROM  Leads l
LEFT JOIN CombinedContacts c ON l."Last Name"  = c."Last Name" 
LEFT JOIN Accounts a ON c."Account Name"  = a."Account Name" 
LEFT JOIN OtherTask_counts_combined tc ON REPLACE(tc.Activity_Link_ID, 'zcrm_', '')  = 
		CASE
			 WHEN c."Last Name"  IS NOT NULL THEN a."Id"
			 ELSE l."Id"
		 END 
LEFT JOIN CallCountsCombined cc ON REPLACE(cc.Activity_Link_ID, 'zcrm_', '')  = 
		CASE
			 WHEN c."Last Name"  IS NOT NULL THEN a."Id"
			 ELSE l."Id"
		 END 
LEFT JOIN MeetingCountsCombined mc ON REPLACE(mc.Activity_Link_ID, 'zcrm_', '')  = 
		CASE
			 WHEN c."Last Name"  IS NOT NULL THEN a."Id"
			 ELSE l."Id"
		 END 
LEFT JOIN "Campaign Members" cm ON REPLACE(cm."Lead ID", 'zcrm_', '')  = l."Id"  
