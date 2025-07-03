from utils.modules import parse_sql
from oracle.db import *
import pandas as pd
from typing import *

conn = connect_to_db()

def _fetch(
    query: str,
    conn,
    params: Optional[Union[Dict[str, Any], Tuple[Any, ...]]] = None
) -> List[Tuple]:
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or {})
        rows = cursor.fetchone()
        return rows
    except Exception as e:
        print(f"Error executing query: {e}")
        return []
    finally:
        try:
            cursor.close()
        except:
            pass

def _update(
    query: str,
    conn,
    params: Optional[Union[Dict[str, Any], Tuple[Any, ...]]] = None
) -> int:
    """
    Execute an UPDATE SQL query using a cursor and return the number of rows affected.

    Args:
        conn: A database connection object.
        query: The SQL UPDATE query to execute (can be parameterized).
        params: Optional parameters for the query (either a dict or tuple).

    Returns:
        The number of rows affected by the UPDATE query.
    """
    try:
        cursor = conn.cursor()  # Open a new cursor
        cursor.execute(query, params or {})  # Execute the UPDATE query
        conn.commit()  # Commit the transaction (if needed)
        rows_affected = cursor.rowcount  # Get the number of affected rows
        return rows_affected
    except Exception as e:
        print(f"Error executing UPDATE query: {e}")
        conn.rollback()  # Rollback in case of error
        return 0  # Return 0 if the update failed
    finally:
        try:
            cursor.close()  # Close the cursor
        except:
            pass