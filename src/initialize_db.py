import sqlite3
from typing import List, Dict
import os
from datetime import datetime, timedelta

DATABASE_NAME = 'sensusmundi.db'

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, DATABASE_NAME)

def create_database_and_tables():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Create a table for each country
    countries = ['Climate', 'UK', 'China', 'Russia_Ukraine', 'Israel_Palestine', 'USA', 'Turkey', 'Germany', 'France', 'NATO']
    
    for country in countries:
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {country} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            seendate TEXT,
            domain TEXT,
            language TEXT,
            sourcecountry TEXT,
            relevance_score REAL,
            date_added DATE DEFAULT CURRENT_DATE,
            news_body TEXT,
            short_title_en TEXT,
            summary_en TEXT,
            sentiment TEXT
        )
        ''')

    conn.commit()
    conn.close()

def insert_data(country: str, data: List[Dict]):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for item in data:
        cursor.execute(f'''
        INSERT INTO {country} (url, title, content, seendate, domain, language, sourcecountry, relevance_score, 
                               short_title_en, summary_en, sentiment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('url', ''),
            item.get('title', ''),
            item.get('content', ''),
            item.get('seendate', ''),
            item.get('domain', ''),
            item.get('language', ''),
            item.get('sourcecountry', ''),
            item.get('relevance_score', 0.0),
            # Removed news_body from here
            item.get('short_title_en', ''),
            item.get('summary_en', ''),
            item.get('sentiment', '')
        ))

    conn.commit()
    conn.close()

# Create the database and tables when this module is imported
create_database_and_tables()