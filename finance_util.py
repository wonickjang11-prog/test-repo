"""
Finance utility module for calculating financial ratios and tracking daily stock data.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import time


def calculate_per(stock_price, eps):
    """
    Calculate PER (Price to Earnings Ratio).

    Args:
        stock_price (float): Current stock price
        eps (float): Earnings Per Share

    Returns:
        float: PER value (stock_price / eps)

    Raises:
        ValueError: If eps is zero or negative
        TypeError: If inputs are not numeric
    """
    if not isinstance(stock_price, (int, float)) or not isinstance(eps, (int, float)):
        raise TypeError("Stock price and EPS must be numeric values")

    if eps <= 0:
        raise ValueError("EPS must be greater than zero")

    if stock_price < 0:
        raise ValueError("Stock price cannot be negative")

    return stock_price / eps


def calculate_per_for_stocks(stocks_data):
    """
    Calculate PER for multiple stocks.

    Args:
        stocks_data (list): List of dictionaries containing stock information.
                           Each dictionary should have 'name', 'price', and 'eps' keys.
                           Example: [{'name': 'Samsung', 'price': 50000, 'eps': 2500}]

    Returns:
        pandas.DataFrame: DataFrame with stock name, price, EPS, and calculated PER

    Raises:
        ValueError: If stocks_data is empty or has invalid format
    """
    if not stocks_data:
        raise ValueError("stocks_data cannot be empty")

    results = []
    for stock in stocks_data:
        if not isinstance(stock, dict):
            raise ValueError("Each stock must be a dictionary")

        if 'name' not in stock or 'price' not in stock or 'eps' not in stock:
            raise ValueError("Each stock must have 'name', 'price', and 'eps' keys")

        try:
            per = calculate_per(stock['price'], stock['eps'])
            results.append({
                'Stock Name': stock['name'],
                'Price': stock['price'],
                'EPS': stock['eps'],
                'PER': round(per, 2)
            })
        except (ValueError, TypeError) as e:
            results.append({
                'Stock Name': stock['name'],
                'Price': stock['price'],
                'EPS': stock['eps'],
                'PER': f'Error: {str(e)}'
            })

    return pd.DataFrame(results)


def export_to_excel(stocks_data, filename='stock_report.xlsx', output_dir=None):
    """
    Calculate PER for multiple stocks and export to Excel file.

    Args:
        stocks_data (list): List of dictionaries containing stock information.
                           Each dictionary should have 'name', 'price', and 'eps' keys.
        filename (str): Output Excel filename (default: 'stock_report.xlsx')
        output_dir (str): Output directory path (default: current directory)

    Returns:
        str: Path to the created Excel file

    Raises:
        ValueError: If stocks_data is empty or has invalid format
    """
    df = calculate_per_for_stocks(stocks_data)

    # Create output directory if it doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Combine directory and filename
    if output_dir:
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = filename

    df.to_excel(filepath, index=False, engine='openpyxl')
    return filepath


def fetch_daily_stock_data(symbol, date=None):
    """
    Fetch daily stock data for a given symbol using Yahoo Finance API.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'NVDA')
        date (str or datetime): Date to fetch data for (default: today)
                               Format: 'YYYY-MM-DD' or datetime object

    Returns:
        dict: Dictionary containing daily stock data with keys:
              - date: Trading date
              - open: Opening price
              - close: Closing price
              - high: Highest price
              - low: Lowest price
              - volume: Trading volume
              - change: Price change (close - prev_close)
              - change_pct: Percentage change
              - prev_close: Previous day's closing price

    Raises:
        ValueError: If symbol is invalid or data cannot be fetched
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    # Parse date
    if date is None:
        target_date = datetime.now()
    elif isinstance(date, str):
        target_date = datetime.strptime(date, '%Y-%m-%d')
    elif isinstance(date, datetime):
        target_date = date
    else:
        raise ValueError("Date must be a string (YYYY-MM-DD) or datetime object")

    # Retry logic with exponential backoff
    max_retries = 4
    retry_delays = [2, 4, 8, 16]  # seconds

    try:
        # Use Yahoo Finance V8 API
        # Get data for a week to ensure we have previous close
        start_timestamp = int((target_date - timedelta(days=7)).timestamp())
        end_timestamp = int((target_date + timedelta(days=1)).timestamp())

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            'period1': start_timestamp,
            'period2': end_timestamp,
            'interval': '1d',
            'includePrePost': 'false'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }

        response = None
        last_error = None

        # Attempt with retries
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    delay = retry_delays[attempt - 1]
                    print(f"⏳ Retry {attempt}/{max_retries} after {delay}s...")
                    time.sleep(delay)

                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                break  # Success, exit retry loop

            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_retries:
                    print(f"⚠️  Network error on attempt {attempt + 1}: {type(e).__name__}")
                    continue
                else:
                    # All retries exhausted
                    raise ValueError(f"Network error fetching data for {symbol} after {max_retries} retries: {str(e)}")

        if response is None:
            raise ValueError(f"Failed to fetch data for {symbol} after {max_retries} retries")

        data = response.json()

        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            raise ValueError(f"No data available for {symbol}")

        result = data['chart']['result'][0]

        # Validate required structure
        if 'timestamp' not in result:
            raise ValueError(f"Invalid data structure for {symbol}: missing timestamp")
        if 'indicators' not in result or 'quote' not in result['indicators'] or not result['indicators']['quote']:
            raise ValueError(f"Invalid data structure for {symbol}: missing quote data")

        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]

        if not timestamps:
            raise ValueError(f"No trading data available for {symbol}")

        # Validate quote data has all required fields
        required_fields = ['open', 'close', 'high', 'low', 'volume']
        for field in required_fields:
            if field not in quotes:
                raise ValueError(f"Invalid data structure for {symbol}: missing {field} in quote data")

        # Convert timestamps to dates
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]

        # Find the most recent trading date on or before target_date
        target_idx = None
        for i in range(len(dates) - 1, -1, -1):  # Search backwards for most recent
            if dates[i].date() <= target_date.date():
                target_idx = i
                break

        if target_idx is None:
            raise ValueError(f"No trading data available on or before {target_date.strftime('%Y-%m-%d')}")

        # Get data for target date
        closest_date = dates[target_idx]
        open_price = quotes['open'][target_idx]
        close_price = quotes['close'][target_idx]
        high_price = quotes['high'][target_idx]
        low_price = quotes['low'][target_idx]
        volume = quotes['volume'][target_idx]

        # Validate that critical price data is not None
        if open_price is None:
            raise ValueError(f"Missing open price data for {symbol} on {closest_date.strftime('%Y-%m-%d')}")
        if close_price is None:
            raise ValueError(f"Missing close price data for {symbol} on {closest_date.strftime('%Y-%m-%d')}")
        if high_price is None:
            raise ValueError(f"Missing high price data for {symbol} on {closest_date.strftime('%Y-%m-%d')}")
        if low_price is None:
            raise ValueError(f"Missing low price data for {symbol} on {closest_date.strftime('%Y-%m-%d')}")

        # Get previous close
        if target_idx > 0:
            prev_close_price = quotes['close'][target_idx - 1]
            if prev_close_price is None:
                # Fallback to open price if previous close is not available
                prev_close_price = open_price
        else:
            prev_close_price = open_price

        # Calculate changes
        change = close_price - prev_close_price
        change_pct = (change / prev_close_price * 100) if prev_close_price > 0 else 0

        return {
            'date': closest_date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'close': round(close_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'volume': int(volume) if volume is not None else 0,
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'prev_close': round(prev_close_price, 2)
        }

    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Error parsing data for {symbol}: {str(e)}")
    except ValueError:
        raise  # Re-raise ValueError from above
    except Exception as e:
        raise ValueError(f"Unexpected error fetching data for {symbol}: {str(e)}")


def fetch_stock_news(symbol, date=None, max_results=5):
    """
    Fetch news for a given stock symbol using Google News RSS.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'NVDA')
        date (str or datetime): Date to fetch news for (default: today)
                               Format: 'YYYY-MM-DD' or datetime object
        max_results (int): Maximum number of news items to return (default: 5)

    Returns:
        list: List of dictionaries containing news items with keys:
              - title: News headline
              - publisher: News source
              - link: URL to the news article
              - published: Publication timestamp

    Raises:
        ValueError: If symbol is invalid or news cannot be fetched
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    # Retry logic with exponential backoff
    max_retries = 4
    retry_delays = [2, 4, 8, 16]  # seconds

    try:
        # Map symbol to company name for better search results
        company_names = {
            'NVDA': 'NVIDIA',
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla',
            'META': 'Meta'
        }
        search_term = company_names.get(symbol, symbol)

        # Use Google News RSS feed
        url = f"https://news.google.com/rss/search"
        params = {
            'q': f'{search_term} stock',
            'hl': 'en-US',
            'gl': 'US',
            'ceid': 'US:en'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/xml,text/xml,application/rss+xml',
            'Accept-Language': 'en-US,en;q=0.9'
        }

        response = None

        # Attempt with retries
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    delay = retry_delays[attempt - 1]
                    time.sleep(delay)

                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                break  # Success, exit retry loop

            except requests.exceptions.RequestException:
                if attempt >= max_retries:
                    # All retries exhausted, return empty list
                    print(f"Warning: Could not fetch news for {symbol} after {max_retries} retries")
                    return []
                continue

        if response is None:
            return []

        # Parse XML
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)

        # Parse date for filtering
        if date is None:
            target_date = datetime.now().date()
        elif isinstance(date, str):
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        elif isinstance(date, datetime):
            target_date = date.date()
        else:
            raise ValueError("Date must be a string (YYYY-MM-DD) or datetime object")

        # Extract news items
        news_items = []
        for item in root.findall('.//item')[:max_results * 2]:
            try:
                title = item.find('title').text
                link = item.find('link').text
                pub_date_str = item.find('pubDate').text

                # Parse publication date (RFC 822 format)
                from email.utils import parsedate_to_datetime
                pub_date = parsedate_to_datetime(pub_date_str)

                # Extract publisher from source tag if available
                source = item.find('source')
                publisher = source.text if source is not None else 'Unknown'

                # Filter by date (within 3 days of target)
                if abs((pub_date.date() - target_date).days) <= 3:
                    news_items.append({
                        'title': title,
                        'publisher': publisher,
                        'link': link,
                        'published': pub_date.strftime('%Y-%m-%d %H:%M:%S')
                    })

                if len(news_items) >= max_results:
                    break
            except (AttributeError, ValueError):
                continue

        return news_items

    except requests.exceptions.RequestException as e:
        # If news fetch fails, return empty list instead of raising error
        print(f"Warning: Could not fetch news for {symbol}: {str(e)}")
        return []
    except Exception as e:
        print(f"Warning: Error fetching news for {symbol}: {str(e)}")
        return []


def append_daily_record(stock_data, news_summary, filename='nvda_daily_tracker.xlsx', output_dir=None):
    """
    Append daily stock record to Excel file, creating it if it doesn't exist.

    Args:
        stock_data (dict): Dictionary containing stock data (from fetch_daily_stock_data)
        news_summary (str): Summary of news/reasons for the day's price movement
        filename (str): Output Excel filename (default: 'nvda_daily_tracker.xlsx')
        output_dir (str): Output directory path (default: current directory)

    Returns:
        str: Path to the Excel file

    Raises:
        ValueError: If stock_data is invalid
    """
    if not stock_data:
        raise ValueError("stock_data cannot be empty")

    required_keys = ['date', 'open', 'close', 'high', 'low', 'volume', 'change', 'change_pct', 'prev_close']
    for key in required_keys:
        if key not in stock_data:
            raise ValueError(f"stock_data must contain '{key}' key")

    # Create output directory if it doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Combine directory and filename
    filepath = os.path.join(output_dir, filename) if output_dir else filename

    # Prepare new record
    new_record = pd.DataFrame([{
        '날짜': stock_data['date'],
        '전일종가': stock_data['prev_close'],
        '시가': stock_data['open'],
        '종가': stock_data['close'],
        '최고가': stock_data['high'],
        '최저가': stock_data['low'],
        '거래량': stock_data['volume'],
        '변동가격': stock_data['change'],
        '변동률(%)': stock_data['change_pct'],
        '뉴스/이유': news_summary
    }])

    # Check if file exists
    if os.path.exists(filepath):
        # Read existing data
        existing_df = pd.read_excel(filepath, engine='openpyxl')

        # Check if date already exists
        if stock_data['date'] in existing_df['날짜'].values:
            # Update existing record
            existing_df.loc[existing_df['날짜'] == stock_data['date']] = new_record.iloc[0]
            df = existing_df
        else:
            # Append new record
            df = pd.concat([existing_df, new_record], ignore_index=True)
    else:
        # Create new file
        df = new_record

    # Sort by date (most recent first)
    df['날짜'] = pd.to_datetime(df['날짜'])
    df = df.sort_values('날짜', ascending=False)
    df['날짜'] = df['날짜'].dt.strftime('%Y-%m-%d')

    # Save to Excel
    df.to_excel(filepath, index=False, engine='openpyxl')
    return filepath


if __name__ == "__main__":
    # Example usage for single stock
    price = 50000
    earnings_per_share = 2500

    per = calculate_per(price, earnings_per_share)
    print(f"Stock Price: {price}")
    print(f"EPS: {earnings_per_share}")
    print(f"PER: {per:.2f}")

    # Example usage for multiple stocks
    print("\n=== Multiple Stocks Analysis ===")
    stocks = [
        {'name': 'Samsung Electronics', 'price': 70000, 'eps': 3500},
        {'name': 'SK Hynix', 'price': 120000, 'eps': 8000},
        {'name': 'NAVER', 'price': 250000, 'eps': 12500},
        {'name': 'Kakao', 'price': 90000, 'eps': 4500},
        {'name': 'Hyundai Motor', 'price': 180000, 'eps': 15000}
    ]

    df = calculate_per_for_stocks(stocks)
    print(df)

    # Export to Excel
    print("\n=== Exporting to Excel ===")
    output_file = export_to_excel(stocks)
    print(f"Excel file created: {output_file}")
