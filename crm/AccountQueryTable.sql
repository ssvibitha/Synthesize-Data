SELECT
		 a."Id" AS "Account Id",
		 i."InvoiceAmount" AS "InvoiceAmount",
		 c."OpenPercent" AS "OpenCasesPercent",
		 i."OverduePercent" AS "OverduePercent",
		 i."InvoiceCount" AS "Invoice Count",
		 c."NumCaseEscalation" AS "NumCaseEscalation",
		 c."EscalataionRate" AS "EscalataionRate",
		 c."AvgResolutionTime" AS "AvgResolutionTime"
FROM (	SELECT
			 "Account Id",
			 COUNT(CASE
					 WHEN "Status"  = 'Active' THEN 1
				 END) * 100.0 / COUNT("Case Id") AS "OpenPercent",
			 SUM("Case Escalation") AS "NumCaseEscalation",
			 SUM("Case Escalation") * 1.0 / COUNT("Case Id") AS "EscalataionRate",
			 AVG("ResolvedInDays") AS "AvgResolutionTime"
	FROM  "Cases" 
	GROUP BY  "Account Id" 
) c
LEFT JOIN(	SELECT
			 "Account Id",
			 COUNT("Invoice Id") AS "InvoiceCount",
			 SUM("Invoice Total") AS "InvoiceAmount",
			 COUNT(CASE
					 WHEN "Delay Days"  > 0 THEN 1
				 END) * 100.0 / COUNT("Invoice Id") AS "OverduePercent"
	FROM  "Invoices" 
	GROUP BY  "Account Id" 
) i ON i."Account Id"  = c."Account Id" 
RIGHT JOIN "Accounts" a ON a."Id"  = REPLACE(c."Account Id", 'zcrm_', '')  
