from dotenv import load_dotenv
import os
import snowflake.connector


load_dotenv()


def connect_to_db():

    try:
        conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database='DB_TEAM_ALBERTA_PRECISION_LABORATORIES_DEVELOPERS',
        schema='APL_USER_DS_MINSHANXIE',
        role=os.getenv("SNOWFLAKE_ROLE"),
        authenticator='externalbrowser',
        )
    
        print(os.getenv("SNOWFLAKE_DATABASE")+'!!!!!')
        print(os.getenv("SNOWFLAKE_SCHEMA")+'!!!!!')
        
        print("Connected to Snowflake Database!")
        return conn
    except snowflake.connector.errors.Error as e:
        print(f"Error connecting to Snowflake: {e}")
        return None


# def connect_to_db(schema):
#     try:
#         conn = snowflake.connector.connect(
#             user=os.getenv("SNOWFLAKE_USER"),
#             password=os.getenv("SNOWFLAKE_PASSWORD"),
#             account=os.getenv("SNOWFLAKE_ACCOUNT"),
#             warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
#             database=os.getenv("SNOWFLAKE_DATABASE"),
#             schema=schema
#         )
#         return conn
#     except snowflake.connector.errors.Error as e:
#         print(f"Error connecting to Snowflake: {e}")
#         return None

