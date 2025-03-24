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
            comments TEXT,
            next_action TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_lead(data):
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leads (company, website, email, contact_person, summary, growth_phase, score, comments, next_action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def fetch_all_leads_df():
    conn = sqlite3.connect('leads.db')
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    # Normalize column names to lowercase and underscore
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df

def update_leads_bulk(df):
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute('''
            UPDATE leads
            SET company=?, website=?, email=?, contact_person=?, summary=?, growth_phase=?, score=?, comments=?, next_action=?
            WHERE id=?
        ''', (
            row['company'], row['website'], row['email'], row['contact_person'],
            row['summary'], row['growth_phase'], int(row['score']),
            row['comments'], row['next_action'], int(row['id'])
        ))
    conn.commit()
    conn.close()



