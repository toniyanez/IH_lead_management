import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('leads.db')
    conn.execute('''
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
    conn.execute('''
        INSERT INTO leads (company, website, email, contact_person, summary, growth_phase, score, next_action, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def fetch_all_leads_df():
    conn = sqlite3.connect('leads.db')
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    return df

def update_leads_bulk(df):
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute('''
            UPDATE leads
            SET company=?, website=?, email=?, contact_person=?, summary=?, growth_phase=?, score=?, next_action=?, comments=?
            WHERE id=?
        ''', (
            row['Company'], row['Website'], row['Email'], row['Contact Person'],
            row['Summary'], row['Growth Phase'], row['Score'],
            row['Next Action'], row['Comments'], row['ID']
        ))
    conn.commit()
    conn.close()


