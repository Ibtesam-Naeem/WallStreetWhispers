def daily_premkt_earnings_tweet(earnings_list):
    """
    Formats the Pre-Market earnings reminder tweet.
    """
    if not earnings_list:
        return "No major earnings reports scheduled for today before the bell."

    tweet = "Major companies reporting earnings TODAY BEFORE the bell:\n\n"

    for stock in earnings_list:
        tweet += f"- ${stock['Ticker']} --->\n"
        tweet += f"  EPS estimate: {stock['EPS Estimate']}\n"
        tweet += f"  Revenue estimate: {stock['Revenue Forecast']}\n\n"

    print (tweet)

def daily_afterhrs_earnings_tweet(earnings_list):
    """
    Formats the After-Market earnings reminder tweet.
    """
    if not earnings_list:
        return "No major earnings reports scheduled for today after the bell."

    tweet = "Major companies reporting earnings TODAY AFTER the bell:\n\n"

    for stock in earnings_list:
        tweet += f"- ${stock['Ticker']} --->\n"
        tweet += f"  EPS estimate: {stock['EPS Estimate']}\n"
        tweet += f"  Revenue estimate: {stock['Revenue Forecast']}\n\n"

    print (tweet)

def econ_reminder_tomorrow(econ_list):
    """
    Formats the economic event reminder tweet for TOMORROW.
    """
    if not econ_list:
        return "No major economic events scheduled for tomorrow."

    tweet = "Major economic events TOMORROW:\n\n"

    for event in econ_list:
        tweet += f"- {event['Event']}\n"

    print (tweet)

def econ_reminder_weekly(econ_list):
    """
    Formats the economic event reminder tweet for THIS WEEK.
    """
    if not econ_list:
        return "No major economic events scheduled for this week."

    tweet = "Major economic events THIS WEEK:\n\n"

    for event in econ_list:
        tweet += f"- {event['Event']}\n"

    print (tweet)

def pre_market_gainer(gainers_list):
    """
    Formats the Pre-Market Gainers tweet.
    """
    if not gainers_list:
        return "No significant pre-market gainers today."

    tweet = "Stocks rising in pre-market\n\n"

    for stock in gainers_list[:10]:
        tweet += f"- {stock['Ticker']} last up {stock['Pre-Market Change']}\n"

    print (tweet)

def pre_market_losers(losers_list):
    """
    Formats the Pre-Market Losers tweet.
    """
    if not losers_list:
        return "No significant pre-market losers today."

    tweet = "Stocks dropping in pre-market\n\n"

    for stock in losers_list[:10]:
        tweet += f"- {stock['Ticker']} last down {stock['Pre-Market Change']}\n"

    print (tweet)

def fear_sentiment(greed_data):
    """
    Formats a tweet for the Fear & Greed Index.
    """
    if not greed_data:
        return "Not available"

    if isinstance(greed_data, list):
        if len(greed_data) == 0:
            return "Not available"
        greed = greed_data[0]
    else:
        greed = greed_data

    category = greed.get("Category", "Unknown")
    fear_value = greed.get("Fear Value", "N/A")

    tweet = "🚨 The Fear & Greed Index has just entered new territory! 🚨\n"
    tweet += f"Current Sentiment: {category}\n"
    tweet += f"Fear & Greed Score: {fear_value}\n\n"
    tweet += "How do you feel about the market? 📉📈"

    print (tweet)

def weekly_market_summary(weekly_data):
    """
    Formats a tweet for the weekly closing
    summary of S&P 500 and Dow Jones.
    """
    if not weekly_data:
        return "Weekly market data unavailable."

    sp500 = weekly_data.get("S&P 500", {})
    dow = weekly_data.get("Dow Jones", {})

    tweet = "For the week, the S&P 500 moved "
    tweet += f"{sp500.get('Weekly Direction', 'unchanged')} {sp500.get('Weekly Percent Change', 'N/A')}%, closing at ${sp500.get('Friday Close', 'N/A')}.\n"
    tweet += f"The Dow Jones finished the week {dow.get('Weekly Direction', 'unchanged')} {dow.get('Weekly Percent Change', 'N/A')}%, ending at ${dow.get('Friday Close', 'N/A')}."

    print (tweet)

def closures(closing_dates):
    """
    Formats the Stock Market Closing dates tweet.
    """
    if not closing_dates:
        return "Stock Market Open All Week"
    
    tweet = f"The Stock Market is closed tomorrow for {closing_dates}."

    print (tweet)

