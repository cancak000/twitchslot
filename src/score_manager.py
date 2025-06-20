import sqlite3

# SQLite接続はスレッドセーフにしておく
conn = sqlite3.connect("slot_scores.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    username TEXT PRIMARY KEY,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

def add_score(username, delta):
    cursor.execute("INSERT OR IGNORE INTO scores (username) VALUES (?)", (username,))
    cursor.execute("UPDATE scores SET score = score + ? WHERE username = ?", (delta, username))
    conn.commit()

def get_score(username):
    cursor.execute("SELECT score FROM scores WHERE username = ?", (username,))
    row = cursor.fetchone()
    return row[0] if row else 0
