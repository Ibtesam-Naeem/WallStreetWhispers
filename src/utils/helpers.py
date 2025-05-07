def parse_market_cap(market_cap_str):
    """
    Parses a market cap string into a numeric value.
    Supports formats like $1.2B, $500M...
    """
    if not market_cap_str:
        return 0

    try:
        value = market_cap_str.replace("$", "").replace(",", "").strip()

        if value.endswith("B"):
            return float(value[:-1]) * 1_000_000_000
        elif value.endswith("M"):
            return float(value[:-1]) * 1_000_000
        else:
            return float(value)

    except (ValueError, TypeError):
        return 0

def sort_by_market_cap(earnings_list):
    """
    Sorts a list of earnings by market cap (descending).
    Adds 'Market Cap Numeric' field for sorting purposes.
    """
    for earning in earnings_list:
        earning["Market Cap Numeric"] = parse_market_cap(earning.get("Market Cap"))

    return sorted(earnings_list, key=lambda x: x.get("Market Cap Numeric", 0), reverse=True)
