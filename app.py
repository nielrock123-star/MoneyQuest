from flask import Flask, render_template, jsonify, request
import yfinance as yf
import os
import re
import requests
from dotenv import load_dotenv
from chatbot import get_advisor

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', False)
app.config['HOST'] = os.getenv('HOST', '0.0.0.0')
app.config['PORT'] = int(os.getenv('PORT', 5000))

PORTFOLIO = {
    "cash": 100000.00,
    "holdings": {}
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

@app.route('/api/news')
def get_market_news():
    """Fetch market news using major market ticker symbols."""
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', '^GSPC']
    formatted_news = []
    
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            news_items = ticker.news
            if not news_items:
                continue

            for item in news_items[:3]:
                content = item.get('content', item)
                title = content.get('title') or item.get('title')
                if not title:
                    continue

                link = content.get('canonicalUrl', {}).get('url') if isinstance(content.get('canonicalUrl'), dict) else None
                if not link:
                    link = content.get('clickThroughUrl', {}).get('url') if isinstance(content.get('clickThroughUrl'), dict) else None
                if not link:
                    link = item.get('link', '#')

                provider = content.get('provider', {}).get('displayName') if isinstance(content.get('provider'), dict) else None
                if not provider:
                    provider = item.get('publisher', 'Market News')

                formatted_news.append({
                    "title": title,
                    "publisher": provider,
                    "link": link,
                    "related": symbol.replace('^GSPC', 'S&P 500'),
                    "pubDate": content.get('pubDate') or item.get('providerPublishTime', '')
                })

                if len(formatted_news) >= 12:
                    break
            if len(formatted_news) >= 12:
                break
        except Exception:
            continue

    if not formatted_news:
        formatted_news = [
            {
                "title": "Markets Await Upcoming Economic Data and Tech Earnings Reports",
                "publisher": "Financial Times",
                "link": "https://finance.yahoo.com",
                "related": "MARKET",
                "pubDate": "Just now"
            },
            {
                "title": "Fed Signals Steady Approach to Interest Rates Amid Economic Stability",
                "publisher": "Wall Street Journal",
                "link": "https://finance.yahoo.com",
                "related": "FED",
                "pubDate": "1 hour ago"
            }
        ]

    return jsonify({"success": True, "news": formatted_news})

@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    try:
        return jsonify(fetch_quote(ticker))
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 502

def fetch_quote(ticker):
    symbol = ticker.strip().upper()
    if not re.fullmatch(r'[A-Z0-9^=.-]{1,15}', symbol):
        raise ValueError('Enter a valid ticker symbol.')

    chart_url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
    params = {'range': '5d', 'interval': '1d', 'events': 'history'}
    try:
        response = requests.get(chart_url, params=params, timeout=10)
        response.raise_for_status()
        chart = response.json().get('chart', {})
        result = (chart.get('result') or [None])[0]
        if result:
            closes = [value for value in result.get('indicators', {}).get('quote', [{}])[0].get('close', []) if value is not None]
            if closes:
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
    except requests.RequestException:
        pass

    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period='5d', interval='1d', auto_adjust=False)
        closes = history['Close'].dropna() if not history.empty and 'Close' in history else []
    except Exception:
        closes = []

    if len(closes) > 0:
        price = float(closes.iloc[-1])
        previous = float(closes.iloc[-2]) if len(closes) > 1 else price
    else:
        fallback_url = f'https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d'
        fallback_response = requests.get(fallback_url, timeout=10)
        fallback_response.raise_for_status()
        rows = [row.split(',') for row in fallback_response.text.strip().splitlines()[1:] if row]
        closes = [float(row[4]) for row in rows if len(row) > 4 and row[4] not in {'', 'N/D'}]
        if not closes:
            raise ValueError(f'No quote data found for {symbol}')
        price = closes[-1]
        previous = closes[-2] if len(closes) > 1 else price

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
    shares = data.get('shares')
    if action not in {'BUY', 'SELL'} or not re.fullmatch(r'[A-Z0-9^=.-]{1,15}', symbol):
        return jsonify({'success': False, 'message': 'Invalid trade details.'}), 400
    try:
        shares = int(shares)
        price = fetch_quote(symbol)['price']
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Enter a valid share quantity and ticker.'}), 400
    if shares <= 0:
        return jsonify({'success': False, 'message': 'Share quantity must be positive.'}), 400

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

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the user."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"success": False, "message": "Message cannot be empty"}), 400
        
        advisor = get_advisor()
        result = advisor.get_response(user_message)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    """Reset the conversation history."""
    try:
        advisor = get_advisor()
        result = advisor.reset_conversation()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/chat/tip', methods=['GET'])
def get_financial_tip():
    """Get a financial tip from the advisor."""
    try:
        advisor = get_advisor()
        result = advisor.get_financial_tip()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host=host, port=port)