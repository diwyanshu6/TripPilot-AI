import os
import sqlite3
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    _pool = None
    _sqlite_path = None
    
    @classmethod
    def initialize(cls):
        # Determine database type
        if DATABASE_URL:
            print("Connecting to PostgreSQL at:", DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL)
            try:
                cls._pool = ConnectionPool(
                    conninfo=DATABASE_URL,
                    min_size=1,
                    max_size=10,
                    open=True
                )
                cls._init_postgres()
                return
            except Exception as e:
                print(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
        
        # SQLite fallback
        print("Using SQLite fallback (local file: backend/trippilot.db)")
        cls._sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "trippilot.db")
        cls._init_sqlite()

    @classmethod
    def _init_postgres(cls):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS trips (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                source VARCHAR(100) NOT NULL,
                destination VARCHAR(100) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                budget NUMERIC(12, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS trip_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
                prompt TEXT NOT NULL,
                generated_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS generated_pdf (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
                pdf_path VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
        with cls._pool.connection() as conn:
            with conn.cursor() as cur:
                for q in queries:
                    cur.execute(q)
                conn.commit()

    @classmethod
    def _init_sqlite(cls):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS trips (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                budget REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS trip_history (
                id TEXT PRIMARY KEY,
                trip_id TEXT,
                prompt TEXT NOT NULL,
                generated_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS generated_pdf (
                id TEXT PRIMARY KEY,
                trip_id TEXT,
                pdf_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
            );
            """
        ]
        with sqlite3.connect(cls._sqlite_path) as conn:
            cur = conn.cursor()
            for q in queries:
                cur.execute(q)
            conn.commit()

    @classmethod
    def execute(cls, query, params=None):
        if params is None:
            params = ()
        
        # PostgreSQL execution
        if cls._pool:
            with cls._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    conn.commit()
                    return cur
        
        # SQLite execution
        # Convert %s placeholder syntax of psycopg to ? for SQLite
        query = query.replace("%s", "?")
        with sqlite3.connect(cls._sqlite_path) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur

    @classmethod
    def fetch_all(cls, query, params=None):
        if params is None:
            params = ()
            
        if cls._pool:
            with cls._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params)
                    return cur.fetchall()
        
        query = query.replace("%s", "?")
        with sqlite3.connect(cls._sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    @classmethod
    def fetch_one(cls, query, params=None):
        if params is None:
            params = ()
            
        if cls._pool:
            with cls._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params)
                    return cur.fetchone()
        
        query = query.replace("%s", "?")
        with sqlite3.connect(cls._sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
