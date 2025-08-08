# WallStreetWhispers
### Automated Earnings, Economic Events, and Market Update Tweets

This project automates the process of tweeting about **earnings reports**, **economic events**, and **market updates** using **Tweepy** and the **Twitter/X API**. It fetches real-time and historical data from **FinancialSuite-Backend**, **Polygon API**, and **SEC API**, formats it into clean, informative tweets, and posts them automatically.

The bot runs on **AWS Lambda** with scheduled triggers via EventBridge, continuously monitoring **real-time earnings reports** via the SEC API to deliver timely tweets as soon as earnings are released.

---

## 🌐 Architecture

This Twitter bot is part of the **FinancialSuite Ecosystem**, designed for **modularity**, **scalability**, and **automation**. It's deployed on AWS Lambda for serverless execution and cost-effective operation.

```
FinancialSuite Ecosystem
├── FinancialSuite-Backend: Collects & processes financial data
├── FinancialSuite-TwitterBot: AWS Lambda function for automated tweets
│   ├── Lambda Handler: Manages different tweet types
│   └── EventBridge: Schedules tweet tasks
└── SEC/Polygon API integrations: Provide real-time and historical financial data
```

### AWS Lambda Configuration
The bot is configured as a Lambda function with the following components:
- **Runtime**: Python 3.13
- **Handler**: lambda_function.lambda_handler
- **Memory**: 128 MB
- **Timeout**: 3 minutes
- **Triggers**: AWS EventBridge (CloudWatch Events) for scheduling

### Environment Variables
The Lambda function requires the following environment variables:
- `TWITTER_API_KEY`: Twitter API Key
- `TWITTER_API_SECRET`: Twitter API Secret
- `TWITTER_ACCESS_TOKEN`: Twitter Access Token
- `TWITTER_ACCESS_TOKEN_SECRET`: Twitter Access Token Secret
- `TWITTER_BEARER_TOKEN`: Twitter Bearer Token
- `BACKEND_API_URL`: FinancialSuite Backend API URL

---

## Features

### 1. Scheduled Tweets

#### 🕖 Pre-Market Earnings Reminder (7 AM)
Tweets a list of major companies reporting earnings **before** the market opens.

**Example Tweet:**
```
Major companies reporting earnings TODAY BEFORE the bell:

- $TSLA --->
  EPS estimate: $1.20
  Revenue estimate: $25B

- $GME --->
  EPS estimate: $-0.15
  Revenue estimate: $1.3B
```

---

#### 🕛 After-Hours Earnings Reminder (12 PM)
Tweets major companies reporting earnings **after** the bell.

**Example Tweet:**
```
Major companies reporting earnings TODAY AFTER the bell:

- $NVDA --->
  EPS estimate: $4.50
  Revenue estimate: $22B

- $NFLX --->
  EPS estimate: $2.80
  Revenue estimate: $8.5B
```

---

#### 📅 Weekly Economic & Earnings Outlook (Sunday, 8 PM)
Posts the full week's **earnings and economic calendar**.

**Example Tweet:**
```
📅 WEEKLY EARNINGS & ECONOMIC OUTLOOK 📅

🔸 Major Earnings Reports This Week:
- $AAPL ---> EPS: $1.82 | Revenue: $100B
- $MSFT ---> EPS: $2.80 | Revenue: $56B

🔸 Major Economic Events:
- FOMC Rate Decision ---> Forecast: 5.5%
- GDP (Q1) ---> Estimate: 3.5%
- Non-Farm Payrolls ---> Estimate: +250K
```

---

#### 📉 Trading Holidays Notification (8 PM)
Alerts users to upcoming **market closures**.

**Example Tweet:**
```
📢 Heads up!

The US Stock Market will be CLOSED tomorrow for Presidents Day 🇺🇸
```

---

#### 😱 Fear & Greed Index (7 PM)
Posts the current **Fear & Greed index** sentiment.

**Example Tweet:**
```
🚨 The Fear & Greed Index has just entered new territory! 🚨

Current Sentiment: EXTREME GREED
Fear & Greed Score: 88/100

How do you feel about the market? 📉📈
```

---

#### 🗓️ Daily Economic Events (10 PM)
Tweets **economic events** scheduled for tomorrow.

**Example Tweet:**
```
Major Economic events to watch for TOMORROW:

- GDP Report ---> Estimate: 3.5%, Prior: 3.2% (8:30 AM EST)
- Jobless Claims ---> Estimate: 210K (8:30 AM EST)
```

---

### 2. Real-Time SEC Earnings Reports
Continuously monitors the **SEC API** for **real-time 10-Q filings**. Tweets earnings as soon as they are reported.

**Example Tweet (Earnings Results):**
```
$TSLA HAS JUST REPORTED EARNINGS 🚨

EPS --->
  Estimate: $1.20
  Reported: $1.30 ✅ BEAT

Revenue --->
  Estimate: $25B
  Reported: $26.2B ✅ BEAT

Guidance: Revenue expected at $27B next quarter!
```

---

### 3. Polygon Financial Threads (8 PM)
Posts **threads** showing historical revenue, net income, and EPS from Polygon.io for top stocks.

**Example Tweet Thread:**

**Thread 1: Revenue**
```
$TSLA QUARTERLY REVENUE (Last 8 Quarters)

2023 Q4: $26.2B
2023 Q3: $25.0B
2023 Q2: $24.1B
2023 Q1: $23.3B
2022 Q4: $22.9B
2022 Q3: $21.8B
2022 Q2: $19.6B
2022 Q1: $18.7B
```
