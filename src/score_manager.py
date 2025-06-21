import sqlite3

# SQLite接続はスレッドセーフに
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
