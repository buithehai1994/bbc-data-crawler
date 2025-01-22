import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from tqdm import tqdm
import json

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

class RSSFeedExtractor:
    def __init__(self, rss_urls):
        self.rss_urls = rss_urls
        self.df = None

    def get_source_name(self, url):
        domain = urlparse(url).netloc
        source = domain.replace('www.', '').split('.')[0]
        return source

    def parser_items_rss(self, url, category):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        source = self.get_source_name(url)

        lista_items = []
        for item in items:
            row = {
                "title": item.find('title').text if item.find('title') else None,
                "description": item.find('description').text if item.find('description') else None,
                "url": item.find('link').text if item.find('link') else None,
                "pubDate": item.find('pubDate').text if item.find('pubDate') else None,
                "source": source,
                "category": category  # Add the category from the dictionary
            }
            lista_items.append(row)

        return lista_items

    def fetch_rss_feeds(self):
        datos = []
        for category, url in self.rss_urls.items():
            datos.extend(self.parser_items_rss(url, category))
        
        self.df = pd.DataFrame(datos)
        self.df = self.df.drop(['pubDate'], axis=1)
        self.df["type"] = self.df["url"].str.extract(r"https://www\.bbc\.com/news/([^/]+)/")
        self.df = self.df[self.df['type'] == 'articles']
        return self.df

class WebPageMetadataExtractor:
    def __init__(self, df):
        self.df = df

    def extract_webpage_info(self, row):
        url = row['url']
        extractor = WebPageExtractor(url)
        
        # Fetch page and extract metadata
        try:
            extractor.fetch_page()
            extractor.extract_json_metadata()
            return {
                'Author': extractor.extract_author(),
                'Date Published': extractor.extract_date(),
                'Headline': extractor.extract_headline(),
                'Content': extractor.extract_content(),
            }
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            return {
                'Author': None,
                'Date Published': None,
                'Headline': None,
                'Content': None,
            }

    def fetch_webpage_metadata(self):
        # Use tqdm for progress bar during extraction
        tqdm.pandas()
        extracted_data = self.df.progress_apply(self.extract_webpage_info, axis=1, result_type='expand')
        return pd.concat([self.df, extracted_data], axis=1)

class FilteredArticles:
    def __init__(self, rss_urls):
        self.rss_extractor = RSSFeedExtractor(rss_urls)
        self.metadata_extractor = None
        self.df = None

    def fetch_rss_articles(self):
        # Fetch RSS feeds and parse items
        self.df = self.rss_extractor.fetch_rss_feeds()
        return self.df

    def fetch_webpage_metadata(self):
        # Fetch metadata for the articles fetched from RSS
        self.metadata_extractor = WebPageMetadataExtractor(self.df)
        self.df = self.metadata_extractor.fetch_webpage_metadata()
        return self.df

    def filter_by_date(self):
        # Convert the "Date Published" column to datetime
        self.df['Date Published'] = pd.to_datetime(self.df['Date Published'])

        # Get today's date
        today = datetime.now().date()

        # Filter articles published today
        filtered_df = self.df[self.df['Date Published'].dt.date == today]
        return filtered_df

    @staticmethod
    def convert_to_json(df, file_path):
        """
        Save the dataframe as a JSON file.
        :param file_path: Path to the output JSON file.
        """
        try:
            # Convert dataframe to dictionary
            data_dict = df.to_dict(orient='records')
            
            # Ensure Timestamp objects are converted to strings
            for record in data_dict:
                if 'Date Published' in record:
                    record['Date Published'] = record['Date Published'].strftime('%Y-%m-%d %H:%M:%S')
    
            # Save the dictionary as a JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)
    
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"Failed to save data as JSON: {e}")
