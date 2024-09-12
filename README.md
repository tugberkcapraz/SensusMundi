# SensusMundi: AI-Powered News Monitoring

**SensusMundi** is an alpha-phase project aimed at democratizing access to global political and geopolitical information through AI-powered insights. We provide daily reports that keep you informed on world events, saving you valuable time and effort.

## Features

- **Comprehensive Scanning:** Daily analysis of over 2,500 articles on key topics and countries.
- **Smart Topic Selection:** Custom algorithm identifies the most relevant and important topics.
- **Near-Deduplication:** Filters out similar topics for a concise, non-redundant experience.
- **GPT-4o-mini for Summarization:** Utilizes advanced AI to generate insightful summaries.
- **Watchlist Formatting:** Compiles summaries into a comprehensive daily watchlist.

## How it Works

SensusMundi employs a multi-step process to deliver clear, concise, and insightful overviews of daily global events:

1. **GDELT Search:** We leverage the GDELT Project's API to identify relevant articles based on predefined queries for each topic and country.
2. **News Scraping:** We scrape the full text of the identified articles using the `newspaper3k` library.
3. **Summarization:** We utilize GPT-4o-mini to generate concise and informative summaries of each article.
4. **Watchlist Generation:** We compile the summaries into a daily watchlist, organized by topic and country.

## Technologies Used

- **Python:** Core backend logic, data processing, and API interaction.
- **FastAPI:** Web framework for building the API.(Will be used in the deployment phase)
- **GDELT Project:** Global database of events, used for identifying relevant articles.
- **Newspaper3k:** Python library for scraping news articles.
- **Cohere:** AI platform for text summarization.
- **OpenAI:** AI platform for text summarization.
- **SQLite:** Database for storing news articles and summaries.(will not be used in the deployment phase)
- **JavaScript:** Frontend development and particle.js integration.
- **HTML/CSS:** Webpage structure and styling.

## Getting Started

**Prerequisites:**

- Python 3.8 or higher

**Installation:**

1. Clone the repository:
   ```bash
   git clone https://github.com/tugberkcapraz/news_monitoring_website.git
   ```
2. Navigate to the project directory:
   ```bash
   cd news_monitoring_website
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
4. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
6. Configure the API keys:
   - Create a file named `.env` in the `src` directory.
   - Use the `config_example.py` file as a template and add the following lines, replacing the placeholders with your actual API keys:
     ```
     COHERE_API_KEY=your_cohere_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```
7. Create the database:
   ```bash
   python src/initialize_db.py

8. Run the daily update script:
   ```bash
   python src/daily_update.py
   ```

## Usage

Once the webapp is completed, daily reports will be accessible on the website.

## Future Development

- **Enhanced Topic Coverage:** Expand the range of topics and countries covered.
- **User Customization:** Allow users to define their own topics and queries.
- **Sentiment Analysis:** Integrate sentiment analysis to provide insights into the tone of news articles.
- **Multilingual Support:** Expand support for languages other than English.
- **Improved User Interface:** Enhance the web interface with more interactive features and visualizations.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License

This project is licensed under the MIT License.
