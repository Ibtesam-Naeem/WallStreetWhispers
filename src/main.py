import os
import time
import schedule
import tweepy
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from config.api_client import (
    get_economic_events,
    get_earnings,
    get_fear_greed,
    get_trading_holidays
)

from twitter.tweet_format import (
    daily_premkt_earnings_tweet,
    daily_afterhrs_earnings_tweet,
    econ_reminder_tomorrow,
    econ_reminder_weekly,
    fear_sentiment,
    closures,
)

from config.logger import setup_logging

logging = setup_logging("TwitterBot")

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

def send_tweet(tweet_text):
    """
    Helper function to send a tweet via the Twitter API.
    """
    if tweet_text:
        try:
            response = client.create_tweet(text=tweet_text)
            logging.info(f"Tweet sent successfully: {tweet_text[:50]}...")
        except Exception as e:
            logging.error(f"Error sending tweet: {e}")

    else:
        logging.info("No tweet content to send.")

def parse_market_cap(market_cap_str):
    """
    Helper function to parse market cap string into numeric value.
    Handles different formats like $1.2B, $500M, etc.
    Returns 0 if the parsing fails.
    """
    try:
        if not market_cap_str:
            return 0
            
        # Remove non-numeric characters and convert to float
        market_cap_str = market_cap_str.replace("$", "").replace(",", "")
        
        # Handle different suffixes (B for billion, M for million)
        if "B" in market_cap_str:
            market_cap_str = market_cap_str.replace("B", "")
            return float(market_cap_str) * 1_000_000_000
        elif "M" in market_cap_str:
            market_cap_str = market_cap_str.replace("M", "")
            return float(market_cap_str) * 1_000_000
        else:
            return float(market_cap_str)
    
    except (ValueError, TypeError):
        return 0

def sort_by_market_cap(earnings_list):
    """
    Helper function to sort earnings list by market cap.
    Returns sorted list with market cap numeric values added.
    """
    try:
        # Add market cap numeric values
        for earning in earnings_list:
            earning["Market Cap Numeric"] = parse_market_cap(earning.get("Market Cap", ""))
        
        # Sort by market cap (descending)
        earnings_list.sort(key=lambda x: x.get("Market Cap Numeric", 0), reverse=True)
        return earnings_list
    
    except Exception as e:
        logging.warning(f"Error sorting earnings by market cap: {e}")
        return earnings_list

def post_pre_market_earnings_tweet():
    """
    Fetches earnings data from the backend API, formats the Pre-Market tweet,
    and sends it. Scheduled for 4:00 AM.
    """
    try:
        today = datetime.today().strftime('%Y-%m-%d')

        earnings_data = get_earnings(limit=50)
        
        # Filter by today's date AND "Before Open"
        pre_market_earnings = [
            e for e in earnings_data
            if e["Date Reporting"] == today and e["Time"] == "Before Open"
        ]

        pre_market_earnings = sort_by_market_cap(pre_market_earnings)[:5]

        if pre_market_earnings:
            tweet = daily_premkt_earnings_tweet(pre_market_earnings)
            send_tweet(tweet)
        else:
            logging.info("No Pre-Market earnings available for today.")
    
    except Exception as e:
        logging.error(f"Error posting pre-market earnings tweet: {e}")

def post_after_hours_earnings_tweet():
    """
    Fetches earnings data from the backend API, formats the After-Hours tweet,
    and sends it. Scheduled for 4:00 PM.
    """
    try:
        today = datetime.today().strftime('%Y-%m-%d')

        earnings_data = get_earnings(limit=50)
        
        # Filter by today's date AND "After Close"
        after_hours_earnings = [
            e for e in earnings_data
            if e["Date Reporting"] == today and e["Time"] == "After Close"
        ]

        after_hours_earnings = sort_by_market_cap(after_hours_earnings)[:5]

        if after_hours_earnings:
            tweet = daily_afterhrs_earnings_tweet(after_hours_earnings)
            send_tweet(tweet)
        else:
            logging.info("No After-Hours earnings available for today.")
    
    except Exception as e:
        logging.error(f"Error posting after-hours earnings tweet: {e}")

def post_daily_econ_tweet():
    """
    Fetches economic data for tomorrow from the backend API, formats the tweet, and sends it.
    Scheduled for 1:17 AM.
    """
    try:
        economic_events = get_economic_events()
        
        if not economic_events:
            logging.info("No economic events available.")
            return
        
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
        
        # Filter only events for tomorrow
        tomorrow_events = []
        for event in economic_events:
            event_date_str = event["Date"].split("T")[0]  # Extract date part
            event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            
            if event_date == tomorrow:
                tomorrow_events.append(event)
        
        if tomorrow_events:
            tweet = econ_reminder_tomorrow(tomorrow_events)
            send_tweet(tweet)
        else:
            logging.info(f"No economic events scheduled for {tomorrow}")
    
    except Exception as e:
        logging.error(f"Error posting daily economic tweet: {e}")


def post_weekly_econ_tweet():
    """
    Fetches economic data for the week from the backend API, formats the tweet, and sends it.
    Scheduled for 1:17 AM (Sunday).
    """
    try:
        economic_events = get_economic_events(limit=50) 
        
        # Filter events for the upcoming week
        from datetime import datetime, timedelta
        today = datetime.now().date()
        one_week_later = today + timedelta(days=7)
        
        # Filter events that are within the next 7 days
        try:
            weekly_events = []
            for event in economic_events:
                if "Date" in event:
                    # Parse the date string (assuming ISO format)
                    event_date_str = event["Date"].split("T")[0]  # Extract date part
                    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
                    
                    # Include events from tomorrow to one week later
                    if today < event_date <= one_week_later:
                        weekly_events.append(event)
            
            economic_events = weekly_events
        
        except Exception as e:
            logging.warning(f"Error filtering weekly economic events: {e}")
        
        if economic_events:
            tweet = econ_reminder_weekly(economic_events)
            send_tweet(tweet)
        else:
            logging.info("No economic events available for the week.")
    
    except Exception as e:
        logging.error(f"Error posting weekly economic tweet: {e}")

def post_fear_sentiment_tweet():
    """
    Fetches fear & greed index from the backend API, formats the tweet, and sends it.
    Scheduled for 9:30 AM.
    """
    try:
        fear_data = get_fear_greed()
        if fear_data:
            tweet = fear_sentiment(fear_data)
            send_tweet(tweet)
        else:
            logging.info("No fear & greed data available.")

    except Exception as e:
        logging.error(f"Error posting fear sentiment tweet: {e}")

def post_trading_holiday():
    """
    Checks if tomorrow is a trading holiday. Tweets if there is one.
    """
    try:
        holiday_data = get_trading_holidays()

        if not holiday_data:
            logging.info("No trading holiday data available.")
            return

        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()

        tomorrow_holidays = []
        for holiday in holiday_data:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
            
            if holiday_date == tomorrow:
                tomorrow_holidays.append(holiday)

        if tomorrow_holidays:
            tweet = closures(tomorrow_holidays)
            send_tweet(tweet)
        else:
            logging.info(f"No trading holidays tomorrow ({tomorrow})")

    except Exception as e:
        logging.error(f"Error posting trading holiday tweet: {e}")


if __name__ == "__main__":
    logging.info("Starting Twitter Bot Scheduler...")

    # Early morning pre-market earnings tweet
    schedule.every().day.at("06:00").do(post_pre_market_earnings_tweet)

    # Fear & Greed index tweet (evening)
    schedule.every().day.at("20:00").do(post_fear_sentiment_tweet)

    # Mid-day after-hours earnings tweet
    schedule.every().day.at("12:00").do(post_after_hours_earnings_tweet)

    # Daily economic events reminder (evening)
    schedule.every().day.at("20:00").do(post_daily_econ_tweet)

    # Weekly economic events reminder (Sunday evening)
    schedule.every().sunday.at("20:00").do(post_weekly_econ_tweet)

    # Trading holiday notification (afternoon)
    schedule.every().day.at("16:00").do(post_trading_holiday)

    logging.info("Twitter Bot Scheduler started with tweets scheduled throughout the day")

    while True:
        schedule.run_pending()
        time.sleep(30)

