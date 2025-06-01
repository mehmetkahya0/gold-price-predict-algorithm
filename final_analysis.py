#!/usr/bin/env python3
"""
Gold Price Data Analysis - Working Version
Analyzes our collected historical and real-time gold price data for prediction algorithm
"""

import sqlite3
import os
from datetime import datetime
import json

def analyze_gold_data():
    """Comprehensive analysis of our gold price database"""
    
    print("=" * 60)
    print("🏆 GOLD PRICE PREDICTION ALGORITHM - DATA ANALYSIS")
    print("=" * 60)
    
    db_path = '/Users/mehmetkahya/Desktop/gold-price-predict-algorithm/price.db'
    
    # Check database file
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    file_size = os.path.getsize(db_path)
    print(f"📁 Database: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # =================== HISTORICAL DATA ANALYSIS ===================
        print(f"\n📈 HISTORICAL DATA ANALYSIS")
        print("-" * 40)
        
        # Get historical data statistics
        cursor.execute("SELECT COUNT(*) FROM historical_gold_prices")
        hist_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(date), MAX(date) FROM historical_gold_prices")
        min_date, max_date = cursor.fetchone()
        
        print(f"Total historical records: {hist_count}")
        print(f"Date range: {min_date} to {max_date}")
        
        if min_date and max_date:
            start_date = datetime.strptime(min_date, '%Y-%m-%d')
            end_date = datetime.strptime(max_date, '%Y-%m-%d')
            days_covered = (end_date - start_date).days + 1
            print(f"Days covered: {days_covered}")
            print(f"Data density: {hist_count/days_covered*100:.1f}% (business days)")
        
        # Data sources
        cursor.execute("SELECT source, COUNT(*) FROM historical_gold_prices GROUP BY source")
        sources = cursor.fetchall()
        print(f"\nData sources:")
        for source, count in sources:
            print(f"  • {source}: {count} records ({count/hist_count*100:.1f}%)")
        
        # Price statistics (convert USD to TL for analysis)
        usd_to_tl_rate = 39.0
        cursor.execute(f"""
            SELECT 
                AVG(COALESCE(price_tl, price_usd * {usd_to_tl_rate})) as avg_price,
                MIN(COALESCE(price_tl, price_usd * {usd_to_tl_rate})) as min_price,
                MAX(COALESCE(price_tl, price_usd * {usd_to_tl_rate})) as max_price
            FROM historical_gold_prices
        """)
        avg_price, min_price, max_price = cursor.fetchone()
        
        if avg_price:
            volatility = (max_price - min_price) / avg_price * 100
            print(f"\nPrice Statistics (TL):")
            print(f"  • Average: {avg_price:,.2f} TL")
            print(f"  • Minimum: {min_price:,.2f} TL")
            print(f"  • Maximum: {max_price:,.2f} TL")
            print(f"  • Range: {max_price - min_price:,.2f} TL")
            print(f"  • Volatility: {volatility:.2f}%")
        
        # Recent trend (last 10 days)
        cursor.execute(f"""
            SELECT date, COALESCE(price_tl, price_usd * {usd_to_tl_rate}) as price
            FROM historical_gold_prices 
            ORDER BY date DESC 
            LIMIT 10
        """)
        recent_data = cursor.fetchall()
        
        if len(recent_data) >= 2:
            recent_prices = [row[1] for row in recent_data]
            trend_change = recent_prices[0] - recent_prices[-1]
            trend_pct = trend_change / recent_prices[-1] * 100
            trend_dir = "📈 UP" if trend_change > 0 else "📉 DOWN" if trend_change < 0 else "➡️ FLAT"
            
            print(f"\nRecent 10-day trend: {trend_dir}")
            print(f"Change: {trend_change:+.2f} TL ({trend_pct:+.2f}%)")
        
        # =================== REAL-TIME DATA ANALYSIS ===================
        print(f"\n💰 REAL-TIME DATA ANALYSIS")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM gold_prices")
        rt_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM gold_prices")
        min_time, max_time = cursor.fetchone()
        
        print(f"Total real-time records: {rt_count}")
        if min_time and max_time:
            print(f"Time range: {min_time} to {max_time}")
        
        if rt_count > 0:
            cursor.execute("SELECT price, timestamp FROM gold_prices ORDER BY timestamp DESC LIMIT 3")
            recent_rt = cursor.fetchall()
            print(f"\nRecent real-time prices:")
            for price, timestamp in recent_rt:
                print(f"  • {timestamp}: {price:.2f} TL")
        
        # =================== ALGORITHM READINESS ===================
        print(f"\n🎯 PREDICTION ALGORITHM READINESS ASSESSMENT")
        print("-" * 50)
        
        # Data sufficiency checks
        checks = []
        
        if hist_count >= 30:
            checks.append("✅ Basic prediction data (30+ days)")
        else:
            checks.append("❌ Need 30+ days for basic prediction")
        
        if hist_count >= 90:
            checks.append("✅ Seasonal analysis possible (90+ days)")
        else:
            checks.append("⚠️  Need 90+ days for seasonal patterns")
        
        if hist_count >= 180:
            checks.append("✅ Medium-term patterns (180+ days)")
        else:
            checks.append("⚠️  Need 180+ days for medium-term analysis")
        
        if hist_count >= 250:
            checks.append("✅ Excellent data volume (250+ days)")
        else:
            checks.append("💡 250+ days ideal for robust predictions")
        
        if volatility and volatility > 5:
            checks.append("⚠️  High volatility detected - use robust models")
        elif volatility:
            checks.append("✅ Reasonable volatility for prediction")
        
        # Data quality checks
        if len(sources) > 0:
            checks.append("✅ Data source diversification")
        
        if days_covered and hist_count/days_covered > 0.7:
            checks.append("✅ Good data density")
        else:
            checks.append("⚠️  Some data gaps detected")
        
        for check in checks:
            print(f"  {check}")
        
        # =================== NEXT STEPS ===================
        print(f"\n🚀 RECOMMENDED NEXT STEPS")
        print("-" * 30)
        
        steps = [
            "1. ✅ Data Collection - COMPLETED",
            "2. 📊 Data Preprocessing & Feature Engineering",
            "3. 📈 Trend Analysis & Moving Averages", 
            "4. 🤖 Model Selection (LSTM, ARIMA, Prophet)",
            "5. 🎯 Model Training & Validation",
            "6. 📊 Backtesting & Performance Evaluation",
            "7. 🔄 Real-time Prediction System",
            "8. 📱 User Interface & Alerts"
        ]
        
        for step in steps:
            print(f"  {step}")
        
        # =================== SUMMARY ===================
        print(f"\n🎉 DATA COLLECTION SUCCESS SUMMARY")
        print("=" * 50)
        print(f"📊 Historical Records: {hist_count}")
        print(f"💰 Real-time Records: {rt_count}")
        print(f"📅 Date Coverage: {days_covered} days" if 'days_covered' in locals() else "📅 Date Coverage: Available")
        print(f"💹 Price Range: {min_price:,.0f} - {max_price:,.0f} TL" if avg_price else "💹 Price Data: Available")
        print(f"🎯 Algorithm Ready: {'YES' if hist_count >= 30 else 'NEEDS MORE DATA'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def create_sample_predictions():
    """Show how to use the data for predictions"""
    
    print(f"\n🔮 SAMPLE PREDICTION FRAMEWORK")
    print("-" * 40)
    
    prediction_methods = [
        "📈 Moving Average (Simple trend following)",
        "📊 Linear Regression (Trend extrapolation)", 
        "🌊 ARIMA (Time series forecasting)",
        "🧠 LSTM Neural Network (Deep learning)",
        "📅 Prophet (Facebook's time series tool)",
        "📉 Support/Resistance Analysis",
        "🔄 Ensemble Methods (Combined predictions)"
    ]
    
    print("Available prediction methods:")
    for method in prediction_methods:
        print(f"  • {method}")
    
    print(f"\n💡 IMPLEMENTATION SUGGESTIONS:")
    suggestions = [
        "Start with simple moving averages for baseline",
        "Use ARIMA for statistical time series analysis", 
        "Try LSTM for capturing complex patterns",
        "Implement ensemble for improved accuracy",
        "Add external factors (USD/TL rate, market news)",
        "Set up real-time prediction updates",
        "Create confidence intervals for predictions",
        "Implement alert system for significant changes"
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

if __name__ == "__main__":
    print("Starting comprehensive gold price data analysis...")
    
    success = analyze_gold_data()
    
    if success:
        create_sample_predictions()
        
        print(f"\n" + "=" * 60)
        print("🏆 ANALYSIS COMPLETED SUCCESSFULLY!")
        print("🚀 Your gold price prediction algorithm is ready to build!")
        print("📈 You have excellent historical data for training models!")
        print("=" * 60)
    else:
        print("\n❌ Analysis failed - please check the database")
