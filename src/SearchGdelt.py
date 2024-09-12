import json
import pandas as pd
import requests
import cohere
from typing import Dict, List
from src.initialize_db import insert_data
from datetime import datetime
from fuzzywuzzy import fuzz  # Import fuzzywuzzy

class GdeltSearcher:
    def __init__(self, query_params_file: str, cohere_api_key: str):
        self.query_params = self._load_query_parameters(query_params_file)
        self.cohere_client = cohere.Client(api_key=cohere_api_key)  # Ensure the API key is properly set

    @staticmethod
    def _load_query_parameters(file_path: str) -> Dict:
        """Load query parameters from a JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def get_gdelt_query_string(self, topic: str) -> str:
        """Retrieve the GDELT query string for a given topic."""
        for t in self.query_params['topics']:
            if t['topic'] == topic:
                return t["gdelt_query_string"]
        raise ValueError(f"Topic '{topic}' not found in the query parameters.")

    @staticmethod
    def fetch_gdelt_data(gdelt_query_string: str) -> pd.DataFrame:
        """Fetch data from GDELT API and return as a DataFrame."""
        response = requests.get(gdelt_query_string)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()["articles"]
        print(f"Fetched {len(data)} articles from GDELT API")  # Debug print
        df = pd.json_normalize(data)
        
        # Drop rows with empty title
        df = df.dropna(subset=['title'])
        
        # Check if 'content' column exists, if not, create it with empty strings
        if 'content' not in df.columns:
            df['content'] = ''
        
        print(f"DataFrame columns: {df.columns}")  # Debug print
        print(f"Sample data: {df.head()}")  # Debug print
        
        return df

    @staticmethod
    def clean_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Clean the DataFrame by dropping duplicates and empty rows."""
        initial_shape = dataframe.shape[0]
        dataframe.drop_duplicates(subset=['title'], inplace=True)
        dataframe = dataframe[dataframe['title'] != '']

        # Fuzzy matching to remove near-duplicates
        threshold = 80  # Threshold for considering strings as duplicates
        rows_to_drop = set()  # Use a set to store unique indices
        for i in range(len(dataframe['title'])):
            for j in range(i + 1, len(dataframe['title'])):
                similarity_score = fuzz.ratio(dataframe['title'].iloc[i], dataframe['title'].iloc[j])
                if similarity_score >= threshold:
                    rows_to_drop.add(dataframe.index[j])  # Add the original index to the set

        dataframe.drop(index=list(rows_to_drop), inplace=True)  # Convert set to list before dropping

        after_shape = dataframe.shape[0]
        print(f"{initial_shape - after_shape} elements dropped")
        return dataframe

    def search_gdelt(self, topic: str) -> pd.DataFrame:
        """Main function to search GDELT for a specific topic and save to database."""
        gdelt_query_string = self.get_gdelt_query_string(topic)
        dataframe = self.fetch_gdelt_data(gdelt_query_string)
        cleaned_df = self.clean_dataframe(dataframe)
        
        # Rerank the documents
        docs = cleaned_df['title'].tolist()
        reranked = self.rerank_documents(topic, docs)
        
        # Create a new DataFrame with only the top 20 reranked documents
        top_20_indices = [result.index for result in reranked.results[:20]]
        top_20_df = cleaned_df.iloc[top_20_indices].copy()
        
        # Add relevance scores and current date to the DataFrame
        relevance_scores = [result.relevance_score for result in reranked.results[:20]]
        top_20_df['relevance_score'] = relevance_scores
        top_20_df['date_added'] = datetime.now().strftime('%Y-%m-%d')
        
        # Initialize new columns with empty strings (excluding news_body)
        new_columns = ['short_title_en', 'summary_en', 'sentiment']
        for col in new_columns:
            top_20_df[col] = ''
        
        # Insert new data without clearing the existing data
        data_to_insert = top_20_df.to_dict('records')
        insert_data(topic, data_to_insert)
        
        return top_20_df

    def rerank_documents(self, question_string: str, docs: List[str]) -> Dict:
        """Rerank documents using Cohere's API."""
        # Filter out empty strings or whitespace-only strings
        docs = [doc for doc in docs if doc.strip()]
        if not docs:
            return {"ranked_documents": []}
        response = self.cohere_client.rerank(
            model='rerank-multilingual-v3.0',
            query=question_string,
            documents=docs,
            top_n=min(len(docs), 20),
        )
        return response

