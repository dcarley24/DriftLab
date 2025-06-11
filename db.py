import sqlite3
from datetime import datetime

DB = 'driftlab.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def insert_prompt(prompt_text):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO prompts (text, created_at) VALUES (?, ?)",
                (prompt_text, datetime.utcnow().isoformat()))
    prompt_id = cur.lastrowid
    conn.commit()
    conn.close()
    return prompt_id

def insert_output(prompt_id, step, content, drift_score, violation):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO outputs (prompt_id, step, content, drift_score, violation) VALUES (?, ?, ?, ?, ?)",
                (prompt_id, step, content, drift_score, violation))
    conn.commit()
    conn.close()

def insert_recovery(prompt_id, recovery_prompt, recovery_output, recovery_score):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO recoveries (prompt_id, recovery_prompt, recovery_output, recovery_score) VALUES (?, ?, ?, ?)",
                (prompt_id, recovery_prompt, recovery_output, recovery_score))
    conn.commit()
    conn.close()

def get_prompt_history():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, text, created_at FROM prompts ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_prompt_details(prompt_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT text FROM prompts WHERE id = ?", (prompt_id,))
    prompt = cur.fetchone()[0]

    cur.execute("SELECT step, content, drift_score, violation FROM outputs WHERE prompt_id = ? ORDER BY step ASC", (prompt_id,))
    rows = cur.fetchall()
    outputs = []
    for row in rows:
        outputs.append({
            'step': row[0],
            'text': row[1],
            'score': row[2],
            'violation': row[3]
        })

    cur.execute("SELECT recovery_prompt, recovery_output, recovery_score FROM recoveries WHERE prompt_id = ?", (prompt_id,))
    recoveries = cur.fetchall()

    conn.close()
    return prompt, outputs, recoveries
