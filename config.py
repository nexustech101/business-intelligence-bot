"""
Configuration file for Company Profiling Bots
"""
import os

# Project settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Crawler settings
CRAWLER_CONFIG = {
    'max_pages': 50,
    'timeout': 30,
    'respect_robots': True,
    'user_agent': 'CompanyProfileBot/1.0',
    'delay': 1  # seconds between requests
}

# Aggregator settings
AGGREGATOR_CONFIG = {
    'timeout': 30,
    'user_agent': 'CompanyProfileBot/1.0',
}

# Source templates
SOURCE_TEMPLATES = {
    'website': '{company_url}',
    'yahoo_finance': 'https://finance.yahoo.com/quote/{ticker}',
    'crunchbase': 'https://www.crunchbase.com/organization/{company_slug}',
    'wikipedia': 'https://en.wikipedia.org/wiki/{company_name}',
    'sec': 'https://www.sec.gov/cgi-bin/browse-edgar?company={company_name}',
    'builtwith': 'https://builtwith.com/{domain}',
    'import_yetti': 'https://www.importyeti.com/company/{company_name}'
}

# Flask settings
FLASK_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}
