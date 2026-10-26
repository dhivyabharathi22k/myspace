
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "replace-with-a-private-secret"

DB = "lifesync.db"


# Database connection
def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


# Create users and tasks tables
def setup():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                day TEXT NOT NULL,
                time TEXT NOT NULL,
                done INTEGER DEFAULT 0
            )
        """)


# Protect pages that require login
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


# First page: redirect to login
@app.route("/")
def index():
    return redirect(url_for("login"))


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email:
            flash("Please enter your name and email.")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        try:
            with connect() as con:
                con.execute(
                    """INSERT INTO users (name, email, password)
                       VALUES (?, ?, ?)""",
                    (name, email, generate_password_hash(password))
                )

            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("This email is already registered.")
            return redirect(url_for("register"))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        with connect() as con:
            user = con.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("home"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Home
@app.route("/home")
@login_required
def home():
    today = date.today().isoformat()

    with connect() as con:
        tasks = con.execute(
            "SELECT * FROM tasks WHERE day=? ORDER BY time",
            (today,)
        ).fetchall()

    total = len(tasks)
    done = sum(task["done"] for task in tasks)

    return render_template(
        "home.html", tasks=tasks, today=today,
        total=total, done=done
    )


# Add task
@app.route("/add", methods=["POST"])
@login_required
def add():
    with connect() as con:
        con.execute(
            """INSERT INTO tasks (title, category, day, time)
               VALUES (?, ?, ?, ?)""",
            (
                request.form["title"],
                request.form["category"],
                request.form["day"],
                request.form["time"]
            )
        )

    return redirect(request.referrer or url_for("home"))


# Mark task complete / incomplete
@app.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle(task_id):
    with connect() as con:
        con.execute(
            "UPDATE tasks SET done = 1 - done WHERE id = ?",
            (task_id,)
        )

    return redirect(request.referrer or url_for("home"))


# Delete task
@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete(task_id):
    with connect() as con:
        con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    return redirect(request.referrer or url_for("home"))


# Studies and career
@app.route("/studies")
@login_required
def studies():
    return category_page(
        "Studies & Career", ["Study", "Interview", "Job Search"]
    )


# Self-care and wellness
@app.route("/wellness")
@login_required
def wellness():
    return category_page(
        "Self-care & Wellness",
        ["Skincare", "Exercise", "Meditation"]
    )


def category_page(title, categories):
    placeholders = ",".join("?" for _ in categories)

    with connect() as con:
        tasks = con.execute(
            f"""SELECT * FROM tasks
                WHERE category IN ({placeholders})
                ORDER BY day, time""",
            categories
        ).fetchall()

    return render_template(
        "category.html", title=title, categories=categories,
        tasks=tasks, today=date.today().isoformat()
    )


# Schedule
@app.route("/schedule")
@login_required
def schedule():
    with connect() as con:
        tasks = con.execute(
            "SELECT * FROM tasks ORDER BY day, time"
        ).fetchall()

    return render_template(
        "schedule.html", tasks=tasks,
        today=date.today().isoformat()
    )


# Expenses
@app.route("/expenses")
@login_required
def expenses():
    return render_template("expenses.html")


# Savings
@app.route("/savings")
@login_required
def savings():
    return render_template("savings.html")


if __name__ == "__main__":
    setup()
    app.run(debug=True, port=5000)
