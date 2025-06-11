import sqlite3

def init_db():
    conn = sqlite3.connect('driftlab.db')
    c = conn.cursor()

    # Create prompts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create outputs table (drift steps)
    c.execute('''
        CREATE TABLE IF NOT EXISTS outputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER,
            step INTEGER,
            content TEXT,
            drift_score REAL,
            violation BOOLEAN,
            FOREIGN KEY(prompt_id) REFERENCES prompts(id)
        )
    ''')

    # Create recoveries table
    c.execute('''
        CREATE TABLE IF NOT EXISTS recoveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER,
            recovery_prompt TEXT,
            recovery_output TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prompt_id) REFERENCES prompts(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Drift Lab database initialized.")

if __name__ == '__main__':
    init_db()
