from flask import Flask, render_template, jsonify, request
import os
import yfinance as yf

app = Flask(__name__)

# Complete 7 Financial Literacy Modules
MODULES = [
    {
        "id": "m1",
        "badge_id": "b1",
        "title": "Budgeting Fundamentals & 50/30/20 Rule",
        "description": "Master income allocation, fixed vs variable costs, and emergency funds.",
        "xp_reward": 100,
        "coin_reward": 50,
        "questions": [{"id": i, "q": f"Question {i} for Module 1"} for i in range(1, 11)]
    },
    {
        "id": "m2",
        "badge_id": "b2",
        "title": "Credit Cards, APR & Credit Scores",
        "description": "Understand interest rates, payment strategies, and building high credit scores.",
        "xp_reward": 150,
        "coin_reward": 75,
        "questions": [{"id": i, "q": f"Question {i} for Module 2"} for i in range(1, 11)]
    },
    {
        "id": "m3",
        "badge_id": "b3",
        "title": "Stock Market, Index Funds & Equity",
        "description": "Learn stocks, market cap, dollar-cost averaging, and long-term compounding.",
        "xp_reward": 200,
        "coin_reward": 100,
        "questions": [{"id": i, "q": f"Question {i} for Module 3"} for i in range(1, 11)]
    },
    {
        "id": "m4",
        "badge_id": "b4",
        "title": "Tax Strategies & Retirement Accounts",
        "description": "Explore 401(k)s, Roth IRAs, capital gains taxes, and tax advantages.",
        "xp_reward": 250,
        "coin_reward": 125,
        "questions": [{"id": i, "q": f"Question {i} for Module 4"} for i in range(1, 11)]
    },
    {
        "id": "m5",
        "badge_id": "b5",
        "title": "Cryptocurrency, DeFi & Blockchain",
        "description": "Understand digital assets, smart contracts, wallets, and volatility risks.",
        "xp_reward": 300,
        "coin_reward": 150,
        "questions": [{"id": i, "q": f"Question {i} for Module 5"} for i in range(1, 11)]
    },
    {
        "id": "m6",
        "badge_id": "b6",
        "title": "Real Estate & Equity Building",
        "description": "Discover mortgages, rental properties, REITs, and property appreciation.",
        "xp_reward": 350,
        "coin_reward": 175,
        "questions": [{"id": i, "q": f"Question {i} for Module 6"} for i in range(1, 11)]
    },
    {
        "id": "m7",
        "badge_id": "b7",
        "title": "Wealth Building & Portfolio Management",
        "description": "Asset allocation, risk diversification, rebalancing, and financial freedom.",
        "xp_reward": 500,
        "coin_reward": 250,
        "questions": [{"id": i, "q": f"Question {i} for Module 7"} for i in range(1, 11)]
    }
]

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/terminal')
def terminal():
    return render_template('index.html')

@app.route('/budget')
def budget():
    return render_template('budget.html')

@app.route('/credit')
def credit():
    return render_template('credit.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/api/quiz/modules')
def get_modules():
    return jsonify({"success": True, "modules": MODULES})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)