"""
Database connection module.
Uses psycopg3 to connect to PostgreSQL.
"""

import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# Database config
POSTGRES_DBNAME = os.getenv("POSTGRES_DBNAME")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")


def get_connection():
    """
    Get a PostgreSQL connection.
    Uses psycopg3 (different from psycopg2).
    
    Returns:
        psycopg connection object
    """
    try:
        conn = psycopg.connect(
            dbname=POSTGRES_DBNAME,
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=5432
        )
        return conn
    except psycopg.Error as e:
        print(f"Could not connect to PostgreSQL: {e}")
        raise


def test_connection():
    """Test if database connection is working."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False
