# 🤖 Company Profiling Bots

A modular Python application that uses Docling to extract and analyze company information from websites and public data sources.

## 📋 Overview

This project consists of two AI-powered bots designed for company profiling and data extraction:

1. **Bot 1: Website Crawler** - Crawls company websites and extracts structured data
2. **Bot 2: Company Info Aggregator** - Aggregates company data from multiple public sources

Both bots use the Docling library for document processing and extraction, with a clean Flask web dashboard for easy access.

## 🏗️ Project Structure

```
company_profiling_bots/
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration settings
├── main.py                   # CLI interface
├── app.py                    # Flask web application
├── bots/
│   ├── __init__.py
│   ├── crawler.py           # Bot 1: Website crawler
│   └── aggregator.py        # Bot 2: Info aggregator
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Logging utilities
│   └── storage.py           # JSON storage utilities
├── data/                    # Extracted data (JSON files)
├── templates/
│   ├── index.html          # Dashboard UI
│   └── results.html        # Results viewer
└── static/
    └── style.css           # Dashboard styles
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd company_profiling_bots
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Usage

#### Option 1: Web Dashboard (Recommended)

Start the Flask web application:

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

The dashboard provides:
- Form-based interface for both bots
- Real-time status updates
- Results viewer with formatted data
- List of all saved extractions

#### Option 2: Command Line Interface

**Crawl a website:**
```bash
python main.py crawl https://example.com --max-pages 30
```

**Aggregate company info:**
```bash
python main.py aggregate "Tesla" --urls https://tesla.com https://finance.yahoo.com/quote/TSLA
```

**Run both bots:**
```bash
python main.py both "Tesla" https://tesla.com --max-pages 20
```

#### Option 3: Python API

```python
from bots.crawler import crawl_company_website
from bots.aggregator import aggregate_company_info

# Crawl a website
website_data = crawl_company_website("https://example.com", max_pages=20)

# Aggregate company info
profile_data = aggregate_company_info("Tesla", urls=[
    "https://tesla.com",
    "https://finance.yahoo.com/quote/TSLA"
])
```

## 🤖 Bot Details

### Bot 1: Website Crawler

**Purpose:** Extracts structured data from company websites

**Features:**
- Respects `robots.txt` automatically
- Stays within the same domain (no external links)
- Extracts contact information (emails, phones, addresses)
- Identifies business keywords and terms
- Logs all crawled pages
- Rate-limited to avoid server overload

**Output:** JSON file with:
- List of crawled pages
- Contact information
- Business terms
- Page metadata (titles, descriptions)
- Text previews

**Configuration:**
```python
CRAWLER_CONFIG = {
    'max_pages': 50,          # Maximum pages to crawl
    'timeout': 30,            # Request timeout (seconds)
    'respect_robots': True,   # Honor robots.txt
    'user_agent': 'CompanyProfileBot/1.0',
    'delay': 1                # Delay between requests (seconds)
}
```

### Bot 2: Company Info Aggregator

**Purpose:** Aggregates company data from multiple public sources

**Supported Sources:**
- Company official website
- Yahoo Finance
- Crunchbase
- Wikipedia
- SEC filings
- BuiltWith

**Features:**
- Flexible source configuration
- Extracts key metrics (revenue, employees, funding)
- Company descriptions and summaries
- Leadership information (CEO, founders)
- Industry and market data
- Unified profile compilation

**Output:** JSON file with:
- Data from each source
- Unified company profile
- Source-specific extractions
- Metadata and timestamps

## 📊 Data Storage

All extracted data is saved to the `data/` directory as JSON files:

- **Website crawls:** `website_<domain>.json`
- **Company profiles:** `profile_<company_name>.json`

Each file includes:
- Extracted data
- Metadata (timestamp, version)
- Source information

## 🎨 Web Dashboard

The Flask web dashboard provides:

### Main Dashboard (`/`)
- Two bot control panels with forms
- Real-time extraction status
- List of all saved data files
- Quick access to results

### Results Viewer (`/results`)
- Formatted display of extracted data
- Organized sections (contacts, pages, profile)
- Interactive data tables
- Raw JSON viewer

### API Endpoints

- `POST /crawl` - Trigger website crawl
- `POST /aggregate` - Trigger info aggregation
- `GET /data/<filename>` - Retrieve saved data
- `GET /data/list` - List all data files

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Crawler settings
CRAWLER_CONFIG = {
    'max_pages': 50,
    'timeout': 30,
    'respect_robots': True,
    'user_agent': 'CompanyProfileBot/1.0',
    'delay': 1
}

# Aggregator settings
AGGREGATOR_CONFIG = {
    'timeout': 30,
    'user_agent': 'CompanyProfileBot/1.0',
}

# Source URL templates
SOURCE_TEMPLATES = {
    'yahoo_finance': 'https://finance.yahoo.com/quote/{ticker}',
    'crunchbase': 'https://www.crunchbase.com/organization/{company_slug}',
    'wikipedia': 'https://en.wikipedia.org/wiki/{company_name}',
    # Add more sources...
}
```

## 🔧 Development

### Adding New Extraction Logic

**For the crawler:**
Edit `bots/crawler.py` and modify extraction methods:
- `_extract_contacts()` - Contact information
- `_extract_business_terms()` - Business keywords
- `_extract_links()` - Page links

**For the aggregator:**
Edit `bots/aggregator.py` and add source-specific extractors:
- `_extract_wikipedia_data()`
- `_extract_yahoo_finance_data()`
- Create new methods for new sources

### Adding New Data Sources

1. Add URL template to `SOURCE_TEMPLATES` in `config.py`
2. Create extraction method in `aggregator.py`
3. Add conditional logic in `aggregate_from_urls()`

## 📝 Example Output

### Website Crawler Output
```json
{
  "base_url": "https://example.com",
  "domain": "example.com",
  "pages": [
    {
      "url": "https://example.com/about",
      "title": "About Us",
      "contacts": {"emails": ["info@example.com"]},
      "business_terms": ["innovation", "technology", "customer"]
    }
  ],
  "contacts": {
    "emails": ["info@example.com", "support@example.com"],
    "phones": ["(555) 123-4567"]
  },
  "business_terms": ["product", "service", "innovation"]
}
```

### Company Aggregator Output
```json
{
  "company_name": "Tesla",
  "sources": {
    "wikipedia": {
      "summary": "Tesla, Inc. is an American electric vehicle...",
      "founded": "July 1, 2003",
      "ceo": "Elon Musk"
    },
    "yahoo_finance": {
      "stock_price": "$242.84",
      "market_cap": "770.63B"
    }
  },
  "profile": {
    "summary": "Tesla, Inc. is an American electric vehicle...",
    "founded": "July 1, 2003",
    "ceo": "Elon Musk",
    "stock_price": "$242.84",
    "market_cap": "770.63B"
  }
}
```

## 🛡️ Best Practices

1. **Respect robots.txt** - The crawler automatically honors robots.txt files
2. **Rate limiting** - Add delays between requests to avoid overloading servers
3. **Error handling** - All operations include comprehensive error handling
4. **Logging** - Detailed logs help debug issues
5. **Data validation** - Always validate extracted data before use

## 🐛 Troubleshooting

**Issue: Crawler not finding data**
- Check if robots.txt blocks the bot
- Verify the website structure hasn't changed
- Increase timeout in config

**Issue: Aggregator returns empty results**
- Verify URLs are accessible
- Check if sites require authentication
- Some sites may block automated access

**Issue: Flask app won't start**
- Check if port 5000 is available
- Verify all dependencies are installed
- Check Flask configuration in config.py

## 📄 License

MIT License - Feel free to use and modify for your needs.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional data sources
- Enhanced extraction algorithms
- Better data cleaning and validation
- Export to different formats (CSV, Excel)
- Scheduled/automated profiling

## 📧 Support

For issues or questions, please open an issue on GitHub or contact the maintainers.

---

**Note:** This tool is for legitimate business intelligence and research purposes only. Always respect websites' terms of service and robots.txt directives.