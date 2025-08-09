# Stock News Agent

An intelligent stock news fetching, processing, and analysis system that scrapes news data from TradingView, automatically summarizes content using LLM, and generates daily reports.

## Features

- 🔍 **News Fetching**: Retrieve news for specific stocks and dates from TradingView
- 🤖 **AI Summarization**: Automatically summarize news content using LLM
- 📊 **Data Storage**: Store news and summaries in SQLite database
- 📝 **Daily Reports**: Generate automated news analysis reports for specified dates
- 📓 **Jupyter Support**: Interactive notebook environment for analysis

## Project Structure

```
├── main.ipynb             # Jupyter notebook main file
├── config.yaml.template   # Configuration template
├── utils/                 # Utility modules
│   ├── fetch_html_content.py  # News fetching
│   ├── news_processor.py      # News processing
│   ├── llm_service.py         # LLM service
│   └── database.py            # Database operations
└── news_data.db           # SQLite database
```

## Quick Start

### 1. Configuration Setup

```bash
# Copy configuration template
cp config.yaml.template config.yaml
```

Edit `config.yaml` to add your TradingView cookie:
- Visit tradingview.com
- Open Developer Tools (F12) → Network tab
- Refresh the page and copy the complete Cookie value from any request

### 2. Install Dependencies

```bash
pip install requests beautifulsoup4 pyyaml sqlite3
```

### 3. Run the Program

**Jupyter Notebook:**
```bash
jupyter notebook main.ipynb
```

## Usage Example

```python
from utils.fetch_html_content import fetch_tradingview_news
from utils.news_processor import NewsProcessor

# Initialize processor
processor = NewsProcessor()

# Fetch news data
news_data = fetch_tradingview_news('GOOGL', target_date='2025-08-08', window=1)

# Process and summarize news
processor.process_and_summarize_news(news_data)

# Generate daily report
daily_report = processor.create_daily_report('2025-08-08', 'GOOGL')
print(daily_report)
```

## Configuration Parameters

- `default_symbol`: Default stock symbol (e.g., GOOGL, TSLA)
- `default_date`: Default query date (YYYY-MM-DD)
- `window_days`: Query time window (days)

## Important Notes

- Cookies may expire and need periodic updates
- Recommended to run the project in a virtual environment
