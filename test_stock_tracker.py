#!/usr/bin/env python3
"""
Test script for stock tracker to verify real data fetching.
"""

import sys
from datetime import datetime
from finance_util import fetch_daily_stock_data, fetch_stock_news


def test_stock_data_fetch(symbol='NVDA'):
    """Test fetching stock data from Yahoo Finance API."""
    print("=" * 70)
    print(f"Testing Stock Data Fetch for {symbol}")
    print("=" * 70)

    try:
        print(f"\n🔍 Attempting to fetch real-time data for {symbol}...")
        print(f"📅 Current date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Fetch stock data
        stock_data = fetch_daily_stock_data(symbol)

        print("✅ Successfully fetched stock data!")
        print("\n" + "─" * 70)
        print("📊 Stock Data Details:")
        print("─" * 70)
        print(f"  Date:           {stock_data['date']}")
        print(f"  Previous Close: ${stock_data['prev_close']:,.2f}")
        print(f"  Open:           ${stock_data['open']:,.2f}")
        print(f"  Close:          ${stock_data['close']:,.2f}")
        print(f"  High:           ${stock_data['high']:,.2f}")
        print(f"  Low:            ${stock_data['low']:,.2f}")
        print(f"  Volume:         {stock_data['volume']:,}")
        print(f"  Change:         ${stock_data['change']:,.2f} ({stock_data['change_pct']:+.2f}%)")

        # Direction indicator
        if stock_data['change'] > 0:
            print(f"  Trend:          📈 UP")
        elif stock_data['change'] < 0:
            print(f"  Trend:          📉 DOWN")
        else:
            print(f"  Trend:          ➡️  FLAT")

        print("─" * 70)

        return True, stock_data

    except Exception as e:
        print(f"❌ Failed to fetch stock data")
        print(f"\nError: {str(e)}")
        print("\n" + "─" * 70)
        print("⚠️  Troubleshooting Tips:")
        print("─" * 70)
        print("  1. Check your internet connection")
        print("  2. Verify the stock symbol is valid")
        print("  3. Try again after a few minutes (rate limiting)")
        print("  4. Check if Yahoo Finance API is accessible")
        print("─" * 70)
        return False, None


def test_news_fetch(symbol='NVDA', date=None):
    """Test fetching news from Google News RSS."""
    print("\n" + "=" * 70)
    print(f"Testing News Fetch for {symbol}")
    print("=" * 70)

    try:
        print(f"\n🔍 Attempting to fetch news for {symbol}...")

        # Fetch news
        news_items = fetch_stock_news(symbol, date)

        if news_items:
            print(f"✅ Successfully fetched {len(news_items)} news items!")
            print("\n" + "─" * 70)
            print("📰 Latest News:")
            print("─" * 70)

            for i, news in enumerate(news_items, 1):
                print(f"\n{i}. {news['title']}")
                print(f"   Publisher: {news['publisher']}")
                print(f"   Published: {news['published']}")
                print(f"   Link: {news['link']}")

            print("─" * 70)
        else:
            print("⚠️  No news items found (this is OK, news may not always be available)")

        return True, news_items

    except Exception as e:
        print(f"❌ Failed to fetch news")
        print(f"\nError: {str(e)}")
        return False, None


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Stock Tracker Real Data Test Suite".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    # Test 1: Stock data fetch
    stock_success, stock_data = test_stock_data_fetch('NVDA')

    # Test 2: News fetch
    news_success, news_items = test_news_fetch('NVDA')

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"  Stock Data Fetch: {'✅ PASS' if stock_success else '❌ FAIL'}")
    print(f"  News Fetch:       {'✅ PASS' if news_success else '⚠️  WARN (not critical)'}")
    print("=" * 70)

    if stock_success:
        print("\n🎉 The stock tracker is working correctly with real data!")
        print("   You can now use nvda_daily_tracker.py to track NVIDIA stock.\n")
        return 0
    else:
        print("\n⚠️  The stock tracker encountered issues.")
        print("   Please check the troubleshooting tips above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
