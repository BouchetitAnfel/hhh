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

    def update_forecast(self, password, date, desc, wind, temp):
        if password != self.password:
            return "Authentication failed"
        if self.lock.locked():
            return "SERVER LOCKED - Cannot update now"
        self.forecasts[date] = (desc, wind, temp)
        return "Forecast updated"

calendar = ForecastCalendar()

@app.route("/get_forecast", methods=["GET"])
def get_forecast():
    date = request.args.get("date")
    result = calendar.get_forecast(date)
    return jsonify({"result": result})

@app.route("/update_forecast", methods=["POST"])
def update_forecast():
    data = request.json
    password = data.get("password")
    date = data.get("date")
    desc = data.get("desc")
    wind = data.get("wind")
    temp = data.get("temp")
    result = calendar.update_forecast(password, date, desc, wind, temp)
    return jsonify({"result": result})

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
