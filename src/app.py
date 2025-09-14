from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

# Create an instance of the Flask class
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Just a random secret key

dataB = "Database/users.db"

# Function to create a users table in the database
def init_db():
    with sqlite3.connect(dataB) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)"
        )
        conn.execute("CREATE TABLE IF NOT EXISTS account (user_id INTEGER NOT NULL, accountName TEXT, amount INTEGER, accessDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)")


# Function to create users
def create_user(username, password):
    pw_hash = generate_password_hash(password)
    try:
        with sqlite3.connect(dataB) as conn:
            cursor = conn.cursor()
            
            # Insert user first
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, pw_hash)
            )
            user_id = cursor.lastrowid  # get the newly created user's ID

            # Insert linked account with that user_id
            cursor.execute(
                "INSERT INTO account (user_id, accountName, amount) VALUES (?, ?, ?)",
                (user_id, "Savings", 0)
            )

        return True
    except sqlite3.IntegrityError as e:
        print("Error creating user:", e)
        return False

    
# Function to check if user is in the users table
def get_user(username):
    with sqlite3.connect(dataB) as conn:
        cur = conn.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return row 

# Functionto get account info 
def account(username):
    with sqlite3.connect(dataB) as conn:
        cur = conn.execute("""
            SELECT u.id, u.username, a.accountName, a.amount, a.accessDate
            FROM users u
            JOIN account a ON u.id = a.user_id
            WHERE u.username = ?
        """, (username,))
        row = cur.fetchone()
        return row

# Define a route for the root URL ("/")
@app.route("/")
def hello_world():
    balanceInfo = account(session["username"])
    return render_template("home.html", session=session, balanceInfo=balanceInfo)

@app.route("/registar", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return redirect(("/registar"))

        if create_user(username, password):
            return redirect(("/login"))
        else:
            return redirect(("/registar"))
    return render_template("registar.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = get_user(username)
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(("/"))
        return "Invalid username or password", 400
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(("/"))

# Run the application
if __name__ == "__main__":
    init_db()
    # create a demo account once
    if not get_user("Bruno"):
        create_user("Bruno", "Mota")
    app.run(debug=True) 