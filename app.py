#extrinout 1.1

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, idr

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["idr"] = idr

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///extrinout.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Get breakdown by category and type
    expense_breakdown = db.execute(
        "SELECT category, SUM(amount) AS total_amount, MAX(date) AS last_date FROM expenses WHERE user_id = ? AND type = 'expense' GROUP BY category ORDER BY last_date DESC",
        session["user_id"]
    )

    income_breakdown = db.execute(
        "SELECT category, SUM(amount) AS total_amount, MAX(date) AS last_date FROM expenses WHERE user_id = ? AND type = 'income' GROUP BY category ORDER BY last_date DESC",
        session["user_id"]
    )

    # Calculate total income, expenses, and balance
    total_income = db.execute(
        "SELECT IFNULL(SUM(amount), 0) AS income FROM expenses WHERE user_id = ? AND type = 'income'", session["user_id"]
    )[0]["income"]

    total_expense = db.execute(
        "SELECT IFNULL(SUM(amount), 0) AS expense FROM expenses WHERE user_id = ? AND type = 'expense'", session["user_id"]
    )[0]["expense"]

    balance = total_income - total_expense

    return render_template(
        "index.html",
        income_breakdown=income_breakdown,
        expense_breakdown=expense_breakdown,
        income=total_income,
        expense=total_expense,
        balance=balance
    )


@app.route("/add_entry", methods=["GET", "POST"])
@login_required
def add_entry():
    if request.method == "GET":
        return render_template("add_entry.html")
    else:
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
                return apology("Amount must be a positive number", 400)
        except ValueError:
            return apology("Invalid amount format", 400)

        db.execute("INSERT INTO expenses (user_id, amount, category, type, date) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], amount, category, type_, date)

        flash(f"{type_.capitalize()} entry added successfully.")
        return redirect("/")


@app.route("/history", methods=["GET"])
@login_required
def history():
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "DESC")
    filter_type = request.args.get("type", "all")

    valid_sort_columns = ["category", "date", "amount"]
    if sort_by not in valid_sort_columns:
        sort_by = "date"
    if order not in ["ASC", "DESC"]:
        order = "DESC"

    if filter_type in ["income", "expense"]:
        expenses = db.execute(f"""
            SELECT amount, category, type, date FROM expenses
            WHERE user_id = ? AND type = ? ORDER BY {sort_by} {order}
        """, session["user_id"], filter_type)
    else:
        expenses = db.execute(f"""
            SELECT amount, category, type, date FROM expenses
            WHERE user_id = ? ORDER BY {sort_by} {order}
        """, session["user_id"])

    return render_template("history.html", expenses=expenses, sort_by=sort_by, order=order, selected_type=filter_type)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        if not password:
            return apology("must provide password", 403)

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
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            return apology("user's input is blank", 400)
        elif len(password) < 8 or len(confirmation) < 8:
            return apology("password of 8 characters", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)
        else:
            try:
                hash = generate_password_hash(password)
                db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
                flash("Account created successfully. You can now log in.")
                return redirect("/")
            except ValueError:
                return apology("username already exists", 400)


@app.route("/delete_entry", methods=["GET", "POST"])
@login_required
def delete_entry():
    if request.method == "GET":
        filter_type = request.args.get("type", "all")

        if filter_type in ["income", "expense"]:
            entries = db.execute(
                "SELECT id, amount, category, type, date FROM expenses WHERE user_id = ? AND type = ?",
                session["user_id"], filter_type
            )
        else:
            entries = db.execute(
                "SELECT id, amount, category, type, date FROM expenses WHERE user_id = ?",
                session["user_id"]
            )

        return render_template("delete_entry.html", entries=entries, selected_type=filter_type)

    else:
        entry_id = request.form.get("entry_id")

        if not entry_id:
            return apology("Please select an entry to delete", 400)

        expense = db.execute(
            "SELECT * FROM expenses WHERE id = ? AND user_id = ?", entry_id, session["user_id"]
        )

        if not expense:
            return apology("Entry not found", 400)

        db.execute("DELETE FROM expenses WHERE id = ?", entry_id)

        flash("Entry deleted.")
        return redirect("/delete_entry")