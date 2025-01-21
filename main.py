from functions import FilteredArticles

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

# Fetch RSS articles
df_articles = filtered_articles.fetch_rss_articles()

# Fetch webpage metadata
df_metadata = filtered_articles.fetch_webpage_metadata()

# Filter articles published today
df_filtered = filtered_articles.filter_by_date()

# Save the filtered DataFrame as a CSV or other formats to be pushed to GitHub
df_filtered.to_csv('filtered_articles.csv', index=False)

print(f"DataFrame dumped to filtered_articles")
