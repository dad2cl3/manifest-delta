CREATE OR REPLACE FUNCTION manifest.fn_get_changes (IN p_manifest_id int4)
RETURNS SETOF record
AS $BODY$
BEGIN
	RETURN QUERY
		SELECT
			table_name,
			SUM(CASE
				WHEN created_by = p_manifest_id THEN
					1
				ELSE 0
			END) inserts,
			SUM(CASE
				WHEN last_updated_by = p_manifest_id AND last_updated_by != created_by THEN
					1
				ELSE
					0
			END) updates,
			SUM(CASE
				WHEN deleted_by = p_manifest_id THEN
					1
				ELSE
					0
			END) deletes
		FROM manifest.t_manifest
		WHERE created_by = p_manifest_id OR deleted_by = p_manifest_id OR last_updated_by = p_manifest_id
		GROUP BY table_name
		ORDER BY table_name;

		RETURN;
END
$BODY$
	LANGUAGE plpgsql
	SECURITY INVOKER;