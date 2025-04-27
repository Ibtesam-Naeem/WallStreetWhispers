#---------------------BACKEND API CLIENT---------------------#
import os
import requests

BACKEND_URL = os.environ["BACKEND_API_URL"]

# ---------------------------- ECON EVENTS ----------------------------
def get_economic_events(limit: int = 10):
    """
    Get the economic events from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/economic-events", params={"limit": limit})
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        print(f"Failed to fetch economic events: {e}")
        return None

# ---------------------------- EARNINGS CALENDAR ----------------------------
def get_earnings(limit: int = 10):
    """
    Get earnings data from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/earnings", params={"limit": limit})
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        print(f"Failed to fetch earnings: {e}")
        return None

# ---------------------------- FEAR GREED ----------------------------
def get_fear_greed():
    """
    Get fear & greed index from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/fear-greed")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        print(f"Failed to fetch fear & greed index: {e}")
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
        print(f"Failed to fetch trading holidays: {e}")
        return None 
    
