/*
	Author:		Brennan Douglas
	Date:		8/23/2017
	Company:	CASS

	This script resolves the "copy order", FK to PK ordering, of the tables in the database
	it is executed on.  The output contains the table_name, group_id, and pass flag.  The table_name
	is self explanatory, the groupt_id is the group in which it should be copied in parallel with
	it's other group mates, and the pass flag indicates if the table is in the correct position (0
	for incorrect position, 1 for correct position).

	WARNING:	Make sure to make exception rules for all circular dependencies in the database by
				filling out the exp_map insert statements, these links will be disregarded in the
				algorithm.
				
	NOTE:		Circular foreign key refrences can be found using SQLQuery_FindCircularRefrences
*/

DECLARE @exp_map TABLE (parent_name VARCHAR(255), child_name VARCHAR(255));
DECLARE @dep_map TABLE (table_name VARCHAR(255), children VARCHAR(MAX));
DECLARE @group TABLE (table_name VARCHAR(255), group_id INT);
DECLARE @tmp_group TABLE (table_name VARCHAR(255), group_id INT);


-- Predefined circular references. These are excluded in the algorithm
INSERT INTO @exp_map ([child_name], [parent_name])
	VALUES	('dbo.CMMNC_LOG',			'dbo.RSPNS_UNIT'),
			('dbo.ITS_STD_EVNT_TYP',	'dbo.EVNT_SUB_TYP'),
			('dbo.REG',					'dbo.TOCS_PER'),
			('dbo.USER_PROF',			'dbo.TOCS_USER');


WITH sys_object_with_schmea AS (
	SELECT	o.object_id,
			o.name,
			o.type_desc,
			o.type,
			s.name AS schema_name
	FROM sys.objects AS o
	INNER JOIN sys.schemas AS s ON o.schema_id = s.schema_id
)

-- Create initial dependency mapping
INSERT INTO @dep_map
SELECT
	o.schema_name + '.' + o.name AS table_name,
	STUFF((SELECT ';' + d.parent_table
			FROM (SELECT DISTINCT * FROM (SELECT 
					SO_P.schema_name + '.' + SO_P.name AS [child_table],
					SO_R.schema_name + '.' + SO_R.name AS [parent_table]
				FROM sys.foreign_key_columns FKC
					JOIN (SELECT * FROM sys_object_with_schmea) SO_P ON SO_P.object_id = FKC.referenced_object_id
					JOIN (SELECT * FROM sys_object_with_schmea) SO_R ON SO_R.object_id = FKC.parent_object_id
				WHERE (SO_P.name = o.name) AND (SO_P.type = 'U') AND (SO_P.name != SO_R.name) AND
					NOT EXISTS(
						SELECT [parent_name], [child_name] FROM @exp_map
						WHERE [parent_name] = (SO_R.schema_name + '.' + SO_R.name) AND
						      [child_name]  = (SO_P.schema_name + '.' + SO_P.name)
					)) as a) as d
			ORDER BY d.parent_table
			FOR XML PATH('')), 1, 1, '') AS children
	FROM sys_object_with_schmea o
		WHERE o.type_desc = 'USER_TABLE' AND o.name != '__RefactorLog';

--SELECT * FROM @dep_map


DECLARE @table_name VARCHAR(255);
DECLARE @children_list VARCHAR(MAX);
DECLARE @current_group INT = 0;
DECLARE @delimiter VARCHAR(1) = ';';


-- Initialize Group 0
INSERT INTO @group ([table_name], [group_id])
SELECT a.[table_name], 0 AS [group_id] FROM @dep_map AS a;


-- Run Algorithm
WHILE @current_group = 0 OR EXISTS(SELECT * FROM @group WHERE [group_id] = @current_group - 1)
BEGIN

	DECLARE GroupCursor CURSOR FAST_FORWARD READ_ONLY
	FOR SELECT [table_name] FROM @group WHERE [group_id] = @current_group OPEN GroupCursor
	FETCH NEXT FROM GroupCursor INTO @table_name
	WHILE @@FETCH_STATUS = 0
	BEGIN
		SELECT @children_list = [children] FROM @dep_map WHERE [table_name] = @table_name

		IF EXISTS ( SELECT table_name FROM
						dbo.fn_Split(@children_list, @delimiter) c
					INNER JOIN @group g ON c.Value = g.table_name
					WHERE g.group_id = @current_group OR g.group_id = @current_group + 1)
		BEGIN
			UPDATE @group SET group_id = @current_group + 1 WHERE table_name = @table_name
		END

		FETCH NEXT FROM GroupCursor INTO @table_name
	END

	-- Close up cursor
	CLOSE GroupCursor
	DEALLOCATE GroupCursor

	SET @current_group = @current_group + 1

END


DECLARE @group_id INT
DECLARE @table_pass TABLE (table_name VARCHAR(255), group_id INT, pass INT)


-- Test the order
DECLARE TestCursor CURSOR FORWARD_ONLY READ_ONLY
	FOR SELECT [table_name], [group_id] FROM @group ORDER BY [group_id] OPEN TestCursor
	FETCH NEXT FROM TestCursor INTO @table_name, @group_id
	WHILE @@FETCH_STATUS = 0
	BEGIN
		SELECT @children_list = [children] FROM @dep_map WHERE [table_name] = @table_name

		DECLARE @pass INT = 0

		IF NOT EXISTS ( SELECT table_name FROM
							dbo.fn_Split(@children_list, @delimiter) c
						INNER JOIN @group g ON c.Value = g.table_name
						WHERE g.group_id >= @group_id )
		BEGIN
			SET @pass = 1
		END
		
		INSERT INTO @table_pass ([table_name], [group_id], [pass]) VALUES (@table_name, @group_id, @pass)

		IF @pass = 0
			PRINT @table_name + ', group ' + CAST(@group_id AS VARCHAR) + ', is not in the group.'

		FETCH NEXT FROM TestCursor INTO @table_name, @group_id
	END

	-- Close up cursor
	CLOSE TestCursor
	DEALLOCATE TestCursor

--SELECT * FROM @group ORDER BY group_id, table_name
SELECT * FROM @table_pass ORDER BY group_id, table_name