from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')
# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, hashed_password))
            conn.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: users.username' in str(e):
                flash('Username already exists', 'error')
            elif 'UNIQUE constraint failed: users.email' in str(e):
                flash('Email already registered', 'error')
            else:
                flash('Database error: ' + str(e), 'error')
            return redirect(url_for('signup'))

        finally:
            conn.close()

    return render_template('signup.html')

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        finally:
            conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

#Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    user_id = session['user_id']
    conn = get_db_connection()

    # Fetch all transactions for this user
    transactions = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()

    # Calculate income, expense, and balance
    income = sum(row['amount'] for row in transactions if row['type'] == 'Income')
    expense = sum(row['amount'] for row in transactions if row['type'] == 'Expense')
    balance = income - expense

    conn.close()

    return render_template("dashboard.html",
                           username=session['username'],
                           income=income,
                           expense=expense,
                           balance=balance,
                           transactions=transactions)
#Add Transaction
@app.route("/add", methods=["POST"])
def add_transaction():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session['user_id']
    date = request.form['date']
    category = request.form['category']
    amount = float(request.form['amount'])
    t_type = request.form['type']

    conn = get_db_connection()
    conn.execute("INSERT INTO transactions (user_id, date, category, amount, type) VALUES (?, ?, ?, ?, ?)",
                 (user_id, date, category, amount, t_type))
    conn.commit()
    conn.close()
    flash("Transaction added successfully.", "success")
    return redirect(url_for("dashboard"))

# Delete Transaction
@app.route("/delete/<int:id>")
def delete_transaction(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    flash("Transaction deleted.", "info")
    return redirect(url_for("dashboard"))

#Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# Run
if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)
