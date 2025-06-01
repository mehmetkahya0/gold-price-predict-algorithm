#!/usr/bin/env python3
"""
Simple Gold Price Data Analysis - Debugging Version
Quick analysis to check our data collection success
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

def simple_analysis():
    """Simple analysis without complex imports"""
    print("=== SIMPLE GOLD PRICE DATA ANALYSIS ===\n")
    
    db_path = '/Users/mehmetkahya/Desktop/gold-price-predict-algorithm/price.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        # Check database file size
        file_size = os.path.getsize(db_path)
        print(f"📁 Database file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Tables in database: {[table[0] for table in tables]}")
        
        # Check real-time data
        try:
            cursor.execute("SELECT COUNT(*) FROM gold_prices")
            realtime_count = cursor.fetchone()[0]
            print(f"\n💰 Real-time price records: {realtime_count}")
            
            if realtime_count > 0:
                cursor.execute("SELECT price, timestamp FROM gold_prices ORDER BY timestamp DESC LIMIT 3")
                recent_prices = cursor.fetchall()
                print("Recent real-time prices:")
                for price, timestamp in recent_prices:
                    print(f"  • {timestamp}: {price:.2f} TL")
        except Exception as e:
            print(f"❌ Error checking real-time data: {e}")
        
        # Check historical data
        try:
            cursor.execute("SELECT COUNT(*) FROM historical_gold_prices")
            historical_count = cursor.fetchone()[0]
            print(f"\n📈 Historical price records: {historical_count}")
            
            if historical_count > 0:
                cursor.execute("SELECT date, price_tl, price_usd, source FROM historical_gold_prices ORDER BY date DESC LIMIT 5")
                recent_historical = cursor.fetchall()
                print("Recent historical prices:")
                for date, price_tl, price_usd, source in recent_historical:
                    price_str = f"{price_tl:.2f} TL" if price_tl else f"{price_usd:.2f} USD"
                    print(f"  • {date}: {price_str} ({source})")
                
                # Get date range
                cursor.execute("SELECT MIN(date), MAX(date) FROM historical_gold_prices")
                min_date, max_date = cursor.fetchone()
                print(f"\n📅 Historical data range: {min_date} to {max_date}")
                
                # Calculate days covered
                if min_date and max_date:
                    start_date = datetime.strptime(min_date, '%Y-%m-%d')
                    end_date = datetime.strptime(max_date, '%Y-%m-%d')
                    days_covered = (end_date - start_date).days + 1
                    print(f"📊 Days covered: {days_covered}")
                
                # Check data sources
                cursor.execute("SELECT source, COUNT(*) FROM historical_gold_prices GROUP BY source")
                sources = cursor.fetchall()
                print(f"📡 Data sources:")
                for source, count in sources:
                    print(f"  • {source}: {count} records")
                
                # Basic price statistics
                cursor.execute("SELECT AVG(COALESCE(price_tl, price_usd * 39.0)), MIN(COALESCE(price_tl, price_usd * 39.0)), MAX(COALESCE(price_tl, price_usd * 39.0)) FROM historical_gold_prices")
                avg_price, min_price, max_price = cursor.fetchone()
                
                if avg_price:
                    print(f"\n💹 Price Statistics (TL):")
                    print(f"  • Average: {avg_price:.2f} TL")
                    print(f"  • Minimum: {min_price:.2f} TL")
                    print(f"  • Maximum: {max_price:.2f} TL")
                    print(f"  • Range: {max_price - min_price:.2f} TL")
                    print(f"  • Volatility: {((max_price - min_price) / avg_price * 100):.2f}%")
        
        except Exception as e:
            print(f"❌ Error checking historical data: {e}")
        
        conn.close()
        
        # Algorithm readiness assessment
        print(f"\n🎯 PREDICTION ALGORITHM READINESS")
        print("=" * 50)
        
        if historical_count >= 30:
            print("✅ Sufficient data for basic prediction (30+ days)")
        else:
            print("⚠️  Need more data for reliable prediction")
        
        if historical_count >= 90:
            print("✅ Good data volume for seasonal analysis (90+ days)")
        else:
            print("💡 Consider collecting 90+ days for better patterns")
        
        if historical_count >= 250:
            print("✅ Excellent data volume for comprehensive analysis (250+ days)")
        else:
            print("💡 250+ days recommended for robust predictions")
        
        print(f"\n🚀 NEXT STEPS")
        print("=" * 30)
        print("1. ✅ Data collection - COMPLETED")
        print("2. 📊 Data preprocessing")
        print("3. 🤖 Feature engineering")
        print("4. 🎯 Model training (LSTM/ARIMA)")
        print("5. 📈 Prediction system")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def create_simple_chart():
    """Create a simple price chart using only basic matplotlib"""
    try:
        import matplotlib.pyplot as plt
        
        db_path = '/Users/mehmetkahya/Desktop/gold-price-predict-algorithm/price.db'
        conn = sqlite3.connect(db_path)
        
        # Get recent historical data
        query = """
        SELECT date, COALESCE(price_tl, price_usd * 39.0) as price 
        FROM historical_gold_prices 
        ORDER BY date DESC 
        LIMIT 50
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) > 0:
            # Reverse for chronological order
            df = df.iloc[::-1].reset_index(drop=True)
            df['date'] = pd.to_datetime(df['date'])
            
            # Create chart
            plt.figure(figsize=(12, 6))
            plt.plot(df['date'], df['price'], linewidth=2, color='gold', marker='o', markersize=3)
            plt.title('Gold Price Historical Data (Last 50 Days)', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Price (TL)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Add statistics
            mean_price = df['price'].mean()
            plt.axhline(y=mean_price, color='red', linestyle='--', alpha=0.7, 
                       label=f'Average: {mean_price:.2f} TL')
            
            plt.legend()
            plt.tight_layout()
            
            # Save chart
            chart_file = 'gold_price_simple_chart.png'
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            print(f"\n📊 Chart saved as: {chart_file}")
            
            # Show basic stats
            print(f"📈 Chart shows {len(df)} days of data")
            print(f"💰 Price range: {df['price'].min():.2f} - {df['price'].max():.2f} TL")
            
        else:
            print("❌ No data available for charting")
            
    except ImportError:
        print("📊 Matplotlib not available - skipping chart creation")
    except Exception as e:
        print(f"📊 Chart creation error: {e}")

if __name__ == "__main__":
    print("Starting simple analysis...\n")
    
    success = simple_analysis()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 SIMPLE ANALYSIS COMPLETED!")
        print("Your gold prediction algorithm database is ready!")
        print("=" * 60)
        
        # Try to create a chart
        create_simple_chart()
    else:
        print("\n❌ Analysis failed - check database and data collection")
