#!/usr/bin/env python3
"""Script to list all unique tags from the database and show categorization."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.supabase_client import db
from collections import Counter

def categorize_tag(tag: str) -> str:
    """Categorize a tag based on our filtering logic."""
    tag_lower = tag.lower()
    
    # Define categories (matching TagFilter.tsx)
    TAG_CATEGORIES = {
        '主要主題': [
            '市場分析', 'market analysis', '市場', '分析',
            '公司動態', 'company news', '公司', '動態',
            '機場與基礎設施', 'airports & infrastructure', '機場', '基礎設施', 'infrastructure',
            '數位與科技', 'digital & tech', '數位', '科技', 'digital', 'tech',
            '永續發展', 'sustainability', '永續', 'saf',
            '特殊貨物', 'special cargo', '特殊', '冷鏈', 'cold chain',
            '法規與安全', 'regulation & security', '法規', '安全', 'security',
            '人事任命', 'people & appointments', '人事', '任命',
        ],
        '地理區域': [
            '亞洲', 'asia', 'asian',
            '歐洲', 'europe', 'european',
            '北美', 'north america', 'north american',
            '中東', 'middle east',
            '亞太地區', 'asia pacific', 'apac',
            '跨太平洋', 'trans-pacific',
            '大西洋', 'atlantic',
            '亞歐貿易', 'asia-europe',
        ],
        '公司/機場': [
            # Airlines
            'fedex', 'dhl', 'lufthansa', 'iag cargo', 'cathay pacific', 'singapore airlines',
            'emirates', 'qatar airways', 'british airways', 'air france', 'klm', 'turkish airlines',
            'korean air', 'japan airlines', 'ana', 'china airlines', 'eva air', 'thai airways',
            'air china', 'china southern', 'china eastern', 'united airlines', 'american airlines',
            'delta air lines', 'ups', 'atlas air', 'kalitta air', 'cargolux', 'airbridgecargo',
            'volga-dnepr', 'nippon cargo', 'polar air cargo', 'southern air', 'western global',
            # Airports
            'heathrow', 'jfk', 'lax', 'cdg', 'frankfurt', 'amsterdam', 'dubai', 'singapore changi',
            'hong kong international', 'narita', 'haneda', 'incheon', 'miami', 'chicago o\'hare',
            'atlanta', 'dallas', 'memphis', 'louisville', 'anchorage', 'liege', 'luxembourg',
            'hong kong', 'singapore', 'tokyo', 'seoul', 'shanghai', 'beijing', 'guangzhou',
            'airport', 'international airport',
            # Ground Handlers & Operators
            'wfs', 'swissport', 'menzies', 'dnata', 'celebi', 'sats', 'cargo', 'ground',
            'handler', 'handling', 'services', 'logistics',
            # Forwarders
            'kuehne+nagel', 'db schenker', 'dsv', 'expeditors', 'panalpina', 'ceva', 'geodis',
            'hellmann', 'bolloré', 'agility', 'nippon express', 'yusen', 'kerry logistics',
            'forwarder', 'forwarding',
            # Other common patterns
            'cargo', 'freight', 'logistics', 'supply chain', 'warehouse', 'warehousing',
        ],
    }
    
    # Check against defined keywords
    for category, keywords in TAG_CATEGORIES.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in tag_lower or tag_lower == keyword_lower:
                return category
    
    # Pattern matching for English tags
    import re
    
    # Company/Airport/Operator patterns
    company_patterns = [
        r'airlines?$', r'airways?$', r'air cargo$', r'cargo$',
        r'airport$', r'international$', r'heathrow$', r'jfk$', r'lax$',
        r'^(fedex|dhl|ups|wfs|swissport|menzies|sats)',
        r'(handler|handling|services|logistics|forwarder|forwarding)$',
        r'\b(inc|llc|ltd|corp|group|holdings|aviation|airlines|airways)\b',
    ]
    
    if any(re.search(pattern, tag_lower, re.IGNORECASE) for pattern in company_patterns):
        return '公司/機場'
    
    # Geographic region patterns
    regions = [
        'asia', 'europe', 'america', 'pacific', 'atlantic', 'middle east',
        'north', 'south', 'east', 'west', 'africa', 'australia', 'oceania',
        'trans-pacific', 'trans-atlantic', 'asia-pacific', 'apac', 'emea',
    ]
    
    if any(region in tag_lower for region in regions):
        return '地理區域'
    
    # Main topic patterns
    topics = [
        'market', 'analysis', 'company', 'news', 'airport', 'infrastructure',
        'digital', 'tech', 'sustainability', 'saf', 'special', 'cargo',
        'regulation', 'security', 'people', 'appointment', 'merger', 'acquisition',
        'financial', 'strategy', 'e-commerce', 'cold chain', 'pharma',
    ]
    
    if any(topic in tag_lower for topic in topics):
        return '主要主題'
    
    return '其他'

def main():
    """List all tags with their categorization."""
    try:
        print("Fetching all tags from database...")
        tags = db.get_all_tags()
        
        if not tags:
            print("No tags found in database.")
            return
        
        print(f"\n📊 Total unique tags: {len(tags)}\n")
        
        # Categorize all tags
        categorized = {
            '主要主題': [],
            '地理區域': [],
            '公司/機場': [],
            '其他': [],
        }
        
        for tag in tags:
            category = categorize_tag(tag)
            categorized[category].append(tag)
        
        # Print by category
        for category, tag_list in categorized.items():
            if tag_list:
                print(f"\n{'='*60}")
                print(f"📁 {category} ({len(tag_list)} tags)")
                print(f"{'='*60}")
                for tag in sorted(tag_list):
                    print(f"  • {tag}")
        
        # Show statistics
        print(f"\n{'='*60}")
        print("📈 Statistics:")
        print(f"{'='*60}")
        for category, tag_list in categorized.items():
            percentage = (len(tag_list) / len(tags)) * 100 if tags else 0
            print(f"  {category}: {len(tag_list)} tags ({percentage:.1f}%)")
        
        # Show top 20 most common tags (if we had frequency data)
        print(f"\n{'='*60}")
        print("🔍 Sample tags from '其他' category (first 30):")
        print(f"{'='*60}")
        for tag in sorted(categorized['其他'])[:30]:
            print(f"  • {tag}")
        
        if len(categorized['其他']) > 30:
            print(f"\n  ... and {len(categorized['其他']) - 30} more in '其他'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

