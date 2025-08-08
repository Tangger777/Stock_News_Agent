import os
from datetime import datetime, timedelta
from . import database
from .llm_service import LLMService

class NewsProcessor:
    def __init__(self):
        self.llm_service = LLMService()
        database.init_db() # Ensure database is initialized when processor is created

    def process_and_summarize_news(self, news_data):
        """
        Processes raw news data: saves to DB and then summarizes new entries.
        news_data is expected to be a dictionary with 'symbol' and 'news' list.
        """
        symbol = news_data.get('symbol', 'UNKNOWN')
        news_items_for_db = []
        for item in news_data.get('news', []):
            # Add symbol to each news item for database storage
            item['symbol'] = symbol
            news_items_for_db.append(item)
        
        if news_items_for_db:
            database.save_news(news_items_for_db)
        else:
            print("No news items to save.")

        # Summarize unsmarized news
        unsmarized_news = database.get_unsmarized_news()
        if unsmarized_news:
            print(f"Found {len(unsmarized_news)} news items to summarize.")
            for news_item in unsmarized_news:
                summary = self.llm_service.summarize_text(news_item['content'])
                database.update_news_summary(news_item['id'], summary)
        else:
            print("No new news items to summarize.")

    def create_daily_report(self, target_date_str: str, symbol: str = None) -> str:
        """
        Generates a daily news report for a specific date and optional symbol.
        target_date_str should be in 'YYYY-MM-DD' format.
        """
        print(f"Generating daily report for {target_date_str} (Symbol: {symbol if symbol else 'All'})")
        news_summaries = database.get_news_by_date_range(target_date_str, target_date_str, symbol)

        if not news_summaries:
            return f"No news summaries found for {target_date_str} (Symbol: {symbol if symbol else 'All'}) to generate a report."
        
        report = self.llm_service.generate_daily_report(news_summaries)
        return report

if __name__ == '__main__':
    # This part is for testing the NewsProcessor functionalities.
    # In a real scenario, fetch_html_content would call this.
    
    processor = NewsProcessor()

    # Example: Simulate fetching news and processing it
    # You would replace this with actual data from fetch_html_content.py
    sample_news_data = {
        "symbol": "AAPL",
        "news": [
            {
                "title": "Apple Q3 Earnings Beat Estimates",
                "source": "Reuters",
                "published": "2025-08-02 10:00:00 UTC",
                "link": "http://example.com/aapl-news-1",
                "content": "Apple Inc. today announced its third-quarter earnings, surpassing analyst expectations with strong iPhone sales and growth in its services division. The company's stock saw a significant rise in after-hours trading. CEO Tim Cook highlighted the continued demand for premium devices and the expanding ecosystem of Apple services."
            },
            {
                "title": "New iPhone Model Leaked",
                "source": "TechCrunch",
                "published": "2025-08-02 11:30:00 UTC",
                "link": "http://example.com/aapl-news-2",
                "content": "Images of what appears to be the next iPhone model have been leaked online, showing a redesigned camera array and a smaller notch. While Apple has not commented, analysts believe the new design could boost sales in the upcoming holiday season."
            },
            {
                "title": "Google Announces AI Breakthrough",
                "source": "Bloomberg",
                "published": "2025-08-02 12:00:00 UTC",
                "link": "http://example.com/goog-news-1",
                "content": "Google's AI division unveiled a new breakthrough in natural language processing, promising more human-like interactions with AI assistants. This development is expected to have wide-ranging implications across various industries."
            }
        ]
    }
    
    print("\n--- Processing and Summarizing News ---")
    processor.process_and_summarize_news(sample_news_data)

    # Example: Generate a daily report
    print("\n--- Generating Daily Report for AAPL ---")
    report_aapl = processor.create_daily_report('2025-08-02', 'AAPL')
    print(report_aapl)

    print("\n--- Generating Daily Report for All Symbols ---")
    report_all = processor.create_daily_report('2025-08-02')
    print(report_all)
