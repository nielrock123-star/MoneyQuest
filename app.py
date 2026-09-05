from flask import Flask, render_template, jsonify, request
import os
import re
import time
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

LESSONS = [
    "Separate needs, wants, and savings. The 50/30/20 framework assigns about 50% of take-home pay to needs, 30% to wants, and 20% to savings or debt payoff. Build an emergency fund covering three to six months of essential expenses.",
    "Credit scores are influenced most by payment history and credit utilization. Pay on time, keep balances well below your limits, and avoid opening several new accounts at once.",
    "Stocks represent ownership in companies. Index funds and ETFs spread risk across many companies, while dollar-cost averaging invests a consistent amount on a schedule instead of trying to time the market.",
    "Tax planning uses legal accounts and timing choices. Traditional retirement contributions may reduce taxable income today, while qualified Roth withdrawals can be tax-free later.",
    "Cryptocurrency uses digital wallets and blockchain networks. Prices can be extremely volatile, transactions may be irreversible, and protecting private keys is the owner’s responsibility.",
    "Real estate returns come from rental income, appreciation, and equity. Buying also includes interest, taxes, insurance, maintenance, and closing costs.",
    "Wealth building combines a savings rate, diversified investments, reasonable risk, and time. Rebalancing restores your target allocation when market movements change it."
]

QUESTION_BANKS = [
    [("What share of take-home pay does the 50/30/20 rule assign to needs?", ["20%", "30%", "50%", "80%"], 2), ("A suitable starter emergency fund is kept primarily for:", ["Daily entertainment", "Unexpected essential expenses", "Speculative trading", "Luxury purchases"], 1), ("Which is usually a want?", ["Rent", "Groceries", "Streaming subscription", "Basic utilities"], 2), ("Compound interest earns returns on:", ["Only taxes", "Principal and accumulated interest", "Only fees", "Credit limits"], 1), ("A high-yield savings account is useful because it offers:", ["Liquidity and interest", "Guaranteed stock gains", "Unlimited credit", "Tax-free wages"], 0), ("Automating savings helps by:", ["Creating consistency", "Eliminating all risk", "Raising a credit limit", "Avoiding every tax"], 0), ("Net income means pay:", ["Before deductions", "After deductions", "Before earning", "Before budgeting"], 1), ("Inflation generally reduces cash's:", ["Purchasing power", "Account number", "Liquidity", "FDIC coverage"], 0), ("A budget is best described as a:", ["Spending plan", "Loan application", "Credit report", "Tax penalty"], 0), ("A good first budgeting step is to:", ["Track income and expenses", "Buy stocks", "Close all accounts", "Ignore irregular bills"], 0)],
    [("The largest FICO factor is usually:", ["Payment history", "Credit mix", "New accounts", "Age only"], 0), ("Credit utilization is:", ["Debt divided by available credit", "Income divided by rent", "Savings divided by taxes", "Interest divided by income"], 0), ("A lower utilization ratio is generally:", ["Better for scores", "Always illegal", "A late payment", "A tax deduction"], 0), ("Checking your own score is normally a:", ["Hard inquiry", "Soft inquiry", "Default", "Collection"], 1), ("A hard inquiry can follow:", ["Applying for a credit card", "Viewing your report", "Paying cash", "Making a budget"], 0), ("Paying on time primarily protects:", ["Payment history", "Stock price", "Mortgage rate forever", "Tax bracket"], 0), ("A secured card is backed by a:", ["Cash deposit", "Stock dividend", "Tax refund", "Mortgage"], 0), ("Closing an old card can reduce available:", ["Credit", "Income", "Rent", "Insurance"], 0), ("APR measures a borrowing cost over:", ["One year", "One hour", "One purchase only", "A lifetime"], 0), ("The safest debt habit is to:", ["Pay at least on time and reduce balances", "Max every card", "Ignore statements", "Open accounts monthly"], 0)],
    [("A stock represents:", ["Company ownership", "A bank deposit", "A tax bill", "A rental lease"], 0), ("An ETF is generally a:", ["Basket of investments", "Credit score", "Checking account", "Mortgage"], 0), ("Diversification mainly reduces:", ["Single-company risk", "Every possible loss", "Taxes to zero", "Inflation completely"], 0), ("Dollar-cost averaging invests:", ["A fixed amount regularly", "Only at market peaks", "Only in cash", "After every rumor"], 0), ("Market capitalization equals price times:", ["Shares outstanding", "Taxes paid", "Employees", "Debt payments"], 0), ("A dividend is a distribution to:", ["Shareholders", "Only regulators", "Credit bureaus", "Tenants"], 0), ("A bond is generally a:", ["Loan to an issuer", "Piece of real estate", "Stock split", "Tax form"], 0), ("Long-term investing should consider:", ["Risk tolerance and time horizon", "Only headlines", "Guaranteed returns", "Daily predictions"], 0), ("An index fund usually aims to:", ["Track a market index", "Guarantee profit", "Avoid all fees", "Set tax rates"], 0), ("Past performance is:", ["Not a guarantee of future results", "A guaranteed forecast", "Always irrelevant", "A tax credit"], 0)],
    [("A traditional 401(k) contribution may reduce:", ["Current taxable income", "Credit utilization", "Rent", "Stock volatility"], 0), ("A Roth IRA is generally funded with:", ["After-tax money", "Only borrowed money", "Mortgage proceeds", "Credit points"], 0), ("A tax bracket applies to:", ["A range of taxable income", "Only your bank balance", "Your credit limit", "Every purchase equally"], 0), ("A W-2 usually reports:", ["Employee wages", "Stock ownership", "Mortgage equity", "Crypto keys"], 0), ("A 1099 may report:", ["Nonemployee income", "A credit score", "A property deed", "A debit PIN"], 0), ("A deduction generally lowers:", ["Taxable income", "Your salary rate", "Your credit limit", "Share count"], 0), ("Capital gains come from selling an asset for:", ["More than its basis", "Less than zero", "A fixed wage", "A credit inquiry"], 0), ("Tax-advantaged accounts should be chosen based on:", ["Goals and eligibility", "Social media only", "Guaranteed returns", "Account color"], 0), ("Keeping tax records helps support:", ["Your tax return", "A stock split", "A credit freeze", "A wallet seed"], 0), ("A tax professional can help with:", ["Personal tax questions", "Guaranteeing refunds", "Setting stock prices", "Removing all taxes"], 0)],
    [("A blockchain is best described as a:", ["Distributed digital ledger", "Savings account", "Credit bureau", "Tax bracket"], 0), ("A crypto wallet primarily manages:", ["Keys and transactions", "Mortgage rates", "W-2 forms", "Credit scores"], 0), ("Crypto prices are often:", ["Volatile", "Fixed by law", "Guaranteed", "Unchangeable"], 0), ("A private key should be:", ["Kept secret", "Posted publicly", "Shared in a chat", "Printed on a billboard"], 0), ("A smart contract is:", ["Code that can execute rules", "A mortgage document", "A credit report", "A tax refund"], 0), ("A major crypto risk is:", ["Irreversible transactions", "Guaranteed insurance", "No price movement", "Unlimited refunds"], 0), ("DeFi commonly refers to:", ["Decentralized finance", "Deferred filing", "Debt fixing", "Daily finance"], 0), ("Diversifying digital assets can:", ["Reduce concentration risk", "Guarantee profit", "Remove volatility", "Recover lost keys"], 0), ("A seed phrase should be stored:", ["Securely offline", "In public comments", "In an unknown link", "With a stranger"], 0), ("Before buying crypto, an investor should:", ["Understand the risks", "Assume guaranteed returns", "Borrow without limits", "Ignore security"], 0)],
    [("Home equity is market value minus:", ["Remaining mortgage debt", "Annual income", "Credit limit", "Stock dividends"], 0), ("A down payment is paid:", ["Up front toward a purchase", "Only after selling", "To a credit bureau", "As a tax bracket"], 0), ("PMI may be required when a down payment is:", ["Below a lender's threshold", "Always 100%", "Paid in cash", "A dividend"], 0), ("A fixed mortgage rate:", ["Stays constant under its terms", "Changes every hour", "Tracks stocks", "Eliminates taxes"], 0), ("Property taxes are paid to:", ["A local government", "A stock exchange", "A credit card", "A wallet"], 0), ("Maintenance is a cost of:", ["Owning property", "Checking credit", "Buying an ETF", "Filing a W-2"], 0), ("Renting often offers more:", ["Flexibility", "Equity", "Ownership", "Appreciation"], 0), ("A mortgage preapproval indicates:", ["Tentative borrowing qualification", "A final deed", "Guaranteed approval", "A tax refund"], 0), ("A REIT can provide exposure to:", ["Real estate", "Credit reports", "Tax brackets", "Private keys"], 0), ("A home inspection evaluates:", ["Property condition", "Your FICO score", "Stock earnings", "Tax rate"], 0)],
    [("Asset allocation means choosing a mix of:", ["Asset classes", "Passwords", "Tax forms", "Credit inquiries"], 0), ("Rebalancing restores a portfolio's:", ["Target allocation", "Guaranteed return", "Tax refund", "Credit limit"], 0), ("A higher risk tolerance may support:", ["More volatile investments", "No emergency fund", "Unlimited debt", "No diversification"], 0), ("An emergency fund helps avoid:", ["Selling investments for surprises", "All taxes", "Every market decline", "Credit checks"], 0), ("Compounding benefits most from:", ["Time and reinvestment", "Daily trading", "High fees", "Late payments"], 0), ("A portfolio review should consider:", ["Goals, time, and risk", "Only yesterday's price", "Rumors", "Guaranteed returns"], 0), ("Fees reduce investment:", ["Returns", "Share ownership always", "Tax law", "Income definition"], 0), ("A diversified portfolio can still:", ["Lose value", "Guarantee profit", "Avoid all risk", "Stop inflation"], 0), ("A long-term plan should be:", ["Consistent and periodically reviewed", "Changed on every headline", "Based on promises", "Unfunded"], 0), ("Financial freedom generally requires:", ["Sustainable saving and planning", "One lucky trade", "No budget", "Maximum debt"], 0)]
]

for module, lesson, bank in zip(MODULES, LESSONS, QUESTION_BANKS):
    module['lesson'] = lesson
    module['questions'] = [
        {'id': index + 1, 'q': question, 'options': options, 'answer': answer,
         'explanation': f'The correct answer is {options[answer]}.'}
        for index, (question, options, answer) in enumerate(bank)
    ]


def fetch_quote(ticker):
    symbol = ticker.strip().upper()
    if not re.fullmatch(r'[A-Z0-9^=.-]{1,15}', symbol):
        raise ValueError('Enter a valid ticker symbol.')

    metadata = {}
    try:
        response = requests.get(
            f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}',
            params={'range': '5d', 'interval': '1d', 'events': 'history'},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        response.raise_for_status()
        result = (response.json().get('chart', {}).get('result') or [None])[0]
        metadata = result.get('meta', {}) if result else {}
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

    price = float(metadata.get('regularMarketPrice') or closes[-1])
    previous = float(
        metadata.get('previousClose')
        or metadata.get('chartPreviousClose')
        or (closes[-2] if len(closes) > 1 else price)
    )
    change = price - previous
    info = {}
    try:
        summary_response = requests.get(
            f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}',
            params={'modules': 'assetProfile,price,summaryDetail,defaultKeyStatistics'},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        summary_response.raise_for_status()
        summary = (summary_response.json().get('quoteSummary', {}).get('result') or [{}])[0]
        for section in summary.values():
            if isinstance(section, dict):
                info.update({key: value.get('raw', value) if isinstance(value, dict) else value for key, value in section.items()})
    except (requests.RequestException, ValueError, KeyError):
        pass

    if not info:
        try:
            info = yf.Ticker(symbol).info
        except Exception:
            info = {}

    if not info.get('marketCap') or not info.get('trailingPE'):
        try:
            fundamentals_response = requests.get(
                f'https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}',
                params={
                    'type': 'quarterlyMarketCap,quarterlyPeRatio',
                    'period1': 0,
                    'period2': int(time.time())
                },
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            fundamentals_response.raise_for_status()
            for series in fundamentals_response.json().get('timeseries', {}).get('result', []):
                for key in ('quarterlyMarketCap', 'quarterlyPeRatio'):
                    values = series.get(key) or []
                    if values and values[-1].get('reportedValue', {}).get('raw') is not None:
                        if key == 'quarterlyMarketCap' and not info.get('marketCap'):
                            info['marketCap'] = values[-1]['reportedValue']['raw']
                        if key == 'quarterlyPeRatio' and not info.get('trailingPE'):
                            info['trailingPE'] = values[-1]['reportedValue']['raw']
        except (requests.RequestException, ValueError, KeyError, TypeError):
            pass
    return {
        'success': True,
        'symbol': symbol,
        'name': info.get('shortName') or info.get('longName') or symbol,
        'price': price,
        'change': change,
        'percent_change': (change / previous * 100) if previous else 0.0,
        'market_cap': info.get('marketCap', 'N/A'),
        'pe_ratio': info.get('trailingPE', 'N/A'),
        'high_52': info.get('fiftyTwoWeekHigh') or metadata.get('fiftyTwoWeekHigh', 'N/A'),
        'low_52': info.get('fiftyTwoWeekLow') or metadata.get('fiftyTwoWeekLow', 'N/A')
    }


def yahoo_news(query='stock market'):
    response = requests.get(
        'https://query1.finance.yahoo.com/v1/finance/search',
        params={'q': query, 'newsCount': 20, 'quotesCount': 0, 'lang': 'en-US', 'region': 'US'},
        headers={'User-Agent': 'Mozilla/5.0'},
        timeout=10
    )
    response.raise_for_status()
    news = response.json().get('news', [])
    return [
        {
            'title': item.get('title'),
            'publisher': item.get('publisher', 'Yahoo Finance'),
            'link': item.get('link', 'https://finance.yahoo.com/'),
            'related': item.get('relatedTickers', ['MARKET'])[0] if item.get('relatedTickers') else 'MARKET',
            'pubDate': item.get('providerPublishTime', '')
        }
        for item in news
        if item.get('title') and item.get('link')
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


@app.route('/api/news')
def get_market_news():
    try:
        articles = yahoo_news()
    except (requests.RequestException, ValueError, KeyError):
        articles = []

    if not articles:
        for symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']:
            try:
                items = yf.Ticker(symbol).news or []
                for item in items[:3]:
                    content = item.get('content', item)
                    title = content.get('title') or item.get('title')
                    link_data = content.get('canonicalUrl') or content.get('clickThroughUrl') or {}
                    link = link_data.get('url') if isinstance(link_data, dict) else item.get('link')
                    if title and link:
                        articles.append({
                            'title': title,
                            'publisher': content.get('provider', {}).get('displayName', 'Yahoo Finance') if isinstance(content.get('provider'), dict) else 'Yahoo Finance',
                            'link': link,
                            'related': symbol,
                            'pubDate': content.get('pubDate', '')
                        })
            except Exception:
                continue
            if len(articles) >= 12:
                break

    return jsonify({'success': True, 'news': articles[:12]})


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


@app.route('/api/portfolio/topup', methods=['POST'])
def top_up_portfolio():
    data = request.get_json(silent=True) or {}
    try:
        amount = float(data.get('amount', 0))
    except (TypeError, ValueError):
        amount = 0
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid cash amount.'}), 400
    PORTFOLIO['cash'] += amount
    return get_portfolio()


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
    app.run(host='0.0.0.0', port=port, debug=False)