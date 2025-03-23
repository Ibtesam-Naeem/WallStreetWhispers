import os
import requests
import logging
from utils.formatters import format_number, format_eps
from dotenv import load_dotenv
# ---------------------------- ENV SETUP ----------------------------
load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL")
BASE_URL = "https://api.polygon.io"

# ---------------------------- LOGGER SETUP ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ---------------------------- API CLIENTS ----------------------------
def get_top_stocks():
    """
    Fetches the latest top stocks from
    the backend API.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/top-stocks")
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            stocks = data.get("data", [])
            return list({stock["ticker"] for stock in stocks})
        
        logging.warning("Failed to fetch top stocks from backend.")
        return []
    
    except Exception as e:
        logging.error(f"Error fetching top stocks: {e}")
        return []

def get_financial_data(ticker):
    """
    Fetch financials for a given ticker from 
    Polygon API.
    """
    url = f"{BASE_URL}/vX/reference/financials"
    params = {
        "ticker": ticker,
        "limit": 8,
        "timeframe": "quarterly",
        "apiKey": POLYGON_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            logging.info(f"No financial data found for {ticker}")
            return None

        sorted_results = sorted(
            results,
            key=lambda x: (x.get("fiscal_year", 0), x.get("fiscal_period", "")),
            reverse=True
        )

        return format_financial_data(ticker, sorted_results)

    except Exception as e:
        logging.error(f"Error fetching financial data for {ticker}: {e}")
        return None

# ---------------------------- FORMATTERS ----------------------------

def format_financial_data(ticker, sorted_results):
    """
    Prepare financial data for tweets.
    """
    tweet_data = {
        "ticker": ticker,
        "revenue": [],
        "net_income": [],
        "eps": []
    }

    for report in sorted_results:
        fiscal_year = report.get("fiscal_year", "N/A")
        fiscal_period = report.get("fiscal_period", "N/A")
        period = f"{fiscal_year} {fiscal_period}"

        income_statement = report.get("financials", {}).get("income_statement", {})
        revenues_value = income_statement.get("revenues", {}).get("value")
        eps_value = income_statement.get("basic_earnings_per_share", {}).get("value")
        net_income = income_statement.get("net_income_loss", {}).get("value")

        tweet_data["revenue"].append(f"{period}: {format_number(revenues_value)}")
        tweet_data["net_income"].append(f"{period}: {format_number(net_income)}")
        tweet_data["eps"].append(f"{period}: {format_eps(eps_value)}")

    return tweet_data

def format_tweet_thread(tweet_data):
    """
    Format the financial data into tweet thread format.
    """
    if not tweet_data:
        return []

    ticker = tweet_data["ticker"]

    tweets = [
        f"{ticker} QUARTERLY REVENUE (Last 8 Quarters)\n\n" + "\n".join(tweet_data["revenue"]),
        f"{ticker} NET INCOME (Last 8 Quarters)\n\n" + "\n".join(tweet_data["net_income"]),
        f"{ticker} EPS (Basic, Last 8 Quarters)\n\n" + "\n".join(tweet_data["eps"])
    ]

    return tweets

# ---------------------------- MAIN RUNNER ----------------------------
def polygon():
    logging.info("Fetching top stocks from backend API...")

    tickers = get_top_stocks()
    if not tickers:
        logging.warning("No stocks found from backend API.")
        return []

    logging.info(f"Found {len(tickers)} tickers to process.")

    all_tweet_threads = []
    for ticker in tickers:
        logging.info(f"Processing {ticker}...")

        financial_data = get_financial_data(ticker)
        if financial_data:
            tweet_thread = format_tweet_thread(financial_data)
            all_tweet_threads.append(tweet_thread)
        else:
            logging.warning(f"No financial data available for {ticker}")

    return all_tweet_threads
