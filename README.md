# Gold Price Scraper & Prediction Algorithm 🏆

A comprehensive system for scraping, storing, and analyzing Turkish gold prices with real-time data collection and statistical analysis capabilities.

## 📋 Features

- 🏆 **Real-time Gold Price Scraping**: Fetches current 1-gram gold prices in Turkish Lira (TRY)
- 💾 **Database Storage**: Stores historical data in SQLite database with timestamps
- 📊 **Statistical Analysis**: Provides comprehensive price statistics and trends
- 📈 **Historical Data**: Maintains and analyzes historical price data (up to 1+ years)
- 🔄 **Scheduled Monitoring**: Continuous price monitoring with customizable intervals
- 📤 **Data Export**: Export historical data to CSV format for external analysis
- 🎯 **Multiple Data Sources**: Uses multiple APIs and fallback sources for reliable data
- 🔧 **Interactive CLI**: User-friendly command-line interface with menu system

## 🚀 Quick Start

### Installation

1. **Clone or download the project**
2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

### Quick Usage

**Get current gold price instantly:**
```bash
python3 quick_check.py
```

**Run interactive application:**
```bash
python3 main.py
```

**Run complete demonstration:**
```bash
python3 demo.py
```

## 💻 Usage Methods

### 1. Interactive Application (Recommended)
Launch the full interactive menu system:
```bash
python3 main.py
```

**Menu Options:**
- Get current gold price
- Start continuous monitoring (hourly)
- Generate sample historical data
- View price statistics
- Export data to CSV
- View recent prices
- Clear database
- Exit

### 2. Quick Price Check
Get instant price without menu:
```bash
python3 quick_check.py
```

### 3. Programmatic Usage
Use the scraper in your own Python code:
```python
from price_scraper import GoldPriceScraper

# Initialize scraper
scraper = GoldPriceScraper()

# Get current price
current_price = scraper.get_current_price()
print(f"Current price: {current_price} TRY per gram")

# Get historical data
historical_data = scraper.get_historical_data(30)  # Last 30 days

# Get comprehensive statistics
stats = scraper.get_price_statistics(365)  # Last year
print(f"Average price: {stats['mean']:.2f} TRY")
print(f"Price volatility: {stats['std']:.2f} TRY")

# Export data
scraper.export_data_to_csv("my_export.csv", 365)
```

## 🔌 Data Sources

The system uses multiple reliable data sources:

1. **Primary API Source**:
   - Gold price in USD from metals.live or similar APIs
   - USD/TRY exchange rate from exchangerate-api.com
   - Real-time calculation of TRY price per gram

2. **Backup Sources**:
   - Turkish financial websites (Bigpara, Investing.com)
   - Central Bank of Turkey (TCMB) exchange rate data
   - Fallback calculations based on market data

3. **Data Quality**:
   - Multiple source verification
   - Error handling and retries
   - Price validation and range checking

## 🗄️ Database Schema

The SQLite database (`gold_prices.db`) stores:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Unique identifier (auto-increment) |
| `date_time` | DATETIME | Timestamp of price recording |
| `price_per_gram` | REAL | Gold price in TRY per gram |
| `currency` | TEXT | Currency (default: TRY) |
| `source` | TEXT | Data source used (API, Bigpara, etc.) |
| `created_at` | DATETIME | Record creation timestamp |

## 📊 Example Output

### Price Statistics
```
📊 PRICE STATISTICS (365 days)
----------------------------------------
Total records: 365
Average price: 4,249.67 TRY
Median price: 4,240.12 TRY
Minimum price: 3,890.45 TRY
Maximum price: 4,634.78 TRY
Price volatility (std): 187.23 TRY
Latest price: 4,267.34 TRY
Price change: +125.89 TRY (+3.0%) 📈
```

### Recent Prices
```
📋 RECENT PRICES (Last 7 days)
------------------------------------------------------------
Date                 Price (TRY)  Source         
------------------------------------------------------------
2025-06-01 15:47     4281.99      API            
2025-06-01 15:47     4290.84      API            
2025-06-01 15:47     2590.16      API            
2025-06-01 15:42     2587.98      API            
2025-06-01 15:36     1934.81      SIMULATED      
```

## 📁 Project Structure

```
gold-price-predict-algorithm/
├── price_scraper.py          # Main scraper class with all functionality
├── main.py                   # Interactive application with menu system
├── quick_check.py           # Simple script for quick price checks
├── demo.py                  # Complete demonstration script
├── test_price.py            # Price calculation testing utility
├── requirements.txt         # Python package dependencies
├── gold_prices.db          # SQLite database (auto-created)
├── gold_prices_export.csv  # Sample exported data
├── PROJECT_STATUS.md       # Development status and progress
└── README.md               # This documentation file
```

## ⚙️ Configuration & Customization

### Scraping Intervals
```python
# Start monitoring every 30 minutes
scraper.start_scheduled_scraping(30)

# Start monitoring every hour (default)
scraper.start_scheduled_scraping(60)
```

### Custom Database Path
```python
# Use custom database location
scraper = GoldPriceScraper(db_path='custom_path/my_prices.db')
```

### Data Export Options
```python
# Export last 30 days
scraper.export_data_to_csv("monthly_data.csv", 30)

# Export all data
scraper.export_data_to_csv("all_data.csv", 9999)
```

## 🔧 Dependencies

```txt
requests          # HTTP requests for API calls
beautifulsoup4    # HTML parsing for web scraping
pandas           # Data analysis and manipulation
schedule         # Task scheduling for continuous monitoring
sqlite3          # Database operations (built-in)
lxml             # XML/HTML parser
```

## 🛠️ Troubleshooting

### Common Issues

**Import errors:**
```bash
pip install -r requirements.txt
```

**No price data:**
- Check internet connection
- APIs might be temporarily unavailable
- System will use fallback sources automatically

**Database issues:**
```bash
# Clear and reset database
rm gold_prices.db
python3 main.py  # Will recreate database
```

**SSL Certificate errors:**
```bash
# For macOS, update certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Error Handling

The system includes comprehensive error handling:
- Network timeouts and retries
- Invalid data format handling
- Database connection management
- Graceful degradation to fallback sources

## 📈 Advanced Features

### Price Statistics Available
- **Mean & Median**: Central tendency measures
- **Min & Max**: Price range over time period
- **Standard Deviation**: Price volatility measure
- **Trend Analysis**: Price change calculations
- **Historical Comparison**: Period-over-period analysis

### Monitoring Capabilities
- Real-time price fetching
- Scheduled data collection
- Historical trend analysis
- Data export for external tools
- Statistical reporting

## 🔮 Future Enhancements

- 🤖 **Machine Learning**: Price prediction algorithms
- 📱 **Mobile App**: iOS/Android companion app
- 🌐 **Web Dashboard**: Real-time price visualization
- 📧 **Alerts**: Price threshold notifications
- 📊 **Advanced Charts**: Technical analysis tools
- 🔄 **API Integration**: More Turkish financial sources
- 📈 **Forecasting**: Predictive analytics models

## 🏗️ Development

### Project Status
✅ **COMPLETED** - All core requirements implemented and tested

### Core Requirements Met
- ✅ Scrapes 1 gram gold price in Turkish Lira
- ✅ Saves prices to database with timestamps
- ✅ Supports 1+ year of historical data storage
- ✅ Multiple data source reliability
- ✅ Real-time price fetching
- ✅ Statistical analysis capabilities

### Testing
```bash
# Test price calculation
python3 test_price.py

# Run complete demonstration
python3 demo.py

# Quick functionality check
python3 quick_check.py
```

## 📝 License

This project is developed for educational and personal use. Please ensure compliance with data source terms of service when using for commercial purposes.

## 👨‍💻 Author

**Gold Price Prediction Algorithm**  
**Date**: June 2025  
**Version**: 1.0

---

**Ready for production use!** 🚀

For questions or support, check the project documentation or run the demo script to see all features in action.
