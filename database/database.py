import sqlite3

DB_NAME = "database/history.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        citation TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_chat(question, answer, citation):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history(question, answer, citation)
        VALUES (?, ?, ?)
        """,
        (question, answer, citation)
    )

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT question, answer, citation
        FROM chat_history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows