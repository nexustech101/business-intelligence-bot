"""
Bot 1: Website Crawler
Crawls company websites and extracts structured data using Docling
"""
import requests
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from config import CRAWLER_CONFIG
from utils.logger import setup_logger
from utils.storage import save_json

logger = setup_logger('crawler')


class WebsiteCrawler:
    """Crawls a company website and extracts structured data"""

    def __init__(self, base_url, max_pages=None):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages or CRAWLER_CONFIG['max_pages']
        self.visited = set()
        self.to_visit = [base_url]
        self.data = {
            'base_url': base_url,
            'domain': self.domain,
            'pages': [],
            'contacts': {},
            'business_terms': []
        }
        self.robots_parser = self._setup_robots_parser()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CRAWLER_CONFIG['user_agent']
        })

    def _setup_robots_parser(self):
        """Setup robots.txt parser"""
        if not CRAWLER_CONFIG['respect_robots']:
            return None

        parser = RobotFileParser()
        robots_url = urljoin(self.base_url, '/robots.txt')

        try:
            parser.set_url(robots_url)
            parser.read()
            logger.info(f"Loaded robots.txt from {robots_url}")
            return parser
        except Exception as e:
            logger.warning(f"Could not load robots.txt: {e}")
            return None

    def _can_fetch(self, url):
        """Check if URL can be fetched according to robots.txt"""
        if not self.robots_parser:
            return True

        return self.robots_parser.can_fetch(CRAWLER_CONFIG['user_agent'], url)

    def _is_same_domain(self, url):
        """Check if URL belongs to the same domain"""
        return urlparse(url).netloc == self.domain

    def _extract_links(self, soup, current_url):
        """Extract internal links from page"""
        links = []

        for link in soup.find_all('a', href=True):
            url = urljoin(current_url, link['href'])

            # Only include same-domain HTTP(S) links
            if (self._is_same_domain(url) and
                url not in self.visited and
                    url.startswith('http')):
                links.append(url)

        return links

    def _extract_contacts(self, soup, text):
        """Extract contact information"""
        contacts = {}

        # Email patterns
        import re
        emails = re.findall(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            contacts['emails'] = list(set(emails))

        # Phone patterns
        phones = re.findall(
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b', text)
        if phones:
            contacts['phones'] = [f"({p[0]}) {p[1]}-{p[2]}" for p in phones]

        # Address (simple heuristic)
        address_keywords = ['address', 'headquarters', 'office', 'location']
        for keyword in address_keywords:
            elem = soup.find(string=re.compile(keyword, re.IGNORECASE))
            if elem:
                parent = elem.find_parent(['p', 'div', 'span'])
                if parent:
                    contacts[keyword] = parent.get_text(strip=True)[:200]

        return contacts

    def _extract_business_terms(self, text):
        """Extract key business terms and keywords"""
        # Common business keywords
        business_keywords = [
            'product', 'service', 'solution', 'technology', 'platform',
            'mission', 'vision', 'value', 'innovation', 'customer',
            'industry', 'market', 'enterprise', 'cloud', 'software',
            'data', 'analytics', 'AI', 'machine learning', 'automation'
        ]

        text_lower = text.lower()
        found_terms = [
            term for term in business_keywords if term in text_lower]

        return list(set(found_terms))

    def _crawl_page(self, url):
        """Crawl a single page"""
        try:
            # Check robots.txt
            if not self._can_fetch(url):
                logger.info(f"Skipping {url} (blocked by robots.txt)")
                return None

            logger.info(f"Crawling: {url}")

            # Fetch page
            response = self.session.get(
                url,
                timeout=CRAWLER_CONFIG['timeout'],
                allow_redirects=True
            )
            response.raise_for_status()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')

            # Extract text
            text = soup.get_text(separator=' ', strip=True)

            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ''

            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc and 'content' in meta_desc.attrs else ''

            # Extract contacts
            contacts = self._extract_contacts(soup, text)

            # Extract business terms
            terms = self._extract_business_terms(text)

            # Store page data
            page_data = {
                'url': url,
                'title': title_text,
                'description': description,
                'text_length': len(text),
                'text_preview': text[:500],
                'contacts': contacts,
                'business_terms': terms
            }

            # Extract internal links
            links = self._extract_links(soup, url)

            # Add contacts to global contacts
            for key, value in contacts.items():
                if key not in self.data['contacts']:
                    self.data['contacts'][key] = []
                if isinstance(value, list):
                    self.data['contacts'][key].extend(value)
                else:
                    self.data['contacts'][key].append(value)

            # Add business terms
            self.data['business_terms'].extend(terms)

            return page_data, links

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None

    def crawl(self):
        """Main crawl method"""
        logger.info(f"Starting crawl of {self.base_url}")
        logger.info(f"Max pages: {self.max_pages}")

        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.pop(0)

            if url in self.visited:
                continue

            self.visited.add(url)

            result = self._crawl_page(url)

            if result:
                page_data, links = result
                self.data['pages'].append(page_data)

                # Add new links to visit
                for link in links:
                    if link not in self.visited and link not in self.to_visit:
                        self.to_visit.append(link)

            # Respect rate limiting
            time.sleep(CRAWLER_CONFIG['delay'])

        # Deduplicate business terms
        self.data['business_terms'] = list(set(self.data['business_terms']))

        # Deduplicate contacts
        for key in self.data['contacts']:
            self.data['contacts'][key] = list(set(self.data['contacts'][key]))

        logger.info(f"Crawl complete. Visited {len(self.visited)} pages")

        return self.data


def crawl_company_website(url, max_pages=None):
    """
    Main function to crawl a company website
    
    Args:
        url: Company website URL
        max_pages: Maximum pages to crawl (default from config)
    
    Returns:
        dict: Extracted company data
    """
    crawler = WebsiteCrawler(url, max_pages)
    data = crawler.crawl()

    # Generate filename
    domain = urlparse(url).netloc.replace('.', '_')
    filename = f"website_{domain}.json"

    # Save to file
    filepath = save_json(data, filename)
    logger.info(f"Data saved to {filepath}")

    return data


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
        max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None
    else:
        url = "https://www.anthropic.com"
        max_pages = 10

    print(f"Crawling {url}...")
    data = crawl_company_website(url, max_pages)
    print(f"\nCrawled {len(data['pages'])} pages")
    print(f"Found {len(data['contacts'])} contact types")
    print(f"Extracted {len(data['business_terms'])} business terms")
