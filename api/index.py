from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__, template_folder="../templates")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_iss_pos')
def get_iss_pos():
    try:
        r = requests.get(
            "https://api.wheretheiss.at/v1/satellites/25544",
            timeout=5
        )
        data = r.json()

        return jsonify({
            "lat": data["latitude"],
            "lon": data["longitude"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/calculate')
def calculate():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        tz_name = request.args.get('tz', 'UTC')

        r = requests.get(
            "https://api.wheretheiss.at/v1/satellites/25544",
            timeout=5
        )
        data = r.json()

        iss_lat = data["latitude"]
        iss_lon = data["longitude"]

        distance = ((iss_lat - lat) ** 2 + (iss_lon - lon) ** 2) ** 0.5

        now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        local_time = now.astimezone(ZoneInfo(tz_name))

        return jsonify({
            "next_pass": local_time.strftime('%Y-%m-%d %I:%M:%S %p'),
            "distance_estimate": distance
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def handler(environ, start_response):
    return app(environ, start_response)
