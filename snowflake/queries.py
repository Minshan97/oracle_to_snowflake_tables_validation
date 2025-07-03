from snowflake.services import _fetch, _update
from typing import *
from utils.modules import *
from snowflake.db import connect_to_db
import pandas as pd

conn = connect_to_db()

def get_rpt_ids(id1):
    query = """
        SELECT ORDER_ID
        FROM DB_TEAM_ALBERTA_PRECISION_LABORATORIES.CURATED_CORE.TB_RPT_RPT_EPIC_CORELAB
        WHERE PAT_ID = %s
    """
    params = (id1,)

    try:
        result = _fetch(query, conn, params)
        return result
    finally:
        try:
            conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

def update_rpt_rcv_time(order_id):
    query = """
        UPDATE DB_TEAM_ALBERTA_PRECISION_LABORATORIES.CURATED_CORE.TB_RPT_RPT_EPIC_CORELAB
        SET RCV_LAST_DTTM = %s
        WHERE ORDER_ID = %s
    """
    params = (curr_datetime(), order_id)

    try:
        result = _update(query, conn, params=params)
        return result
    finally:
        try:
            conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

            
def get_snowflake_rpt_data(date) -> pd.DataFrame:
    query = """
        SELECT * FROM DB_TEAM_ALBERTA_PRECISION_LABORATORIES.CURATED_CORE.TB_RPT_RPT_EPIC_CORELAB WHERE PAT_ADMIT_DTTM > %s LIMIT 10;
    """
    conn = connect_to_db()
    params = (date,)

    result = _fetch(query, conn, params)
    return result

rpt_data = get_snowflake_rpt_data('2025-01-01')

print(f"DATA:\n{rpt_data}")