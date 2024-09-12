import sqlite3
import json
import aiohttp
import asyncio
from datetime import date
from typing import List, Dict
import os
import sys
import time

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
from src.config import DATABASE_PATH, OPENAI_API_KEY

async def get_summaries_from_database(country: str, target_date: date = date.today()) -> List[Dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT id, url, summary_en 
    FROM {country} 
    WHERE date(date_added) = ? AND summary_en IS NOT NULL
    GROUP BY url  -- This line deduplicates based on the url column
    """, (target_date.isoformat(),))
    results = [{"id": row[0], "url": row[1], "summary": row[2]} for row in cursor.fetchall()]
    conn.close()
    return results

async def generate_watchlist(session, country: str, summaries: List[Dict]) -> Dict:
    if not summaries:
        return {"error": "No summaries found for the given date"}

    combined_summary = " ".join([item["summary"] for item in summaries])
    urls = [item["url"] for item in summaries]

    url = "https://api.openai.com/v1/chat/completions"
    
    payload = {
        "model": "gpt-4o-mini",
        "max_tokens": 6000,
        "temperature": 0.45,
        "messages": [
            {
                "role": "user",
                "content": f"Summarize the key points from these news summaries about {country}: {combined_summary}"
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "WatchlistGenerator",
                    "description": "Generate BBC news monitoring style executive summary of the major and most important points from multiple news summaries.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "watchlist": {"type": "string", "description": "1-2 pager (3-6 paragraphs) well structured, not markdown, no lists, no numbered points, just a narrative flow executive summary. Priority order:Geopolitical, economic, and military points, local politics."}
                        },
                        "required": ["watchlist"]
                    }
                }
            }
        ]
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    async with session.post(url, json=payload, headers=headers) as response:
        result = await response.json()
        if 'choices' in result and result['choices'] and 'message' in result['choices'][0] and 'tool_calls' in result['choices'][0]['message']:
            try:
                response_text = json.loads(result['choices'][0]['message']['tool_calls'][0]['function']['arguments'])
                response_text['urls'] = urls
                return response_text
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response from OpenAI: {e}")
                response_text = {"error": "Invalid JSON response from OpenAI"}
        else:
            print(f"Unexpected response format from OpenAI: {result}")
            response_text = {"error": "Unexpected response format from OpenAI"}
    
    return response_text

async def update_watchlist_database(country: str, watchlist_data: Dict, target_date: date = date.today()):
    if 'error' in watchlist_data:
        print(f"Skipping database update for {country} due to error in watchlist data")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create watchlist table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        date_added DATE NOT NULL,
        watchlist TEXT NOT NULL,
        urls_used TEXT NOT NULL
    )
    ''')

    # Insert or update the watchlist for the given country and date
    cursor.execute('''
    INSERT OR REPLACE INTO watchlist (country, date_added, watchlist, urls_used)
    VALUES (?, ?, ?, ?)
    ''', (
        country,
        target_date.isoformat(),
        watchlist_data.get('watchlist', ''),
        json.dumps(watchlist_data.get('urls', []))
    ))

    conn.commit()
    conn.close()
    print(f"Updated watchlist for {country} on {target_date}")

async def generate_and_store_watchlist(country: str, target_date: date = date.today()):
    async with aiohttp.ClientSession() as session:
        summaries = await get_summaries_from_database(country, target_date)
        if summaries:
            watchlist_data = await generate_watchlist(session, country, summaries)
            await update_watchlist_database(country, watchlist_data, target_date)
        else:
            print(f"No summaries found for {country} on {target_date}")

async def run_watchlist_generator(countries: List[str], target_date: date = date.today()):
    tasks = [generate_and_store_watchlist(country, target_date) for country in countries]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    countries = ['Climate', 'UK', 'China', 'Russia_Ukraine', 'Israel_Palestine', 'USA', 'Turkey', 'Germany', 'France', 'NATO']
    asyncio.run(run_watchlist_generator(countries))
