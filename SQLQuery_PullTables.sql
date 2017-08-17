SELECT DB_NAME() AS dbname,
	o.name AS referenced_table_name,
	SCHEMA_NAME(o.schema_id) AS referenced_schema
	FROM sys.objects o
		WHERE o.type_desc = 'USER_TABLE'
		--GROUP BY o.name
		ORDER BY referenced_schema, referenced_table_name