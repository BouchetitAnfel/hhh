from flask import Flask, request, jsonify
from threading import Lock

app = Flask(__name__)

class ForecastCalendar:
    def __init__(self):
        self.forecasts = {
            "2012-11-05": ("Sunny", 5, 22),
            "2012-11-06": ("Cloudy", 3, 18)
        }
        self.lock = Lock()
        self.lock_owner = None
        self.password = "master-of-weather"

    def acquire_lock(self, client_id):
        if not self.lock.locked():
            self.lock_owner = client_id
            self.lock.acquire()
            return True
        return False

    def release_lock(self, client_id):
        if self.lock_owner == client_id:
            self.lock.release()
            self.lock_owner = None
            return True
        return False

    def get_forecast(self, date):
        if self.lock.locked():
            return "SERVER LOCKED - Try again later"
        if date in self.forecasts:
            desc, wind, temp = self.forecasts[date]
            return f"Weather: {desc}, Wind: {wind}, Temp: {temp}°C"
        return "No forecast"

calendar = ForecastCalendar()

@app.route("/acquire_lock", methods=["POST"])
def acquire_lock():
    client_id = request.json.get("client_id")
    success = calendar.acquire_lock(client_id)
    return jsonify({"success": success})

@app.route("/release_lock", methods=["POST"])
def release_lock():
    client_id = request.json.get("client_id")
    success = calendar.release_lock(client_id)
    return jsonify({"success": success})

if __name__ == "__main__":
    app.run(port=10001, debug=True)
