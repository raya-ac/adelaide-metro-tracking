#!/usr/bin/env python3
"""
Adelaide Metro Real-Time Data Integration
Fetches actual GTFS-RT feeds from Adelaide Metro
"""

import os
import re
import subprocess
import tempfile
import threading
from datetime import datetime, timezone

from google.transit import gtfs_realtime_pb2

from utils import (
    calculate_distance,
    format_adelaide_time,
    get_adelaide_time,
    is_in_adelaide,
    load_stop_id_map,
)

# GTFS-RT URLs
VEHICLE_POSITIONS_URL = "https://gtfs.adelaidemetro.com.au/v1/realtime/vehicle_positions"
TRIP_UPDATES_URL = "https://gtfs.adelaidemetro.com.au/v1/realtime/trip_updates"
SERVICE_ALERTS_URL = "https://gtfs.adelaidemetro.com.au/v1/realtime/service_alerts"

# Adelaide Metro route ID mapping - GTFS-RT uses short codes
TRAIN_ROUTES = {
    # Numeric train route IDs
    '1', '2', '3', '4', '5', '6', '7',
    # Full names
    'Belair', 'Gawler', 'Seaford', 'Flinders', 'Outer Harbor', 'Grange', 'Tonsley',
    # GTFS-RT short codes for trains
    'BEL',      # Belair
    'GAWC',     # Gawler Central
    'GAW',      # Gawler
    'SEAFRD',   # Seaford
    'FLNDRS',   # Flinders
    'OUTHA',    # Outer Harbor
    'PTDOCK',   # Port Dock
    'GRNG',     # Grange
    'TONSL',    # Tonsley
}

TRAM_ROUTES = {
    # Full names
    'Glenelg', 'Botanic', 'glenelg', 'botanic',
    # GTFS-RT short codes for trams
    'GLNELG',   # Glenelg
    'BTANIC',   # Botanic
    'FESTVL',   # Festival Plaza/Entertainment Centre
}

# Load stop ID map from JSON data file (was previously ~8400 lines inline)
STOP_ID_MAP = load_stop_id_map()


def get_vehicle_type(route_id):
    """Determine vehicle type from Adelaide Metro route ID."""
    if route_id in TRAIN_ROUTES or route_id.startswith(('1:', '2:', '3:', '4:', '5:', '6:', '7:')):
        return 'train'
    if route_id in TRAM_ROUTES:
        return 'tram'
    return 'bus'


def get_route_name(route_id):
    """Get human-readable route name."""
    route_names = {
        '1': 'Belair',
        '2': 'Gawler Central',
        '3': 'Seaford',
        '4': 'Flinders',
        '5': 'Outer Harbor',
        '6': 'Grange',
        '7': 'Tonsley',
        'Belair': 'Belair',
        'Gawler': 'Gawler Central',
        'Seaford': 'Seaford',
        'Flinders': 'Flinders',
        'Outer Harbor': 'Outer Harbor',
        'Grange': 'Grange',
        'Tonsley': 'Tonsley',
        'Glenelg': 'Glenelg Tram',
        'Botanic': 'Botanic Tram',
        # GTFS-RT short codes
        'BEL': 'Belair',
        'GAWC': 'Gawler Central',
        'GAW': 'Gawler',
        'SEAFRD': 'Seaford',
        'FLNDRS': 'Flinders',
        'OUTHA': 'Outer Harbor',
        'PTDOCK': 'Port Dock',
        'GRNG': 'Grange',
        'TONSL': 'Tonsley',
        'GLNELG': 'Glenelg Tram',
        'BTANIC': 'Botanic Tram',
        'FESTVL': 'Entertainment Centre',
    }
    return route_names.get(route_id, f'Route {route_id}')


def get_route_destination(route_id):
    """Get destination for a route."""
    destinations = {
        '1': 'Belair', 'Belair': 'Belair',
        '2': 'Gawler Central', 'Gawler': 'Gawler Central',
        '3': 'Seaford', 'Seaford': 'Seaford',
        '4': 'Flinders', 'Flinders': 'Flinders',
        '5': 'Outer Harbor', 'Outer Harbor': 'Outer Harbor',
        '6': 'Grange', 'Grange': 'Grange',
        '7': 'Tonsley', 'Tonsley': 'Tonsley',
        'Glenelg': 'Glenelg',
        'Botanic': 'Botanic Gardens',
    }
    return destinations.get(route_id, 'City')


def get_stop_name(stop_id):
    """Get stop name from stop ID - with comprehensive fallback."""
    if not stop_id:
        return 'Unknown'

    # Convert to string if needed
    stop_id = str(stop_id)

    # Try exact match
    if stop_id in STOP_ID_MAP:
        return STOP_ID_MAP[stop_id]

    # Try uppercase
    if stop_id.upper() in STOP_ID_MAP:
        return STOP_ID_MAP[stop_id.upper()]

    # Try without leading zeros
    stop_id_clean = stop_id.lstrip('0')
    if stop_id_clean in STOP_ID_MAP:
        return STOP_ID_MAP[stop_id_clean]

    # Try extracting numeric part
    numeric_match = re.search(r'\d+', stop_id)
    if numeric_match:
        numeric_id = numeric_match.group()
        if numeric_id in STOP_ID_MAP:
            return STOP_ID_MAP[numeric_id]
        if numeric_id.lstrip('0') in STOP_ID_MAP:
            return STOP_ID_MAP[numeric_id.lstrip('0')]

    # If it's a short ID, return as-is with formatting
    if len(stop_id) <= 4:
        return f'Stop {stop_id}'

    # For longer IDs, truncate
    return f'Stop {stop_id[:20]}'


# Cache for real-time data
_cached_vehicles = []
_last_fetch_time = None
_fetch_lock = threading.Lock()


def fetch_trip_updates():
    """Fetch trip updates to get next stop info using curl (IPv6 workaround)."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        result = subprocess.run(
            ['curl', '-s', '-4', '-o', tmp_path, '-m', '10', TRIP_UPDATES_URL],
            capture_output=True,
            timeout=15
        )

        if result.returncode != 0:
            return {}

        with open(tmp_path, 'rb') as f:
            data = f.read()
        os.unlink(tmp_path)

        if len(data) < 100:
            return {}

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)

        trip_updates = {}
        for entity in feed.entity:
            if not entity.HasField('trip_update'):
                continue

            tu = entity.trip_update
            trip_id = tu.trip.trip_id if tu.trip else None

            if trip_id and tu.stop_time_update:
                next_stu = tu.stop_time_update[0]
                trip_updates[trip_id] = {
                    'next_stop_id': next_stu.stop_id,
                    'arrival_time': next_stu.arrival.time if next_stu.HasField('arrival') else None
                }

        return trip_updates
    except Exception:
        return {}


def fetch_gtfs_vehicles():
    """Fetch real vehicle positions from Adelaide Metro GTFS-RT using curl (IPv6 workaround)."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        result = subprocess.run(
            ['curl', '-s', '-4', '-o', tmp_path, '-m', '15', VEHICLE_POSITIONS_URL],
            capture_output=True,
            timeout=20
        )

        if result.returncode != 0:
            print(f"[GTFS] curl failed: {result.stderr.decode()[:100]}")
            return None

        with open(tmp_path, 'rb') as f:
            data = f.read()
        os.unlink(tmp_path)

        if len(data) < 100:
            print("[GTFS] Empty response")
            return None

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)

        # Fetch trip updates for next stop info
        trip_updates = fetch_trip_updates()

        vehicles = []
        for entity in feed.entity:
            if not entity.HasField('vehicle'):
                continue

            v = entity.vehicle
            route_id = v.trip.route_id if v.trip else 'unknown'
            trip_id = v.trip.trip_id if v.trip else None

            vehicle_type = get_vehicle_type(route_id)
            route_name = get_route_name(route_id)

            if not v.position.HasField('latitude') or not v.position.HasField('longitude'):
                continue

            lat = v.position.latitude
            lon = v.position.longitude

            if not is_in_adelaide(lat, lon):
                continue

            # Get next stop info from trip updates
            next_stop = 'Unknown'
            arrival_minutes = 5
            if trip_id and trip_id in trip_updates:
                tu = trip_updates[trip_id]
                stop_id = tu.get('next_stop_id', '')
                next_stop = get_stop_name(stop_id)
                if tu.get('arrival_time'):
                    now = datetime.now(timezone.utc).timestamp()
                    arrival_minutes = max(1, int((tu['arrival_time'] - now) / 60))

            vehicle = {
                'id': entity.id,
                'route_id': route_id,
                'route_name': route_name,
                'type': vehicle_type,
                'lat': lat,
                'lon': lon,
                'bearing': v.position.bearing if v.position.HasField('bearing') else 0,
                'speed': round(v.position.speed * 3.6, 1) if v.position.HasField('speed') else 0,
                'timestamp': v.timestamp,
                'trip_id': trip_id,
                'updated_at': format_adelaide_time(get_adelaide_time()),
                'destination': get_route_destination(route_id),
                'next_stop': next_stop,
                'arrival_minutes': arrival_minutes,
                'status': 'on-time'
            }

            vehicles.append(vehicle)

        print(f"[GTFS] Fetched {len(vehicles)} vehicles")
        return vehicles

    except Exception as e:
        print(f"[GTFS] Fetch error: {e}")
        return None


def get_cached_vehicles(max_age_seconds=60):
    """Get cached vehicles if not too old - with on-demand refresh."""
    global _cached_vehicles, _last_fetch_time

    with _fetch_lock:
        # Check if cache is still valid
        if _last_fetch_time is not None:
            age = (get_adelaide_time() - _last_fetch_time).total_seconds()
            if age <= max_age_seconds:
                return _cached_vehicles

        # Cache expired or empty - fetch fresh data
        try:
            vehicles = fetch_gtfs_vehicles()
            if vehicles:
                _cached_vehicles = vehicles
                _last_fetch_time = get_adelaide_time()
                return vehicles
        except Exception as e:
            print(f"[GTFS] Fetch error: {e}")

        # Return stale data if we have it (even if expired)
        return _cached_vehicles if _cached_vehicles else None
