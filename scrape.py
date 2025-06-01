# Gold coin scraper for Turkish gold coin prices from döviz.com
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import time
import json

# New imports for historical data
try:
    import yfinance as yf
    import pandas as pd
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available. Historical data collection will be limited.")


class GoldPriceScraper:
    """A class to scrape Turkish gold prices from doviz.com and save to database."""
    
    def __init__(self, db_path: str = 'price.db', url: str = "https://altin.doviz.com/gram-altin"):
        """
        Initialize the scraper.
        
        Args:
            db_path (str): Path to the SQLite database file
            url (str): URL to scrape gold prices from
        """
        self.db_path = db_path
        self.url = url
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the database and create table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create main gold prices table for real-time data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gold_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    price REAL NOT NULL,
                    raw_price_text TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create historical gold prices table for daily historical data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_gold_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    price_tl REAL,
                    price_usd REAL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    source TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster date queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_historical_date 
                ON historical_gold_prices(date)
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            raise Exception(f"Database initialization failed: {e}")
    
    def scrape_gold_price(self) -> dict:
        """
        Scrape the current gold price from the website.
        
        Returns:
            dict: Dictionary containing price, raw text, and timestamp
            
        Raises:
            Exception: If scraping fails or price element not found
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for the price element
            price_element = (
                soup.find('span', class_='text-success') or
                soup.find('span', class_='value') or
                soup.find('div', class_='price') or
                soup.select_one('.gold-price .value')
            )
            
            if price_element:
                raw_price = price_element.text.strip()
                # Extract numeric value from price text
                numeric_price = self._extract_numeric_price(raw_price)
                
                return {
                    'price': numeric_price,
                    'raw_price_text': raw_price,
                    'timestamp': datetime.now(),
                    'success': True
                }
            else:
                raise ValueError("Price element not found on the page.")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while scraping: {e}")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")
    
    def _extract_numeric_price(self, price_text: str) -> float:
        """
        Extract numeric price from price text.
        
        Args:
            price_text (str): Raw price text from website
            
        Returns:
            float: Numeric price value
        """
        import re
        # Remove Turkish currency symbols and extract numbers
        # Handle formats like "2.850,45 ₺" or "2,850.45" 
        clean_text = re.sub(r'[^\d,.]', '', price_text)
        
        # Handle Turkish number format (comma as decimal separator)
        if ',' in clean_text and '.' in clean_text:
            # Format: 2.850,45 (dot as thousands separator, comma as decimal)
            clean_text = clean_text.replace('.', '').replace(',', '.')
        elif ',' in clean_text:
            # Check if comma is decimal separator or thousands separator
            parts = clean_text.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Likely decimal separator
                clean_text = clean_text.replace(',', '.')
        
        try:
            return float(clean_text)
        except ValueError:
            raise ValueError(f"Could not parse price from text: {price_text}")
    
    def save_price_to_db(self, price_data: dict) -> bool:
        """
        Save price data to the database.
        
        Args:
            price_data (dict): Price data dictionary from scrape_gold_price()
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO gold_prices (price, raw_price_text, timestamp) 
                VALUES (?, ?, ?)
            ''', (price_data['price'], price_data['raw_price_text'], price_data['timestamp']))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database save error: {e}")
            return False
    
    def get_latest_price(self) -> Optional[dict]:
        """
        Get the latest price from the database.
        
        Returns:
            dict or None: Latest price data or None if no data exists
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT price, raw_price_text, timestamp 
                FROM gold_prices 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'price': row[0],
                    'raw_price_text': row[1],
                    'timestamp': row[2]
                }
            return None
            
        except Exception as e:
            print(f"Database query error: {e}")
            return None
    
    def get_price_history(self, limit: int = 100) -> list:
        """
        Get price history from the database.
        
        Args:
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of price records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, price, raw_price_text, timestamp 
                FROM gold_prices 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'price': row[1],
                    'raw_price_text': row[2],
                    'timestamp': row[3]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Database query error: {e}")
            return []
    
    def scrape_and_save(self) -> dict:
        """
        Scrape current price and save to database in one operation.
        
        Returns:
            dict: Result with success status and price data
        """
        try:
            price_data = self.scrape_gold_price()
            saved = self.save_price_to_db(price_data)
            
            return {
                'success': saved,
                'price_data': price_data,
                'message': 'Price scraped and saved successfully' if saved else 'Price scraped but save failed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'price_data': None,
                'message': f"Error: {e}"
            }
    
    def fetch_historical_data(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch historical gold price data from yfinance and format for database insertion.
        
        Args:
            start_date (str): Start date for historical data (YYYY-MM-DD)
            end_date (str): End date for historical data (YYYY-MM-DD)
            
        Returns:
            List[Dict]: List of dictionaries containing historical price data
        """
        if not YFINANCE_AVAILABLE:
            print("yfinance is not available. Cannot fetch historical data.")
            return []
        
        try:
            # Download historical data from Yahoo Finance
            df = yf.download("GC=F", start=start_date, end=end_date, interval="1d")
            
            # Reset index to get date as a column
            df = df.reset_index()
            
            # Rename columns to match our database schema
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Adj Close': 'price_usd',
                'Volume': 'volume'
            })
            
            # Add source and created_at columns
            df['source'] = 'yfinance'
            df['created_at'] = datetime.now()
            
            # Select only the columns we need
            historical_data = df[[
                'date', 'price_usd', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'source', 'created_at'
            ]]
            
            # Convert to a list of dictionaries
            historical_data_list = historical_data.to_dict(orient='records')
            
            return historical_data_list
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return []
    
    def save_historical_data(self, data: List[Dict]) -> bool:
        """
        Save a batch of historical gold price data to the database.
        
        Args:
            data (List[Dict]): List of historical data dictionaries
            
        Returns:
            bool: True if all data saved successfully, False otherwise
        """
        if not data:
            print("No data to save.")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert data into the historical_gold_prices table
            cursor.executemany('''
                INSERT OR IGNORE INTO historical_gold_prices 
                (date, price_tl, price_usd, open_price, high_price, low_price, close_price, volume, source, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                (
                    d['date'],
                    None,  # price_tl not available in yfinance data
                    d['price_usd'],
                    d['open_price'],
                    d['high_price'],
                    d['low_price'],
                    d['close_price'],
                    d['volume'],
                    d['source'],
                    d['created_at']
                )
                for d in data
            ])
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database save error: {e}")
            return False
    
    def download_and_save_historical_data(self, start_date: str, end_date: str) -> dict:
        """
        Download historical gold price data from Yahoo Finance and save to database.
        
        Args:
            start_date (str): Start date for historical data (YYYY-MM-DD)
            end_date (str): End date for historical data (YYYY-MM-DD)
            
        Returns:
            dict: Result with success status and details
        """
        try:
            # Fetch historical data
            historical_data = self.fetch_historical_data(start_date, end_date)
            
            if not historical_data:
                return {
                    'success': False,
                    'message': "No historical data found for the given date range."
                }
            
            # Save to database
            saved = self.save_historical_data(historical_data)
            
            return {
                'success': saved,
                'message': 'Historical data downloaded and saved successfully' if saved else 'Historical data downloaded but save failed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error: {e}"
            }
    
    def collect_historical_data(self, days: int = 365, source: str = "auto") -> Dict:
        """
        Collect historical gold price data for the specified number of days.
        
        Args:
            days (int): Number of days of historical data to collect (default: 365)
            source (str): Data source ("auto", "yahoo", "doviz", "multiple")
            
        Returns:
            dict: Result with success status and data statistics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            print(f"Collecting historical gold price data from {start_date.date()} to {end_date.date()}")
            
            historical_data = []
            
            if source in ["auto", "yahoo", "multiple"] and YFINANCE_AVAILABLE:
                yahoo_data = self._get_yahoo_gold_data(start_date, end_date)
                if yahoo_data:
                    historical_data.extend(yahoo_data)
                    print(f"✅ Collected {len(yahoo_data)} records from Yahoo Finance")
            
            if source in ["auto", "doviz", "multiple"]:
                doviz_data = self._get_doviz_historical_data(start_date, end_date)
                if doviz_data:
                    historical_data.extend(doviz_data)
                    print(f"✅ Collected {len(doviz_data)} records from Doviz.com")
            
            if not historical_data:
                return {
                    'success': False,
                    'message': 'No historical data could be collected from any source',
                    'data_points': 0
                }
            
            # Save to database
            saved_count = self._save_historical_data(historical_data)
            
            return {
                'success': True,
                'message': f'Successfully collected and saved {saved_count} historical data points',
                'data_points': saved_count,
                'date_range': f"{start_date.date()} to {end_date.date()}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error collecting historical data: {e}",
                'data_points': 0
            }
    
    def _get_yahoo_gold_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get historical gold price data from Yahoo Finance.
        
        Args:
            start_date (datetime): Start date for data collection
            end_date (datetime): End date for data collection
            
        Returns:
            list: List of historical price dictionaries
        """
        if not YFINANCE_AVAILABLE:
            return []
        
        try:
            # Gold futures ticker (GC=F) and Gold ETF (GLD) for USD prices
            gold_tickers = ['GC=F', 'GLD', 'IAU']  # Different gold instruments
            
            for ticker in gold_tickers:
                try:
                    print(f"Trying Yahoo Finance ticker: {ticker}")
                    gold = yf.Ticker(ticker)
                    hist = gold.history(start=start_date, end=end_date, interval="1d")
                    
                    if not hist.empty:
                        historical_data = []
                        
                        for date, row in hist.iterrows():
                            # Convert USD to TL (approximate, using current rate for historical estimation)
                            # In a real implementation, you'd want historical USD/TL rates
                            usd_to_tl_rate = 39.0  # Approximate current rate
                            
                            data_point = {
                                'date': date.date(),
                                'price_usd': float(row['Close']),
                                'price_tl': float(row['Close']) * usd_to_tl_rate,  # Approximate
                                'open_price': float(row['Open']),
                                'high_price': float(row['High']),
                                'low_price': float(row['Low']),
                                'close_price': float(row['Close']),
                                'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0,
                                'source': f'yahoo_{ticker}'
                            }
                            historical_data.append(data_point)
                        
                        print(f"Successfully collected {len(historical_data)} records from {ticker}")
                        return historical_data
                        
                except Exception as e:
                    print(f"Failed to get data from {ticker}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            print(f"Error collecting Yahoo Finance data: {e}")
            return []
    
    def _get_doviz_historical_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Attempt to get historical data from Doviz.com using various methods.
        
        Args:
            start_date (datetime): Start date for data collection
            end_date (datetime): End date for data collection
            
        Returns:
            list: List of historical price dictionaries
        """
        try:
            # Method 1: Try to find API endpoints
            api_data = self._try_doviz_api(start_date, end_date)
            if api_data:
                return api_data
            
            # Method 2: Parse JavaScript chart data from webpage
            chart_data = self._parse_chart_data_from_webpage()
            if chart_data:
                return chart_data
            
            # Method 3: Scrape daily pages (time-consuming, use as last resort)
            # This would involve accessing historical daily pages if they exist
            
            return []
            
        except Exception as e:
            print(f"Error collecting Doviz.com historical data: {e}")
            return []
    
    def _try_doviz_api(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Try different API endpoint patterns for Doviz.com"""
        try:
            # API configuration found from webpage
            api_prefix = "https://api.doviz.com/api/v12"
            access_tokens = [
                "2646ad120b3a29b0172f331b8d44479a8157577b0a57f78545b2a7f0f0e69b21",
                "9d6e4f23f72ec00b253987ce3e8fd37e0659bf3b14ad2b09d7fc27b8e396bd3c"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://altin.doviz.com/gram-altin'
            }
            
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            endpoints = [
                "/charts/gram-altin",
                "/historical/gram-altin",
                "/data/gram-altin"
            ]
            
            for token in access_tokens:
                for endpoint in endpoints:
                    test_urls = [
                        f"{api_prefix}{endpoint}?access_token={token}&from={start_timestamp}&to={end_timestamp}",
                        f"{api_prefix}{endpoint}?access_token={token}&period=1Y"
                    ]
                    
                    for url in test_urls:
                        try:
                            response = requests.get(url, headers=headers, timeout=10)
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                    if isinstance(data, dict) and len(data) > 0:
                                        # Parse the API response format (would need to be customized based on actual response)
                                        return self._parse_api_response(data)
                                except json.JSONDecodeError:
                                    continue
                            
                            time.sleep(0.5)  # Rate limiting
                            
                        except Exception:
                            continue
            
            return []
            
        except Exception as e:
            print(f"API test failed: {e}")
            return []
    
    def _parse_chart_data_from_webpage(self) -> List[Dict]:
        """Parse chart data directly from the Doviz.com webpage JavaScript"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []
            
            content = response.text
            
            # Look for embedded chart data patterns
            patterns = [
                "chartData",
                "priceData",
                "historicalData",
                "timeSeriesData",
                "series"
            ]
            
            for pattern in patterns:
                if pattern in content:
                    lines = content.split('\n')
                    for line in lines:
                        if pattern in line and '[' in line and ']' in line:
                            try:
                                # Extract JSON array
                                start = line.find('[')
                                end = line.rfind(']') + 1
                                if start != -1 and end != -1:
                                    data_str = line[start:end]
                                    chart_data = json.loads(data_str)
                                    
                                    if len(chart_data) > 10:  # Likely historical data
                                        return self._convert_chart_data_to_historical(chart_data)
                            except (json.JSONDecodeError, ValueError):
                                continue
            
            return []
            
        except Exception as e:
            print(f"Chart data parsing failed: {e}")
            return []
    
    def _convert_chart_data_to_historical(self, chart_data: List) -> List[Dict]:
        """Convert chart data format to our historical data format"""
        historical_data = []
        
        try:
            for point in chart_data:
                if isinstance(point, list) and len(point) >= 2:
                    # Assuming format: [timestamp, price] or [timestamp, price, volume]
                    timestamp = point[0]
                    price = point[1]
                    
                    # Convert timestamp (could be milliseconds or seconds)
                    if timestamp > 1e12:  # Milliseconds
                        date = datetime.fromtimestamp(timestamp / 1000).date()
                    else:  # Seconds
                        date = datetime.fromtimestamp(timestamp).date()
                    
                    data_point = {
                        'date': date,
                        'price_tl': float(price),
                        'price_usd': None,
                        'open_price': float(price),
                        'high_price': float(price),
                        'low_price': float(price),
                        'close_price': float(price),
                        'volume': 0,
                        'source': 'doviz_chart'
                    }
                    historical_data.append(data_point)
                    
                elif isinstance(point, dict):
                    # Handle dictionary format
                    if 'date' in point and 'price' in point:
                        data_point = {
                            'date': datetime.strptime(point['date'], '%Y-%m-%d').date(),
                            'price_tl': float(point['price']),
                            'price_usd': None,
                            'open_price': float(point.get('open', point['price'])),
                            'high_price': float(point.get('high', point['price'])),
                            'low_price': float(point.get('low', point['price'])),
                            'close_price': float(point.get('close', point['price'])),
                            'volume': int(point.get('volume', 0)),
                            'source': 'doviz_chart'
                        }
                        historical_data.append(data_point)
        
        except Exception as e:
            print(f"Error converting chart data: {e}")
        
        return historical_data
    
    def _parse_api_response(self, data: Dict) -> List[Dict]:
        """Parse API response and convert to our historical data format"""
        # This would need to be implemented based on the actual API response structure
        # For now, return empty list since we haven't found the working API format
        return []
    
    def _save_historical_data(self, historical_data: List[Dict]) -> int:
        """
        Save historical data to the database.
        
        Args:
            historical_data (list): List of historical price dictionaries
            
        Returns:
            int: Number of records saved
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for data_point in historical_data:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO historical_gold_prices 
                        (date, price_tl, price_usd, open_price, high_price, low_price, close_price, volume, source) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data_point['date'],
                        data_point.get('price_tl'),
                        data_point.get('price_usd'),
                        data_point.get('open_price'),
                        data_point.get('high_price'),
                        data_point.get('low_price'),
                        data_point.get('close_price'),
                        data_point.get('volume', 0),
                        data_point.get('source', 'unknown')
                    ))
                    saved_count += 1
                    
                except sqlite3.Error as e:
                    print(f"Error saving data point {data_point['date']}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            print(f"Database save error: {e}")
            return 0
    
    def get_historical_data(self, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None, 
                          limit: int = 1000) -> List[Dict]:
        """
        Get historical data from the database.
        
        Args:
            start_date (datetime, optional): Start date for data retrieval
            end_date (datetime, optional): End date for data retrieval
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of historical price records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT date, price_tl, price_usd, open_price, high_price, low_price, 
                       close_price, volume, source, created_at 
                FROM historical_gold_prices 
            '''
            params = []
            
            conditions = []
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date.date())
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date.date())
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'date': row[0],
                    'price_tl': row[1],
                    'price_usd': row[2],
                    'open_price': row[3],
                    'high_price': row[4],
                    'low_price': row[5],
                    'close_price': row[6],
                    'volume': row[7],
                    'source': row[8],
                    'created_at': row[9]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Database query error: {e}")
            return []
    
    def get_data_statistics(self) -> Dict:
        """Get statistics about the collected data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Real-time data stats
            cursor.execute("SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM gold_prices")
            realtime_stats = cursor.fetchone()
            
            # Historical data stats
            cursor.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM historical_gold_prices")
            historical_stats = cursor.fetchone()
            
            # Latest prices
            cursor.execute("SELECT price, timestamp FROM gold_prices ORDER BY timestamp DESC LIMIT 1")
            latest_realtime = cursor.fetchone()
            
            cursor.execute("SELECT price_tl, date FROM historical_gold_prices ORDER BY date DESC LIMIT 1")
            latest_historical = cursor.fetchone()
            
            conn.close()
            
            return {
                'realtime_data': {
                    'count': realtime_stats[0],
                    'first_timestamp': realtime_stats[1],
                    'last_timestamp': realtime_stats[2],
                    'latest_price': latest_realtime[0] if latest_realtime else None
                },
                'historical_data': {
                    'count': historical_stats[0],
                    'first_date': historical_stats[1],
                    'last_date': historical_stats[2],
                    'latest_price': latest_historical[0] if latest_historical else None
                }
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gold Price Scraper with Historical Data Collection')
    parser.add_argument('--mode', choices=['current', 'historical', 'both'], default='both',
                       help='Scraping mode: current prices, historical data, or both')
    parser.add_argument('--days', type=int, default=365,
                       help='Number of days of historical data to collect (default: 365)')
    parser.add_argument('--source', choices=['auto', 'yahoo', 'doviz', 'multiple'], default='auto',
                       help='Data source for historical data')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics')
    
    args = parser.parse_args()
    
    scraper = GoldPriceScraper()
    
    try:
        if args.stats:
            print("=== Database Statistics ===")
            stats = scraper.get_data_statistics()
            
            if stats.get('realtime_data'):
                rt = stats['realtime_data']
                print(f"\nReal-time Data:")
                print(f"  Records: {rt['count']}")
                print(f"  Date range: {rt['first_timestamp']} to {rt['last_timestamp']}")
                print(f"  Latest price: {rt['latest_price']:.2f} TL" if rt['latest_price'] else "  Latest price: None")
            
            if stats.get('historical_data'):
                hist = stats['historical_data']
                print(f"\nHistorical Data:")
                print(f"  Records: {hist['count']}")
                print(f"  Date range: {hist['first_date']} to {hist['last_date']}")
                print(f"  Latest price: {hist['latest_price']:.2f} TL" if hist['latest_price'] else "  Latest price: None")
        
        if args.mode in ['current', 'both']:
            print("\n=== Collecting Current Price ===")
            result = scraper.scrape_and_save()
            
            if result['success']:
                price_data = result['price_data']
                print(f"✅ Current gold price: {price_data['price']:.2f} TL")
                print(f"   Raw price text: {price_data['raw_price_text']}")
                print(f"   Timestamp: {price_data['timestamp']}")
                print("   Price saved to database successfully.")
            else:
                print(f"❌ Failed: {result['message']}")
        
        if args.mode in ['historical', 'both']:
            print(f"\n=== Collecting Historical Data ({args.days} days) ===")
            hist_result = scraper.collect_historical_data(days=args.days, source=args.source)
            
            if hist_result['success']:
                print(f"✅ {hist_result['message']}")
                print(f"   Date range: {hist_result['date_range']}")
                print(f"   Data points: {hist_result['data_points']}")
            else:
                print(f"❌ {hist_result['message']}")
        
        # Show final statistics
        if args.mode in ['historical', 'both'] or args.stats:
            print("\n=== Final Statistics ===")
            final_stats = scraper.get_data_statistics()
            
            if final_stats.get('historical_data'):
                hist = final_stats['historical_data']
                print(f"Total historical records: {hist['count']}")
                
                if hist['count'] > 0:
                    # Show sample of recent data
                    recent_data = scraper.get_historical_data(limit=5)
                    print(f"\nRecent historical data (last 5 records):")
                    for record in recent_data:
                        price_str = f"{record['price_tl']:.2f} TL" if record['price_tl'] else f"{record['price_usd']:.2f} USD"
                        print(f"  {record['date']}: {price_str} ({record['source']})")
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    
    print("\n🎯 Scraper execution completed!")
    print("\nUsage examples:")
    print("  python3 scrape.py --mode current              # Get current price only")
    print("  python3 scrape.py --mode historical --days 30  # Get 30 days of historical data")
    print("  python3 scrape.py --mode both --days 365       # Get current + 1 year historical")
    print("  python3 scrape.py --stats                      # Show database statistics")
