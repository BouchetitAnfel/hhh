import xmlrpc.client
import time
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

attack_running = False

def attack_simulation():
    global attack_running
    attack_running = True
    proxy = xmlrpc.client.ServerProxy("http://localhost:10001")  

    if proxy.acquire_lock("client1"):
        print("🔒 LOCK ACQUIRED - Other clients will be blocked")
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
    return render_template('index.html', attack_status=attack_running)

@app.route('/launch_attack', methods=['POST'])
def launch_attack():
    global attack_running
    if attack_running:
        return jsonify({"error": "The server is already under attack!"}), 400
    threading.Thread(target=attack_simulation).start()
    return jsonify({"message": "Attack launched successfully!"})

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    global attack_running
    if not attack_running:
        return jsonify({"error": "No attack is currently running!"}), 400
    attack_running = False
    proxy = xmlrpc.client.ServerProxy("http://localhost:10001")
    proxy.release_lock("client1")
    return jsonify({"message": "Attack stopped successfully!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)  