
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FOLDER = os.path.join(BASE_DIR, "database")

os.makedirs(DATABASE_FOLDER, exist_ok=True)

DATABASE_PATH = os.path.join(DATABASE_FOLDER, "careeriq.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_filename TEXT,
            match_percentage REAL,
            text_similarity REAL,
            readiness_level TEXT,
            detected_skills TEXT,
            required_skills TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(analyses)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "user_id" not in columns:
        cursor.execute("""
            ALTER TABLE analyses
            ADD COLUMN user_id INTEGER REFERENCES students(id)
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_filename TEXT NOT NULL,
            upload_status TEXT DEFAULT 'Uploaded',
            analysis_id INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES students(id),
            FOREIGN KEY(analysis_id) REFERENCES analyses(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_analyses_user_id
        ON analyses(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_uploads_user_id
        ON resume_uploads(user_id)
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("CareerIQ database initialized successfully!")
