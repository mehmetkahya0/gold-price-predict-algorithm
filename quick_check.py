#!/usr/bin/env python3
"""
Quick Gold Price Checker
========================

This script quickly fetches and displays the current gold price in Turkish Lira.
"""

from price_scraper import GoldPriceScraper

def quick_price_check():
    """Get current gold price quickly"""
    print("🔍 Fetching current gold price...")
    
    scraper = GoldPriceScraper()
    price = scraper.get_current_price()
    
    if price:
        print(f"💰 Current gold price: {price} TRY per gram")
        
        # Get recent trend if available
        recent_data = scraper.get_historical_data(7)
        if len(recent_data) > 1:
            old_price = recent_data.iloc[-1]['price_per_gram']
            change = price - old_price
            change_percent = (change / old_price) * 100
            
            if change > 0:
                trend = f"📈 +{change:.2f} TRY (+{change_percent:.1f}%) from last week"
            elif change < 0:
                trend = f"📉 {change:.2f} TRY ({change_percent:.1f}%) from last week"
            else:
                trend = "➡️ No change from last week"
            
            print(f"Trend: {trend}")
    else:
        print("❌ Failed to fetch current gold price")

if __name__ == "__main__":
    quick_price_check()
