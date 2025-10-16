# utils/db_handler.py
import sqlite3
from datetime import datetime, timedelta

# Initialize the database
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    company TEXT,
                    job_title TEXT,
                    file_hash TEXT,
                    score REAL,
                    status TEXT,
                    reason TEXT,
                    date TEXT
                )''')
    conn.commit()
    conn.close()


# Check if a candidate was rejected within the last 6 months
def check_six_month_policy(email, company):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    six_months_ago = datetime.now() - timedelta(days=180)

    c.execute(
        "SELECT date FROM applications WHERE email=? AND company=? AND status='Rejected' ORDER BY date DESC LIMIT 1",
        (email, company)
    )

    row = c.fetchone()
    conn.close()

    if row:
        try:
            last_rejected_date = datetime.strptime(row[0], "%Y-%m-%d")
            return last_rejected_date > six_months_ago
        except Exception:
            return False
    return False
