import os
import math
import pandas as pd
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from oracle.db import connect_to_db as oracledb
from oracle.helper import cf_column_selection_oracle
from snowflake.db import connect_to_db as snowflakedb
from snowflake.helper import column_selection_snowflake
from utils.modules import *

# === CONFIGURATION ===
PK1 = 'RESULT_ID'
PK2 = 'LINE'
IDS = [PK1, PK2]
CATEGORY = "result_comments"
ORACLE_DATABASE = 'CLDR_EXTRACT'
ORACLE_TABLE = 'EX_CLDR_EPIC_RESULT_COMMENT'
SNOWFLAKE_DATABASE = 'DB_TEAM_ALBERTA_PRECISION_LABORATORIES_DEVELOPERS'
SNOWFLAKE_SCHEMA = 'APL_USER_DS_MINSHANXIE'
SNOWFLAKE_TABLE = 'TGT_RESULT_COMMENT_TABLE'

# === NORMALIZATION + COMPARISON ===
def normalize_value(val):
    if pd.isnull(val):
        return ''
    return re.sub(r'\W+', '', str(val).strip().lower())

def compare_values(v1, v2):
    if pd.isnull(v1) and pd.isnull(v2): return 'Pass'
    if v1 == v2: return 'Pass'

    v1_stripped = str(v1).strip()
    v2_stripped = str(v2).strip()

    if v1_stripped == v2_stripped and str(v1) != str(v2):
        return 'Warning'

    def remove_special(s):
        return re.sub(r'\W+', '', s.lower())
    if remove_special(v1_stripped) == remove_special(v2_stripped):
        return 'Warning'

    try:
        list1 = sorted([remove_special(x.strip()) for x in v1_stripped.split(',')])
        list2 = sorted([remove_special(x.strip()) for x in v2_stripped.split(',')])
        if list1 == list2:
            return 'Warning'
    except:
        pass

    return 'Fail'

def classify_row(results):
    values = [v for k, v in results.items() if k.endswith("_RESULT")]
    if 'Fail' in values: return 'Fail'
    if 'Warning' in values: return 'Warning'
    return 'Pass'

# === DB CONNECTIONS ===
oracle_db = oracledb()
snowflake_db = snowflakedb()

def get_count(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()[0]
    cur.close()
    return result

# Get row counts
oracle_total = get_count(oracle_db, f"SELECT COUNT(*) FROM {ORACLE_DATABASE}.{ORACLE_TABLE}")
snowflake_total = get_count(snowflake_db, f"SELECT COUNT(*) FROM {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{SNOWFLAKE_TABLE}")
print(f"Total Oracle rows: {oracle_total}")
print(f"Total Snowflake rows: {snowflake_total}")
total_batches = math.ceil(min(oracle_total, snowflake_total) / 1000)

# === HASH FUNCTION ===
def oracle_hash(schema, table, offset=0):
    select_columns, concat_expr, exclusion_columns = cf_column_selection_oracle(oracle_db, schema, table)
    query = f"""
        SELECT {select_columns}, STANDARD_HASH({concat_expr}, 'SHA256') AS ROW_HASH
        FROM {schema}.{table}
        ORDER BY {PK1}, {PK2}
        OFFSET {offset} ROWS FETCH NEXT 1000 ROWS ONLY
    """
    cur = oracle_db.cursor()
    cur.execute(query)
    data = hex_conversion(cur.fetchall())
    df = return_df(cur, data)
    cur.close()
    return df, exclusion_columns

def snowflake_hash(database, schema, table, offset=0):
    select_columns, concat_expr = column_selection_snowflake(snowflake_db, database, schema, table)
    q = f"""
        SELECT {select_columns}, UPPER(SHA2({concat_expr}, 256)) AS ROW_HASH
        FROM {database}.{schema}.{table}
        ORDER BY {PK1}, {PK2}
        LIMIT 1000 OFFSET {offset}
    """
    cur = snowflake_db.cursor()
    cur.execute(q)
    df = return_df(cur, cur.fetchall())
    cur.close()
    return df

# === MAIN LOOP ===
output_dir = os.path.join(os.getcwd(), 'outputs')
os.makedirs(output_dir, exist_ok=True)

offset_value = 0
all_results = []

for batch in range(total_batches):
    print(f"Processing batch {batch + 1}/{total_batches} (offset {offset_value})")
    oracle_rows, exclusion_columns = oracle_hash(ORACLE_DATABASE, ORACLE_TABLE, offset_value)
    snowflake_rows = snowflake_hash(SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_TABLE, offset_value)
    offset_value += 1000

    df_ora = pd.DataFrame(oracle_rows)
    df_snow = pd.DataFrame(snowflake_rows)

    # Merge and filter rows with different hashes
    df_merged = df_ora.merge(df_snow, on=IDS, suffixes=("_oracle", "_snowflake"))
    print(f"Merged row count before hash filter comparison: {len(df_merged)}")

    df_diff_hash = df_merged[df_merged["ROW_HASH_oracle"] != df_merged["ROW_HASH_snowflake"]]


    if df_diff_hash.empty: 
        print(f"{TermColor.GREEN}All rows matched based on hash.{TermColor.RESET}")
        continue
    else:
        print(f"{TermColor.RED}{len(df_diff_hash)} rows have different hashes and need field-by-field comparison.{TermColor.RESET}")

    # === Field-by-field comparison for differing rows ===
    result_rows = []
    for _, row in df_diff_hash.iterrows():
        row_out = {k: row[k] for k in IDS}
        row_results = []
        for col in df_ora.columns:
            if col in IDS or col == "ROW_HASH":
                continue
            o, s = f"{col}_oracle", f"{col}_snowflake"
            if o in row and s in row:
                val_oracle = row[o]
                val_snow = row[s]
                result = compare_values(val_oracle, val_snow)
                row_out[o] = val_oracle
                row_out[s] = val_snow
                row_out[f"{col}_RESULT"] = result
                row_results.append(result)

        row_out["ROW_STATUS"] = (
            'Fail' if 'Fail' in row_results else
            'Warning' if 'Warning' in row_results else
            'Pass'
        )
        result_rows.append(row_out)

    result_df = pd.DataFrame(result_rows)
    if not (result_df['ROW_STATUS'] == 'Fail').any():
        print(f"{TermColor.GREEN} All rows matched in field-by-field comparison.{TermColor.RESET}")
    else:
        print(f"{TermColor.RED} Differences found in field-level comparison.{TermColor.RESET}")

    columns_to_drop = ["ROW_HASH_oracle", "ROW_HASH_snowflake", "ROW_HASH_RESULT"]
    result_df.drop(columns=[col for col in columns_to_drop if col in result_df.columns], inplace=True)

    batch_file = os.path.join(output_dir, f'column_differences_slim_{CATEGORY}_offset_{offset_value}_{curr_datetime_ff()}.csv')
    result_df.to_csv(batch_file, index=False)
    all_results.append(result_df)

# === EXPORT ALL RESULTS ===
if all_results:
    final_df = pd.concat(all_results, ignore_index=True)
    final_csv = os.path.join(output_dir, f'column_differences_slim_{CATEGORY}_ALL_{curr_datetime_ff()}.csv')
    final_df.to_csv(final_csv, index=False)

# === CLOSE DB CONNECTIONS ===
oracle_db.close()
snowflake_db.close()
