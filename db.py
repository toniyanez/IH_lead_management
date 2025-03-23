import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            website TEXT,
            email TEXT,
            contact_person TEXT,
            summary TEXT,
            growth_phase TEXT,
            score INTEGER,
            next_action TEXT,
            comments TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_lead(data):
    conn = sqlite3.connect('leads.db')
    cursor
