"""
Finance utility module for calculating financial ratios.
"""


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


if __name__ == "__main__":
    # Example usage
    price = 50000
    earnings_per_share = 2500

    per = calculate_per(price, earnings_per_share)
    print(f"Stock Price: {price}")
    print(f"EPS: {earnings_per_share}")
    print(f"PER: {per:.2f}")
