# ---------------------------- TWITTER SCHEDULER ----------------------------
from datetime import datetime, timedelta, timezone

from config.logger import setup_logger
from config.twitter_client import get_twitter_client

from config.backend_api import (
    get_economic_events,
    get_earnings,
    get_fear_greed,
    get_trading_holidays
)

from twitter.tweet_formatting import (
    premarket_earnings_tweet,
    afterhrs_earnings_tweet,
    earnings_results,
    econ_reminder_tomorrow,
    econ_reminder_weekly,
    fear_sentiment,
    trading_holiday
)

from utils.helpers import sort_by_market_cap

# ---------------------------- LOGGER SETUP ----------------------------
logger = setup_logger("TwitterBotScheduler")

# ---------------------------- TWITTER API CLIENT ----------------------------
def send_tweet(tweet_text, reply_to_id=None):
    """
    Sends a tweet using the Twitter API client.
    """
    client = get_twitter_client()

    if not tweet_text:
        logger.info("No tweet content to send.")
        return None

    try:
        if reply_to_id:
            response = client.create_tweet(
                text=tweet_text,
                in_reply_to_tweet_id=reply_to_id
            )
        else:
            response = client.create_tweet(text=tweet_text)

        logger.info(f"Tweet sent successfully: {tweet_text[:50]}...")
        return response.data['id']

    except Exception as e:
        logger.error(f"Error sending tweet: {e}")
        return None

# ---------------------------- GENERALIZED EARNINGS TWEET FUNCTION ----------------------------
def post_earnings_tweet(earnings_time, formatter_func, log_context):
    """
    Generalized function to fetch earnings, format, and post tweets.
    """
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        earnings_data = get_earnings(limit=None)

        filtered_earnings = [
            e for e in earnings_data
            if e["Date Reporting"] == today and e["Time"] == earnings_time
        ]

        sorted_earnings = sort_by_market_cap(filtered_earnings)[:5]
 
        if sorted_earnings:
            tweet = formatter_func(sorted_earnings)
            send_tweet(tweet)
        else:
            logger.info(f"No {log_context} earnings available for today.")

    except Exception as e:
        logger.error(f"Error posting {log_context} earnings tweet: {e}")

# ---------------------------- ECONOMIC EVENT TWEETS ----------------------------
def post_daily_econ_tweet():
    """
    Posts economic events for tomorrow.
    """
    try:
        economic_events = get_economic_events()

        if not economic_events:
            logger.info("No economic events available.")
            return

        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()

        tomorrow_events = [
            e for e in economic_events
            if datetime.strptime(e["Date"].split("T")[0], "%Y-%m-%d").date() == tomorrow
        ]

        if tomorrow_events:
            tweet = econ_reminder_tomorrow(tomorrow_events)
            send_tweet(tweet)
        else:
            logger.info(f"No economic events scheduled for {tomorrow}")

    except Exception as e:
        logger.error(f"Error posting daily economic tweet: {e}")

def post_weekly_econ_tweet():
    """
    Posts economic events for the week.
    """
    try:
        economic_events = get_economic_events(limit=50)

        today = datetime.now().date()
        one_week_later = today + timedelta(days=7)

        weekly_events = [
            e for e in economic_events
            if today < datetime.strptime(e["Date"].split("T")[0], "%Y-%m-%d").date() <= one_week_later
        ]

        if weekly_events:
            tweet = econ_reminder_weekly(weekly_events)
            send_tweet(tweet)
        else:
            logger.info("No economic events available for the week.")

    except Exception as e:
        logger.error(f"Error posting weekly economic tweet: {e}")

# ---------------------------- FEAR & GREED INDEX ----------------------------
def post_fear_sentiment_tweet():
    """
    Posts the Fear & Greed Index tweet.
    """
    try:
        fear_data = get_fear_greed()

        if fear_data:
            tweet = fear_sentiment(fear_data)
            send_tweet(tweet)
        else:
            logger.info("No fear & greed data available.")

    except Exception as e:
        logger.error(f"Error posting fear sentiment tweet: {e}")

# ---------------------------- TRADING HOLIDAY ----------------------------
def post_trading_holiday():
    """
    Posts about upcoming trading holidays.
    """
    try:
        holiday_data = get_trading_holidays()

        if not holiday_data:
            logger.info("No trading holiday data available.")
            return

        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()

        tomorrow_holidays = [
            h for h in holiday_data
            if datetime.strptime(h["date"], "%Y-%m-%d").date() == tomorrow
        ]

        if tomorrow_holidays:
            tweet = trading_holiday(tomorrow_holidays)
            send_tweet(tweet)
        else:
            logger.info(f"No trading holidays tomorrow ({tomorrow})")

    except Exception as e:
        logger.error(f"Error posting trading holiday tweet: {e}")

# ---------------------------- EARNINGS WRAPPERS ----------------------------
def post_pre_market_earnings_tweet():
    post_earnings_tweet(
        earnings_time="Before Open",
        formatter_func=premarket_earnings_tweet,
        log_context="Pre-Market"
    )

def post_after_hours_earnings_tweet():
    post_earnings_tweet(
        earnings_time="After Close",
        formatter_func=afterhrs_earnings_tweet,
        log_context="After-Hours"
    )

# ---------------------------- SCHEDULING TASKS ----------------------------
def run_bot():
    """
    Main function for the tweet scheduler.
    """
    logger.info("Twitter Bot started. Posting tweets immediately...")

    # Post all tweets immediately
    post_pre_market_earnings_tweet()
    post_after_hours_earnings_tweet()
    post_trading_holiday()
    post_fear_sentiment_tweet()
    post_weekly_econ_tweet()
    post_daily_econ_tweet()
    
    logger.info("All tweets have been posted.")

