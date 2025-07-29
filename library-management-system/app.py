from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="library",
    port=3307
)
cursor = db.cursor(dictionary=True)

def ensure_connection():
    global db, cursor
    if not db.is_connected():
        db.reconnect()
        cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        ensure_connection()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        ensure_connection()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists. Try a different one.", "danger")
            return redirect(url_for('register'))

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = (
            request.form['title'],
            request.form['author'],
            request.form['isbn'],
            request.form['publisher'],
            request.form['year'],
            request.form['category']
        )
        ensure_connection()
        cursor.execute(
            "INSERT INTO books (title, author, isbn, publisher, year, category) VALUES (%s, %s, %s, %s, %s, %s)",
            data
        )
        db.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_book.html')

@app.route('/books')
def books():
    if 'username' not in session:
        return redirect(url_for('login'))

    ensure_connection()
    cursor.execute("SELECT * FROM books")
    book_list = cursor.fetchall()
    return render_template('view_books.html', books=book_list)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
