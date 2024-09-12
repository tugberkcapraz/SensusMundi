import unittest
import pandas as pd
from src.SearchGdelt import GdeltSearcher
import os
import json

class TestGdeltSearcher(unittest.TestCase):

    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        query_params_path = os.path.join(project_root, 'app/query_parameters.json')
        self.searcher = GdeltSearcher(query_params_path, 'YOUR_COHERE_API_KEY')

    def test_load_query_parameters(self):
        self.assertIsInstance(self.searcher.query_params, dict)
        self.assertIn('topics', self.searcher.query_params)

    def test_get_gdelt_query_string(self):
        for topic in self.searcher.query_params['topics']:
            query_string = self.searcher.get_gdelt_query_string(topic['topic'])
            self.assertEqual(query_string, topic['gdelt_query_string'])

    def test_search_gdelt(self):
        for topic in self.searcher.query_params['topics']:
            with self.subTest(topic=topic['topic']):
                result = self.searcher.search_gdelt(topic['topic'])
                self.assertIsInstance(result, pd.DataFrame)
                self.assertGreater(len(result), 0)
                self.assertIn('title', result.columns)
                self.assertIn('content', result.columns)
                # Check for other expected columns
                expected_columns = ['url', 'url_mobile', 'title', 'seendate', 'socialimage', 'domain', 'language', 'sourcecountry']
                for col in expected_columns:
                    if col not in result.columns:
                        print(f"Warning: Expected column '{col}' not found in result for topic '{topic['topic']}'")

    def test_rerank_documents(self):
        topic = self.searcher.query_params['topics'][0]
        df = self.searcher.search_gdelt(topic['topic'])
        documents = df['content'].tolist()[:10]  # Use the first 10 documents for testing
        query = topic['question_string']

        result = self.searcher.rerank_documents(query, documents)

        self.assertIsInstance(result, dict)
        self.assertIn('ranked_documents', result)
        self.assertLessEqual(len(result['ranked_documents']), min(len(documents), 30))

    def test_invalid_topic(self):
        with self.assertRaises(ValueError):
            self.searcher.search_gdelt("InvalidTopic")

if __name__ == '__main__':
    unittest.main()