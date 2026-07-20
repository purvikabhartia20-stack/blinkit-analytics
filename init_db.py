import sqlite3
import yaml
import os
import sys

def load_config():
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config.yaml: {e}")
        sys.exit(1)

def init_db():
    config = load_config()
    db_path = config.get("database", {}).get("db_path", "blinkit_data.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT,
                date TEXT,
                rating INTEGER,
                review_text TEXT,
                username TEXT,
                country_code TEXT,
                hash TEXT UNIQUE NOT NULL
            )
        """)
        
        # tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_id INTEGER,
                theme TEXT,
                sentiment TEXT,
                category_mentioned TEXT,
                behavior_signal TEXT,
                pain_point TEXT,
                unmet_need TEXT,
                trust_barrier_mentioned BOOLEAN,
                trust_barrier_text TEXT,
                severity TEXT,
                key_quote TEXT,
                FOREIGN KEY(review_id) REFERENCES reviews(id)
            )
        """)
        
        # insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme TEXT,
                summary_markdown TEXT,
                backing_data_json TEXT,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # validation_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spot_check_date TEXT,
                sample_size INTEGER,
                agreement_rate REAL,
                notes TEXT
            )
        """)
        
        # fallback_cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fallback_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_fallback BOOLEAN DEFAULT 1,
                data_type TEXT,
                data_content TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"Database initialized successfully at {db_path} with all schema tables.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
