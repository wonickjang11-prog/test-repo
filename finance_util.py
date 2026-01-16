"""
Finance utility module for calculating financial ratios.
"""

import pandas as pd


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


def export_to_excel(stocks_data, filename='stock_report.xlsx'):
    """
    Calculate PER for multiple stocks and export to Excel file.

    Args:
        stocks_data (list): List of dictionaries containing stock information.
                           Each dictionary should have 'name', 'price', and 'eps' keys.
        filename (str): Output Excel filename (default: 'stock_report.xlsx')

    Returns:
        str: Path to the created Excel file

    Raises:
        ValueError: If stocks_data is empty or has invalid format
    """
    df = calculate_per_for_stocks(stocks_data)
    df.to_excel(filename, index=False, engine='openpyxl')
    return filename


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
