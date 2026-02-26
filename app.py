#!/usr/bin/env python3
"""
Adelaide Metro Live Tracker - Flask Application
Real-time public transport tracking for Adelaide, Australia
"""

import json
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from adelaide_metro_routes import adelaide_metro_bp
from utils import calculate_distance

app = Flask(__name__)
app.register_blueprint(adelaide_metro_bp)

# Configuration
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/adelaide-metro/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    })

# Note: /adelaide-metro/api/vehicles, /adelaide-metro/api/routes, and
# /adelaide-metro/api/alerts are handled by the adelaide_metro_bp blueprint.

@app.route('/adelaide-metro/api/nearby')
def api_nearby():
    """Find stops near a location"""
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius', 500))
        limit = int(request.args.get('limit', 5))

        # Load stops data safely
        stops_path = os.path.join(app.root_path, 'static', 'adelaide-metro-stops.js')
        with open(stops_path, 'r') as f:
            raw = f.read()
        # The JS file has extra functions after the array; extract just the JSON array
        after_eq = raw.split('=', 1)[1]
        bracket_end = after_eq.index('];') + 1
        stops = json.loads(after_eq[:bracket_end].strip())

        nearby = []
        for stop in stops:
            # calculate_distance returns km, convert to meters
            dist_m = calculate_distance(lat, lon, stop['lat'], stop['lon']) * 1000
            if dist_m <= radius:
                nearby.append({**stop, 'distance': round(dist_m)})

        nearby.sort(key=lambda x: x['distance'])

        return jsonify({
            'stops': nearby[:limit],
            'center': {'lat': lat, 'lon': lon},
            'radius': radius
        })
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Invalid parameters: {e}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adelaide-metro/api/plan', methods=['POST'])
def api_plan_trip():
    """Plan a trip between two stops"""
    try:
        data = request.get_json()
        from_stop = data.get('from')
        to_stop = data.get('to')
        
        if not from_stop or not to_stop:
            return jsonify({'error': 'From and to stops required'}), 400
        
        # Simple route planning logic
        # In a real app, this would use GTFS static data
        routes = [{
            'type': 'transit',
            'totalTime': 25,
            'transfers': 0,
            'walkingDistance': 0,
            'legs': [{
                'type': 'transit',
                'mode': 'bus',
                'route': 'Route 174',
                'from': from_stop,
                'to': to_stop,
                'departure': data.get('departure_time', '12:00'),
                'arrival': '12:25',
                'duration': 25
            }]
        }]
        
        return jsonify({'routes': routes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
