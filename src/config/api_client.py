import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

def get_economic_events(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the economic events from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/economic-events", params={"limit": limit})
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch economic events: {e}")

def get_earnings(limit: int = 10) -> List[Dict[str, Any]]:
    """Get earnings data from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/earnings", params={"limit": limit})
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        raise Exception(f"Failed to fetch earnings: {e}")

def get_fear_greed() -> Dict[str, Any]:
    """Get fear & greed index from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/fear-greed")
        response.raise_for_status()
        data = response.json()["data"]
        
        # Handle both array and single object responses
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        else:
            return data

    except Exception as e:
        raise Exception(f"Failed to fetch fear & greed index: {e}")

def get_premarket_movers() -> Dict[str, Any]:
    """Get pre-market movers from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/premarket")
        response.raise_for_status()
        return response.json()["data"]
    
    except Exception as e:
        raise Exception(f"Failed to fetch pre-market movers: {e}")

def get_52_week_highs() -> List[Dict[str, Any]]:
    """Get stocks at 52-week highs from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/market-data/52-week-highs")
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch 52-week highs: {e}")

def get_52_week_lows() -> List[Dict[str, Any]]:
    """Get stocks at 52-week lows from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/market-data/52-week-lows")
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch 52-week lows: {e}")

def get_all_time_highs() -> List[Dict[str, Any]]:
    """Get stocks at all-time highs from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/market-data/all-time-highs")
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch all-time highs: {e}")

def get_gap_stocks() -> List[Dict[str, Any]]:
    """Get stocks with significant price gaps from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/market-data/gaps")
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch gap stocks: {e}")

def get_daily_market_summary() -> Dict[str, Any]:
    """Get daily market summary from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/market-data/daily-summary")
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch daily market summary: {e}")

def get_weekly_market_summary() -> Dict[str, Any]:
    """
    Gets the weekly market summary from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/market-data/weekly-summary")
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch weekly market summary: {e}")

def get_trading_holidays() -> List[Dict[str, Any]]:
    """
    Gets the trading holidays from the backend API
    """
    try:
        response = requests.get(f"{BACKEND_URL}/market-data/trading-holidays")
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        raise Exception(f"Failed to fetch trading holidays: {e}") 