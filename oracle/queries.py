from oracle.db import connect_to_db
from oracle.services import _fetch, _update
import pandas as pd

conn = connect_to_db()

def get_rpt_epic_corelab_order_ids():
    query = """
        select order_id from cldr_ahsdata.rpt_epic_corelab fetch first 10 rows only;
    """

    conn = connect_to_db()
    if conn:
        try:
            result = _fetch(query, conn)
            return result
        finally:
            try:
                conn.close()
            except Exception as e:
                print(f"Error closing connection: {e}")


            """
            query = "SELECT * FROM users WHERE id = :user_id"
            params = {"user_id": 1}
            df = pd.read_sql(query, con=conn, params=params)
            """

def get_oracle_rpt_ids(id1):
    query = """
        SELECT ORDER_ID
        FROM CLDR_AHSDATA.RPT_EPIC_CORELAB
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

def get_oracle_rpt_data():
    query = """
        SELECT *
        FROM CLDR_AHSDATA.RPT_EPIC_CORELAB
        FETCH FIRST 10 ROWS ONLY;    
    """

    try:
        result = _fetch(query, conn)
        return result
    finally:
        try:
            conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")


rpt_corelab_order_ids = get_rpt_epic_corelab_order_ids()
first_id = rpt_corelab_order_ids[0]
print(first_id)