import sqlite3
import json
import asyncio
import aiohttp
import time
import os
from newspaper import Article
from newspaper.article import ArticleException
from src.config import DATABASE_PATH, OPENAI_API_KEY
from typing import List, Dict

async def get_urls_from_database(country: str) -> List[Dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, url FROM {country} WHERE news_body IS NULL")
    results = [{"id": row[0], "url": row[1]} for row in cursor.fetchall()]
    conn.close()
    print(f"Found {len(results)} articles to process for {country}")  # Debug print
    return results

def scrape_article(url: str) -> str:
    article = Article(url)
    article.download()  # Remove the timeout parameter
    article.parse()
    return article.text

async def get_completion(session, article_text: str, topic: str) -> Dict:
    topic_params_path = os.path.join(os.path.dirname(__file__), 'topic_params.json')
    with open(topic_params_path) as f:
        data = json.load(f)
    
    prompt = None
    for t in data['topics']:
        if t['topic'] == topic:
            prompt = t["prompt"]
            topic_name = t["topic_name"]
            break

    if prompt is None:
        raise ValueError(f"Topic '{topic}' not found in the JSON data.")
    
    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": "gpt-4o-mini",
        "max_tokens": 700,
        "temperature": 0.7,
        "messages": [
            {
                "role": "user",
                "content": f"""You receive news articles. They are centered around the {topic_name}. Your task is to summarise: {article_text}."""
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "Summarizer",
                    "description": "You are a news summariser in english. Your summaries should directly address the key points of the news article. Just write the summary. No need for intro sentences like 'this article talks about...'. You are summarising as if you write that news article. Not as a third person.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "short_title_en": {"type": "string", "description": "short title in english"},
                            "summary_en": {"type": "string", "description": "4-5 sentence summary in english"},
                            "sentiment": {"type": "string", "description": "sentiment of the news summary (positive, negative, or neutral)"}
                        },
                        "required": ["short_title_en", "summary_en", "sentiment"]
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
    
    start = time.time()
    async with session.post(url, json=payload, headers=headers) as response:
        result = await response.json()
        if 'choices' in result and result['choices'] and 'message' in result['choices'][0] and 'tool_calls' in result['choices'][0]['message']:
            try:
                response_text = json.loads(result['choices'][0]['message']['tool_calls'][0]['function']['arguments'])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response from OpenAI: {e}")
                response_text = {"error": "Invalid JSON response from OpenAI"}
        else:
            print(f"Unexpected response format from OpenAI: {result}")
            response_text = {"error": "Unexpected response format from OpenAI"}
    end = time.time()
    
    print(f"Time taken: {end-start} seconds")
    
    return response_text

async def update_database(country: str, article_id: int, news_body: str, summaries: Dict):
    if not summaries or 'error' in summaries:
        print(f"Skipping database update for article {article_id} in {country} due to empty or error in summaries")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
    UPDATE {country}
    SET news_body = ?, 
        short_title_en = ?, 
        summary_en = ?, 
        sentiment = ?
    WHERE id = ?
    """, (
        news_body, 
        summaries.get('short_title_en', ''), 
        summaries.get('summary_en', ''),
        summaries.get('sentiment', ''),
        article_id
    ))
    conn.commit()
    conn.close()
    print(f"Updated database for article {article_id} in {country}")

async def process_article(session, country: str, article: Dict):
    try:
        print(f"Processing article {article['id']} for {country}")  # Debug print
        news_body = scrape_article(article['url'])
        summaries = await get_completion(session, news_body, country)
        await update_database(country, article['id'], news_body, summaries)
        print(f"Processed article {article['id']} for {country}")
    except ArticleException as e:
        print(f"ArticleException for article {article['id']} in {country}: {str(e)}")
    except aiohttp.ClientError as e:
        print(f"Network error for article {article['id']} in {country}: {str(e)}")
    except sqlite3.Error as e:
        print(f"Database error for article {article['id']} in {country}: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON decoding error for article {article['id']} in {country}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error processing article {article['id']} for {country}: {str(e)}")
        print(f"Error type: {type(e).__name__}")

async def process_articles(country: str):
    articles = await get_urls_from_database(country)
    if articles:  # Check if there are any articles to process
        async with aiohttp.ClientSession() as session:
            tasks = [process_article(session, country, article) for article in articles]
            await asyncio.gather(*tasks)
    else:
        print(f"No articles found to process for {country}")

async def run_news_scraper(country: str):
    async with aiohttp.ClientSession() as session:
        await process_articles(country)
        print(f"Completed processing for {country}")

if __name__ == "__main__":
    # For testing purposes, you can still run it for all countries if needed
    countries = ['Climate', 'UK', 'China', 'Russia_Ukraine', 'Israel_Palestine', 'USA', 'Turkey', 'Germany', 'France', 'NATO']
    for country in countries:
        asyncio.run(run_news_scraper(country))


