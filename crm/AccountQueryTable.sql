SELECT
		 c."Account Id" AS "Account Id",
		 c."OpenPercent" AS "OpenPercent",
		 i."InvoiceCount" AS "InvoiceCount",
		 i."InvoiceAmount" AS "InvoiceAmount",
		 i."OverduePercent" AS "OverduePercent"
FROM (	SELECT
			 "Account Id",
			 COUNT(CASE
					 WHEN "Status"  = 'Open' THEN 1
				 END) * 100.0 / COUNT("Case Id") AS "OpenPercent"
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
