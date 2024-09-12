import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_NAME = 'news4u.db'
DATABASE_PATH = os.path.join(BASE_DIR, 'src', DATABASE_NAME)
QUERY_PARAMS_PATH = os.path.join(BASE_DIR, 'src', 'query_parameters.json')
COHERE_API_KEY = 'YOUR COHERE API KEY'
OPENAI_API_KEY = 'YOUR OPENAI API KEY'

print(f"Looking for query_parameters.json at: {QUERY_PARAMS_PATH}")
print(f"Current working directory: {os.getcwd()}")