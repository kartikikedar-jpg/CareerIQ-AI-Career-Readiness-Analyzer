
from db import get_db_connection, init_db
from werkzeug.security import generate_password_hash

# Initialize database
init_db()

conn = get_db_connection()

email = "admin@gmail.com"
password = "admin123"

password_hash = generate_password_hash(password)

try:
    admin = conn.execute(
        "SELECT id FROM admins LIMIT 1"
    ).fetchone()

    if admin:
        conn.execute("""
            UPDATE admins
            SET username = ?, password_hash = ?
            WHERE id = ?
        """, (email, password_hash, admin["id"]))

    else:
        conn.execute("""
            INSERT INTO admins (username, password_hash)
            VALUES (?, ?)
        """, (email, password_hash))

    conn.commit()
    print("Admin credentials updated successfully!")

finally:
    conn.close()
