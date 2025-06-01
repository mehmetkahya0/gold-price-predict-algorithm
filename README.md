# Gold Price Scraper & Prediction Algorithm

A comprehensive system for scraping, storing, and analyzing gold prices in Turkish Lira (TRY).

## Features

- 🏆 **Real-time Gold Price Scraping**: Fetches current 1-gram gold prices in Turkish Lira
- 💾 **Database Storage**: Stores historical data in SQLite database
- 📊 **Statistical Analysis**: Provides comprehensive price statistics
- 📈 **Historical Data**: Maintains up to 1 year of historical price data
- 🔄 **Scheduled Monitoring**: Continuous price monitoring with customizable intervals
- 📤 **Data Export**: Export historical data to CSV format
- 🎯 **Multiple Data Sources**: Uses multiple APIs for reliable price fetching

## Installation

1. **Clone or download the project**
2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Price Check
Get the current gold price instantly:
```bash
python quick_check.py
```

### Interactive Application
Run the full interactive application:
```bash
python main.py
```

### Direct Usage
Use the scraper programmatically:
```python
from price_scraper import GoldPriceScraper

# Initialize scraper
scraper = GoldPriceScraper()

# Get current price
current_price = scraper.get_current_price()
print(f"Current price: {current_price} TRY per gram")

# Get historical data
historical_data = scraper.get_historical_data(30)  # Last 30 days

# Get statistics
stats = scraper.get_price_statistics(365)  # Last year
```

## Data Sources

The scraper uses multiple data sources for reliability:

1. **Primary**: Metals.live API + Exchange Rate API
   - Gold price in USD from metals.live
   - USD/TRY exchange rate from exchangerate-api.com
   - Calculates TRY price per gram

2. **Backup**: Turkish financial websites (Bigpara, etc.)
3. **Alternative**: Central Bank of Turkey (TCMB) data

## Database Schema

The SQLite database stores:
- `id`: Unique identifier
- `date_time`: Timestamp of price recording
- `price_per_gram`: Gold price in TRY per gram
- `currency`: Currency (default: TRY)
- `source`: Data source used
- `created_at`: Record creation timestamp

## Menu Options

1. **Get current gold price** - Fetch and display current price
2. **Start continuous monitoring** - Monitor prices every hour
3. **Generate sample historical data** - Create test data for development
4. **View price statistics** - Comprehensive statistical analysis
5. **Export data to CSV** - Export historical data
6. **View recent prices** - Display recent price history
7. **Clear database** - Reset all stored data
8. **Exit** - Close application

## Example Output

```
📊 PRICE STATISTICS (365 days)
----------------------------------------
Total records: 365
Average price: 2,045.67 TRY
Median price: 2,040.12 TRY
Minimum price: 1,890.45 TRY
Maximum price: 2,234.78 TRY
Price volatility (std): 87.23 TRY
Latest price: 2,067.34 TRY
Price change: +125.89 TRY (+6.5%) 📈
```

## Files

- `price_scraper.py` - Main scraper class with all functionality
- `main.py` - Interactive application with menu system
- `quick_check.py` - Simple script for quick price checks
- `requirements.txt` - Python package dependencies
- `gold_prices.db` - SQLite database (created automatically)

## Configuration

You can customize:
- **Scraping interval**: Modify in `start_scheduled_scraping(interval_minutes)`
- **Database path**: Change in `GoldPriceScraper(db_path='custom_path.db')`
- **Data sources**: Add/modify source methods in the scraper class

## Notes

- The scraper respects rate limits and includes error handling
- Sample data generation is available for testing
- All prices are in Turkish Lira (TRY) per gram
- The system works offline once historical data is collected

## Troubleshooting

If you encounter issues:

1. **Import errors**: Install requirements with `pip install -r requirements.txt`
2. **No price data**: Check internet connection, APIs might be temporarily unavailable
3. **Database issues**: Delete `gold_prices.db` and restart - it will be recreated

## Future Enhancements

- Price prediction algorithms using machine learning
- Price alerts and notifications
- Web dashboard for visualization
- Integration with more Turkish financial data sources
- Real-time price charts and trends

---

**Author**: Gold Price Prediction Algorithm  
**Date**: June 2025  
**Version**: 1.0
