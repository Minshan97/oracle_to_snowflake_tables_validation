from datetime import datetime
from typing import Optional, Union
import binascii
import dask.dataframe as dd
import pandas as pd

class TermColor:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def parse_sql(query, conn, params: Optional[Union[dict, tuple]] = None) -> pd.DataFrame:
    ## examples
    # query = """SELECT * FROM TABLE WHERE id = %s"""
    # params = (2,)

    df = pd.read_sql(query, conn, params=params)
    return df

def curr_datetime():
    return datetime.now()

def curr_datetime_ff():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def oracle_time_to_timestamp(oracle_time):
    if oracle_time is None:
        return None
    else:
        dt = pd.to_datetime(oracle_time, format='%d-%b-%Y %H:%M:%S')

    # Convert to Snowflake format: 'YYYY-MM-DD HH24:MI:SS.FFF'
    snowflake_format = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    return snowflake_format

# Consistent normalization
def normalize_string(val):
    return val.strip().lower() if val is not None else ''

def hex_upper(val):
    return val.upper() if val is not None else ''

# Merge on 'id' to align hash values from both DataFrames
def merge_hashes(df1, df2, id):
    # print(f"df1:\n{df1.to_string()}")
    # print(f"df2:\n{df2.to_string()}")
    # Merge DataFrames on 'id' (or any other common column)
    merged = dd.merge(df1, df2, on=id, how='outer', suffixes=('_snowflake', '_oracle'))
    print('merged lines number:'+str(len(merged)))
    # print(f"merged:\n{merged.head(5).to_string()}")
    merged.head(5).to_csv('../outputs/merged_desc_order.csv')
    # Identify rows where the hash values differ (including where one is missing)
    mismatched = merged[merged['ROW_HASH_snowflake'] != merged['ROW_HASH_oracle']]

    return mismatched

def return_df(cursor, data):
    # Create a DataFrame from the cursor data
    df = pd.DataFrame(data, columns=[
        col[0] for col in cursor.description
    ])
    
    return df.fillna(value="-1") 


def hex_conversion(data):
    hex_values = []
    for row in data:
        # Convert binary data (bytes) to hexadecimal
        hex_row = tuple(
            hex_upper(binascii.hexlify(item).decode('utf-8')) if isinstance(item, bytes) else item
            for item in row
        )
        hex_values.append(hex_row)

    return hex_values

def print_full_df(df):
    """Prints all rows and columns of a DataFrame without truncation."""
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        print(df)

