SELECT DB_NAME() AS dbname,
	o.name AS referenced_table_name,
	SCHEMA_NAME(o.schema_id) AS referenced_schema,
	STUFF((SELECT ';' + d.parent_table
			FROM (SELECT DISTINCT * FROM (SELECT 
					SO_P.name AS [child_table],
					SO_R.name AS [parent_table]
				FROM sys.foreign_key_columns FKC
					JOIN sys.objects SO_P ON SO_P.object_id = FKC.parent_object_id
					JOIN sys.objects SO_R ON SO_R.object_id = FKC.referenced_object_id
				WHERE (SO_P.name = o.name) AND (SO_P.type = 'U')) as a) as d
			ORDER BY d.parent_table
			FOR XML PATH('')), 1, 1, '') AS object_dependencies
	FROM sys.objects o
		WHERE o.type_desc = 'USER_TABLE'
		--GROUP BY o.name
		ORDER BY referenced_schema, referenced_table_name