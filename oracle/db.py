from dotenv import load_dotenv
import oracledb
import os

# Load environment variables from .env
load_dotenv()

def connect_to_db():
    oracledb.init_oracle_client(lib_dir=r"C:\Users\MinshanXie\Documents\instantclient_23_8")
    try:
        # Connect to the Oracle database using the full TNS descriptor
        conn = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN")
        )
        print("Connected to Oracle Database!")
        return conn
    except oracledb.Error as e:
        print(f"Error connecting to Oracle: {e}")
        return None
