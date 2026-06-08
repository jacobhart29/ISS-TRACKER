from flask import Flask, render_template, request, jsonify
from skyfield.api import load, wgs84
from zoneinfo import ZoneInfo
from datetime import datetime

app = Flask(__name__)

# LOCATION DATA
stations_url = 'https://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
iss = {sat.name: sat for sat in satellites}['ISS (ZARYA)']
ts = load.timescale()

# MAIN PAGE
@app.route('/')
def index():
    return render_template('index.html')

# CALCULATE NEXT PASS
@app.route('/calculate')
def calculate():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        tz_name = request.args.get('tz', 'UTC')
        location = wgs84.latlon(lat, lon)
        t0 = ts.now()
        t1 = ts.utc(t0.utc.year, t0.utc.month, t0.utc.day + 3)
        t, events = iss.find_events(location, t0, t1, altitude_degrees=15.0)
        for ti, event in zip(t, events):
            if event == 0:
                local_time = ti.utc_datetime().astimezone(ZoneInfo(tz_name))
                return jsonify({"next_pass": local_time.strftime('%Y-%m-%d %I:%M:%S %p')})
        return jsonify({"next_pass": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# CURRENT ISS POSITION
@app.route('/get_iss_pos')
def get_iss_pos():
    t = ts.now()
    geocentric = iss.at(t)
    subpoint = wgs84.subpoint(geocentric)
    return jsonify({
        "lat": subpoint.latitude.degrees,
        "lon": subpoint.longitude.degrees
    })

if __name__ == '__main__':
    app.run("0.0.0.0", port=8080, debug=True)
