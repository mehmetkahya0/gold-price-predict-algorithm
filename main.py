#!/usr/bin/env python3
"""
Gold Price Prediction Algorithm - Main Entry Point
==================================================

This script demonstrates how to use the GoldPriceScraper to collect
Turkish gold price data and perform basic analysis.
"""

from price_scraper import GoldPriceScraper
import sys
import os

def print_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("GOLD PRICE SCRAPER & ANALYZER")
    print("="*50)
    print("1. Get current gold price")
    print("2. Start continuous monitoring (hourly)")
    print("3. Generate sample historical data")
    print("4. View price statistics")
    print("5. Export data to CSV")
    print("6. View recent prices")
    print("7. Clear database")
    print("8. Exit")
    print("-"*50)

def main():
    """Main application loop"""
    
    # Initialize the scraper
    print("Initializing Gold Price Scraper...")
    scraper = GoldPriceScraper()
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                print("\nFetching current gold price...")
                price = scraper.get_current_price()
                if price:
                    print(f"✅ Current gold price: {price} TRY per gram")
                else:
                    print("❌ Failed to fetch current price")
            
            elif choice == "2":
                print("\n⚠️  Starting continuous monitoring...")
                print("This will fetch prices every hour. Press Ctrl+C to stop.")
                try:
                    scraper.start_scheduled_scraping(60)  # Every 60 minutes
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped by user")
            
            elif choice == "3":
                days = input("Enter number of days to generate (default 365): ").strip()
                days = int(days) if days.isdigit() else 365
                print(f"\nGenerating {days} days of sample data...")
                scraper.generate_sample_data(days)
                print("✅ Sample data generated successfully")
            
            elif choice == "4":
                days = input("Enter number of days for statistics (default 365): ").strip()
                days = int(days) if days.isdigit() else 365
                
                print(f"\nCalculating statistics for last {days} days...")
                stats = scraper.get_price_statistics(days)
                
                if stats and stats['count'] > 0:
                    print(f"\n📊 PRICE STATISTICS ({days} days)")
                    print("-" * 40)
                    print(f"Total records: {stats['count']}")
                    print(f"Average price: {stats['mean']:.2f} TRY")
                    print(f"Median price: {stats['median']:.2f} TRY")
                    print(f"Minimum price: {stats['min']:.2f} TRY")
                    print(f"Maximum price: {stats['max']:.2f} TRY")
                    print(f"Price volatility (std): {stats['std']:.2f} TRY")
                    if stats['latest']:
                        print(f"Latest price: {stats['latest']:.2f} TRY")
                    
                    # Calculate price change
                    if stats['latest'] and stats['oldest']:
                        change = stats['latest'] - stats['oldest']
                        change_percent = (change / stats['oldest']) * 100
                        trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                        print(f"Price change: {change:+.2f} TRY ({change_percent:+.1f}%) {trend}")
                else:
                    print("❌ No data available for statistics")
            
            elif choice == "5":
                days = input("Enter number of days to export (default 365): ").strip()
                days = int(days) if days.isdigit() else 365
                filename = input("Enter filename (default: gold_prices_export.csv): ").strip()
                filename = filename if filename else "gold_prices_export.csv"
                
                print(f"\nExporting {days} days of data...")
                scraper.export_data_to_csv(filename, days)
                print(f"✅ Data exported to {filename}")
            
            elif choice == "6":
                days = input("Enter number of days to view (default 7): ").strip()
                days = int(days) if days.isdigit() else 7
                
                print(f"\nFetching last {days} days of data...")
                df = scraper.get_historical_data(days)
                
                if not df.empty:
                    print(f"\n📋 RECENT PRICES (Last {days} days)")
                    print("-" * 60)
                    print(f"{'Date':<20} {'Price (TRY)':<12} {'Source':<15}")
                    print("-" * 60)
                    
                    for _, row in df.head(20).iterrows():  # Show max 20 records
                        date_str = row['date_time'][:16]  # Format datetime
                        print(f"{date_str:<20} {row['price_per_gram']:<12.2f} {row['source']:<15}")
                    
                    if len(df) > 20:
                        print(f"... and {len(df) - 20} more records")
                else:
                    print("❌ No recent data available")
            
            elif choice == "7":
                confirm = input("⚠️  Are you sure you want to clear all data? (yes/no): ").strip().lower()
                if confirm == "yes":
                    try:
                        os.remove(scraper.db_path)
                        scraper.init_database()
                        print("✅ Database cleared successfully")
                    except Exception as e:
                        print(f"❌ Error clearing database: {e}")
                else:
                    print("Operation cancelled")
            
            elif choice == "8":
                print("\nThank you for using Gold Price Scraper! 👋")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Operation interrupted by user")
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
        
        # Pause before showing menu again
        if choice != "8":
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()