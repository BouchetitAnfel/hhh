import xmlrpc.client
import time
import threading
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import socketserver
import threading

app = Flask(__name__)

attack_running = False
lock_holder = None

class ThreadedXMLRPCServer(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    pass

def acquire_lock(client_id):
    global lock_holder
    if lock_holder is None:
        lock_holder = client_id
        print(f"Lock acquired by {client_id}")
        return True
    else:
        print(f"Lock acquisition failed for {client_id}, already held by {lock_holder}")
        return False

def release_lock(client_id):
    global lock_holder
    if lock_holder == client_id:
        lock_holder = None
        print(f"Lock released by {client_id}")
        return True
    else:
        print(f"Release failed: {client_id} doesn't hold the lock")
        return False

def get_lock_status():
    global lock_holder
    return lock_holder

def start_xmlrpc_server():
    server = ThreadedXMLRPCServer(("localhost", 10001), 
                                  allow_none=True)
    server.register_function(acquire_lock, "acquire_lock")
    server.register_function(release_lock, "release_lock")
    server.register_function(get_lock_status, "get_lock_status")
    
    print("XML-RPC server started on port 10001")
    server.serve_forever()

xmlrpc_thread = threading.Thread(target=start_xmlrpc_server, daemon=True)
xmlrpc_thread.start()

def attack_simulation():
    global attack_running
    attack_running = True
    proxy = xmlrpc.client.ServerProxy("http://localhost:10001")

    if proxy.acquire_lock("client1"):
        print("🔒 LOCK ACQUIRED - Other clients will be blocked")
        print("Attack running - app in error state")
        try:
            while attack_running: 
                time.sleep(1)
        except KeyboardInterrupt:
            proxy.release_lock("client1")
            print("🔓 Lock released")
    else:
        print("Server is already locked by another client")

    attack_running = False  




@app.route('/')
def home():
    global attack_running, lock_holder
    if True:
       return redirect(url_for('error'))
    return render_template('HomePage.html')  

@app.route('/error')
def error():
    return render_template('error_page.html')

@app.route('/main')
def main():
    global attack_running, lock_holder
    if attack_running or lock_holder is not None:
        return redirect(url_for('error')) 

    return render_template('MainPage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global attack_running, lock_holder
    if attack_running or lock_holder is not None:
        return redirect(url_for('error')) 

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('clients.db')  
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM clients WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        if user:
            return redirect(url_for('home'))  
        else:
            return "Invalid email or password"  

    return render_template('login.html')  


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if password != confirmPassword:
            return "Passwords do not match!"

        conn = sqlite3.connect('clients.db') 
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('main'))  

    return render_template('signup.html')

@app.route('/launch_attack', methods=['POST'])
def launch_attack():
    global attack_running
    if attack_running:
        return jsonify({"error": "The server is already under attack!"}), 400
    threading.Thread(target=attack_simulation).start()
    return jsonify({"message": "Attack launched successfully!"})

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    global attack_running, lock_holder
    if not attack_running:
        return jsonify({"error": "No attack is currently running!"}), 400
    attack_running = False
    proxy = xmlrpc.client.ServerProxy("http://localhost:10001")
    if lock_holder is not None:
        proxy.release_lock("client1")
    return jsonify({"message": "Attack stopped successfully!"})

if __name__ == "__main__":
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

    app.run(debug=True, port=8000)  
