# Gold price prediction using matplotlib, scikit-learn and tensorflow
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from scrape import GoldPriceScraper


def main():
    """Main function to demonstrate gold price scraping and basic analysis."""
    
    # Initialize the scraper
    scraper = GoldPriceScraper()
    
    # Scrape and save current price
    print("Scraping current gold price...")
    result = scraper.scrape_and_save()
    
    if result['success']:
        current_price = result['price_data']
        print(f"✅ Current gold price: {current_price['price']:.2f} TL")
        print(f"📅 Timestamp: {current_price['timestamp']}")
        print(f"📝 Raw text: {current_price['raw_price_text']}")
    else:
        print(f"❌ Failed to scrape price: {result['message']}")
        return
    
    # Get price history
    print("\nFetching price history...")
    history = scraper.get_price_history(limit=50)
    
    if len(history) > 1:
        print(f"📊 Found {len(history)} price records in database")
        
        # Basic analysis
        prices = [record['price'] for record in history]
        timestamps = [record['timestamp'] for record in history]
        
        print(f"💰 Average price: {np.mean(prices):.2f} TL")
        print(f"📈 Max price: {max(prices):.2f} TL")
        print(f"📉 Min price: {min(prices):.2f} TL")
        
        # Simple price trend
        if len(prices) >= 2:
            recent_trend = prices[0] - prices[1]
            trend_indicator = "📈" if recent_trend > 0 else "📉" if recent_trend < 0 else "➡️"
            print(f"{trend_indicator} Recent trend: {recent_trend:+.2f} TL")
        
        # Plot price history if we have enough data
        if len(history) >= 5:
            plot_price_history(history)
    else:
        print("📝 Not enough historical data for analysis")


def plot_price_history(history):
    """Plot price history using matplotlib."""
    try:
        # Reverse to show chronological order
        history.reverse()
        
        prices = [record['price'] for record in history]
        timestamps = [datetime.fromisoformat(record['timestamp']) for record in history]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, prices, marker='o', linewidth=2, markersize=4)
        plt.title('Gold Price History (TL per gram)', fontsize=16, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Price (TL)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Add latest price annotation
        if len(prices) > 0:
            plt.annotate(f'Latest: {prices[-1]:.2f} TL', 
                        xy=(timestamps[-1], prices[-1]),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.show()
        print("📊 Price chart displayed")
        
    except Exception as e:
        print(f"❌ Could not create chart: {e}")


def schedule_price_collection():
    """Example function for scheduled price collection."""
    import time
    
    scraper = GoldPriceScraper()
    
    print("🔄 Starting scheduled price collection...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            result = scraper.scrape_and_save()
            
            if result['success']:
                price_data = result['price_data']
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Price: {price_data['price']:.2f} TL")
            else:
                print(f"❌ {datetime.now().strftime('%H:%M:%S')} - Error: {result['message']}")
            
            # Wait 5 minutes before next scrape
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n🛑 Price collection stopped")


if __name__ == "__main__":
    main()
    
    # Uncomment to run scheduled collection
    # schedule_price_collection()
