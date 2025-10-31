"""
test_bots.py - Test script for the company profiling bots
"""
from bots.crawler import crawl_company_website
from bots.aggregator import aggregate_company_info


def test_crawler():
    """Test the website crawler"""
    print("\n" + "="*60)
    print("Testing Website Crawler")
    print("="*60)
    
    # Test with a small crawl
    url = "https://www.anthropic.com"
    print(f"Crawling: {url}")
    
    try:
        data = crawl_company_website(url, max_pages=5)
        print(f"\n✅ Success!")
        print(f"   Pages crawled: {len(data['pages'])}")
        print(f"   Contacts found: {sum(len(v) for v in data['contacts'].values())}")
        print(f"   Business terms: {len(data['business_terms'])}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_aggregator():
    """Test the company info aggregator"""
    print("\n" + "="*60)
    print("Testing Company Info Aggregator")
    print("="*60)
    
    company = "Anthropic"
    urls = [
        "https://www.anthropic.com",
        "https://en.wikipedia.org/wiki/Anthropic"
    ]
    
    print(f"Aggregating info for: {company}")
    print(f"Sources: {len(urls)}")
    
    try:
        data = aggregate_company_info(company, urls)
        print(f"\n✅ Success!")
        print(f"   Sources queried: {len(data['sources'])}")
        print(f"   Profile fields: {len(data['profile'])}")
        
        if data['profile']:
            print("\n   Profile preview:")
            for key, value in list(data['profile'].items())[:3]:
                print(f"      • {key}: {str(value)[:80]}...")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    print("\n🧪 Company Profiling Bots - Test Suite")
    
    # Run tests
    test_crawler()
    test_aggregator()
    
    print("\n" + "="*60)
    print("="*60 + "\n")
