import sqlite3
import pandas as pd

DB_FILE = "scout_hub.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def initialize_database():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS team_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS private_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS event_pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            location TEXT,
            event_date TEXT,
            category TEXT,
            est_attendance INTEGER,
            gross_revenue REAL,
            total_expenses REAL,
            net_profit REAL,
            roi_text TEXT,
            decision_tier TEXT,
            prep_dumplings INTEGER,
            status TEXT DEFAULT 'Discovered',
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filter_type TEXT,
            keyword TEXT,
            reason TEXT,
            added_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_team_message(user_name: str, message: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO team_chat (user_name, message) VALUES (?, ?)", (user_name, message))
    conn.commit()
    conn.close()

def load_team_messages():
    conn = get_connection()
    df = pd.read_sql("SELECT user_name, message, timestamp FROM team_chat ORDER BY id ASC", conn)
    conn.close()
    return df

def save_private_message(user_name: str, role: str, message: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO private_chats (user_name, role, message) VALUES (?, ?, ?)", (user_name, role, message))
    conn.commit()
    conn.close()

def load_private_messages(user_name: str):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT role, message FROM private_chats WHERE user_name = ? ORDER BY id ASC",
        conn,
        params=(user_name,)
    )
    conn.close()
    return df

def add_event_to_pipeline(data: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO event_pipeline (
            event_name, location, event_date, category, est_attendance,
            gross_revenue, total_expenses, net_profit, roi_text,
            decision_tier, prep_dumplings, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("event_name"), data.get("location"), data.get("event_date"),
        data.get("category"), data.get("est_attendance"), data.get("gross_revenue"),
        data.get("total_expenses"), data.get("net_profit"), data.get("roi_text"),
        data.get("decision_tier"), data.get("prep_dumplings"),
        data.get("status", "Discovered"), data.get("notes", "")
    ))
    conn.commit()
    conn.close()

def load_pipeline():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM event_pipeline ORDER BY net_profit DESC", conn)
    conn.close()
    return df

def update_event_status(event_id: int, new_status: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE event_pipeline SET status = ? WHERE id = ?", (new_status, event_id))
    conn.commit()
    conn.close()
