#!/usr/bin/env python3
"""
Adelaide Metro Live Tracker - Flask Application
Real-time public transport tracking for Adelaide, Australia
"""

from flask import Flask, jsonify, render_template, request
import os
from datetime import datetime

# Import our modules
from adelaide_metro_routes import adelaide_metro_bp
from adelaide_metro_gtfs_realtime import get_vehicles, get_routes, get_alerts

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
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/adelaide-metro/api/vehicles')
def api_vehicles():
    """Get live vehicle positions"""
    try:
        vehicles = get_vehicles()
        return jsonify({
            'vehicles': vehicles,
            'count': len(vehicles),
            'updated_at': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adelaide-metro/api/routes')
def api_routes():
    """Get all route definitions"""
    try:
        routes = get_routes()
        return jsonify({
            'routes': routes,
            'count': len(routes)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adelaide-metro/api/alerts')
def api_alerts():
    """Get active service alerts"""
    try:
        alerts = get_alerts()
        return jsonify({
            'alerts': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adelaide-metro/api/nearby')
def api_nearby():
    """Find stops near a location"""
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius', 500))
        limit = int(request.args.get('limit', 5))
        
        # Import stops data
        import json
        stops = json.loads(open('static/adelaide-metro-stops.js').read().split('=')[1].rstrip(';'))
        
        # Calculate distances and filter
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000  # Earth radius in meters
            phi1, phi2 = radians(lat1), radians(lat2)
            dphi = radians(lat2 - lat1)
            dlambda = radians(lon2 - lon1)
            a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
            return 2 * R * atan2(sqrt(a), sqrt(1-a))
        
        nearby = []
        for stop in stops:
            dist = haversine(lat, lon, stop['lat'], stop['lon'])
            if dist <= radius:
                nearby.append({**stop, 'distance': round(dist)})
        
        nearby.sort(key=lambda x: x['distance'])
        
        return jsonify({
            'stops': nearby[:limit],
            'center': {'lat': lat, 'lon': lon},
            'radius': radius
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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
