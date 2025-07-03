from utils.modules import TermColor


def column_selection_oracle(conn, schema, table):
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT column_name, data_type
        FROM all_tab_columns
        WHERE table_name = '{table}'
            AND owner = '{schema}'
        ORDER BY column_id
    """)
    results = cursor.fetchall()

    exclude = {'CLDR_RES_CMT_ID', 'PROCESS_EXECUTION_ID','CLDR_ORDER_COMMENT_ID'}

    columns = [row[0] for row in results][1:-1]
    column_types = [row[1] for row in results][1:-1]

    # print(columns)

    filtered = [(col, dtype) for col, dtype in results if col not in exclude]
    columns = [col for col, _ in filtered]
    column_types = [dtype for _, dtype in filtered]

    # print(columns)
    
    concat_parts = []

    for col, data_type in zip(columns, column_types):
        if data_type in ('DATE', 'TIMESTAMP', 'TIMESTAMP WITH TIME ZONE', 'TIMESTAMP WITH LOCAL TIME ZONE'):
            part = f"NVL(TO_CHAR({col}, 'YYYY-MM-DD HH24:MI:SS'), '')"
        else:
            part = f"NVL(TO_CHAR({col}), '')"
        concat_parts.append(part)

    concat_expr = f" || ".join(concat_parts)

    select_columns = columns
    select_columns = ", ".join(select_columns) + ","

    print(f"{TermColor.BLUE}SELECTED COLUMNS ORACLE:\n\n{select_columns}{TermColor.RESET}")

    excl_cols = [row[0] for row in results]
    excl_cols = [excl_cols[0], excl_cols[-1]]
    # print(f"concat_expr: {concat_expr}")
    # print(f"{TermColor.RED}Exclusion columns:{TermColor.RED} {excl_cols}")

    return select_columns, concat_expr, list(exclude) #, excl_cols

def cf_column_selection_oracle(conn, schema, table):
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT column_name, data_type
        FROM all_tab_columns
        WHERE table_name = '{table}'
          AND owner = '{schema}'
        ORDER BY column_id
    """)
    results = cursor.fetchall()

    exclude = {'CLDR_RES_CMT_ID', 'PROCESS_EXECUTION_ID', 'CLDR_ORDER_COMMENT_ID'}

    filtered = [(col, dtype) for col, dtype in results if col not in exclude]
    columns = [col for col, _ in filtered]
    column_types = [dtype for _, dtype in filtered]

    concat_parts = []
    for col, data_type in zip(columns, column_types):
        if data_type in ('DATE', 'TIMESTAMP', 'TIMESTAMP WITH TIME ZONE', 'TIMESTAMP WITH LOCAL TIME ZONE'):
            part = f"NVL(TO_CHAR({col}, 'YYYY-MM-DD HH24:MI:SS'), '')"
        else:
            part = f"NVL(TO_CHAR({col}), '')"
        concat_parts.append(part)

    concat_expr = " || ".join(concat_parts)
    select_columns = ", ".join(columns)  # 🔧 FIXED: no trailing comma

    return select_columns, concat_expr, list(exclude)

