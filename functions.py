import pandas as pd
import pytz
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
import json

def get_source_name(url):
    domain = urlparse(url).netloc
    source = domain.replace('www.', '').split('.')[0]
    return source

def parser_items_rss(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')
    source = get_source_name(url)

    lista_items = []
    for item in items:
        row = {
            "title": item.find('title').text if item.find('title') else None,
            "description": item.find('description').text if item.find('description') else None,
            "url": item.find('link').text if item.find('link') else None,
            "pubDate": item.find('pubDate').text if item.find('pubDate') else None,
            "source": source
        }
        lista_items.append(row)

    return lista_items

class WebPageExtractor:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.json_data = None

    def fetch_page(self):
        """Fetches the web page content and initializes BeautifulSoup."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            self.soup = BeautifulSoup(response.content, 'html.parser')
            print("Page fetched successfully.")
        except requests.RequestException as e:
            print(f"Failed to fetch page: {e}")
            self.soup = None

    def extract_json_metadata(self):
        """Extracts JSON metadata from the <script> tag with type 'application/ld+json'."""
        if self.soup:
            script_tag = self.soup.find('script', type='application/ld+json')
            if script_tag:
                try:
                    self.json_data = json.loads(script_tag.string)
                    print("JSON metadata extracted successfully.")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON metadata: {e}")
                    self.json_data = None
            else:
                print("No JSON metadata found.")
        else:
            print("Soup object not initialized. Call fetch_page() first.")

    def extract_author(self):
        """Extracts author(s) from the JSON metadata."""
        if self.json_data:
            author_info = self.json_data.get("author", None)
            if author_info:
                if isinstance(author_info, list):
                    authors = [author.get("name", "Unknown") for author in author_info]
                else:
                    authors = [author_info.get("name", "Unknown")]
                return authors
            else:
                return "No author information found."
        return "No JSON metadata found."

    def extract_date(self):
        """Extracts the publication date from the JSON metadata."""
        if self.json_data:
            return self.json_data.get("datePublished", "No publication date found.")
        return "No JSON metadata found."

    def extract_headline(self):
        """Extracts the headline from the JSON metadata."""
        if self.json_data:
            return self.json_data.get("headline", "No headline found.")
        return "No JSON metadata found."

    def extract_content(self):
        """Extracts the article content from <p> tags."""
        if self.soup:
            paragraphs = self.soup.find_all('p')
            article_content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            return article_content if article_content else "No content found."
        return "Soup object not initialized. Call fetch_page() first."
