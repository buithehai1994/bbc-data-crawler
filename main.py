from functions import FilteredArticles
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from tqdm import tqdm
import json


# RSS feed URLs
world_news = [
    'https://feeds.bbci.co.uk/news/business/rss.xml?edition=uk',
    'https://feeds.bbci.co.uk/news/education/rss.xml?edition=uk',
    'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml?edition=uk',
    'https://feeds.bbci.co.uk/news/health/rss.xml?edition=uk',
    'https://feeds.bbci.co.uk/news/technology/rss.xml?edition=uk',
    'https://feeds.bbci.co.uk/news/world/rss.xml?edition=uk',
    'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml?edition=uk'
]

# Create the main class instance
filtered_articles = FilteredArticles(world_news)

def main():
    try:
        # Fetch RSS articles
        df_articles = filtered_articles.fetch_rss_articles()

        # Fetch webpage metadata
        df_metadata = filtered_articles.fetch_webpage_metadata()

        # Filter articles published today
        dict_filtered = filtered_articles.filter_by_date()

        # Save the filtered DataFrame as a JSON file to be pushed to GitHub
        file_path = 'processed_files/bbc_articles_{}.json'.format(datetime.today().strftime('%Y-%m-%d'))
        
       # Save the filtered DataFrame as a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(dict_filtered, json_file, indent=4, ensure_ascii=False)

        print(f"DataFrame dumped to dict_filtered.json")

        return dict_filtered  # Return the dictionary

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs

if __name__ == '__main__':
    main()
