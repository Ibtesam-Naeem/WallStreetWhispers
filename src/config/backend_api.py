#---------------------BACKEND API CLIENT---------------------#
import os
import requests
from config.logger import setup_logger

logger = setup_logger("BackendAPI")

BACKEND_URL = os.environ.get("BACKEND_API_URL", "").rstrip("/")

# ---------------------------- ECON EVENTS ----------------------------
def get_economic_events(limit: int = 10):
    """
    Gets the economic events from the backend API
    """
    if not BACKEND_URL:
        logger.error("BACKEND_API_URL environment variable is not set")
        return None

    try:
        url = f"{BACKEND_URL}/economic-events"
        logger.info(f"Fetching economic events from: {url}")
        
        response = requests.get(url, params={"limit": limit})
        response.raise_for_status()
        
        data = response.json()
        if not data or "data" not in data:
            logger.error("Invalid response format from backend API")
            return None
            
        return data["data"]
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch economic events: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching economic events: {e}")
        return None

# ---------------------------- EARNINGS CALENDAR ----------------------------
def get_earnings(limit: int = 10):
    """
    Gets earnings data from the backend API
    """
    if not BACKEND_URL:
        logger.error("BACKEND_API_URL environment variable is not set")
        return None

    try:
        url = f"{BACKEND_URL}/earnings"
        logger.info(f"Fetching earnings from: {url}")
        
        response = requests.get(url, params={"limit": limit})
        response.raise_for_status()
        
        data = response.json()
        if not data or "data" not in data:
            logger.error("Invalid response format from backend API")
            return None
            
        return data["data"]
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch earnings: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching earnings: {e}")
        return None

# ---------------------------- FEAR & GREED INDEX ----------------------------
def get_fear_greed():
    """
    Gets fear & greed index from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/fear-greed")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        logger.error(f"Failed to fetch fear & greed index: {e}")
        return None

# ---------------------------- TRADING HOLIDAY ----------------------------
def get_trading_holidays():
    """
    Gets the trading holidays from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/market-holidays")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        logger.errror(f"Failed to fetch trading holidays: {e}")
        return None 
    
