from twitter.tweet_scheduler import (
    post_pre_market_earnings_tweet,
    post_after_hours_earnings_tweet,
    post_fear_sentiment_tweet,
    post_trading_holiday,
    post_weekly_econ_tweet,
    post_daily_econ_tweet,
)
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda handler that dispatches to the correct task 
    based on the event payload.
    """
    task = event.get("task")
    
    try:
        if task == "pre_market":
            post_pre_market_earnings_tweet()
        elif task == "after_hours":
            post_after_hours_earnings_tweet()
        elif task == "fear_greed":
            post_fear_sentiment_tweet()
        elif task == "trading_holiday":
            post_trading_holiday()
        elif task == "weekly_econ":
            post_weekly_econ_tweet()
        elif task == "daily_econ":
            post_daily_econ_tweet()
        else:
            raise ValueError(f"Unknown or missing task: {task}")

        logger.info(f"Successfully ran task: {task}")

    except Exception as e:
        logger.error(f"Error running task {task}: {str(e)}")
        raise
