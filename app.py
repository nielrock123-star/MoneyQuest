from flask import Flask, render_template, jsonify, request
import yfinance as yf
import os
from dotenv import load_dotenv
from chatbot import get_advisor

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', True)
app.config['HOST'] = os.getenv('HOST', '127.0.0.1')
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
        symbol = ticker.upper()
        stock = yf.Ticker(symbol)
        info = stock.info

        price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0.0)
        prev_close = info.get('previousClose') or price
        change = price - prev_close
        percent_change = (change / prev_close * 100) if prev_close else 0.0

        return jsonify({
            "success": True,
            "symbol": symbol,
            "name": info.get('shortName', symbol),
            "price": float(price),
            "change": float(change),
            "percent_change": float(percent_change),
            "market_cap": info.get('marketCap', 'N/A'),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "high_52": info.get('fiftyTwoWeekHigh', 'N/A'),
            "low_52": info.get('fiftyTwoWeekLow', 'N/A')
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

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
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)