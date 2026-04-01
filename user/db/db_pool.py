import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
import psycopg

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Test connection before creating pool
try:
    print("[DB Config] Testing connection...")
    test_conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    test_conn.close()
    print("[DB Config] ✓ Connection test successful!")
except psycopg.OperationalError as e:
    print(f"[DB Config] ✗ Connection test failed: {e}")
    print(f"[DB Config] This might indicate:")
    print(f"  - User '{DB_USER}' doesn't exist in PostgreSQL")
    print(f"  - Password is incorrect")
    print(f"  - User doesn't have permission to connect to database '{DB_NAME}'")
    print(f"  - Check pg_hba.conf for authentication method restrictions")
    # Don't raise here - let the pool handle it, but we've logged the issue

db_pool = AsyncConnectionPool(DATABASE_URL, min_size=1, max_size=10)

async def close_pool():
    await db_pool.close()
    return "Database pool closed."

def get_db_pool():
    return db_pool

def get_connection():
    return db_pool.getconn()

def release_connection(conn):
    db_pool.putconn(conn)