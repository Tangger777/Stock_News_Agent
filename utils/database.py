import sqlite3
from datetime import datetime

DATABASE_FILE = 'news_data.db' # This will be configurable in config.yaml later

def init_db():
    """
    Initializes the SQLite database and creates the news table if it doesn't exist.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            summary TEXT,
            link TEXT UNIQUE NOT NULL,
            source TEXT,
            published_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized and table 'news' ensured in {DATABASE_FILE}")

def save_news(news_items):
    """
    Saves a list of news items into the database.
    Skips items if their link already exists to prevent duplicates.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    saved_count = 0
    for item in news_items:
        try:
            cursor.execute('''
                INSERT INTO news (symbol, title, content, link, source, published_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item.get('symbol'),
                item.get('title'),
                item.get('content'),
                item.get('link'),
                item.get('source'),
                item.get('published')
            ))
            saved_count += 1
        except sqlite3.IntegrityError:
            print(f"Skipping duplicate news: {item.get('title')} (Link: {item.get('link')})")
        except Exception as e:
            print(f"Error saving news item {item.get('title')}: {e}")
    conn.commit()
    conn.close()
    print(f"Saved {saved_count} new news items to the database.")

def get_unsmarized_news():
    """
    Retrieves news items that do not have a summary yet.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content FROM news WHERE summary IS NULL OR summary = ""')
    news_to_summarize = []
    for row in cursor.fetchall():
        news_to_summarize.append({
            'id': row[0],
            'title': row[1],
            'content': row[2]
        })
    conn.close()
    return news_to_summarize

def update_news_summary(news_id, summary):
    """
    Updates the summary for a specific news item by its ID.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE news SET summary = ? WHERE id = ?', (summary, news_id))
    conn.commit()
    conn.close()
    print(f"Updated summary for news ID: {news_id}")

def get_news_by_date_range(start_date_str, end_date_str, symbol=None):
    """
    Retrieves news items (with summaries) within a specified date range for a given symbol.
    Dates should be in 'YYYY-MM-DD' format.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    query = 'SELECT title, summary, published_at, link FROM news WHERE published_at BETWEEN ? AND ?'
    params = (f"{start_date_str} 00:00:00 UTC", f"{end_date_str} 23:59:59 UTC")
    
    if symbol:
        query += ' AND symbol = ?'
        params += (symbol,)
        
    cursor.execute(query, params)
    
    news_summaries = []
    for row in cursor.fetchall():
        news_summaries.append({
            'title': row[0],
            'summary': row[1],
#            'published_at': row[2],
#            'link': row[3]
        })
    conn.close()
    return news_summaries

if __name__ == '__main__':
    init_db()
    # Example usage (for testing purposes)
    # save_news([
    #     {'symbol': 'TEST', 'title': 'Test News 1', 'content': 'Content 1', 'link': 'http://example.com/1', 'source': 'Test', 'published': '2025-08-01 10:00:00 UTC'},
    #     {'symbol': 'TEST', 'title': 'Test News 2', 'content': 'Content 2', 'link': 'http://example.com/2', 'source': 'Test', 'published': '2025-08-01 11:00:00 UTC'}
    # ])
    # news = get_unsmarized_news()
    # print(f"Unsummarized news: {news}")
    # if news:
    #     update_news_summary(news[0]['id'], "This is a test summary.")
    #     print(get_news_by_date_range('2025-08-01', '2025-08-01', 'TEST'))
