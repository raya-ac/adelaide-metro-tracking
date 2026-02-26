#!/usr/bin/env python3
"""
Shared utility functions for Adelaide Metro Tracker.
Eliminates duplicate code across modules.
"""

import math
import os
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Adelaide timezone
ADELAIDE_TZ = ZoneInfo('Australia/Adelaide')

# Adelaide metro area bounds - covers all of Greater Adelaide
ADELAIDE_BOUNDS = {
    'min_lat': -35.25,  # South to Aldinga/Seaford
    'max_lat': -34.55,  # North to Gawler
    'min_lon': 138.40,  # West to Outer Harbor/Glenelg
    'max_lon': 138.80   # East to Mount Barker/Hills
}


def get_adelaide_time():
    """Get current time in Adelaide timezone (handles DST automatically)."""
    return datetime.now(ADELAIDE_TZ)


def format_adelaide_time(dt):
    """Format datetime for Adelaide timezone with correct UTC offset."""
    adelaide_dt = dt.astimezone(ADELAIDE_TZ) if dt.tzinfo else dt.replace(tzinfo=ADELAIDE_TZ)
    offset = adelaide_dt.strftime('%z')
    # Format offset as +HH:MM
    formatted_offset = f"{offset[:3]}:{offset[3:]}"
    return adelaide_dt.strftime('%Y-%m-%dT%H:%M:%S') + formatted_offset


def is_in_adelaide(lat, lon):
    """Check if coordinates are within Adelaide metro area."""
    return (ADELAIDE_BOUNDS['min_lat'] <= lat <= ADELAIDE_BOUNDS['max_lat'] and
            ADELAIDE_BOUNDS['min_lon'] <= lon <= ADELAIDE_BOUNDS['max_lon'])


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing between two points in degrees."""
    d_lon = math.radians(lon2 - lon1)
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)

    x = math.sin(d_lon) * math.cos(lat2_r)
    y = (math.cos(lat1_r) * math.sin(lat2_r) -
         math.sin(lat1_r) * math.cos(lat2_r) * math.cos(d_lon))

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def load_stop_id_map():
    """Load the stop ID to name mapping from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), 'static', 'stop_id_map.json')
    with open(json_path, 'r') as f:
        return json.load(f)
