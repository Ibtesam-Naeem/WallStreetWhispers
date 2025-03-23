#---------------------BACKEND API CLIENT---------------------#

import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

def get_economic_events(limit: int = 10):
    """
    Get the economic events from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/economic-events", params={"limit": limit})
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch economic events: {e}")

def get_earnings(limit: int = 10):
    """
    Get earnings data from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/earnings", params={"limit": limit})
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        raise Exception(f"Failed to fetch earnings: {e}")

def get_fear_greed():
    """
    Get fear & greed index from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/fear-greed")
        response.raise_for_status()
        data = response.json()["data"]
        
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        else:
            return data

    except Exception as e:
        raise Exception(f"Failed to fetch fear & greed index: {e}")

def get_trading_holidays():
    """
    Gets the trading holidays from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/market-holidays")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        raise Exception(f"Failed to fetch trading holidays: {e}") 
    
