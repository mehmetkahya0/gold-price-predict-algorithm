#!/usr/bin/env python3
"""
Test script to find the correct API endpoint for historical gold price data
"""
import requests
import json
from datetime import datetime, timedelta
import time


def test_api_endpoints():
    """Test different API endpoint patterns to find working historical data API"""
    
    # API info found from the website
    api_prefix = "https://api.doviz.com/api/v12"
    access_tokens = [
        "2646ad120b3a29b0172f331b8d44479a8157577b0a57f78545b2a7f0f0e69b21",
        "9d6e4f23f72ec00b253987ce3e8fd37e0659bf3b14ad2b09d7fc27b8e396bd3c"
    ]
    
    # Calculate timestamps (1 year ago from now)
    now = int(time.time())
    one_year_ago = now - (365 * 24 * 60 * 60)
    
    print(f"Testing API endpoints...")
    print(f"Current timestamp: {now}")
    print(f"One year ago timestamp: {one_year_ago}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://altin.doviz.com/gram-altin'
    }
    
    # Different endpoint patterns to test
    endpoints = [
        "/charts/gram-altin",
        "/historical/gram-altin", 
        "/prices/gram-altin",
        "/data/gram-altin",
        "/chart/gram-altin"
    ]
    
    for token in access_tokens:
        print(f"\n--- Testing with token: {token[:20]}... ---")
        
        for endpoint in endpoints:
            # Test different parameter combinations
            test_urls = [
                f"{api_prefix}{endpoint}?access_token={token}&from={one_year_ago}&to={now}",
                f"{api_prefix}{endpoint}?token={token}&from={one_year_ago}&to={now}",
                f"{api_prefix}{endpoint}?access_token={token}&period=1Y",
                f"{api_prefix}{endpoint}?access_token={token}&range=1Y",
                f"{api_prefix}{endpoint}?access_token={token}",
            ]
            
            for url in test_urls:
                try:
                    print(f"Testing: {url[:100]}...")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if isinstance(data, dict) and len(data) > 0:
                                print(f"✅ SUCCESS! Found working endpoint:")
                                print(f"URL: {url}")
                                print(f"Response keys: {list(data.keys())}")
                                print(f"Sample data: {json.dumps(data, indent=2)[:500]}...")
                                return url, data
                        except json.JSONDecodeError:
                            content = response.text[:200]
                            if "html" not in content.lower():
                                print(f"Non-JSON response: {content}...")
                    
                    time.sleep(0.5)  # Be respectful with requests
                    
                except Exception as e:
                    print(f"Error: {e}")
                    continue
    
    print("\n❌ No working API endpoint found with the tested patterns.")
    return None, None


def test_direct_chart_scraping():
    """Test scraping chart data directly from the webpage"""
    print("\n--- Testing direct webpage chart data extraction ---")
    
    url = "https://altin.doviz.com/gram-altin"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Look for embedded chart data in JavaScript
            content = response.text
            
            # Search for chart data patterns
            patterns = [
                "chartData",
                "priceData", 
                "historicalData",
                "timeSeriesData",
                "series",
                "data:"
            ]
            
            for pattern in patterns:
                if pattern in content:
                    # Find the line containing the pattern
                    lines = content.split('\n')
                    for line in lines:
                        if pattern in line:
                            print(f"Found {pattern} in line: {line[:100]}...")
                            
                            # Try to extract JSON-like data
                            if '[' in line and ']' in line:
                                start = line.find('[')
                                end = line.rfind(']') + 1
                                if start != -1 and end != -1:
                                    try:
                                        data_str = line[start:end]
                                        data = json.loads(data_str)
                                        if len(data) > 10:  # Likely historical data
                                            print(f"✅ Found potential chart data: {len(data)} points")
                                            print(f"Sample: {data[:3]}")
                                            return data
                                    except json.JSONDecodeError:
                                        continue
    except Exception as e:
        print(f"Error scraping webpage: {e}")
    
    return None


if __name__ == "__main__":
    print("=== Gold Price API Endpoint Discovery ===\n")
    
    # Test API endpoints
    working_url, api_data = test_api_endpoints()
    
    # Test direct webpage scraping 
    chart_data = test_direct_chart_scraping()
    
    print("\n=== Summary ===")
    if working_url:
        print(f"✅ Working API URL found: {working_url}")
    else:
        print("❌ No working API URL found")
        
    if chart_data:
        print(f"✅ Chart data found on webpage: {len(chart_data)} data points")
    else:
        print("❌ No chart data found on webpage")
        
    if not working_url and not chart_data:
        print("\n💡 Alternative approaches:")
        print("1. Use web scraping with Selenium to capture JavaScript-rendered chart data")
        print("2. Find alternative gold price APIs (Yahoo Finance, Alpha Vantage, etc.)")
        print("3. Use financial data libraries like yfinance")
