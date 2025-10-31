"""
Main script for running Company Profiling Bots from command line
"""
import argparse
import sys
from bots.crawler import crawl_company_website
from bots.aggregator import aggregate_company_info
from utils.logger import setup_logger

logger = setup_logger('main')


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description='Company Profiling Bots - Extract and analyze company data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl a website
  python main.py crawl https://example.com --max-pages 30
  
  # Aggregate company info
  python main.py aggregate "Tesla" --urls https://tesla.com https://finance.yahoo.com/quote/TSLA
  
  # Run both for a company
  python main.py both "Tesla" https://tesla.com --max-pages 20
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Crawler command
    crawler_parser = subparsers.add_parser(
        'crawl', help='Crawl a company website')
    crawler_parser.add_argument('url', help='Company website URL')
    crawler_parser.add_argument(
        '--max-pages',
        type=int,
        default=20,
        help='Maximum number of pages to crawl (default: 20)'
    )

    # Aggregator command
    aggregator_parser = subparsers.add_parser(
        'aggregate', help='Aggregate company info')
    aggregator_parser.add_argument('company', help='Company name')
    aggregator_parser.add_argument(
        '--urls',
        nargs='+',
        help='Custom URLs to scrape (optional)'
    )

    # Both command
    both_parser = subparsers.add_parser(
        'both', help='Run both crawler and aggregator')
    both_parser.add_argument('company', help='Company name')
    both_parser.add_argument('url', help='Company website URL')
    both_parser.add_argument(
        '--max-pages',
        type=int,
        default=20,
        help='Maximum number of pages to crawl (default: 20)'
    )
    both_parser.add_argument(
        '--urls',
        nargs='+',
        help='Additional URLs for aggregator (optional)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        if args.command == 'crawl':
            logger.info(f"Starting website crawl: {args.url}")
            data = crawl_company_website(args.url, args.max_pages)

            print("\n" + "="*60)
            print("✅ CRAWL COMPLETE")
            print("="*60)
            print(f"Pages crawled: {len(data['pages'])}")
            print(
                f"Contacts found: {sum(len(v) for v in data['contacts'].values())}")
            print(f"Business terms: {len(data['business_terms'])}")
            print("="*60 + "\n")

        elif args.command == 'aggregate':
            logger.info(f"Starting company info aggregation: {args.company}")
            data = aggregate_company_info(args.company, args.urls)

            print("\n" + "="*60)
            print("✅ AGGREGATION COMPLETE")
            print("="*60)
            print(f"Company: {data['company_name']}")
            print(f"Sources queried: {len(data['sources'])}")
            print(f"Profile fields: {len(data['profile'])}")
            print("\nProfile summary:")
            for key, value in list(data['profile'].items())[:5]:
                print(f"  • {key}: {str(value)[:100]}...")
            print("="*60 + "\n")

        elif args.command == 'both':
            logger.info(f"Starting full company profiling: {args.company}")

            # Run crawler
            print("\n🔄 Phase 1: Crawling website...")
            crawler_data = crawl_company_website(args.url, args.max_pages)
            print(f"✅ Crawled {len(crawler_data['pages'])} pages\n")

            # Run aggregator
            print("🔄 Phase 2: Aggregating company data...")
            aggregator_urls = args.urls if args.urls else None
            aggregator_data = aggregate_company_info(
                args.company, aggregator_urls)
            print(
                f"✅ Aggregated from {len(aggregator_data['sources'])} sources\n")

            print("\n" + "="*60)
            print("✅ FULL PROFILING COMPLETE")
            print("="*60)
            print(f"Company: {args.company}")
            print(f"Website pages: {len(crawler_data['pages'])}")
            print(f"Data sources: {len(aggregator_data['sources'])}")
            print(f"Profile fields: {len(aggregator_data['profile'])}")
            print("="*60 + "\n")

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n⚠️  Process interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
