from flask import Flask, render_template, jsonify, request
import os
import re
import requests
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

PORTFOLIO = {
    "cash": 100000.0,
    "holdings": {}
}


def fetch_quote(ticker):
    symbol = ticker.strip().upper()
    if not re.fullmatch(r'[A-Z0-9^=.-]{1,15}', symbol):
        raise ValueError('Enter a valid ticker symbol.')

    try:
        response = requests.get(
            f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}',
            params={'range': '5d', 'interval': '1d', 'events': 'history'},
            timeout=10
        )
        response.raise_for_status()
        result = (response.json().get('chart', {}).get('result') or [None])[0]
        closes = [] if not result else [
            value for value in result.get('indicators', {}).get('quote', [{}])[0].get('close', [])
            if value is not None
        ]
    except requests.RequestException:
        closes = []

    if not closes:
        try:
            history = yf.Ticker(symbol).history(period='5d', interval='1d', auto_adjust=False)
            closes = history['Close'].dropna().tolist() if 'Close' in history else []
        except Exception:
            closes = []

    if not closes:
        try:
            response = requests.get(
                f'https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d',
                timeout=10
            )
            response.raise_for_status()
            rows = [row.split(',') for row in response.text.strip().splitlines()[1:] if row]
            closes = [float(row[4]) for row in rows if len(row) > 4 and row[4] not in {'', 'N/D'}]
        except (requests.RequestException, ValueError):
            closes = []

    if not closes:
        raise ValueError(f'No quote data found for {symbol}')

    price = float(closes[-1])
    previous = float(closes[-2]) if len(closes) > 1 else price
    change = price - previous
    return {
        'success': True,
        'symbol': symbol,
        'name': symbol,
        'price': price,
        'change': change,
        'percent_change': (change / previous * 100) if previous else 0.0,
        'market_cap': 'N/A',
        'pe_ratio': 'N/A',
        'high_52': 'N/A',
        'low_52': 'N/A'
    }

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


@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    try:
        return jsonify(fetch_quote(ticker))
    except ValueError as error:
        return jsonify({'success': False, 'message': str(error)}), 404
    except Exception as error:
        return jsonify({'success': False, 'message': str(error)}), 502


@app.route('/api/portfolio')
def get_portfolio():
    portfolio = {'cash': PORTFOLIO['cash'], 'holdings': {}}
    for symbol, holding in PORTFOLIO['holdings'].items():
        item = dict(holding)
        try:
            item['current_price'] = fetch_quote(symbol)['price']
        except Exception:
            item['current_price'] = item['avg_price']
        portfolio['holdings'][symbol] = item
    return jsonify({'success': True, 'portfolio': portfolio})


@app.route('/api/trade', methods=['POST'])
def execute_trade():
    data = request.get_json(silent=True) or {}
    action = str(data.get('action', '')).upper()
    symbol = str(data.get('ticker', '')).strip().upper()
    try:
        shares = int(data.get('shares'))
        price = fetch_quote(symbol)['price']
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Enter a valid share quantity and ticker.'}), 400

    if action not in {'BUY', 'SELL'} or shares <= 0:
        return jsonify({'success': False, 'message': 'Invalid trade details.'}), 400

    holding = PORTFOLIO['holdings'].get(symbol)
    if action == 'BUY':
        total = shares * price
        if total > PORTFOLIO['cash']:
            return jsonify({'success': False, 'message': 'Insufficient buying power.'}), 400
        if holding:
            total_shares = holding['shares'] + shares
            holding['avg_price'] = ((holding['shares'] * holding['avg_price']) + total) / total_shares
            holding['shares'] = total_shares
        else:
            PORTFOLIO['holdings'][symbol] = {'shares': shares, 'avg_price': price}
        PORTFOLIO['cash'] -= total
    else:
        if not holding or holding['shares'] < shares:
            return jsonify({'success': False, 'message': 'Not enough shares to sell.'}), 400
        PORTFOLIO['cash'] += shares * price
        holding['shares'] -= shares
        if holding['shares'] == 0:
            del PORTFOLIO['holdings'][symbol]

    return get_portfolio()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)