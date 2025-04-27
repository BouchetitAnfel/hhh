from flask import Flask, render_template, request, redirect, url_for
import sqlite3
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('HomePage.html')  # your welcome page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        conn = sqlite3.connect('clients.db')
        cursor = conn.cursor()

        # Check if the email exists and the password matches
        cursor.execute("SELECT * FROM clients WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        if user:
            return redirect(url_for('home'))  # If login is successful, redirect to the homepage
        else:
            return "Invalid email or password"  # Error message if login fails

    return render_template('login.html')  # Display the login page if it's a GET request



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if password != confirmPassword:
            return "Passwords do not match!"

        # Save to database
        conn = sqlite3.connect('clients.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))  # After signup, go back to home

    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)
