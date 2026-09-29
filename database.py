import sqlite3


def init_db():
    conn = sqlite3.connect("diagnosis.db")
    cursor = conn.cursor()

    # 创建历史记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem TEXT NOT NULL,
            summary TEXT,
            causes TEXT,
            steps TEXT,
            suggestions TEXT,
            mode TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 如果数据库是以前创建的旧版本，
    # 自动补充新的字段
    cursor.execute("""
        PRAGMA table_info(diagnosis_history)
    """)

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "causes" not in columns:
        cursor.execute("""
            ALTER TABLE diagnosis_history
            ADD COLUMN causes TEXT
        """)

    if "steps" not in columns:
        cursor.execute("""
            ALTER TABLE diagnosis_history
            ADD COLUMN steps TEXT
        """)

    if "suggestions" not in columns:
        cursor.execute("""
            ALTER TABLE diagnosis_history
            ADD COLUMN suggestions TEXT
        """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("数据库初始化完成")