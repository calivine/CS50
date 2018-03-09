from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *
from datetime import datetime, date, time

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        id = session["user_id"]
        port = db.execute("SELECT * FROM portfolio WHERE id = :session", session = id)
        portfolio = []
        total_holding = []
        for sym in port:
            stock_info = lookup(sym["symbol"])
            stock = merge_two_dicts(sym, stock_info)
            stock.update({'total':sym["shares"] * stock_info["price"]})
            stock["price"] = usd(stock_info["price"])
            total_holding.append(stock['total'])
            stock['total'] = usd(stock['total'])
            portfolio.append(stock)
        
        stockholdings = sum(total_holding)
        cashbal = db.execute("SELECT cash FROM users WHERE id = :session", session = id)
        
        return render_template("index.html", portfolios = portfolio, total = usd(stockholdings), balance = usd(int(cashbal[0]["cash"])))
        
    if request.method == "POST":
        id = session["user_id"]
        port = db.execute("SELECT * FROM portfolio WHERE id = :session", session = id)
        portfolio = []
        total_holding = []
        for sym in port:
            stock_info = lookup(sym["symbol"])
            stock = merge_two_dicts(sym, stock_info)
            stock.update({'total':sym["shares"] * stock_info["price"]})
            stock["price"] = usd(stock_info["price"])
            total_holding.append(stock['total'])
            stock['total'] = usd(stock['total'])
            portfolio.append(stock)
        
        stockholdings = sum(total_holding)
        cashbal = db.execute("SELECT cash FROM users WHERE id = :session", session = id)
        
        if not request.form.get("deposit"):
            return apology("Must enter a dollar amount")
        set = "!@#$%^&*(),<>?/;:"
        for c in set:
            if c in request.form.get("deposit"):
                return apology("No special characters")
            
        if str.isalpha(request.form.get("deposit")):
            return apology("Must enter a dollar amount")
        if int(request.form.get("deposit")) <= 0:
            return apology("Deposit amount must be greater than zero")
        
        deposit = int(request.form.get("deposit"))
            # balance = db.execute("SELECT cash FROM users WHERE id = :session", session = id)
        cashbalance = cashbal[0]["cash"]
        cashbalance = cashbalance + deposit
        db.execute("UPDATE users SET cash = :cash WHERE id = :userid", userid = id, cash = cashbalance)
        return render_template("index.html", portfolios = portfolio, total = usd(stockholdings), balance = usd(int(cashbal[0]["cash"])))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "GET":
        return render_template("buy.html")
    if request.method == "POST":
    # Ensure proper useage:
        if not request.form.get("symbol"):
            return apology("Must enter ticker symbol")
        elif not request.form.get("shares"):
            return apology("How many shares?")
        sharetest = request.form.get("shares")
        if "." in sharetest:
            return apology("Shares must be a whole number")
        if sharetest.isalpha():
            return apology("Must be numeric")
        if int(request.form.get("shares")) <= 0:
            return apology("shares must be positive. otherwise it doesn't make sense")
        # set user 
        id=session["user_id"]
        # get symbol and number of shares
        symbol=request.form.get("symbol")
        shares=int(request.form.get("shares"))
        
        # Check that stock symbol is valid
        if lookup(symbol) == None:
            return apology("must provide valid stock symbol")
        # get user's balance
        balance=db.execute("SELECT cash FROM users WHERE id = :session", session=id)
        balance=balance[0]["cash"]
    
        # get stock data
        stock=lookup(symbol)
    
        # calculate price and check that user has sufficient funds
        price=stock["price"] * shares
        
        if balance < price:
            return apology("Insufficient Funds")
        # Insert transaction into History table
        db.execute("INSERT INTO history (id, symbol, shares, price, type) Values(:id, :symbol, :shares, :price, :type)", id = id, symbol = stock["symbol"], shares = shares, price = price, type="Buy")
        
        # Update user's portfolio with shares purchased
        check_symbol = db.execute("SELECT * FROM portfolio WHERE id = :session AND symbol = :symbol", session = id, symbol = stock["symbol"])
        if not check_symbol:
            db.execute("INSERT INTO portfolio (id, symbol, shares) Values(:id, :symbol, :shares)", id = id, symbol = stock["symbol"], shares = shares)
        else:
            updated_shares = int(check_symbol[0]["shares"] + shares)
            db.execute("UPDATE portfolio SET shares = :shares WHERE id = :session AND symbol = :symbol", shares = updated_shares, session = id, symbol = stock["symbol"])
        
        # update user's balance
        balance=balance-price
        db.execute("UPDATE users SET cash = :cash WHERE id = :userid", userid = id, cash = balance)
        
        return redirect(url_for("index"))

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    if request.method == "GET":
        id = session["user_id"]
        history = db.execute("SELECT * FROM history WHERE id = :session", session = id)
        for hist in history:
            hist["price"] = usd(hist["price"])
        return render_template("history.html", history = history)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must enter symbol")
        else:
            symbol = lookup(request.form.get("symbol"))
            if symbol is None:
                return apology("Must enter valid symbol")
            return render_template("quoted.html", symbol=symbol["name"], result=usd(symbol["price"]), resultn=symbol["name"])
    elif request.method == "GET":
        return render_template("quote.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        if not request.form.get("username"):
            return apology("Must enter username")
        elif not request.form.get("password"):
            return apology("Must create a password")
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("Passwords do not match")
        
        hap = pwd_context.hash(request.form.get("password"))
        # check for duplicate username
        result = db.execute("INSERT INTO users (hash, username) Values(:hap, :username)", hap=pwd_context.hash(request.form.get("password")), username = request.form.get("username"))
        if not result:
            return apology("User name already exists")
        # Query database to let user access page
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
        
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "GET":
        id = session["user_id"]
        stocks = db.execute("SELECT * FROM portfolio WHERE id = :session", session = id)
        return render_template("sell.html", stocks = stocks)
    elif request.method == "POST":
        id = session["user_id"]
        # Check that user selected a stock
        if not request.form.get("symbol"):
            return apology("Must provide stock symbol")
        elif not request.form.get("shares"):
            return apology("How many shares?")
        if int(request.form.get("shares")) <= 0:
            return apology("Cannot sell negative shares")
        # Get values from sell template
        stock = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        # Check that user has sufficient funds
        check_shares = db.execute("SELECT shares FROM portfolio WHERE id = :session AND symbol =:symbol", session = id, symbol = stock)
        if int(check_shares[0]["shares"]) < shares:
            return apology("You don't have enough shares to sell")
        balance = db.execute("SELECT cash FROM users WHERE id = :session", session = id)
        balance = balance[0]["cash"]
        sale = lookup(stock)
        saleprice = shares * sale["price"]
        sharecount = check_shares[0]["shares"] - shares
        #Update Portfolio
        if sharecount == 0:
            # delete stock entry from portfolio
            db.execute("DELETE FROM portfolio WHERE id = :session AND symbol =:symbol", session = id, symbol = stock)
        else:
            db.execute("UPDATE portfolio SET shares = :shares WHERE id = :session AND symbol =:symbol", session = id, shares = sharecount, symbol = stock)
        # Update Cash balance
        db.execute("UPDATE users SET cash = :cash WHERE id = :userid", userid = id, cash = (balance + saleprice))
        
        db.execute("INSERT INTO history (id, symbol, shares, price, type) Values(:id, :symbol, :shares, :price, :type)", id = id, symbol = stock, shares = shares, price = saleprice, type="Sell")
        
        stocks = db.execute("SELECT * FROM portfolio WHERE id = :session", session = id)

        return redirect(url_for("index"))