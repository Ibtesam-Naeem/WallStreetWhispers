import os
import logging
from dotenv import load_dotenv
from sec_api import QueryApi
from utils.formatters import format_number, format_eps

# ---------------------------- ENV & LOGGER SETUP ---------------------------- #
load_dotenv()
SEC_API_KEY = os.getenv("SEC_API_KEY")

logger = logging.getLogger("SECFetcher")
logging.basicConfig(level=logging.INFO)

# ---------------------------- SEC API CLIENT ---------------------------- #
queryApi = QueryApi(api_key=SEC_API_KEY)

# ---------------------------- FETCH LATEST 10-Q ---------------------------- #
def get_latest_10q(ticker):
    """
    Get the latest 10-Q filing for a company.
    """
    query = {
        "query": {
            "query_string": {
                "query": f"ticker:{ticker} AND formType:\"10-Q\""
            }
        },
        "from": "0",
        "size": "1",
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    try:
        response = queryApi.get_filings(query)
        filings = response.get('filings', [])
        
        if filings:
            logger.info(f"Found 10-Q filing for {ticker}")
            return filings[0]
        
        logger.warning(f"No 10-Q filings found for {ticker}")
        return None
    
    except Exception as e:
        logger.error(f"Error fetching 10-Q for {ticker}: {e}")
        return None

# ---------------------------- PARSE FINANCIAL DATA FROM 10-Q ---------------------------- #
def get_sec_financial_data(ticker):
    """
    Get revenue, net income, and EPS data from the latest 10-Q filing.
    """
    filing = get_latest_10q(ticker)
    
    if not filing:
        return None

    try:
        income_statement = filing.get('financials', {}).get('incomeStatement', {})
        quarters = income_statement.get('quarters', [])

        if not quarters:
            logger.warning(f"No quarters found in income statement for {ticker}")
            return None

        tweet_data = {
            "ticker": ticker,
            "revenue": [],
            "net_income": [],
            "eps": []
        }

        for quarter in quarters[:8]:  
            fiscal_year = quarter.get('year', 'N/A')
            fiscal_quarter = quarter.get('quarter', 'N/A')
            period = f"{fiscal_year} Q{fiscal_quarter}"

            revenue = quarter.get('revenues', {}).get('value')
            net_income = quarter.get('netIncomeLoss', {}).get('value')
            eps = quarter.get('basicEarningsPerShare', {}).get('value')

            tweet_data["revenue"].append(f"{period}: {format_number(revenue)}")
            tweet_data["net_income"].append(f"{period}: {format_number(net_income)}")
            tweet_data["eps"].append(f"{period}: {format_eps(eps)}")

        return tweet_data

    except Exception as e:
        logger.error(f"Error processing financial data for {ticker}: {e}")
        return None


