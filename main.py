from functions import WebPageExtractor, RSSFeedExtractor, WebPageMetadataExtractor, FilteredArticles
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, timedelta
from tqdm import tqdm
import json


# RSS feed URLs
dict_news = {
    "business": 'https://feeds.bbci.co.uk/news/business/rss.xml?edition=uk',
    "education": 'https://feeds.bbci.co.uk/news/education/rss.xml?edition=uk',
    "entertainment_and_arts": 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml?edition=uk',
    "health": 'https://feeds.bbci.co.uk/news/health/rss.xml?edition=uk',
    "technology": 'https://feeds.bbci.co.uk/news/technology/rss.xml?edition=uk',
    "world": 'https://feeds.bbci.co.uk/news/world/rss.xml?edition=uk',
    "science_and_environment": 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml?edition=uk'
}

# Create the main class instance with correct RSS URLs
filtered_articles = FilteredArticles(list(dict_news.values()))

def main():
    try:
       # Fetch RSS articles
        df_articles = filtered_articles.fetch_rss_articles()
        
        # Fetch webpage metadata
        df_metadata = filtered_articles.fetch_webpage_metadata()
        
        # Filter articles published yesterday
        df_filtered = filtered_articles.filter_by_date()

        # Save the filtered DataFrame as a JSON file to be pushed to GitHub
        file_path = f'processed_files/bbc_articles_{yesterday}.json'
        result_dict = filtered_articles.convert_to_json(df_filtered, file_path)
        
        return result_dict  # Return the dictionary

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs

if __name__ == '__main__':
    main()
