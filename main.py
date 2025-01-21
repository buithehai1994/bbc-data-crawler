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
        df_filtered = filtered_articles.filter_by_date()

        if df_filtered.empty:
            print("No articles found for today")
            return None  # Return None if no articles are found

        # Convert DataFrame to a dictionary where each key is the row index and the value is the article details
        articles_dict = df_filtered.to_dict(orient='index')  # Convert DataFrame to dictionary

        # Save the dictionary as a JSON file
        json_filename = 'processed_files/bbc_articles_{}.json'.format(datetime.today().strftime('%Y-%m-%d'))
        with open(json_filename, 'w') as json_file:
            json.dump(articles_dict, json_file, indent=4)  # Save the dictionary to a JSON file

        print(f"DataFrame dumped to filtered_articles.json")

        return articles_dict  # Return the dictionary of articles

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs

if __name__ == '__main__':
    main()
