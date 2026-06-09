from flask import Flask, render_template, request, jsonify
from skyfield.api import Loader, wgs84
from zoneinfo import ZoneInfo

load = Loader('/tmp')

app = Flask(__name__, template_folder='../templates')
_iss = None
_ts = None

def get_iss():
    global _iss, _ts
    if _iss is None:
        ts = load.timescale()
        satellites = load.tle_file('https://celestrak.org/NORAD/elements/stations.txt')
        _iss = {sat.name: sat for sat in satellites}['ISS (ZARYA)']
        _ts = ts
    return _iss, _ts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate')
def calculate():
    try:
        iss, ts = get_iss()
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

@app.route('/get_iss_pos')
def get_iss_pos():
    iss, ts = get_iss()
    t = ts.now()
    geocentric = iss.at(t)
    subpoint = wgs84.subpoint(geocentric)
    return jsonify({"lat": subpoint.latitude.degrees, "lon": subpoint.longitude.degrees})
