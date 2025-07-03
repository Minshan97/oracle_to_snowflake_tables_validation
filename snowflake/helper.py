from utils.modules import TermColor
import json


def column_selection_snowflake(conn, database, table): 
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT column_name, data_type
        FROM {database}.information_schema.columns 
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    results = cursor.fetchall()
    columns = [row[0] for row in results]
    column_types = [row[1] for row in results]

    concat_parts = []

    for col, data_type in zip(columns, column_types):
        if data_type in ['DATE', 'TIMESTAMP', 'TIMESTAMP_NTZ']:
            part = f"COALESCE(TO_VARCHAR({col}, 'YYYY-MM-DD HH24:MI:SS'), '')"
        else:
            part = f"COALESCE(TO_VARCHAR({col}), '')"
        concat_parts.append(part)

    concat_expr = f" || ".join(concat_parts)

    select_columns = columns # select which columns to show in output
    select_columns = ", ".join(select_columns) + ","

    # print(f"{TermColor.BLUE}SELECTED COLUMNS SNOWFLAKE:\n\n{select_columns}{TermColor.RESET}")

    return select_columns, concat_expr


def column_selection_snowflake(conn, database, schema, table):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT column_name
        FROM {database}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{schema}'
          AND TABLE_NAME = '{table}'
        ORDER BY ORDINAL_POSITION
    """)
    results = cursor.fetchall()
    columns = [row[0] for row in results]

    concat_parts = [f"COALESCE(TO_VARCHAR({col}), '')" for col in columns]
    concat_expr = " || ".join(concat_parts)

    select_columns = ", ".join(columns)  # ✅ No trailing comma

    return select_columns, concat_expr
