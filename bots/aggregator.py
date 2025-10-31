"""
Bot 2: Company Info Aggregator
Aggregates company information from multiple sources using Docling
"""
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
from config import AGGREGATOR_CONFIG, SOURCE_TEMPLATES
from utils.logger import setup_logger
from utils.storage import save_json

logger = setup_logger('aggregator')


class CompanyInfoAggregator:
    """Aggregates company information from multiple sources"""

    def __init__(self, company_name):
        self.company_name = company_name
        self.company_slug = company_name.lower().replace(' ', '-')
        self.data = {
            'company_name': company_name,
            'sources': {},
            'profile': {}
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': AGGREGATOR_CONFIG['user_agent']
        })

    def _fetch_url(self, url, source_name):
        """Fetch and parse URL content"""
        try:
            logger.info(f"Fetching {source_name}: {url}")

            response = self.session.get(
                url,
                timeout=AGGREGATOR_CONFIG['timeout'],
                allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            text = soup.get_text(separator=' ', strip=True)

            return soup, text

        except Exception as e:
            logger.error(f"Error fetching {source_name}: {e}")
            return None, None

    def _extract_wikipedia_data(self, soup, text):
        """Extract data from Wikipedia"""
        data = {'source': 'wikipedia'}

        try:
            # Summary (first paragraph)
            content = soup.find('div', {'id': 'mw-content-text'})
            if content:
                paragraphs = content.find_all('p', recursive=False)
                for p in paragraphs:
                    if p.get_text(strip=True):
                        data['summary'] = p.get_text(strip=True)[:1000]
                        break

            # Infobox
            infobox = soup.find('table', {'class': 'infobox'})
            if infobox:
                infobox_data = {}
                rows = infobox.find_all('tr')

                for row in rows:
                    header = row.find('th')
                    value = row.find('td')

                    if header and value:
                        key = header.get_text(strip=True).lower()
                        val = value.get_text(strip=True)
                        infobox_data[key] = val

                data['infobox'] = infobox_data

                # Extract key fields
                if 'founded' in infobox_data:
                    data['founded'] = infobox_data['founded']
                if 'founder' in infobox_data or 'founders' in infobox_data:
                    data['founders'] = infobox_data.get(
                        'founder') or infobox_data.get('founders')
                if 'industry' in infobox_data:
                    data['industry'] = infobox_data['industry']
                if 'headquarters' in infobox_data:
                    data['headquarters'] = infobox_data['headquarters']
                if 'revenue' in infobox_data:
                    data['revenue'] = infobox_data['revenue']
                if 'ceo' in infobox_data:
                    data['ceo'] = infobox_data['ceo']

            return data

        except Exception as e:
            logger.error(f"Error extracting Wikipedia data: {e}")
            return data

    def _extract_yahoo_finance_data(self, soup, text):
        """Extract data from Yahoo Finance"""
        data = {'source': 'yahoo_finance'}

        try:
            # Company name
            title = soup.find('h1')
            if title:
                data['company_full_name'] = title.get_text(strip=True)

            # Stock price and metrics
            price_elem = soup.find(
                'fin-streamer', {'data-field': 'regularMarketPrice'})
            if price_elem:
                data['stock_price'] = price_elem.get_text(strip=True)

            # Market cap
            market_cap = soup.find('fin-streamer', {'data-field': 'marketCap'})
            if market_cap:
                data['market_cap'] = market_cap.get_text(strip=True)

            # Extract key statistics using regex patterns
            stats_patterns = {
                'market_cap': r'Market Cap[:\s]+([0-9.,]+[BMK]?)',
                'pe_ratio': r'PE Ratio[:\s]+([0-9.]+)',
                'revenue': r'Revenue[:\s]+([0-9.,]+[BMK]?)',
                'employees': r'Employees[:\s]+([0-9,]+)'
            }

            for key, pattern in stats_patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[key] = match.group(1)

            # Business summary
            summary_section = soup.find(
                'section', {'data-testid': 'description'})
            if summary_section:
                data['business_summary'] = summary_section.get_text(strip=True)[
                    :1000]

            return data

        except Exception as e:
            logger.error(f"Error extracting Yahoo Finance data: {e}")
            return data

    def _extract_crunchbase_data(self, soup, text):
        """Extract data from Crunchbase"""
        data = {'source': 'crunchbase'}

        try:
            # Description
            desc_patterns = [
                r'Description[:\s]+(.{100,500})',
                r'Overview[:\s]+(.{100,500})'
            ]

            for pattern in desc_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    data['description'] = match.group(1).strip()[:500]
                    break

            # Funding
            funding_match = re.search(
                r'Total Funding Amount[:\s]+\$([0-9.,]+[BMK]?)', text, re.IGNORECASE)
            if funding_match:
                data['total_funding'] = funding_match.group(1)

            # Founded date
            founded_match = re.search(
                r'Founded Date[:\s]+([A-Za-z]+\s+\d{1,2},\s+\d{4})', text, re.IGNORECASE)
            if founded_match:
                data['founded'] = founded_match.group(1)

            # Employees
            employees_match = re.search(
                r'Number of Employees[:\s]+([0-9,\-]+)', text, re.IGNORECASE)
            if employees_match:
                data['employees'] = employees_match.group(1)

            return data

        except Exception as e:
            logger.error(f"Error extracting Crunchbase data: {e}")
            return data

    def _extract_generic_data(self, soup, text, source_name):
        """Generic extraction for any source"""
        data = {'source': source_name}

        try:
            # Title
            title = soup.find('h1')
            if title:
                data['title'] = title.get_text(strip=True)

            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and 'content' in meta_desc.attrs:
                data['description'] = meta_desc['content']

            # Extract key numbers (revenue, employees, etc.)
            numbers = {
                'revenue': r'revenue[:\s]+\$?([0-9.,]+\s*[BMK]?)',
                'employees': r'employees?[:\s]+([0-9,]+)',
                'founded': r'founded[:\s]+([0-9]{4})',
            }

            for key, pattern in numbers.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[key] = match.group(1)

            # First substantial paragraph
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text_content = p.get_text(strip=True)
                if len(text_content) > 100:
                    data['summary'] = text_content[:500]
                    break

            return data

        except Exception as e:
            logger.error(f"Error in generic extraction: {e}")
            return data
        
    def _extract_importyeti_data(self, soup, text):
        """Extract data from ImportYeti"""
        data = {'source': 'importyeti'}

        try:
            # Company description / overview
            desc_elem = soup.find('div', {'class': 'company-overview'})
            if desc_elem:
                data['description'] = desc_elem.get_text(strip=True)[:500]

            # Extract top suppliers / customers if present
            suppliers = []
            suppliers_table = soup.find('table', {'id': 'suppliers_table'})
            if suppliers_table:
                rows = suppliers_table.find_all('tr')[1:]  # skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        suppliers.append({
                            'name': cols[0].get_text(strip=True),
                            'country': cols[1].get_text(strip=True)
                        })
            if suppliers:
                data['suppliers'] = suppliers

            # Extract total transactions or shipment stats from text
            transactions_match = re.search(
                r'Total Transactions[:\s]+([0-9,]+)', text, re.IGNORECASE)
            if transactions_match:
                data['total_transactions'] = transactions_match.group(1)

            # Extract number of countries / products if available
            countries_match = re.search(
                r'Countries[:\s]+([0-9]+)', text, re.IGNORECASE)
            if countries_match:
                data['countries'] = countries_match.group(1)

            products_match = re.search(
                r'Products[:\s]+([0-9]+)', text, re.IGNORECASE)
            if products_match:
                data['products'] = products_match.group(1)

            return data

        except Exception as e:
            logger.error(f"Error extracting ImportYeti data: {e}")
            return data


    def aggregate_from_urls(self, urls):
        """Aggregate data from multiple URLs"""
        for url in urls:
            # Determine source type
            source_name = 'custom'

            if 'wikipedia.org' in url:
                source_name = 'wikipedia'
            elif 'yahoo.com' in url or 'finance.yahoo' in url:
                source_name = 'yahoo_finance'
            elif 'crunchbase.com' in url:
                source_name = 'crunchbase'
            elif 'sec.gov' in url:
                source_name = 'sec'
            elif 'builtwith.com' in url:
                source_name = 'builtwith'
            elif 'importyetti.com' in url:
                source_name = 'import_yetti'

            soup, text = self._fetch_url(url, source_name)

            if not soup:
                continue

            # Extract based on source
            if source_name == 'wikipedia':
                extracted = self._extract_wikipedia_data(soup, text)
            elif source_name == 'yahoo_finance':
                extracted = self._extract_yahoo_finance_data(soup, text)
            elif source_name == 'crunchbase':
                extracted = self._extract_crunchbase_data(soup, text)
            elif source_name == 'import_yetti':
                extracted = self._extract_importyeti_data(soup, text)
            else:
                extracted = self._extract_generic_data(soup, text, source_name)

            self.data['sources'][source_name] = extracted

        # Compile unified profile
        self._compile_profile()

        return self.data

    def _compile_profile(self):
        """Compile unified company profile from all sources"""
        profile = {}

        # Aggregate fields across sources
        fields_to_aggregate = [
            'summary', 'description', 'business_summary',
            'founded', 'founders', 'ceo', 'industry',
            'headquarters', 'revenue', 'market_cap',
            'employees', 'total_funding'
        ]

        for field in fields_to_aggregate:
            for source_name, source_data in self.data['sources'].items():
                if field in source_data and source_data[field]:
                    if field not in profile:
                        profile[field] = source_data[field]

        self.data['profile'] = profile


def aggregate_company_info(company_name, urls=None):
    """
    Main function to aggregate company information
    
    Args:
        company_name: Name of the company
        urls: List of URLs to scrape (optional, will use defaults)
    
    Returns:
        dict: Aggregated company data
    """
    aggregator = CompanyInfoAggregator(company_name)

    # Use provided URLs or generate defaults
    if not urls:
        company_slug = company_name.lower().replace(' ', '-')
        company_url = company_name.lower().replace(' ', '')

        urls = [
            f"https://{company_url}.com",
            f"https://finance.yahoo.com/quote/{company_name.upper()}",
            f"https://www.crunchbase.com/organization/{company_slug}",
            f"https://en.wikipedia.org/wiki/{quote(company_name)}",
            f"https://www.importyeti.com/company/{company_name}"
        ]

    data = aggregator.aggregate_from_urls(urls)

    # Save to file
    filename = f"profile_{company_name.lower().replace(' ', '_')}.json"
    filepath = save_json(data, filename)
    logger.info(f"Profile saved to {filepath}")

    return data


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) > 1:
        company = sys.argv[1]
    else:
        company = "Tesla"

    print(f"Aggregating info for {company}...")

    # Custom URLs for Tesla
    urls = [
        "https://www.tesla.com",
        "https://finance.yahoo.com/quote/TSLA",
        "https://www.crunchbase.com/organization/tesla-motors",
        "https://en.wikipedia.org/wiki/Tesla,_Inc.",
    ]

    data = aggregate_company_info(company, urls)
    print(f"\nAggregated from {len(data['sources'])} sources")
    print(f"Profile fields: {', '.join(data['profile'].keys())}")
