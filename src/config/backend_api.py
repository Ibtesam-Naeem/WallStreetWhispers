#---------------------BACKEND API CLIENT---------------------#
import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
if not BACKEND_URL:
    raise ValueError("BACKEND_URL environment variable is required")

logger = logging.getLogger("TwitterBotScheduler")

# ---------------------------- ECON EVENTS ----------------------------
def get_economic_events(limit: int = 10):
    """
    Get the economic events from the backend API
    """
    try:
        url = f"{BACKEND_URL}/economic-events"
        logger.info(f"Fetching economic events from: {url}")
        response = requests.get(url, params={"limit": limit})
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text[:200]}...")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        logger.error(f"Failed to fetch economic events: {str(e)}")
        raise Exception(f"Failed to fetch economic events: {e}")

# ---------------------------- EARNINGS CALENDAR ----------------------------
def get_earnings(limit: int = 10):
    """
    Get earnings data from the backend API
    """
    try:
        url = f"{BACKEND_URL}/earnings"
        logger.info(f"Fetching earnings from: {url}")
        response = requests.get(url, params={"limit": limit})
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text[:200]}...")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        logger.error(f"Failed to fetch earnings: {str(e)}")
        raise Exception(f"Failed to fetch earnings: {e}")

# ---------------------------- FEAR GREED ----------------------------
def get_fear_greed():
    """
    Get fear & greed index from the backend API - only need the latest value
    """
    try:
        url = f"{BACKEND_URL}/fear-greed"
        logger.info(f"Fetching fear & greed from: {url}")
        response = requests.get(url, params={"limit": 1})
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text[:200]}...")
        response.raise_for_status()
        
        data = response.json()["data"]
        
        if isinstance(data, list) and len(data) > 1:
            logger.info(f"API returned {len(data)} records, using only the first one")
            data = data[0] if data else None
        
        return data
    
    except Exception as e:
        logger.error(f"Failed to fetch fear & greed index: {str(e)}")
        raise Exception(f"Failed to fetch fear & greed index: {e}")

# ---------------------------- TRADING HOLIDAY ----------------------------
def get_trading_holidays():
    """
    Gets the trading holidays from the backend API - only need upcoming ones
    """
    try:
        url = f"{BACKEND_URL}/market-holidays"
        logger.info(f"Fetching trading holidays from: {url}")
        response = requests.get(url, params={"limit": 10})
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text[:200]}...")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        logger.error(f"Failed to fetch trading holidays: {str(e)}")
        raise Exception(f"Failed to fetch trading holidays: {e}") 
    
