# ---------------------------- TWITTER SCHEDULER ----------------------------

import time
import threading
import schedule
from datetime import datetime, timedelta, timezone

from config.logger import setup_logger
from config.twitter_client import get_twitter_client

from config.backend_api import (
    get_economic_events,
    get_earnings,
    get_fear_greed,
    get_trading_holidays
)

from data.polygon_financials import polygon, get_top_stocks
from data.sec_results import get_sec_financial_data

from twitter.tweet_formatting import (
    premarket_earnings_tweet,
    afterhrs_earnings_tweet,
    earnings_results,
    sec_tweet_thread,
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
        earnings_data = get_earnings(limit=50)

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

# ---------------------------- FINANCIAL THREADS ----------------------------
def post_polygon_threads():
    """
    Posts the threads of the stock financial data.
    """
    threads = polygon()

    for thread in threads:
        first_tweet_id = None
        for tweet in thread:
            first_tweet_id = send_tweet(tweet, reply_to_id=first_tweet_id)

# ---------------------------- SEC EARNINGS WATCHER (REAL-TIME) ----------------------------
def sec_earnings_watcher():
    """
    Continuously checks for SEC earnings reports and posts them in real-time.
    """
    logger.info("Starting SEC Earnings Watcher...")

    reported_tickers = set()
    today = datetime.today().strftime('%Y-%m-%d')

    earnings_calendar = get_earnings(limit=50)
    tickers_to_watch = [e['Ticker'] for e in earnings_calendar if e['Date Reporting'] == today]

    logger.info(f"Watching tickers: {tickers_to_watch}")

    while True:
        for ticker in tickers_to_watch:
            if ticker in reported_tickers:
                continue

            sec_data = get_sec_financial_data(ticker)

            if not sec_data:
                logger.info(f"{ticker} has not reported yet.")
                continue

            logger.info(f"{ticker} has reported! Posting thread...")

            announcement = f"${ticker} HAS JUST REPORTED EARNINGS"
            first_tweet_id = send_tweet(announcement)

            eps_estimate = next((e['EPS Estimate'] for e in earnings_calendar if e['Ticker'] == ticker), "N/A")
            revenue_estimate = next((e['Revenue Forecast'] for e in earnings_calendar if e['Ticker'] == ticker), "N/A")

            reported_eps = sec_data['eps'][0] if sec_data['eps'] else "N/A"
            reported_revenue = sec_data['revenue'][0] if sec_data['revenue'] else "N/A"

            results_tweet = earnings_results(ticker, eps_estimate, reported_eps, revenue_estimate, reported_revenue)
            results_tweet_id = send_tweet(results_tweet, reply_to_id=first_tweet_id)

            tweet_thread = sec_tweet_thread(sec_data)

            current_tweet_id = results_tweet_id
            for tweet in tweet_thread:
                current_tweet_id = send_tweet(tweet, reply_to_id=current_tweet_id)
                time.sleep(2)

            reported_tickers.add(ticker)

        time.sleep(60)

# ---------------------------- SCHEDULING TASKS ----------------------------
def tweet_scheduler():
    """
    Main function for the tweet scheduler.
    """
    # Pre-Market Earnings Tweets
    schedule.every().day.at("07:00").do(post_pre_market_earnings_tweet)

    # After-Hours Earnings Tweets
    schedule.every().day.at("12:00").do(post_after_hours_earnings_tweet)

    # Trading Holidays Notification
    schedule.every().day.at("20:00").do(post_trading_holiday)

    # Fear & Greed Index Tweet
    schedule.every().day.at("19:00").do(post_fear_sentiment_tweet)

    # Weekly Economic Event Tweet (Sunday)
    schedule.every().sunday.at("20:00").do(post_weekly_econ_tweet)

    # Daily Economic Event Recap Tweet
    schedule.every().day.at("22:00").do(post_daily_econ_tweet)

    # Polygon Financial Threads
    schedule.every().sunday.at("20:00").do(post_polygon_threads)

    logger.info("Twitter Bot Scheduler started. Tasks are scheduled and running...")

    while True:
        schedule.run_pending()
        time.sleep(30)

# ---------------------------- MAIN RUNNER ----------------------------
def run_bot():
    """
    Runs both the tweet scheduler and SEC earnings watcher concurrently.
    """
    scheduler_thread = threading.Thread(target=tweet_scheduler)
    sec_watcher_thread = threading.Thread(target=sec_earnings_watcher)

    scheduler_thread.start()
    sec_watcher_thread.start()

    scheduler_thread.join()
    sec_watcher_thread.join()