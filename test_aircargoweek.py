#!/usr/bin/env python3
"""
Test script for Aircargoweek scraper.
Run this from the project root: python3 test_aircargoweek.py
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import logging
from app.scraper.aircargoweek_scraper import AircargoweekScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Test the aircargoweek scraper."""
    print("=" * 70)
    print("Testing Aircargoweek Scraper")
    print("=" * 70)
    print()
    
    scraper = None
    try:
        # Create scraper
        scraper = AircargoweekScraper(delay_seconds=2, max_retries=3)
        
        # Test URL extraction
        listing_url = "https://aircargoweek.com/news/"
        print(f"Listing URL: {listing_url}")
        print("Extracting article URLs...")
        print()
        
        urls = scraper.get_article_urls(
            listing_url, 
            max_pages=2,  # Just test 2 pages
            check_duplicates=False
        )
        
        print(f"\n✓ Found {len(urls)} article URLs")
        print()
        
        if urls:
            print("First 5 URLs:")
            for i, url in enumerate(urls[:5], 1):
                print(f"  {i}. {url}")
            print()
            
            # Test scraping one article
            print("Testing article scraping on first URL...")
            print(f"URL: {urls[0]}")
            print()
            
            article_data = scraper.scrape_article(urls[0])
            
            if article_data:
                print("✓ Article scraped successfully!")
                print(f"  Title: {article_data.get('title', 'N/A')[:80]}...")
                print(f"  Content length: {len(article_data.get('content', ''))} characters")
                print(f"  Published date: {article_data.get('published_date', 'N/A')}")
            else:
                print("✗ Failed to scrape article")
        else:
            print("⚠️  No URLs found. Possible issues:")
            print("  1. Playwright browsers not installed")
            print("  2. Website blocking requests")
            print("  3. Network issues")
            print()
            print("To install Playwright browsers, run:")
            print("  source venv/bin/activate")
            print("  playwright install chromium")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()

