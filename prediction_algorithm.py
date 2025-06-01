#!/usr/bin/env python3
"""
Gold Price Prediction Algorithm - Starter Implementation
Using our collected historical data to make price predictions
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta
import json

class GoldPricePredictionAlgorithm:
    """Simple gold price prediction algorithm using collected historical data"""
    
    def __init__(self, db_path='price.db'):
        self.db_path = db_path
        self.usd_to_tl_rate = 39.0  # Current approximate rate
        
    def load_historical_data(self, days=None):
        """Load historical price data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if days:
                # Get last N days
                query = f"""
                    SELECT date, COALESCE(price_tl, price_usd * {self.usd_to_tl_rate}) as price
                    FROM historical_gold_prices 
                    ORDER BY date DESC 
                    LIMIT {days}
                """
            else:
                # Get all data
                query = f"""
                    SELECT date, COALESCE(price_tl, price_usd * {self.usd_to_tl_rate}) as price
                    FROM historical_gold_prices 
                    ORDER BY date ASC
                """
            
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            
            if not data:
                return [], []
            
            dates = [row[0] for row in data]
            prices = [float(row[1]) for row in data]
            
            return dates, prices
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return [], []
    
    def simple_moving_average_prediction(self, window=7, forecast_days=1):
        """Simple moving average prediction"""
        dates, prices = self.load_historical_data()
        
        if len(prices) < window:
            return None, "Not enough data for moving average"
        
        # Calculate moving average for the last 'window' days
        recent_prices = prices[-window:]
        moving_avg = np.mean(recent_prices)
        
        # Simple prediction: assume price will be close to moving average
        predicted_price = moving_avg
        
        # Calculate confidence based on recent volatility
        recent_std = np.std(recent_prices)
        confidence = max(0, 100 - (recent_std / moving_avg * 100))
        
        return {
            'method': 'Simple Moving Average',
            'window_days': window,
            'predicted_price': round(predicted_price, 2),
            'confidence': round(confidence, 1),
            'price_range': {
                'low': round(predicted_price - recent_std, 2),
                'high': round(predicted_price + recent_std, 2)
            },
            'based_on_days': len(prices),
            'last_actual_price': round(prices[-1], 2)
        }
    
    def trend_analysis_prediction(self, days=30):
        """Linear trend analysis prediction"""
        dates, prices = self.load_historical_data(days)
        
        if len(prices) < 10:
            return None, "Not enough data for trend analysis"
        
        # Simple linear regression
        x = np.arange(len(prices))
        z = np.polyfit(x, prices, 1)
        trend_slope = z[0]  # Price change per day
        
        # Predict next day price
        next_price = prices[-1] + trend_slope
        
        # Calculate trend strength
        price_range = max(prices) - min(prices)
        trend_strength = abs(trend_slope * len(prices)) / price_range * 100
        
        trend_direction = "UPWARD" if trend_slope > 0 else "DOWNWARD"
        
        return {
            'method': 'Linear Trend Analysis',
            'analysis_days': days,
            'predicted_price': round(next_price, 2),
            'trend_direction': trend_direction,
            'daily_change': round(trend_slope, 2),
            'trend_strength': round(trend_strength, 1),
            'based_on_days': len(prices),
            'last_actual_price': round(prices[-1], 2)
        }
    
    def volatility_analysis(self, days=30):
        """Analyze price volatility for risk assessment"""
        dates, prices = self.load_historical_data(days)
        
        if len(prices) < 5:
            return None
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(prices)):
            daily_return = (prices[i] - prices[i-1]) / prices[i-1] * 100
            returns.append(daily_return)
        
        volatility = np.std(returns)
        avg_return = np.mean(returns)
        
        # Risk assessment
        if volatility < 1:
            risk_level = "LOW"
        elif volatility < 3:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"
        
        return {
            'volatility_percent': round(volatility, 2),
            'average_daily_return': round(avg_return, 2),
            'risk_level': risk_level,
            'analysis_days': days,
            'price_stability': "STABLE" if volatility < 2 else "VOLATILE"
        }
    
    def support_resistance_levels(self, days=60):
        """Identify support and resistance levels"""
        dates, prices = self.load_historical_data(days)
        
        if len(prices) < 20:
            return None
        
        # Simple support/resistance calculation
        sorted_prices = sorted(prices)
        
        # Support levels (lower prices where price bounced back)
        support_level = np.percentile(sorted_prices, 20)
        
        # Resistance levels (higher prices where price fell back)
        resistance_level = np.percentile(sorted_prices, 80)
        
        current_price = prices[-1]
        
        # Determine position relative to support/resistance
        if current_price <= support_level * 1.02:
            position = "NEAR_SUPPORT"
            signal = "POTENTIAL_BUY"
        elif current_price >= resistance_level * 0.98:
            position = "NEAR_RESISTANCE"
            signal = "POTENTIAL_SELL"
        else:
            position = "MIDDLE_RANGE"
            signal = "HOLD"
        
        return {
            'support_level': round(support_level, 2),
            'resistance_level': round(resistance_level, 2),
            'current_price': round(current_price, 2),
            'position': position,
            'trading_signal': signal,
            'analysis_days': days
        }
    
    def comprehensive_prediction(self):
        """Combine multiple prediction methods for better accuracy"""
        
        print("🔮 GOLD PRICE PREDICTION ANALYSIS")
        print("=" * 50)
        
        # Method 1: Moving Average
        ma_pred = self.simple_moving_average_prediction(window=7)
        if ma_pred:
            print(f"\n📈 Moving Average Prediction (7-day):")
            print(f"  Predicted Price: {ma_pred['predicted_price']:,} TL")
            print(f"  Confidence: {ma_pred['confidence']}%")
            print(f"  Range: {ma_pred['price_range']['low']:,} - {ma_pred['price_range']['high']:,} TL")
        
        # Method 2: Trend Analysis
        trend_pred = self.trend_analysis_prediction(days=30)
        if trend_pred:
            print(f"\n📊 Trend Analysis Prediction (30-day):")
            print(f"  Predicted Price: {trend_pred['predicted_price']:,} TL")
            print(f"  Trend: {trend_pred['trend_direction']}")
            print(f"  Daily Change: {trend_pred['daily_change']:+.2f} TL")
            print(f"  Trend Strength: {trend_pred['trend_strength']}%")
        
        # Method 3: Volatility Analysis
        volatility = self.volatility_analysis(days=30)
        if volatility:
            print(f"\n⚡ Volatility Analysis (30-day):")
            print(f"  Risk Level: {volatility['risk_level']}")
            print(f"  Volatility: {volatility['volatility_percent']}%")
            print(f"  Avg Daily Return: {volatility['average_daily_return']:+.2f}%")
            print(f"  Market Status: {volatility['price_stability']}")
        
        # Method 4: Support/Resistance
        sr_levels = self.support_resistance_levels(days=60)
        if sr_levels:
            print(f"\n🎯 Support/Resistance Analysis (60-day):")
            print(f"  Support Level: {sr_levels['support_level']:,} TL")
            print(f"  Resistance Level: {sr_levels['resistance_level']:,} TL")
            print(f"  Current Position: {sr_levels['position']}")
            print(f"  Trading Signal: {sr_levels['trading_signal']}")
        
        # Combined Prediction
        print(f"\n🎯 COMBINED PREDICTION SUMMARY")
        print("-" * 30)
        
        predictions = []
        if ma_pred:
            predictions.append(ma_pred['predicted_price'])
        if trend_pred:
            predictions.append(trend_pred['predicted_price'])
        
        if len(predictions) >= 2:
            avg_prediction = np.mean(predictions)
            prediction_range = max(predictions) - min(predictions)
            
            print(f"Average Prediction: {avg_prediction:,.2f} TL")
            print(f"Prediction Range: {prediction_range:.2f} TL")
            print(f"Prediction Agreement: {'HIGH' if prediction_range < 1000 else 'MODERATE' if prediction_range < 3000 else 'LOW'}")
        
        # Investment Recommendation
        print(f"\n💡 INVESTMENT RECOMMENDATION")
        print("-" * 30)
        
        signals = []
        if sr_levels:
            signals.append(sr_levels['trading_signal'])
        
        if trend_pred and trend_pred['trend_direction'] == 'UPWARD':
            signals.append('POTENTIAL_BUY')
        elif trend_pred and trend_pred['trend_direction'] == 'DOWNWARD':
            signals.append('POTENTIAL_SELL')
        
        if volatility and volatility['risk_level'] == 'HIGH':
            signals.append('CAUTION')
        
        # Count signal types
        buy_signals = signals.count('POTENTIAL_BUY')
        sell_signals = signals.count('POTENTIAL_SELL') 
        hold_signals = signals.count('HOLD')
        caution_signals = signals.count('CAUTION')
        
        if buy_signals > sell_signals and caution_signals == 0:
            recommendation = "💚 CONSIDER BUYING"
        elif sell_signals > buy_signals:
            recommendation = "❤️ CONSIDER SELLING"
        elif caution_signals > 0:
            recommendation = "⚠️ EXERCISE CAUTION"
        else:
            recommendation = "💛 HOLD POSITION"
        
        print(f"Recommendation: {recommendation}")
        print(f"Confidence: {'HIGH' if abs(buy_signals - sell_signals) >= 2 else 'MODERATE'}")
        
        return {
            'moving_average': ma_pred,
            'trend_analysis': trend_pred,
            'volatility': volatility,
            'support_resistance': sr_levels,
            'recommendation': recommendation
        }

def show_data_summary():
    """Show summary of our collected data"""
    
    try:
        conn = sqlite3.connect('price.db')
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM historical_gold_prices")
        count, min_date, max_date = cursor.fetchone()
        
        cursor.execute("SELECT ROUND(AVG(price_usd * 39), 2), ROUND(MIN(price_usd * 39), 2), ROUND(MAX(price_usd * 39), 2) FROM historical_gold_prices")
        avg_price, min_price, max_price = cursor.fetchone()
        
        conn.close()
        
        print("📊 COLLECTED DATA SUMMARY")
        print("=" * 30)
        print(f"Total Records: {count}")
        print(f"Date Range: {min_date} to {max_date}")
        print(f"Average Price: {avg_price:,} TL")
        print(f"Price Range: {min_price:,} - {max_price:,} TL")
        print(f"Data Quality: {'EXCELLENT' if count >= 200 else 'GOOD' if count >= 100 else 'ADEQUATE'}")
        
        # Calculate days covered
        if min_date and max_date:
            start_date = datetime.strptime(min_date, '%Y-%m-%d')
            end_date = datetime.strptime(max_date, '%Y-%m-%d')
            days_covered = (end_date - start_date).days + 1
            print(f"Coverage: {days_covered} days ({count/days_covered*100:.1f}% density)")
        
        return True
        
    except Exception as e:
        print(f"Error reading data: {e}")
        return False

if __name__ == "__main__":
    print("🏆 GOLD PRICE PREDICTION ALGORITHM")
    print("=" * 50)
    
    # Show data summary
    if show_data_summary():
        print("")
        
        # Create prediction algorithm instance
        predictor = GoldPricePredictionAlgorithm()
        
        # Run comprehensive prediction
        results = predictor.comprehensive_prediction()
        
        print(f"\n" + "=" * 50)
        print("🎉 PREDICTION ANALYSIS COMPLETED!")
        print("📈 Use these insights for your gold trading decisions!")
        print("⚠️  Remember: Past performance doesn't guarantee future results!")
        print("=" * 50)
    else:
        print("❌ Could not load data for prediction analysis")
