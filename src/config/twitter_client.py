#---------------------TWITTER API CLIENT---------------------#
import os
import tweepy

# Environment variables using AWS Environment Variables
API_KEY = os.environ["TWITTER_API_KEY"]
API_SECRET = os.environ["TWITTER_API_SECRET"]
ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

def get_twitter_client():
    """
    Returns the Twitter API client.
    """
    return client 