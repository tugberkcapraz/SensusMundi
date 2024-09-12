import os
import sys
import asyncio
import json
import newspaper

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.SearchGdelt import GdeltSearcher
from src.ScrapeNews import run_news_scraper
from src.GetWatchlist import run_watchlist_generator
from src.config import QUERY_PARAMS_PATH, COHERE_API_KEY

async def run_end_to_end_test(country: str):
    print(f"Starting end-to-end test for country: {country}")
    print(f"QUERY_PARAMS_PATH: {QUERY_PARAMS_PATH}")
    print(f"File exists: {os.path.exists(QUERY_PARAMS_PATH)}")
    
    # Step 1: GDELT Search
    searcher = GdeltSearcher(QUERY_PARAMS_PATH, COHERE_API_KEY)
    topic = next((t for t in searcher.query_params['topics'] if t['topic'] == country), None)
    
    if topic:
        print(f"Step 1: Updating data for topic: {topic['topic']}")
        searcher.search_gdelt(topic['topic'])
        print("GDELT search completed successfully.")
        
        # Step 2: News Scraping and Summarization
        print("Step 2: Starting news scraping and summarization process...")
        await run_news_scraper(country)
        print("News scraping and summarization completed successfully.")
        
        # Step 3: Watchlist Generation
        print("Step 3: Generating watchlist...")
        await run_watchlist_generator([country])
        print("Watchlist generation completed successfully.")
        
        print(f"End-to-end test for {country} completed successfully.")
    else:
        print(f"Error: No topic found for country: {country}")

if __name__ == "__main__":
    countries = ['Climate', 'UK', 'China', 'Russia_Ukraine', 'Israel_Palestine', 'USA', 'Turkey', 'Germany', 'France', 'NATO']

    async def main():
        for country in countries:
            await run_end_to_end_test(country)

    asyncio.run(main())