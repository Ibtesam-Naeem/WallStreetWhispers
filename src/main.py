import os
import time
import schedule
import tweepy
from dotenv import load_dotenv

from config.api_client import (
    get_economic_events,
    get_earnings,
    get_fear_greed,
    get_premarket_movers,
    get_52_week_highs,
    get_52_week_lows,
    get_all_time_highs,
    get_trading_holidays
)

from twitter.tweet_format import (
    daily_premkt_earnings_tweet,
    daily_afterhrs_earnings_tweet,
    econ_reminder_tomorrow,
    econ_reminder_weekly,
    pre_market_gainer,
    pre_market_losers,
    week_high_52,
    week_low_52,
    all_time_high,
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

def post_pre_market_earnings_tweet():
    """
    Fetches earnings data from the backend API, formats the Pre-Market tweet,
    and sends it. Scheduled for 4:00 AM.
    """
    try:
        earnings_data = get_earnings()
        pre_market_earnings = [e for e in earnings_data if e["Time"] == "Before Open"]

        # Sort by market cap if available, otherwise keep original order
        try:
            # Convert market cap to numeric value for sorting
            for earning in pre_market_earnings:
                if "Market Cap" in earning:
                    # Remove non-numeric characters and convert to float
                    market_cap_str = earning["Market Cap"].replace("$", "").replace(",", "")
                    # Handle different suffixes (B for billion, M for million)
                    if "B" in market_cap_str:
                        market_cap_str = market_cap_str.replace("B", "")
                        earning["Market Cap Numeric"] = float(market_cap_str) * 1_000_000_000
                    elif "M" in market_cap_str:
                        market_cap_str = market_cap_str.replace("M", "")
                        earning["Market Cap Numeric"] = float(market_cap_str) * 1_000_000
                    else:
                        earning["Market Cap Numeric"] = float(market_cap_str)
                else:
                    earning["Market Cap Numeric"] = 0
            
            # Sort by market cap (descending)
            pre_market_earnings.sort(key=lambda x: x.get("Market Cap Numeric", 0), reverse=True)
        except Exception as e:
            logging.warning(f"Error sorting earnings by market cap: {e}")
        
        # Take only the top 5
        pre_market_earnings = pre_market_earnings[:5]

        if pre_market_earnings:
            tweet = daily_premkt_earnings_tweet(pre_market_earnings)
            send_tweet(tweet)
        else:
            logging.info("No Pre-Market earnings available.")
    except Exception as e:
        logging.error(f"Error posting pre-market earnings tweet: {e}")

def post_after_hours_earnings_tweet():
    """
    Fetches earnings data from the backend API, formats the After-Hours tweet,
    and sends it. Scheduled for 12:00 PM.
    """
    try:
        earnings_data = get_earnings()
        after_hours_earnings = [e for e in earnings_data if e["Time"] == "After Close"]

        # Sort by market cap if available, otherwise keep original order
        try:
            # Convert market cap to numeric value for sorting
            for earning in after_hours_earnings:
                if "Market Cap" in earning:
                    # Remove non-numeric characters and convert to float
                    market_cap_str = earning["Market Cap"].replace("$", "").replace(",", "")
                    # Handle different suffixes (B for billion, M for million)
                    if "B" in market_cap_str:
                        market_cap_str = market_cap_str.replace("B", "")
                        earning["Market Cap Numeric"] = float(market_cap_str) * 1_000_000_000
                    elif "M" in market_cap_str:
                        market_cap_str = market_cap_str.replace("M", "")
                        earning["Market Cap Numeric"] = float(market_cap_str) * 1_000_000
                    else:
                        earning["Market Cap Numeric"] = float(market_cap_str)
                else:
                    earning["Market Cap Numeric"] = 0
            
            # Sort by market cap (descending)
            after_hours_earnings.sort(key=lambda x: x.get("Market Cap Numeric", 0), reverse=True)
        except Exception as e:
            logging.warning(f"Error sorting earnings by market cap: {e}")
        
        # Take only the top 5
        after_hours_earnings = after_hours_earnings[:5]

        if after_hours_earnings:
            tweet = daily_afterhrs_earnings_tweet(after_hours_earnings)
            send_tweet(tweet)
        else:
            logging.info("No After-Hours earnings available.")
    except Exception as e:
        logging.error(f"Error posting after-hours earnings tweet: {e}")

def post_daily_econ_tweet():
    """
    Fetches economic data for tomorrow from the backend API, formats the tweet, and sends it.
    Scheduled for 1:17 AM.
    """
    try:
        economic_events = get_economic_events()
        if economic_events:
            tweet = econ_reminder_tomorrow(economic_events)
            send_tweet(tweet)
        else:
            logging.info("No economic events available.")

    except Exception as e:
        logging.error(f"Error posting daily economic tweet: {e}")

def post_weekly_econ_tweet():
    """
    Fetches economic data for the week from the backend API, formats the tweet, and sends it.
    Scheduled for 1:17 AM (Sunday).
    """
    try:
        economic_events = get_economic_events(limit=50)  # Get more events for the week
        
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

def post_pre_market_gainers_tweet():
    """
    Fetches pre-market gainers from the backend API, formats the tweet, and sends it.
    Scheduled for 8:30 AM.
    """
    try:
        premarket_data = get_premarket_movers()
        if premarket_data and "gainers" in premarket_data:
            tweet = pre_market_gainer(premarket_data["gainers"])
            send_tweet(tweet)
        else:
            logging.info("No pre-market gainers available.")

    except Exception as e:
        logging.error(f"Error posting pre-market gainers tweet: {e}")

def post_pre_market_losers_tweet():
    """
    Fetches pre-market losers from the backend API, formats the tweet, and sends it.
    Scheduled for 8:30 AM.
    """
    try:
        premarket_data = get_premarket_movers()
        if premarket_data and "losers" in premarket_data:
            tweet = pre_market_losers(premarket_data["losers"])
            send_tweet(tweet)
        else:
            logging.info("No pre-market losers available.")

    except Exception as e:
        logging.error(f"Error posting pre-market losers tweet: {e}")

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

# def post_week_high_52_tweet():
#     """
#     Fetches 52-week high stocks from the backend API, formats the tweet, and sends it.
#     Scheduled for 4:00 PM.
#     """
#     try:
#         high_data = get_52_week_highs()
#         if high_data:
#             tweet = week_high_52(high_data)
#             send_tweet(tweet)
#         else:
#             logging.info("No 52-week high data available.")

#     except Exception as e:
#         logging.error(f"Error posting 52-week high tweet: {e}")

# def post_week_low_52_tweet():
#     """
#     Fetches 52-week low stocks from the backend API, formats the tweet, and sends it.
#     Scheduled for 4:05 PM.
#     """
#     try:
#         low_data = get_52_week_lows()
#         if low_data:
#             tweet = week_low_52(low_data)
#             send_tweet(tweet)
#         else:
#             logging.info("No 52-week low data available.")

#     except Exception as e:
#         logging.error(f"Error posting 52-week low tweet: {e}")

def post_all_time_high_tweet():
    """
    Fetches all-time high stocks from the backend API, formats the tweet, and sends it.
    Scheduled for 4:10 PM.
    """
    try:
        ath_data = get_all_time_highs()
        if ath_data:
            tweet = all_time_high(ath_data)
            send_tweet(tweet)
        else:
            logging.info("No all-time high data available.")

    except Exception as e:
        logging.error(f"Error posting all-time high tweet: {e}")

# def post_gap_tweet():
#     """
#     Fetches gap stocks from the backend API, formats the tweet, and sends it.
#     Scheduled for 4:15 PM.
#     """
#     try:
#         gap_data = get_gap_stocks()
#         if gap_data:
#             tweet = pre_market_gap(gap_data)
#             send_tweet(tweet)
#         else:
#             logging.info("No gap data available.")
        
#     except Exception as e:
#         logging.error(f"Error posting gap tweet: {e}")

# def post_daily_market_summary():
#     """
#     Fetches daily market summary from the backend API, formats the tweet, and sends it.
#     Scheduled for 4:30 PM.
#     """
#     try:
#         summary_data = get_daily_market_summary()
#         if summary_data:
#             tweet = daily_market_summary(summary_data)
#             send_tweet(tweet)
#         else:
#             logging.info("No daily market summary data available.")

#     except Exception as e:
#         logging.error(f"Error posting daily market summary tweet: {e}")

# def post_weekly_market_summary():
#     """
#     Fetches weekly market summary from the backend API, formats the tweet, and sends it.
#     Scheduled for 4:30 PM (Friday).
#     """
#     try:
#         summary_data = get_weekly_market_summary()
#         if summary_data:
#             tweet = weekly_market_summary(summary_data)
#             send_tweet(tweet)
#         else:
#             logging.info("No weekly market summary data available.")

#     except Exception as e:
#         logging.error(f"Error posting weekly market summary tweet: {e}")

# def post_trading_holiday():
#     """
#     Fetches trading holidays from the backend API, formats the tweet, and sends it.
#     Scheduled for 8:00 AM.
#     """
#     try:
#         holiday_data = get_trading_holidays()
#         if holiday_data:
#             tweet = closures(holiday_data)
#             send_tweet(tweet)
#         else:
#             logging.info("No trading holiday data available.")

#     except Exception as e:
#         logging.error(f"Error posting trading holiday tweet: {e}")

if __name__ == "__main__":
    logging.info("Starting Twitter Bot Scheduler...")

    # Pre-market tweets (early morning before market open)
    schedule.every().day.at("08:00").do(post_pre_market_earnings_tweet)  # 8:00 AM
    schedule.every().day.at("08:30").do(post_pre_market_gainers_tweet)   # 8:30 AM
    schedule.every().day.at("08:35").do(post_pre_market_losers_tweet)    # 8:35 AM
    
    # Market open tweets
    schedule.every().day.at("09:30").do(post_fear_sentiment_tweet)       # 9:30 AM (market open)
    
    # Mid-day tweets
    schedule.every().day.at("12:00").do(post_after_hours_earnings_tweet) # 12:00 PM
    
    # After market close tweets
    schedule.every().day.at("16:15").do(post_all_time_high_tweet)        # 4:15 PM
    
    # Evening tweets
    schedule.every().day.at("18:00").do(post_daily_econ_tweet)           # 6:00 PM
    
    # Weekly tweets (Sunday evening)
    schedule.every().sunday.at("18:00").do(post_weekly_econ_tweet)       # Sunday at 6:00 PM
    
    # schedule.every().day.at("16:00").do(post_week_high_52_tweet)       # 4:00 PM
    # schedule.every().day.at("16:05").do(post_week_low_52_tweet)        # 4:05 PM
    # schedule.every().day.at("08:00").do(post_trading_holiday)          # 8:00 AM
    
    logging.info("Twitter Bot Scheduler started with tweets scheduled throughout the day")
    
    while True:
        schedule.run_pending()
        time.sleep(30)