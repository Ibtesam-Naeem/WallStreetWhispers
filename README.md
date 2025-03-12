# Automated Earnings, Economic Events, and Market Updates Tweets

This project automates the process of tweeting about earnings reports, economic events, and market updates using **Tweepy** and **X API**. It fetches data from the **FinancialSuite-Backend** API, formats it into clean, readable tweets, and posts them automatically. The project is designed to be hosted on **AWS Lambda**, ensuring low-cost, efficient automation.

---

## **Architecture**

This Twitter bot is part of a larger system:

1. **FinancialSuite-Backend**: Handles all data scraping, processing, and storage
2. **FinancialSuite-TwitterBot**: Consumes the backend API and posts formatted tweets

This separation of concerns allows for:
- Centralized data collection and processing
- Multiple frontends/bots using the same data source
- Easier maintenance and updates
- Better error handling and monitoring

---

## **Features**

### **1. Daily Tweets**
- **Morning Updates (7 AM):**
  - **Earnings Calendar:**
    - Example:
      ```
      Major companies reporting earnings today after the bell:
      - $AAPL --->
        EPS estimate: $1.82  
        Revenue estimate: $100B  
      ```
  - **Economic Events:**
    - Example:
      ```
      Major economic events today:
      - GDP ---> Estimate: 3.5%, Prior: 3.2% (9:30 AM EST)  
      ```

- **After Market Close Updates:**
  - **52-Week Highs:**
    - Example:
      ```
      At some point today, all these stocks hit a new 52-week high:
      - $AAPL - Apple  
      - $MSFT - Microsoft  
      ```
  - **52-Week Lows:**
    - Example:
      ```
      At some point today, all these stocks hit a new 52-week low:
      - $NFLX - Netflix  
      - $TSLA - Tesla  
      ```

---

### **2. Weekly Tweets (Sunday, 8 PM)**
- **Weekly Outlook:**
  - **Top 10 Earnings for the Week:**
    - Example:
      ```
      Major companies reporting earnings this week:
      - $MSFT --->
        EPS estimate: $2.85  
        Revenue estimate: $54B  

      - $AAPL --->
        EPS estimate: $1.82  
        Revenue estimate: $100B  
      ```
  - **Economic Events:**
    - Example:
      ```
      Major economic events this week:
      - GDP ---> Estimate: 3.5%, Prior: 3.2%  
      - FOMC Rate Decision ---> Forecast: 5.5%, Prior: 5.25%  
      ```

---

### **3. Real-Time Earnings Tweets**
- **Earnings Reports:**
  - Example:
    ```
    $AAPL has just reported its Q3 earnings:

    EPS ---> Estimate: $1.82  
    Reported: $1.95 ✅ BEAT  

    Revenue ---> Estimate: $100B  
    Reported: $97B ❌ MISS  

    Guidance for the next quarter:  
    Revenue expected at $110B (higher than analyst expectations).  
    ```

- **Stock Price Reaction Tweets:**
  - Example:
    ```
    $AAPL stock has dropped $14 (4%) in reaction to the news.  
    Current price: $310 (as of 4:05 PM EST).  
    ```

---

## **Data Sources**
- **FinancialSuite-Backend API:**
  - Provides all market data through a unified API
  - Handles data collection, processing, and storage
  - Exposes endpoints for earnings, economic events, market movers, etc.

---

## **Project Workflow**

### **1. Daily Workflow**
- **Morning (7 AM):**
  1. Fetch earnings and economic data from the backend API
  2. Format the data into daily tweets
  3. Post tweets via **Tweepy**

- **After Market Close:**
  1. Fetch 52-week highs and lows from the backend API
  2. Format the data into tweets
  3. Post the tweets

### **2. Weekly Workflow (Sunday, 8 PM):**
1. Fetch earnings and economic events for the week from the backend API
2. Format the data into a weekly outlook tweet
3. Post the tweet

### **3. Real-Time Workflow:**
1. Fetch real-time earnings data from the backend API
2. Format and post the earnings tweet
3. Fetch stock price reaction data and post a reply tweet

---

## **Project Structure**

```
├── data/
│   ├── cache/                       # Cached API responses if needed
├── src/
│   ├── config/
│   │   ├── api_client.py            # Handles API calls to the backend
│   │   ├── logger.py                # Logging configuration
│   ├── twitter/
│   │   ├── tweet_format.py          # Formats tweet content
│   ├── main.py                      # Orchestrates workflows and scheduling
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── .env                             # Environment variables (gitignored)
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore file
```

---

## **Hosting**

- **AWS Lambda:**
  - All workflows are deployed and hosted on AWS Lambda for efficient and low-cost automation.
- **AWS CloudWatch:**
  - Schedules daily and weekly workflows.
- **Environment Variables:**
  - API keys and sensitive credentials are securely managed using environment variables.

---

## **Technologies Used**

- **API Client:** `requests`
- **Twitter API:** `tweepy`
- **Scheduling:** `schedule`
- **Hosting and Scheduling:** `AWS Lambda`, `AWS CloudWatch`
- **Environment Management:** `python-dotenv`

---

## **Getting Started**

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the cleanup script to remove unnecessary files:
   ```bash
   python cleanup.py
   ```

4. Configure environment variables in `.env`:
   ```env
   # Twitter API Credentials
   API_KEY=your_twitter_api_key
   API_SECRET=your_twitter_api_secret
   ACCESS_TOKEN=your_twitter_access_token
   ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   BEARER_TOKEN=your_twitter_bearer_token
   
   # Backend API Configuration
   BACKEND_URL=http://localhost:8000  # Change this to your backend URL
   ```

5. Make sure the FinancialSuite-Backend is running:
   ```bash
   # In the FinancialSuite-Backend directory
   python src/main.py --mode both
   ```

6. Run the Twitter bot:
   ```bash
   python src/main.py
   ```

7. Deploy to AWS Lambda (optional):
   ```bash
   # Package the application
   zip -r twitter-bot.zip .
   
   # Upload to AWS Lambda
   aws lambda update-function-code --function-name YourLambdaFunction --zip-file fileb://twitter-bot.zip
   ```

---

## **Dependencies**

The Twitter bot depends on the FinancialSuite-Backend API being available. Make sure the backend is running and accessible before starting the bot.

### **Required Backend Endpoints**

The Twitter bot expects the following endpoints to be available in the backend:

1. `/economic-events` - Economic calendar events
2. `/earnings` - Company earnings data
3. `/fear-greed` - Fear & Greed index
4. `/premarket` - Pre-market movers
5. `/market-data/52-week-highs` - 52-week high stocks
6. `/market-data/52-week-lows` - 52-week low stocks
7. `/market-data/all-time-highs` - All-time high stocks
8. `/market-data/gaps` - Gap stocks
9. `/market-data/daily-summary` - Daily market summary
10. `/market-data/weekly-summary` - Weekly market summary
11. `/market-data/trading-holidays` - Trading holidays

See `BACKEND_ENDPOINTS.md` for details on implementing these endpoints in the backend.

## **Future Improvements**
- Add sentiment analysis for earnings tweets.
- Include more granular stock price metrics (e.g., volume changes).
- Expand coverage to international markets.

---

## **License**
This project is licensed under the MIT License. See the LICENSE file for more details.
