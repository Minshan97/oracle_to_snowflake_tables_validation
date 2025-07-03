import json
import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

print("User:", os.getenv("SNOWFLAKE_USER"))

try:
    conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    role=os.getenv("SNOWFLAKE_ROLE"),
    authenticator='externalbrowser',
    )
   

    cur = conn.cursor()
    # Read and execute the SQL file
    cur.execute("USE DATABASE DB_TEAM_ALBERTA_PRECISION_LABORATORIES_DEVELOPERS;")
    cur.execute("USE SCHEMA APL_USER_DS_MINSHANXIE;")
    
    # Run sp_load_order_comment creation script
    # with open("sp_load_order_comment.sql", "r") as f:
    #     proc_sql = f.read()

    # cur.execute(proc_sql)
    # print("sp_load_order_comment created")


    # Run sp_load_result_comment creation script
    with open("sp_load_result_comment.sql", "r") as f:
        proc_sql = f.read()

    cur.execute(proc_sql)
    print("sp_load_result_comment created")


    # Call the stored procedures
    # cur.execute("CALL APL_USER_DS_MINSHANXIE.sp_load_order_comment();")
    # print("sp_load_order_comment executed")

    cur.execute("CALL APL_USER_DS_MINSHANXIE.sp_load_result_comment();")
    print("sp_load_result_comment executed")


except Exception as e:
    print("❌ Connection failed:", e)

finally:
    try:
        cur.close()
        conn.close()
    except:
        pass