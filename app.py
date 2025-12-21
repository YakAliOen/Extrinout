# CS50x
from collections import defaultdict
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, idr

app = Flask(__name__)
app.jinja_env.filters["idr"] = idr
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///extrinout.db")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# portfolio
@app.route("/")
@login_required
def index():
    expense_breakdown = db.execute(
        "SELECT category, SUM(amount) AS total_amount, MAX(date) AS last_date FROM expenses WHERE user_id = ? AND type = 'expense' GROUP BY category ORDER BY last_date DESC", session["user_id"])
    income_breakdown = db.execute(
        "SELECT category, SUM(amount) AS total_amount, MAX(date) AS last_date FROM expenses WHERE user_id = ? AND type = 'income' GROUP BY category ORDER BY last_date DESC", session["user_id"])
    total_income = db.execute(
        "SELECT IFNULL(SUM(amount), 0) AS income FROM expenses WHERE user_id = ? AND type = 'income'", session["user_id"])[0]["income"]
    total_expense = db.execute(
        "SELECT IFNULL(SUM(amount), 0) AS expense FROM expenses WHERE user_id = ? AND type = 'expense'", session["user_id"])[0]["expense"]
    balance = total_income - total_expense
    nominal_breakdown = db.execute(
        "SELECT category, SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income_total, SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense_total, SUM(CASE WHEN type = 'income' THEN amount WHEN type = 'expense' THEN -amount ELSE 0 END) AS net_total, MAX(date) AS last_date FROM expenses WHERE user_id = ? GROUP BY category ORDER BY last_date DESC", session["user_id"])
    return render_template("index.html", income_breakdown=income_breakdown, expense_breakdown=expense_breakdown, nominal_breakdown=nominal_breakdown, income=total_income, expense=total_expense, balance=balance)


# add entry
@app.route("/add_entry", methods=["GET", "POST"])
@login_required
def add_entry():
    if request.method == "GET":
        rows = db.execute(
            "SELECT DISTINCT category FROM expenses WHERE user_id = ? ORDER BY category COLLATE NOCASE", session["user_id"])
        categories = [r["category"] for r in rows] if rows else []
        return render_template("add_entry.html", categories=categories)
    amount = request.form.get("amount")
    category = request.form.get("category")
    type_ = request.form.get("type")
    date = request.form.get("date")
    if not amount or not category or not date or not type_:
        return apology("All fields must be filled", 400)
    if type_ not in ["income", "expense"]:
        return apology("Invalid type selected", 400)
    try:
        amount = float(amount)
        if amount <= 0:
            return apology("Amount must be positive", 400)
    except ValueError:
        return apology("Invalid amount format", 400)
    db.execute("INSERT INTO expenses (user_id, amount, category, type, date) VALUES (?, ?, ?, ?, ?)",
               session["user_id"], amount, category, type_, date)
    flash("Entry added successfully.")
    return redirect("/add_entry")


# history


@app.route("/history", methods=["GET"])
@login_required
def history():
    filter_type = request.args.get("type", "all")
    if filter_type in ["income", "expense"]:
        rows = db.execute(
            "SELECT amount, category, type, DATE(date) AS day FROM expenses WHERE user_id = ? AND type = ? ORDER BY day DESC, date DESC", session["user_id"], filter_type)
    else:
        rows = db.execute(
            "SELECT amount, category, type, DATE(date) AS day FROM expenses WHERE user_id = ? ORDER BY day DESC, date DESC", session["user_id"])
    grouped_expenses = defaultdict(list)
    for row in rows:
        grouped_expenses[row["day"]].append(row)
    return render_template("history.html", grouped_expenses=grouped_expenses, selected_type=filter_type)


# CS50x
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return apology("must provide username/password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        flash(f"Welcome back, {session['username']}!")
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    if not username or not password or not confirmation:
        return apology("user's input is blank", 400)
    elif len(password) < 8:
        return apology("password of 8 characters", 400)
    elif password != confirmation:
        return apology("passwords do not match", 400)
    try:
        hash_ = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_)
        flash("Account created successfully.")
        return redirect("/")
    except ValueError:
        return apology("username already exists", 400)


# delete entry
@app.route("/delete_entry", methods=["GET", "POST"])
@login_required
def delete_entry():
    if request.method == "POST":
        entry_id = request.form.get("entry_id")
        if not entry_id:
            return apology("Please select an entry to delete", 400)
        entry = db.execute("SELECT id FROM expenses WHERE id = ? AND user_id = ?",
                           entry_id, session["user_id"])
        if not entry:
            return apology("Entry not found", 400)
        db.execute("DELETE FROM expenses WHERE id = ?", entry_id)
        flash("Entry deleted.")
        return redirect("/delete_entry")
    expenses = db.execute(
        "SELECT id, amount, category, date FROM expenses WHERE user_id = ? AND type = 'expense' ORDER BY date DESC", session["user_id"])
    incomes = db.execute(
        "SELECT id, amount, category, date FROM expenses WHERE user_id = ? AND type = 'income' ORDER BY date DESC", session["user_id"])
    return render_template("delete_entry.html", expenses=expenses, incomes=incomes)
