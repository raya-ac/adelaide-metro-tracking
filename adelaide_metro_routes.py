#!/usr/bin/env python3
"""
Adelaide Metro Tracker - Flask Blueprint
Comprehensive public transport tracking for Adelaide
"""

from flask import Blueprint, jsonify, request, render_template_string, current_app
import json
import os
import math
from datetime import datetime, timedelta

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

# Import GTFS manager
try:
    from adelaide_metro_gtfs import adelaide_metro
except ImportError:
    adelaide_metro = None

adelaide_metro_bp = Blueprint('adelaide_metro', __name__, url_prefix='/adelaide-metro')

# Route type mapping
ROUTE_TYPES = {
    0: 'tram',
    1: 'subway',
    2: 'train',
    3: 'bus',
    4: 'ferry',
    5: 'cable_car',
    6: 'gondola',
    7: 'funicular'
}

# Adelaide Metro specific route data with realistic waypoints
ADELAIDE_ROUTES = {
    'trains': [
        {
            'id': 'Belair',
            'name': 'Belair',
            'color': '#0072c6',
            'destinations': ['Belair', 'Adelaide'],
            'waypoints': [  # Approximate route from Adelaide to Belair
                (-34.9211, 138.5958), (-34.9300, 138.6000), (-34.9400, 138.6100),
                (-34.9500, 138.6200), (-34.9600, 138.6300), (-34.9700, 138.6400),
                (-34.9800, 138.6500), (-34.9900, 138.6600), (-35.0000, 138.6700),
                (-35.0100, 138.6800)
            ]
        },
        {
            'id': 'Gawler',
            'name': 'Gawler Central',
            'color': '#e31837',
            'destinations': ['Gawler Central', 'Adelaide'],
            'waypoints': [  # North from Adelaide
                (-34.9211, 138.5958), (-34.9000, 138.5950), (-34.8800, 138.5940),
                (-34.8600, 138.5930), (-34.8400, 138.5920), (-34.8200, 138.5910),
                (-34.8000, 138.5900), (-34.7800, 138.5890), (-34.7600, 138.5880),
                (-34.7400, 138.5870)
            ]
        },
        {
            'id': 'Seaford',
            'name': 'Seaford',
            'color': '#f7931d',
            'destinations': ['Seaford', 'Adelaide'],
            'waypoints': [  # South from Adelaide
                (-34.9211, 138.5958), (-34.9400, 138.5900), (-34.9600, 138.5850),
                (-34.9800, 138.5800), (-35.0000, 138.5750), (-35.0200, 138.5700),
                (-35.0400, 138.5650), (-35.0600, 138.5600), (-35.0800, 138.5550),
                (-35.1000, 138.5500)
            ]
        },
        {
            'id': 'Flinders',
            'name': 'Flinders',
            'color': '#00a651',
            'destinations': ['Flinders', 'Adelaide'],
            'waypoints': [  # South-east to Flinders
                (-34.9211, 138.5958), (-34.9400, 138.6100), (-34.9600, 138.6200),
                (-34.9800, 138.6300), (-35.0000, 138.6400), (-35.0200, 138.6500)
            ]
        },
        {
            'id': 'Outer Harbor',
            'name': 'Outer Harbor',
            'color': '#8c6cae',
            'destinations': ['Outer Harbor', 'Adelaide'],
            'waypoints': [  # North-west
                (-34.9211, 138.5958), (-34.9000, 138.5800), (-34.8800, 138.5600),
                (-34.8600, 138.5400), (-34.8400, 138.5200), (-34.8200, 138.5000)
            ]
        },
        {
            'id': 'Grange',
            'name': 'Grange',
            'color': '#9c6cae',
            'destinations': ['Grange', 'Adelaide'],
            'waypoints': [  # West
                (-34.9211, 138.5958), (-34.9200, 138.5700), (-34.9190, 138.5500),
                (-34.9180, 138.5300), (-34.9170, 138.5100)
            ]
        },
    ],
    'trams': [
        {
            'id': 'Glenelg',
            'name': 'Glenelg Tram',
            'color': '#e31837',
            'destinations': ['Glenelg', 'Entertainment Centre'],
            'waypoints': [  # West to Glenelg
                (-34.9060, 138.5880), (-34.9200, 138.5700), (-34.9400, 138.5500),
                (-34.9600, 138.5300), (-34.9807, 138.5120)
            ]
        },
        {
            'id': 'Botanic',
            'name': 'Botanic Tram',
            'color': '#0072c6',
            'destinations': ['Botanic Gardens', 'Festival Plaza'],
            'waypoints': [  # Short route in city
                (-34.9060, 138.5880), (-34.9150, 138.5950), (-34.9200, 138.6000),
                (-34.9250, 138.6050), (-34.9300, 138.6100)
            ]
        }
    ],
    'buses': [
        # North East - O-Bahn corridor
        {
            'id': 'G40',
            'name': 'G40',
            'color': '#0072c6',
            'destinations': ['Golden Grove', 'City'],
            'waypoints': [(-34.7900, 138.7000), (-34.8100, 138.6900), (-34.8300, 138.6800), (-34.8500, 138.6700), (-34.8700, 138.6500), (-34.8900, 138.6200), (-34.9211, 138.5958)]
        },
        {
            'id': 'H20',
            'name': 'H20',
            'color': '#e31837',
            'destinations': ['Paradise', 'City'],
            'waypoints': [(-34.8700, 138.6800), (-34.8750, 138.6650), (-34.8850, 138.6450), (-34.9000, 138.6200), (-34.9100, 138.6050), (-34.9211, 138.5958)]
        },
        {
            'id': 'H30',
            'name': 'H30',
            'color': '#f7931d',
            'destinations': ['Tea Tree Plaza', 'City'],
            'waypoints': [(-34.8336, 138.6919), (-34.8450, 138.6850), (-34.8600, 138.6700), (-34.8750, 138.6500), (-34.8900, 138.6300), (-34.9050, 138.6100), (-34.9211, 138.5958)]
        },
        {
            'id': 'C1',
            'name': 'C1',
            'color': '#00a651',
            'destinations': ['Tea Tree Plaza', 'City'],
            'waypoints': [(-34.8336, 138.6919), (-34.8400, 138.6800), (-34.8550, 138.6600), (-34.8750, 138.6350), (-34.9000, 138.6100), (-34.9211, 138.5958)]
        },
        {
            'id': 'C2',
            'name': 'C2',
            'color': '#8c6cae',
            'destinations': ['Paradise', 'City'],
            'waypoints': [(-34.8700, 138.6800), (-34.8600, 138.6650), (-34.8800, 138.6400), (-34.9000, 138.6150), (-34.9211, 138.5958)]
        },
        # North West
        {
            'id': 'J1',
            'name': 'J1',
            'color': '#0072c6',
            'destinations': ['West Lakes', 'City'],
            'waypoints': [(-34.8800, 138.5000), (-34.8850, 138.5150), (-34.8900, 138.5350), (-34.8950, 138.5550), (-34.9050, 138.5750), (-34.9211, 138.5958)]
        },
        {
            'id': 'J2',
            'name': 'J2',
            'color': '#e31837',
            'destinations': ['West Lakes', 'City'],
            'waypoints': [(-34.8800, 138.5000), (-34.8900, 138.5250), (-34.9050, 138.5500), (-34.9150, 138.5750), (-34.9211, 138.5958)]
        },
        {
            'id': 'W90',
            'name': 'W90',
            'color': '#f7931d',
            'destinations': ['Westfield West Lakes', 'City'],
            'waypoints': [(-34.8850, 138.4950), (-34.8900, 138.5200), (-34.9000, 138.5450), (-34.9100, 138.5700), (-34.9211, 138.5958)]
        },
        {
            'id': '150',
            'name': '150',
            'color': '#00a651',
            'destinations': ['West Lakes', 'City'],
            'waypoints': [(-34.8800, 138.5000), (-34.8900, 138.5300), (-34.9000, 138.5600), (-34.9100, 138.5800), (-34.9211, 138.5958)]
        },
        {
            'id': '117',
            'name': '117',
            'color': '#8c6cae',
            'destinations': ['West Lakes', 'City'],
            'waypoints': [(-34.8750, 138.5050), (-34.8850, 138.5350), (-34.8950, 138.5650), (-34.9100, 138.5850), (-34.9211, 138.5958)]
        },
        # South
        {
            'id': 'M44',
            'name': 'M44',
            'color': '#0072c6',
            'destinations': ['Marion', 'City'],
            'waypoints': [(-35.0169, 138.5542), (-35.0000, 138.5580), (-34.9800, 138.5620), (-34.9600, 138.5700), (-34.9400, 138.5800), (-34.9211, 138.5958)]
        },
        {
            'id': '300',
            'name': '300',
            'color': '#e31837',
            'destinations': ['Marion', 'City'],
            'waypoints': [(-35.0200, 138.5500), (-35.0000, 138.5550), (-34.9750, 138.5650), (-34.9500, 138.5750), (-34.9211, 138.5958)]
        },
        {
            'id': 'Noarlunga',
            'name': 'Noarlunga Line',
            'color': '#f7931d',
            'destinations': ['Noarlunga', 'City'],
            'waypoints': [(-35.1380, 138.4970), (-35.1000, 138.5200), (-35.0500, 138.5500), (-34.9900, 138.5700), (-34.9500, 138.5850), (-34.9211, 138.5958)]
        },
        {
            'id': 'G20',
            'name': 'G20',
            'color': '#00a651',
            'destinations': ['Colonnades', 'City'],
            'waypoints': [(-35.1200, 138.5000), (-35.0800, 138.5200), (-35.0200, 138.5500), (-34.9700, 138.5750), (-34.9211, 138.5958)]
        },
        # Hills
        {
            'id': 'T721',
            'name': '721',
            'color': '#0072c6',
            'destinations': ['Mount Barker', 'City'],
            'waypoints': [(-35.0600, 138.8500), (-35.0400, 138.8000), (-35.0200, 138.7500), (-35.0000, 138.7000), (-34.9800, 138.6500), (-34.9500, 138.6200), (-34.9211, 138.5958)]
        },
        {
            'id': 'T722',
            'name': '722',
            'color': '#e31837',
            'destinations': ['Aldgate', 'City'],
            'waypoints': [(-35.0200, 138.7500), (-35.0000, 138.7000), (-34.9800, 138.6500), (-34.9500, 138.6200), (-34.9211, 138.5958)]
        },
        {
            'id': 'T723',
            'name': '723',
            'color': '#f7931d',
            'destinations': ['Stirling', 'City'],
            'waypoints': [(-35.0100, 138.7200), (-34.9900, 138.6800), (-34.9700, 138.6400), (-34.9500, 138.6100), (-34.9211, 138.5958)]
        },
        {
            'id': 'T864',
            'name': '864',
            'color': '#00a651',
            'destinations': ['Crafers', 'City'],
            'waypoints': [(-34.9900, 138.7000), (-34.9700, 138.6600), (-34.9500, 138.6200), (-34.9400, 138.6000), (-34.9211, 138.5958)]
        },
        {
            'id': '835',
            'name': '835',
            'color': '#8c6cae',
            'destinations': ['Lobethal', 'City'],
            'waypoints': [(-34.9500, 138.8800), (-34.9600, 138.8400), (-34.9700, 138.7800), (-34.9800, 138.7000), (-34.9500, 138.6200), (-34.9211, 138.5958)]
        },
        # Inner suburbs
        {
            'id': '190',
            'name': '190',
            'color': '#0072c6',
            'destinations': ['Glenelg', 'City'],
            'waypoints': [(-34.9800, 138.5200), (-34.9700, 138.5400), (-34.9600, 138.5600), (-34.9500, 138.5750), (-34.9400, 138.5850), (-34.9211, 138.5958)]
        },
        {
            'id': '263',
            'name': '263',
            'destinations': ['Henley Beach', 'City'],
            'waypoints': [(-34.9200, 138.4900), (-34.9150, 138.5100), (-34.9100, 138.5350), (-34.9150, 138.5600), (-34.9211, 138.5958)]
        },
        {
            'id': 'H30N',
            'name': 'H30N',
            'destinations': ['Northgate', 'City'],
            'waypoints': [(-34.8500, 138.6400), (-34.8600, 138.6250), (-34.8750, 138.6100), (-34.8900, 138.6000), (-34.9211, 138.5958)]
        },
        {
            'id': '271',
            'name': '271',
            'destinations': ['Unley', 'City'],
            'waypoints': [(-34.9500, 138.6100), (-34.9450, 138.6050), (-34.9350, 138.6000), (-34.9211, 138.5958)]
        },
        {
            'id': 'T723',
            'name': '723',
            'color': '#f7931d',
            'destinations': ['Stirling', 'City'],
            'waypoints': [(-35.0100, 138.7200), (-34.9900, 138.6800), (-34.9700, 138.6400), (-34.9500, 138.6100), (-34.9211, 138.5958)]
        },
        {
            'id': 'T864',
            'name': '864',
            'color': '#00a651',
            'destinations': ['Crafers', 'City'],
            'waypoints': [(-34.9900, 138.7000), (-34.9700, 138.6600), (-34.9500, 138.6200), (-34.9400, 138.6000), (-34.9211, 138.5958)]
        },
    ]
}

# Comprehensive stops for each route - used for next-stop calculation
ROUTE_STOPS = {
    # Belair Line stops (from city to Belair)
    'Belair': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Mile End', 'lat': -34.925, 'lon': 138.58},
        {'name': 'Adelaide Showground', 'lat': -34.945, 'lon': 138.585},
        {'name': 'Goodwood', 'lat': -34.952, 'lon': 138.588},
        {'name': 'Clarence Park', 'lat': -34.965, 'lon': 138.595},
        {'name': 'Emerson', 'lat': -34.97, 'lon': 138.60},
        {'name': 'Unley', 'lat': -34.955, 'lon': 138.60},
        {'name': 'Mitcham', 'lat': -34.965, 'lon': 138.61},
        {'name': 'Torrens Park', 'lat': -34.97, 'lon': 138.61},
        {'name': 'Lynton', 'lat': -34.975, 'lon': 138.615},
        {'name': 'Eden Hills', 'lat': -35.00, 'lon': 138.62},
        {'name': 'Blackwood', 'lat': -35.02, 'lon': 138.62},
        {'name': 'Glenalta', 'lat': -35.025, 'lon': 138.625},
        {'name': 'Pinera', 'lat': -35.03, 'lon': 138.63},
        {'name': 'Belair', 'lat': -35.01, 'lon': 138.65},
    ],
    # Gawler Line stops (from city to Gawler)
    'Gawler': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Mawson Lakes', 'lat': -34.82, 'lon': 138.61},
        {'name': 'Green Fields', 'lat': -34.8, 'lon': 138.62},
        {'name': 'Parafield', 'lat': -34.79, 'lon': 138.63},
        {'name': 'Parafield Gardens', 'lat': -34.78, 'lon': 138.64},
        {'name': 'Salisbury', 'lat': -34.76, 'lon': 138.65},
        {'name': 'Elizabeth', 'lat': -34.72, 'lon': 138.67},
        {'name': 'Gawler Central', 'lat': -34.595, 'lon': 138.745},
    ],
    # Seaford Line stops (from city to Seaford)
    'Seaford': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Mile End', 'lat': -34.925, 'lon': 138.58},
        {'name': 'Adelaide Showground', 'lat': -34.945, 'lon': 138.585},
        {'name': 'Goodwood', 'lat': -34.952, 'lon': 138.588},
        {'name': 'Clarence Park', 'lat': -34.965, 'lon': 138.595},
        {'name': 'Emerson', 'lat': -34.97, 'lon': 138.60},
        {'name': 'Unley', 'lat': -34.955, 'lon': 138.60},
        {'name': 'Mitcham', 'lat': -34.965, 'lon': 138.61},
        {'name': 'Torrens Park', 'lat': -34.97, 'lon': 138.61},
        {'name': 'Marino', 'lat': -35.05, 'lon': 138.52},
        {'name': 'Hallett Cove', 'lat': -35.08, 'lon': 138.51},
        {'name': 'Noarlunga Centre', 'lat': -35.14, 'lon': 138.49},
        {'name': 'Seaford', 'lat': -35.19, 'lon': 138.47},
    ],
    # Flinders Line stops
    'Flinders': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Mile End', 'lat': -34.925, 'lon': 138.58},
        {'name': 'Mitchell Park', 'lat': -35.01, 'lon': 138.565},
        {'name': 'Tonsley', 'lat': -35.02, 'lon': 138.57},
        {'name': 'Flinders', 'lat': -35.02, 'lon': 138.57},
    ],
    # Outer Harbor Line stops
    'Outer Harbor': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Port Adelaide', 'lat': -34.845, 'lon': 138.505},
        {'name': 'Glanville', 'lat': -34.855, 'lon': 138.495},
        {'name': 'Ethelton', 'lat': -34.865, 'lon': 138.485},
        {'name': 'Largs', 'lat': -34.875, 'lon': 138.475},
        {'name': 'Outer Harbor', 'lat': -34.885, 'lon': 138.465},
    ],
    # Grange Line stops
    'Grange': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Cheltenham', 'lat': -34.87, 'lon': 138.525},
        {'name': 'Albert Park', 'lat': -34.865, 'lon': 138.51},
        {'name': 'Seaton Park', 'lat': -34.91, 'lon': 138.52},
        {'name': 'West Lakes', 'lat': -34.87, 'lon': 138.49},
        {'name': 'Grange', 'lat': -34.905, 'lon': 138.49},
    ],
    # Glenelg Tram stops
    'Glenelg': [
        {'name': 'Entertainment Centre', 'lat': -34.906, 'lon': 138.588},
        {'name': 'City West', 'lat': -34.9225, 'lon': 138.585},
        {'name': 'Victoria Square', 'lat': -34.9285, 'lon': 138.598},
        {'name': 'King William Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605},
        {'name': 'Rundle Mall', 'lat': -34.9218, 'lon': 138.6009},
        {'name': 'South Terrace', 'lat': -34.935, 'lon': 138.595},
        {'name': 'Greenhill Road', 'lat': -34.94, 'lon': 138.59},
        {'name': 'Keswick', 'lat': -34.945, 'lon': 138.585},
        {'name': 'Glengowrie', 'lat': -34.965, 'lon': 138.53},
        {'name': 'Morphettville', 'lat': -34.975, 'lon': 138.52},
        {'name': 'Glenelg', 'lat': -34.9807, 'lon': 138.512},
    ],
    # Botanic Tram stops
    'Botanic': [
        {'name': 'Festival Plaza', 'lat': -34.906, 'lon': 138.588},
        {'name': 'Victoria Square', 'lat': -34.9285, 'lon': 138.598},
        {'name': 'King William Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605},
        {'name': 'Art Gallery', 'lat': -34.92, 'lon': 138.605},
        {'name': 'Botanic Gardens', 'lat': -34.92, 'lon': 138.61},
    ],
}

# Bus route-specific stops for accurate next-stop names
BUS_ROUTE_STOPS = {
    # O-Bahn buses - North East
    'G40': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Klemzig', 'lat': -34.895, 'lon': 138.635},
        {'name': 'Paradise Interchange', 'lat': -34.87, 'lon': 138.67},
        {'name': 'Modbury Interchange', 'lat': -34.83, 'lon': 138.68},
        {'name': 'Tea Tree Plaza', 'lat': -34.8336, 'lon': 138.6919},
        {'name': 'Golden Grove', 'lat': -34.79, 'lon': 138.70},
    ],
    'H20': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
        {'name': 'Klemzig', 'lat': -34.895, 'lon': 138.635},
        {'name': 'Paradise Interchange', 'lat': -34.87, 'lon': 138.67},
    ],
    'H30': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
        {'name': 'Klemzig', 'lat': -34.895, 'lon': 138.635},
        {'name': 'Paradise Interchange', 'lat': -34.87, 'lon': 138.67},
        {'name': 'Tea Tree Plaza', 'lat': -34.8336, 'lon': 138.6919},
    ],
    'C1': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605},
        {'name': 'Klemzig', 'lat': -34.895, 'lon': 138.635},
        {'name': 'Tea Tree Plaza', 'lat': -34.8336, 'lon': 138.6919},
    ],
    'C2': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Klemzig', 'lat': -34.895, 'lon': 138.635},
        {'name': 'Paradise Interchange', 'lat': -34.87, 'lon': 138.67},
    ],
    # West Lakes buses
    'J1': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
        {'name': 'Kilkenny', 'lat': -34.88, 'lon': 138.54},
        {'name': 'West Lakes', 'lat': -34.87, 'lon': 138.49},
        {'name': 'Westfield West Lakes', 'lat': -34.885, 'lon': 138.495},
    ],
    'J2': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Woodville', 'lat': -34.875, 'lon': 138.535},
        {'name': 'West Lakes', 'lat': -34.87, 'lon': 138.49},
    ],
    'W90': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'King William Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Arndale Shopping Centre', 'lat': -34.8808, 'lon': 138.5567},
        {'name': 'Westfield West Lakes', 'lat': -34.885, 'lon': 138.495},
    ],
    '150': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
        {'name': 'Woodville', 'lat': -34.875, 'lon': 138.535},
        {'name': 'West Lakes', 'lat': -34.87, 'lon': 138.49},
    ],
    '117': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grote Street', 'lat': -34.93, 'lon': 138.585},
        {'name': 'Findon', 'lat': -34.9, 'lon': 138.53},
        {'name': 'West Lakes', 'lat': -34.87, 'lon': 138.49},
    ],
    # Marion/South buses
    'M44': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605},
        {'name': 'Edwardstown', 'lat': -34.96, 'lon': 138.57},
        {'name': 'Marion Shopping Centre', 'lat': -35.0169, 'lon': 138.5542},
    ],
    '300': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Clovelly Park', 'lat': -34.98, 'lon': 138.56},
        {'name': 'Marion Shopping Centre', 'lat': -35.0169, 'lon': 138.5542},
    ],
    'Noarlunga': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
        {'name': 'Reynella', 'lat': -35.09, 'lon': 138.52},
        {'name': 'Noarlunga Centre', 'lat': -35.138, 'lon': 138.497},
    ],
    'G20': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Wakefield Street', 'lat': -34.93, 'lon': 138.595},
        {'name': 'Christie Downs', 'lat': -35.13, 'lon': 138.50},
        {'name': 'Colonnades', 'lat': -35.12, 'lon': 138.50},
    ],
    # Hills buses
    'T721': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Crafers', 'lat': -34.99, 'lon': 138.70},
        {'name': 'Mount Barker', 'lat': -35.06, 'lon': 138.85},
    ],
    'T722': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
        {'name': 'Stirling', 'lat': -35.01, 'lon': 138.72},
        {'name': 'Aldgate', 'lat': -35.02, 'lon': 138.75},
    ],
    'T723': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605},
        {'name': 'Stirling', 'lat': -35.01, 'lon': 138.72},
    ],
    'T864': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'King William Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Crafers', 'lat': -34.99, 'lon': 138.70},
    ],
    '835': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grote Street', 'lat': -34.93, 'lon': 138.585},
        {'name': 'Lobethal', 'lat': -34.95, 'lon': 138.88},
    ],
    # Glenelg buses
    '190': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6},
        {'name': 'Glenelg South', 'lat': -34.98, 'lon': 138.51},
        {'name': 'Glenelg', 'lat': -34.9807, 'lon': 138.512},
    ],
    '263': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
        {'name': 'Henley Beach', 'lat': -34.92, 'lon': 138.49},
    ],
    # Inner suburbs
    'H30N': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Prospect', 'lat': -34.885, 'lon': 138.595},
        {'name': 'Northgate', 'lat': -34.85, 'lon': 138.64},
    ],
    '271': [
        {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
        {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605},
        {'name': 'Unley', 'lat': -34.95, 'lon': 138.61},
    ],
}

# Bus stops mapping
BUS_STOPS = [
    {'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958},
    {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59},
    {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6},
    {'name': 'Grote Street', 'lat': -34.93, 'lon': 138.585},
    {'name': 'King William Street', 'lat': -34.925, 'lon': 138.6},
    {'name': 'Morphett Street', 'lat': -34.925, 'lon': 138.58},
    {'name': 'North Terrace', 'lat': -34.915, 'lon': 138.595},
    {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605},
    {'name': 'Rundle Mall', 'lat': -34.9218, 'lon': 138.6009},
    {'name': 'South Terrace', 'lat': -34.935, 'lon': 138.595},
    {'name': 'Victoria Square', 'lat': -34.9285, 'lon': 138.598},
    {'name': 'Wakefield Street', 'lat': -34.93, 'lon': 138.595},
    {'name': 'Tea Tree Plaza', 'lat': -34.8336, 'lon': 138.6919},
    {'name': 'Marion Shopping Centre', 'lat': -35.0169, 'lon': 138.5542},
    {'name': 'Arndale Shopping Centre', 'lat': -34.8808, 'lon': 138.5567},
    {'name': 'Golden Grove', 'lat': -34.79, 'lon': 138.70},
    {'name': 'Paradise Interchange', 'lat': -34.87, 'lon': 138.67},
    {'name': 'Modbury Interchange', 'lat': -34.83, 'lon': 138.68},
    {'name': 'West Lakes', 'lat': -34.87, 'lon': 138.49},
    {'name': 'Henley Beach', 'lat': -34.92, 'lon': 138.49},
    {'name': 'Glenelg South', 'lat': -34.98, 'lon': 138.51},
    {'name': 'Unley', 'lat': -34.95, 'lon': 138.61},
    {'name': 'Mount Barker', 'lat': -35.06, 'lon': 138.85},
    {'name': 'Stirling', 'lat': -35.01, 'lon': 138.72},
    {'name': 'Crafers', 'lat': -34.99, 'lon': 138.70},
    {'name': 'Aldgate', 'lat': -35.02, 'lon': 138.75},
    {'name': 'Lobethal', 'lat': -34.95, 'lon': 138.88},
    {'name': 'Colonnades', 'lat': -35.12, 'lon': 138.50},
    {'name': 'Noarlunga', 'lat': -35.138, 'lon': 138.497},
    {'name': 'Brompton', 'lat': -34.895, 'lon': 138.58},
    {'name': 'Croydon', 'lat': -34.895, 'lon': 138.555},
    {'name': 'Fitzroy', 'lat': -34.885, 'lon': 138.595},
    {'name': 'Northgate', 'lat': -34.85, 'lon': 138.64},
    {'name': 'Prospect', 'lat': -34.885, 'lon': 138.595},
    {'name': 'Klemzig', 'lat': -34.895, 'lon': 138.635},
    {'name': 'Kilburn', 'lat': -34.86, 'lon': 138.59},
    {'name': 'Woodville', 'lat': -34.875, 'lon': 138.535},
]

# Legacy MAJOR_STOPS for backward compatibility
MAJOR_STOPS = [
    {'id': 'Adelaide', 'name': 'Adelaide Railway Station', 'lat': -34.9211, 'lon': 138.5958, 'type': 'train'},
    {'id': 'Entertainment Centre', 'name': 'Entertainment Centre', 'lat': -34.906, 'lon': 138.588, 'type': 'tram'},
    {'id': 'Glenelg', 'name': 'Glenelg Tram Stop', 'lat': -34.9807, 'lon': 138.512, 'type': 'tram'},
    {'id': 'Tea Tree Plaza', 'name': 'Tea Tree Plaza Interchange', 'lat': -34.8336, 'lon': 138.6919, 'type': 'bus'},
    {'id': 'Marion', 'name': 'Marion Shopping Centre', 'lat': -35.0169, 'lon': 138.5542, 'type': 'bus'},
    {'id': 'Arndale', 'name': 'Arndale Shopping Centre', 'lat': -34.8808, 'lon': 138.5567, 'type': 'bus'},
]

@adelaide_metro_bp.route('/')
def index():
    """Main Adelaide Metro tracker page"""
    return send_from_directory('/opt/raya-monitor/templates/adelaide-metro', 'index.html')

@adelaide_metro_bp.route('/qrcode.js')
def serve_qrcode_js():
    """Serve QR code library"""
    return send_from_directory('/opt/raya-monitor/templates/adelaide-metro', 'qrcode.js')

@adelaide_metro_bp.route('/sw.js')
def serve_sw_js():
    """Serve Service Worker"""
    return send_from_directory('/opt/raya-monitor/templates/adelaide-metro', 'sw.js')

@adelaide_metro_bp.route('/api/routes')
def get_routes():
    """Get all routes"""
    route_type = request.args.get('type')
    
    if route_type and route_type in ['train', 'tram', 'bus']:
        routes = ADELAIDE_ROUTES.get(route_type + 's', [])
    else:
        routes = []
        for rtype in ['trains', 'trams', 'buses']:
            for route in ADELAIDE_ROUTES.get(rtype, []):
                route_copy = route.copy()
                if rtype == 'buses':
                    route_copy['type'] = 'bus'
                else:
                    route_copy['type'] = rtype[:-1]  # Remove 's' (trains->train, trams->tram)
                routes.append(route_copy)
    
    return jsonify({
        'routes': routes,
        'count': len(routes),
        'updated_at': datetime.now().isoformat()
    })

# Import GTFS realtime fetcher
try:
    from adelaide_metro_gtfs_realtime import fetch_realtime_vehicles, get_cached_vehicles
    GTFS_AVAILABLE = True
except ImportError:
    GTFS_AVAILABLE = False

# Adelaide stops data (moved here to avoid import issues)
ADELAIDE_STOPS = {
    'b_belair': {'name': 'Belair', 'lat': -35.01, 'lon': 138.65, 'type': 'train'},
    'b_blackwood': {'name': 'Blackwood', 'lat': -35.02, 'lon': 138.62, 'type': 'train'},
    'b_clapham': {'name': 'Clapham', 'lat': -34.965, 'lon': 138.605, 'type': 'train'},
    'b_eden_hills': {'name': 'Eden Hills', 'lat': -35.0, 'lon': 138.62, 'type': 'train'},
    'b_glenalta': {'name': 'Glenalta', 'lat': -35.025, 'lon': 138.625, 'type': 'train'},
    'b_goodwood': {'name': 'Goodwood', 'lat': -34.952, 'lon': 138.588, 'type': 'train'},
    'b_lynton': {'name': 'Lynton', 'lat': -34.975, 'lon': 138.615, 'type': 'train'},
    'b_mile_end': {'name': 'Mile End', 'lat': -34.925, 'lon': 138.58, 'type': 'train'},
    'b_mitcham': {'name': 'Mitcham', 'lat': -34.965, 'lon': 138.605, 'type': 'train'},
    'b_pinera': {'name': 'Pinera', 'lat': -35.03, 'lon': 138.63, 'type': 'train'},
    'b_showground': {'name': 'Adelaide Showground', 'lat': -34.945, 'lon': 138.585, 'type': 'train'},
    'b_tornsdale': {'name': 'Torrens Park', 'lat': -34.97, 'lon': 138.61, 'type': 'train'},
    'b_unley': {'name': 'Unley', 'lat': -34.955, 'lon': 138.6, 'type': 'train'},
    'c_adelaide_station': {'name': 'Adelaide Railway Station', 'lat': -34.921115, 'lon': 138.595834, 'type': 'train'},
    'c_city_west': {'name': 'City West', 'lat': -34.9225, 'lon': 138.585, 'type': 'train'},
    'c_currie_st': {'name': 'Currie Street', 'lat': -34.925, 'lon': 138.59, 'type': 'bus'},
    'c_ent_centre': {'name': 'Entertainment Centre', 'lat': -34.906, 'lon': 138.588, 'type': 'tram'},
    'c_grenfell_st': {'name': 'Grenfell Street', 'lat': -34.925, 'lon': 138.6, 'type': 'bus'},
    'c_grote_st': {'name': 'Grote Street', 'lat': -34.93, 'lon': 138.585, 'type': 'bus'},
    'c_king_william_st': {'name': 'King William Street', 'lat': -34.925, 'lon': 138.6, 'type': 'bus'},
    'c_morphett_st': {'name': 'Morphett Street', 'lat': -34.925, 'lon': 138.58, 'type': 'bus'},
    'c_north_terrace': {'name': 'North Terrace', 'lat': -34.915, 'lon': 138.595, 'type': 'tram'},
    'c_pulteney_st': {'name': 'Pulteney Street', 'lat': -34.92, 'lon': 138.605, 'type': 'bus'},
    'c_rundle_mall': {'name': 'Rundle Mall', 'lat': -34.9218, 'lon': 138.6009, 'type': 'tram'},
    'c_south_terrace': {'name': 'South Terrace', 'lat': -34.935, 'lon': 138.595, 'type': 'tram'},
    'c_victoria_sq': {'name': 'Victoria Square', 'lat': -34.9285, 'lon': 138.598, 'type': 'tram'},
    'c_wakefield_st': {'name': 'Wakefield Street', 'lat': -34.93, 'lon': 138.595, 'type': 'bus'},
    'hi_aldgate': {'name': 'Aldgate', 'lat': -35.02, 'lon': 138.75, 'type': 'bus'},
    'hi_crafers': {'name': 'Crafers', 'lat': -34.99, 'lon': 138.7, 'type': 'bus'},
    'hi_heathfield': {'name': 'Heathfield', 'lat': -35.04, 'lon': 138.76, 'type': 'bus'},
    'hi_mount_barker': {'name': 'Mount Barker ParknRide', 'lat': -35.06, 'lon': 138.85, 'type': 'bus'},
    'hi_stirling': {'name': 'Stirling ParknRide', 'lat': -35.01, 'lon': 138.72, 'type': 'bus'},
    'hi_verdun': {'name': 'Verdun', 'lat': -35.0, 'lon': 138.73, 'type': 'bus'},
    'in_brompton': {'name': 'Brompton', 'lat': -34.895, 'lon': 138.58, 'type': 'bus'},
    'in_croydon': {'name': 'Croydon', 'lat': -34.895, 'lon': 138.555, 'type': 'bus'},
    'in_fitzroy': {'name': 'Fitzroy', 'lat': -34.885, 'lon': 138.595, 'type': 'bus'},
    'in_hindmarsh': {'name': 'Hindmarsh', 'lat': -34.905, 'lon': 138.57, 'type': 'bus'},
    'in_nailsworth': {'name': 'Nailsworth', 'lat': -34.875, 'lon': 138.595, 'type': 'bus'},
    'in_ovingham': {'name': 'Ovingham', 'lat': -34.9, 'lon': 138.595, 'type': 'bus'},
    'in_prospect_rd': {'name': 'Prospect Road', 'lat': -34.88, 'lon': 138.6, 'type': 'bus'},
    'in_ridleyton': {'name': 'Ridleyton', 'lat': -34.89, 'lon': 138.56, 'type': 'bus'},
    'is_frewville': {'name': 'Frewville', 'lat': -34.94, 'lon': 138.62, 'type': 'bus'},
    'is_fullarton': {'name': 'Fullarton', 'lat': -34.945, 'lon': 138.625, 'type': 'bus'},
    'is_glenside': {'name': 'Glenside', 'lat': -34.945, 'lon': 138.635, 'type': 'bus'},
    'is_malvern': {'name': 'Malvern', 'lat': -34.955, 'lon': 138.62, 'type': 'bus'},
    'is_norwood': {'name': 'The Parade Norwood', 'lat': -34.92, 'lon': 138.63, 'type': 'bus'},
    'is_parkside': {'name': 'Parkside', 'lat': -34.94, 'lon': 138.615, 'type': 'bus'},
    'is_toorak_gardens': {'name': 'Toorak Gardens', 'lat': -34.935, 'lon': 138.63, 'type': 'bus'},
    'is_unley_shopping': {'name': 'Unley Shopping Centre', 'lat': -34.95, 'lon': 138.61, 'type': 'bus'},
    'iw_black_forest': {'name': 'Black Forest', 'lat': -34.94, 'lon': 138.57, 'type': 'bus'},
    'iw_goodwood_rd': {'name': 'Goodwood Road', 'lat': -34.955, 'lon': 138.595, 'type': 'bus'},
    'iw_keswick': {'name': 'Keswick', 'lat': -34.935, 'lon': 138.555, 'type': 'tram'},
    'iw_kurralta_park': {'name': 'Kurralta Park', 'lat': -34.945, 'lon': 138.565, 'type': 'bus'},
    'iw_mile_end_south': {'name': 'Mile End South', 'lat': -34.93, 'lon': 138.575, 'type': 'bus'},
    'iw_wayville': {'name': 'Wayville', 'lat': -34.945, 'lon': 138.59, 'type': 'bus'},
    'n_blair_athol': {'name': 'Blair Athol', 'lat': -34.855, 'lon': 138.595, 'type': 'train'},
    'n_bowden': {'name': 'Bowden', 'lat': -34.895, 'lon': 138.59, 'type': 'train'},
    'n_broadmeadows': {'name': 'Broadmeadows', 'lat': -34.62, 'lon': 138.695, 'type': 'train'},
    'n_cavan': {'name': 'Cavan', 'lat': -34.825, 'lon': 138.6, 'type': 'train'},
    'n_dry_creek': {'name': 'Dry Creek', 'lat': -34.84, 'lon': 138.59, 'type': 'train'},
    'n_dudley_park': {'name': 'Dudley Park', 'lat': -34.875, 'lon': 138.585, 'type': 'train'},
    'n_elizabeth': {'name': 'Elizabeth Interchange', 'lat': -34.72, 'lon': 138.67, 'type': 'train'},
    'n_elizabeth_south': {'name': 'Elizabeth South', 'lat': -34.735, 'lon': 138.665, 'type': 'train'},
    'n_gawler': {'name': 'Gawler Central', 'lat': -34.596, 'lon': 138.747, 'type': 'train'},
    'n_kilburn': {'name': 'Kilburn', 'lat': -34.86, 'lon': 138.58, 'type': 'train'},
    'n_kudla': {'name': 'Kudla', 'lat': -34.68, 'lon': 138.68, 'type': 'train'},
    'n_munno_para': {'name': 'Munno Para', 'lat': -34.66, 'lon': 138.685, 'type': 'train'},
    'n_ovingham': {'name': 'Ovingham', 'lat': -34.9, 'lon': 138.595, 'type': 'train'},
    'n_parafield': {'name': 'Parafield', 'lat': -34.79, 'lon': 138.635, 'type': 'train'},
    'n_parafield_gardens': {'name': 'Parafield Gardens', 'lat': -34.785, 'lon': 138.64, 'type': 'train'},
    'n_pooraka': {'name': 'Pooraka', 'lat': -34.815, 'lon': 138.61, 'type': 'train'},
    'n_prospect': {'name': 'Prospect', 'lat': -34.85, 'lon': 138.6, 'type': 'train'},
    'n_salisbury': {'name': 'Salisbury Interchange', 'lat': -34.76, 'lon': 138.64, 'type': 'train'},
    'n_salisbury_north': {'name': 'Salisbury North', 'lat': -34.75, 'lon': 138.645, 'type': 'train'},
    'n_smithfield': {'name': 'Smithfield', 'lat': -34.64, 'lon': 138.69, 'type': 'train'},
    'n_womma': {'name': 'Womma', 'lat': -34.7, 'lon': 138.675, 'type': 'train'},
    'ne_dernancourt': {'name': 'Dernancourt', 'lat': -34.86, 'lon': 138.67, 'type': 'bus'},
    'ne_gilles_plains': {'name': 'Gilles Plains', 'lat': -34.84, 'lon': 138.66, 'type': 'bus'},
    'ne_golden_grove': {'name': 'Golden Grove Village', 'lat': -34.79, 'lon': 138.7, 'type': 'bus'},
    'ne_greenwith': {'name': 'Greenwith', 'lat': -34.77, 'lon': 138.715, 'type': 'bus'},
    'ne_highbury': {'name': 'Highbury', 'lat': -34.87, 'lon': 138.66, 'type': 'bus'},
    'ne_hope_valley': {'name': 'Hope Valley', 'lat': -34.85, 'lon': 138.67, 'type': 'bus'},
    'ne_klemzig': {'name': 'Klemzig', 'lat': -34.88, 'lon': 138.64, 'type': 'bus'},
    'ne_mawson_lakes': {'name': 'Mawson Lakes Interchange', 'lat': -34.82, 'lon': 138.61, 'type': 'bus'},
    'ne_modbury_hospital': {'name': 'Modbury Hospital', 'lat': -34.83, 'lon': 138.68, 'type': 'bus'},
    'ne_modbury_interchange': {'name': 'Modbury Interchange', 'lat': -34.835, 'lon': 138.685, 'type': 'bus'},
    'ne_paradise': {'name': 'Paradise Interchange', 'lat': -34.87, 'lon': 138.68, 'type': 'bus'},
    'ne_surrey_downs': {'name': 'Surrey Downs', 'lat': -34.78, 'lon': 138.71, 'type': 'bus'},
    'ne_tea_tree_plaza': {'name': 'Tea Tree Plaza Interchange', 'lat': -34.8336, 'lon': 138.6919, 'type': 'bus'},
    'ne_windsor_gardens': {'name': 'Windsor Gardens', 'lat': -34.86, 'lon': 138.65, 'type': 'bus'},
    'nw_albert_park': {'name': 'Albert Park', 'lat': -34.91, 'lon': 138.54, 'type': 'train'},
    'nw_birkenhead': {'name': 'Birkenhead', 'lat': -34.84, 'lon': 138.5, 'type': 'bus'},
    'nw_cheltenham': {'name': 'Cheltenham', 'lat': -34.905, 'lon': 138.545, 'type': 'train'},
    'nw_glanville': {'name': 'Glanville', 'lat': -34.84, 'lon': 138.49, 'type': 'train'},
    'nw_grange': {'name': 'Grange', 'lat': -34.92, 'lon': 138.53, 'type': 'train'},
    'nw_hendon': {'name': 'Hendon', 'lat': -34.865, 'lon': 138.5, 'type': 'bus'},
    'nw_largs': {'name': 'Largs', 'lat': -34.78, 'lon': 138.47, 'type': 'train'},
    'nw_osborne': {'name': 'Osborne', 'lat': -34.82, 'lon': 138.485, 'type': 'train'},
    'nw_outer_harbor': {'name': 'Outer Harbor', 'lat': -34.78, 'lon': 138.48, 'type': 'train'},
    'nw_port_adelaide': {'name': 'Port Adelaide', 'lat': -34.85, 'lon': 138.51, 'type': 'train'},
    'nw_royal_park': {'name': 'Royal Park', 'lat': -34.87, 'lon': 138.505, 'type': 'bus'},
    'nw_seaton_park': {'name': 'Seaton Park', 'lat': -34.915, 'lon': 138.535, 'type': 'train'},
    'nw_semaphore': {'name': 'Semaphore', 'lat': -34.835, 'lon': 138.485, 'type': 'bus'},
    'nw_taperoo': {'name': 'Taperoo', 'lat': -34.8, 'lon': 138.48, 'type': 'train'},
    'nw_west_lakes': {'name': 'Westfield West Lakes', 'lat': -34.885, 'lon': 138.495, 'type': 'bus'},
    's_ascot_park': {'name': 'Ascot Park', 'lat': -34.985, 'lon': 138.565, 'type': 'train'},
    's_brighton': {'name': 'Brighton', 'lat': -35.03, 'lon': 138.535, 'type': 'train'},
    's_edwardstown': {'name': 'Edwardstown', 'lat': -34.975, 'lon': 138.575, 'type': 'train'},
    's_hove': {'name': 'Hove', 'lat': -35.025, 'lon': 138.54, 'type': 'train'},
    's_marion': {'name': 'Westfield Marion', 'lat': -35.015, 'lon': 138.54, 'type': 'bus'},
    's_marion_train': {'name': 'Marion Station', 'lat': -35.005, 'lon': 138.555, 'type': 'train'},
    's_mitchell_park': {'name': 'Mitchell Park', 'lat': -34.995, 'lon': 138.565, 'type': 'train'},
    's_oaklands': {'name': 'Oaklands', 'lat': -35.015, 'lon': 138.55, 'type': 'train'},
    's_park_holme': {'name': 'Park Holme', 'lat': -35.0, 'lon': 138.56, 'type': 'bus'},
    's_plympton': {'name': 'Plympton', 'lat': -34.96, 'lon': 138.55, 'type': 'bus'},
    's_south_plympton_bus': {'name': 'South Plympton Bus', 'lat': -34.955, 'lon': 138.545, 'type': 'bus'},
    's_tonsley': {'name': 'Tonsley', 'lat': -35.005, 'lon': 138.57, 'type': 'train'},
    's_warradale': {'name': 'Warradale', 'lat': -35.02, 'lon': 138.545, 'type': 'train'},
    's_woodlands_park': {'name': 'Woodlands Park', 'lat': -34.98, 'lon': 138.57, 'type': 'train'},
    'se_aldinga': {'name': 'Aldinga Shopping Centre', 'lat': -35.28, 'lon': 138.47, 'type': 'bus'},
    'se_bedford_park': {'name': 'Bedford Park', 'lat': -35.005, 'lon': 138.635, 'type': 'train'},
    'se_christies_beach': {'name': 'Christies Beach', 'lat': -35.135, 'lon': 138.495, 'type': 'train'},
    'se_flinders': {'name': 'Flinders', 'lat': -35.02, 'lon': 138.65, 'type': 'train'},
    'se_flinders_medical': {'name': 'Flinders Medical Centre', 'lat': -35.015, 'lon': 138.645, 'type': 'train'},
    'se_hallett_cove': {'name': 'Hallett Cove', 'lat': -35.075, 'lon': 138.51, 'type': 'train'},
    'se_hallett_cove_beach': {'name': 'Hallett Cove Beach', 'lat': -35.085, 'lon': 138.505, 'type': 'train'},
    'se_lonsdale': {'name': 'Lonsdale', 'lat': -35.095, 'lon': 138.5, 'type': 'train'},
    'se_marino': {'name': 'Marino', 'lat': -35.045, 'lon': 138.525, 'type': 'train'},
    'se_noarlunga': {'name': 'Noarlunga Centre Interchange', 'lat': -35.14, 'lon': 138.5, 'type': 'bus'},
    'se_seacliff_train': {'name': 'Seacliff Station', 'lat': -35.035, 'lon': 138.53, 'type': 'train'},
    'se_seaford': {'name': 'Seaford Station', 'lat': -35.185, 'lon': 138.478, 'type': 'train'},
    'se_sturt_creek': {'name': 'Sturt Creek', 'lat': -34.995, 'lon': 138.625, 'type': 'train'},
    'sw_brighton': {'name': 'Brighton', 'lat': -35.03, 'lon': 138.535, 'type': 'bus'},
    'sw_brighton_rd': {'name': 'Brighton Road', 'lat': -34.97, 'lon': 138.52, 'type': 'tram'},
    'sw_glenelg': {'name': 'Glenelg', 'lat': -34.9807, 'lon': 138.512, 'type': 'tram'},
    'sw_glenelg_bus': {'name': 'Glenelg Bus Interchange', 'lat': -34.98, 'lon': 138.515, 'type': 'bus'},
    'sw_glengowrie': {'name': 'Glengowrie', 'lat': -34.955, 'lon': 138.535, 'type': 'tram'},
    'sw_hove': {'name': 'Hove', 'lat': -35.025, 'lon': 138.54, 'type': 'bus'},
    'sw_jetty_rd': {'name': 'Jetty Road', 'lat': -34.975, 'lon': 138.515, 'type': 'tram'},
    'sw_moseley_sq': {'name': 'Moseley Square', 'lat': -34.978, 'lon': 138.513, 'type': 'tram'},
    'sw_seacliff': {'name': 'Seacliff', 'lat': -35.035, 'lon': 138.53, 'type': 'bus'},
    'sw_south_plympton': {'name': 'South Plympton', 'lat': -34.95, 'lon': 138.54, 'type': 'tram'},
    'w_arndale': {'name': 'Arndale Shopping Centre', 'lat': -34.8808, 'lon': 138.5567, 'type': 'bus'},
    'w_cheltenham_halt': {'name': 'Cheltenham Railway Station', 'lat': -34.905, 'lon': 138.545, 'type': 'train'},
    'w_findon': {'name': 'Findon', 'lat': -34.9, 'lon': 138.53, 'type': 'bus'},
    'w_grange': {'name': 'Grange', 'lat': -34.925, 'lon': 138.485, 'type': 'bus'},
    'w_henley_beach': {'name': 'Henley Beach', 'lat': -34.92, 'lon': 138.49, 'type': 'bus'},
    'w_kilkenny': {'name': 'Kilkenny', 'lat': -34.88, 'lon': 138.54, 'type': 'bus'},
    'w_woodville': {'name': 'Woodville', 'lat': -34.87, 'lon': 138.53, 'type': 'bus'},
}

def get_closest_stop(user_lat, user_lon):
    """Find the closest stop to user location"""
    closest = None
    min_distance = float('inf')
    
    for stop_id, stop in ADELAIDE_STOPS.items():
        dist = calculate_distance(user_lat, user_lon, stop['lat'], stop['lon'])
        if dist < min_distance:
            min_distance = dist
            closest = {**stop, 'id': stop_id, 'distance': dist}
    
    return closest

def get_nearby_stops(user_lat, user_lon, radius_km=2):
    """Get all stops within radius"""
    nearby = []
    
    for stop_id, stop in ADELAIDE_STOPS.items():
        dist = calculate_distance(user_lat, user_lon, stop['lat'], stop['lon'])
        if dist <= radius_km:
            nearby.append({**stop, 'id': stop_id, 'distance': dist})
    
    # Sort by distance
    nearby.sort(key=lambda x: x['distance'])
    return nearby

@adelaide_metro_bp.route('/api/stops')
def get_stops():
    """Get stops with accurate positions"""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', 2, type=float)
    
    if lat and lon:
        # Return nearby stops sorted by distance
        stops = []
        for stop_id, stop in ADELAIDE_STOPS.items():
            dist = calculate_distance(lat, lon, stop['lat'], stop['lon'])
            if dist <= radius:
                stops.append({
                    'id': stop_id,
                    'name': stop['name'],
                    'lat': stop['lat'],
                    'lon': stop['lon'],
                    'type': stop['type'],
                    'distance': round(dist, 2)
                })
        stops.sort(key=lambda x: x['distance'])
        return jsonify({'stops': stops, 'count': len(stops)})
    else:
        # Return all stops
        stops = [{**stop, 'id': sid} for sid, stop in ADELAIDE_STOPS.items()]
        return jsonify({'stops': stops, 'count': len(stops)})

@adelaide_metro_bp.route('/api/stop/closest')
def get_closest_stop_api():
    """Get the closest stop to user location"""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    
    if not lat or not lon:
        return jsonify({'error': 'lat and lon required'}), 400
    
    closest = get_closest_stop(lat, lon)
    return jsonify(closest)

def interpolate_position(waypoints, progress):
    """Interpolate position along waypoints based on progress (0-1)"""
    if not waypoints:
        return (-34.9285, 138.6007)
    
    if len(waypoints) == 1:
        return waypoints[0]
    
    # Calculate total distance
    total_distance = 0
    for i in range(len(waypoints) - 1):
        lat1, lon1 = waypoints[i]
        lat2, lon2 = waypoints[i + 1]
        # Simple distance (not haversine, but good enough for interpolation)
        dist = ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5
        total_distance += dist
    
    if total_distance == 0:
        return waypoints[0]
    
    # Find which segment we're on
    target_distance = total_distance * progress
    current_distance = 0
    
    for i in range(len(waypoints) - 1):
        lat1, lon1 = waypoints[i]
        lat2, lon2 = waypoints[i + 1]
        segment_dist = ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5
        
        if current_distance + segment_dist >= target_distance:
            # We're on this segment
            segment_progress = (target_distance - current_distance) / segment_dist if segment_dist > 0 else 0
            lat = lat1 + (lat2 - lat1) * segment_progress
            lon = lon1 + (lon2 - lon1) * segment_progress
            return (lat, lon)
        
        current_distance += segment_dist
    
    # Return last waypoint if we get here
    return waypoints[-1]

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing between two points"""
    import math
    d_lon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    
    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
    
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

# Adelaide timezone offset (UTC+10:30 or UTC+9:30 for DST)
# Simplified: using UTC+10:30 (Adelaide standard time)
from datetime import datetime, timedelta

# Adelaide metro area bounds - covers all of Greater Adelaide
ADELAIDE_BOUNDS = {
    'min_lat': -35.25,  # South to Aldinga/Seaford
    'max_lat': -34.55,  # North to Gawler
    'min_lon': 138.40,  # West to Outer Harbor/Glenelg
    'max_lon': 138.80   # East to Mount Barker/Hills
}

def is_in_adelaide(lat, lon):
    """Check if coordinates are within Adelaide metro area"""
    return (ADELAIDE_BOUNDS['min_lat'] <= lat <= ADELAIDE_BOUNDS['max_lat'] and
            ADELAIDE_BOUNDS['min_lon'] <= lon <= ADELAIDE_BOUNDS['max_lon'])

def get_adelaide_time():
    """Get current time in Adelaide timezone"""
    # Adelaide is UTC+10:30 (standard) or UTC+9:30 (DST)
    utc_now = datetime.utcnow()
    # Simple approximation: Adelaide is +10:30 from UTC
    adelaide_offset = timedelta(hours=10, minutes=30)
    return utc_now + adelaide_offset

ADELAIDE_TZ = 'Australia/Adelaide'

def format_adelaide_time(dt):
    """Format datetime for Adelaide timezone"""
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + '+10:30'

def get_next_stop_for_position(lat, lon, waypoints, destinations, route_type, route_id=None):
    """Calculate the actual next stop based on vehicle position and route direction"""
    import math
    
    city_lat, city_lon = -34.9211, 138.5958  # Adelaide CBD
    
    # Determine if heading to city or away from city
    dist_to_start = math.sqrt((lat - waypoints[0][0])**2 + (lon - waypoints[0][1])**2)
    dist_to_end = math.sqrt((lat - waypoints[-1][0])**2 + (lon - waypoints[-1][1])**2)
    dist_start_to_city = math.sqrt((waypoints[0][0] - city_lat)**2 + (waypoints[0][1] - city_lon)**2)
    dist_end_to_city = math.sqrt((waypoints[-1][0] - city_lat)**2 + (waypoints[-1][1] - city_lon)**2)
    
    # If start is closer to city, heading to city means going towards start
    heading_to_city = dist_start_to_city < dist_end_to_city
    
    # Get appropriate stops list
    stops = []
    if route_type == 'train' and route_id and route_id in ROUTE_STOPS:
        stops = ROUTE_STOPS[route_id]
    elif route_type == 'tram' and route_id and route_id in ROUTE_STOPS:
        stops = ROUTE_STOPS[route_id]
    elif route_type == 'bus' and route_id and route_id in BUS_ROUTE_STOPS:
        stops = BUS_ROUTE_STOPS[route_id]
    else:
        stops = BUS_STOPS
    
    # Find closest stop to current position
    closest_stop = None
    closest_dist = float('inf')
    closest_idx = 0
    
    for i, stop in enumerate(stops):
        dist = math.sqrt((stop['lat'] - lat)**2 + (stop['lon'] - lon)**2)
        if dist < closest_dist:
            closest_dist = dist
            closest_stop = stop
            closest_idx = i
    
    # Determine next stop based on direction
    if heading_to_city:
        # Heading towards city (earlier stops in list)
        if closest_idx > 0:
            next_stop = stops[closest_idx - 1]
        else:
            next_stop = stops[0] if stops else closest_stop
    else:
        # Heading away from city (later stops in list)
        if closest_idx < len(stops) - 1:
            next_stop = stops[closest_idx + 1]
        else:
            next_stop = stops[-1] if stops else closest_stop
    
    # Calculate arrival time based on distance
    if next_stop:
        dist_to_next = calculate_distance(lat, lon, next_stop['lat'], next_stop['lon'])
        # Speed in km/h: train ~50, tram ~25, bus ~30
        avg_speed = {'train': 50, 'tram': 25, 'bus': 30}.get(route_type, 30)
        arrival_mins = max(1, int((dist_to_next / avg_speed) * 60))
        return next_stop['name'], arrival_mins
    
    return 'Unknown', 5

@adelaide_metro_bp.route('/api/vehicles')
def get_vehicles():
    """Get real-time vehicle positions - GTFS-RT with simulation fallback"""
    route_id = request.args.get('route')
    vehicle_type = request.args.get('type')
    
    # Try real-time GTFS data first
    try:
        from adelaide_metro_gtfs_realtime import get_cached_vehicles
        real_vehicles = get_cached_vehicles(max_age_seconds=60)
        
        if real_vehicles and len(real_vehicles) > 0:
            vehicles = real_vehicles
            if route_id:
                vehicles = [v for v in vehicles if v['route_id'] == route_id]
            if vehicle_type:
                vehicles = [v for v in vehicles if v['type'] == vehicle_type]
            
            return jsonify({
                'vehicles': vehicles,
                'count': len(vehicles),
                'source': 'gtfs-rt-live',
                'updated_at': format_adelaide_time(get_adelaide_time())
            })
    except Exception as e:
        print(f"[API] GTFS unavailable: {e}")
    
    # Fall back to simulation
    vehicles = []
    import random
    
    # Set seed for consistent vehicle generation during this request
    random.seed(42)
    
    # Add trains - FIXED count per train line
    for train in ADELAIDE_ROUTES['trains']:
        if route_id and train['id'] != route_id:
            continue
        if vehicle_type and vehicle_type != 'train':
            continue
        
        waypoints = train.get('waypoints', [(-34.9285, 138.6007)])
        
        # Generate exactly 3 vehicles per train line
        for i in range(3):
            progress = (i + 0.5) / 3  # Evenly spaced along route
            lat, lon = interpolate_position(waypoints, progress)
            lat += random.uniform(-0.001, 0.001)
            lon += random.uniform(-0.001, 0.001)
            
            # Skip if not in Adelaide bounds
            if not is_in_adelaide(lat, lon):
                continue
            
            next_progress = min(1, progress + 0.01)
            next_lat, next_lon = interpolate_position(waypoints, next_progress)
            bearing = calculate_bearing(lat, lon, next_lat, next_lon)
            
            # Get actual next stop
            next_stop, arrival_mins = get_next_stop_for_position(
                lat, lon, waypoints, train['destinations'], 'train', train['id']
            )
            
            vehicles.append({
                'id': f"{train['id']}_{i}",
                'route_id': train['id'],
                'route_name': train['name'],
                'type': 'train',
                'lat': lat,
                'lon': lon,
                'bearing': bearing,
                'speed': random.randint(40, 80),
                'destination': random.choice(train['destinations']),
                'status': random.choice(['on-time', 'on-time', 'on-time', 'delayed']),
                'next_stop': next_stop,
                'arrival_minutes': arrival_mins,
                'updated_at': format_adelaide_time(get_adelaide_time())
            })
    
    # Add trams - FIXED count per tram line
    for tram in ADELAIDE_ROUTES['trams']:
        if route_id and tram['id'] != route_id:
            continue
        if vehicle_type and vehicle_type != 'tram':
            continue
        
        waypoints = tram.get('waypoints', [(-34.9285, 138.6007)])
        
        # Generate exactly 3 vehicles per tram line
        for i in range(3):
            progress = (i + 0.5) / 3
            lat, lon = interpolate_position(waypoints, progress)
            lat += random.uniform(-0.0005, 0.0005)
            lon += random.uniform(-0.0005, 0.0005)
            
            if not is_in_adelaide(lat, lon):
                continue
            
            next_progress = min(1, progress + 0.01)
            next_lat, next_lon = interpolate_position(waypoints, next_progress)
            bearing = calculate_bearing(lat, lon, next_lat, next_lon)
            
            next_stop, arrival_mins = get_next_stop_for_position(
                lat, lon, waypoints, tram['destinations'], 'tram', tram['id']
            )
            
            vehicles.append({
                'id': f"{tram['id']}_{i}",
                'route_id': tram['id'],
                'route_name': tram['name'],
                'type': 'tram',
                'lat': lat,
                'lon': lon,
                'bearing': bearing,
                'speed': random.randint(20, 50),
                'destination': random.choice(tram['destinations']),
                'status': random.choice(['on-time', 'on-time', 'on-time', 'delayed']),
                'next_stop': next_stop,
                'arrival_minutes': arrival_mins,
                'updated_at': format_adelaide_time(get_adelaide_time())
            })
    
    # Add buses - FIXED count per bus route
    for bus in ADELAIDE_ROUTES['buses']:
        if route_id and bus['id'] != route_id:
            continue
        if vehicle_type and vehicle_type != 'bus':
            continue
        
        waypoints = bus.get('waypoints', [(-34.9285, 138.6007)])
        
        # Generate exactly 4 vehicles per bus route
        for i in range(4):
            progress = (i + 0.5) / 4
            lat, lon = interpolate_position(waypoints, progress)
            lat += random.uniform(-0.002, 0.002)
            lon += random.uniform(-0.002, 0.002)
            
            if not is_in_adelaide(lat, lon):
                continue
            
            next_progress = min(1, progress + 0.01)
            next_lat, next_lon = interpolate_position(waypoints, next_progress)
            bearing = calculate_bearing(lat, lon, next_lat, next_lon)
            
            next_stop, arrival_mins = get_next_stop_for_position(
                lat, lon, waypoints, bus['destinations'], 'bus', bus['id']
            )
            
            vehicles.append({
                'id': f"{bus['id']}_{i}",
                'route_id': bus['id'],
                'route_name': bus['name'],
                'type': 'bus',
                'lat': lat,
                'lon': lon,
                'bearing': bearing,
                'speed': random.randint(30, 60),
                'destination': random.choice(bus['destinations']),
                'status': random.choice(['on-time', 'on-time', 'delayed', 'early']),
                'next_stop': next_stop,
                'arrival_minutes': arrival_mins,
                'updated_at': format_adelaide_time(get_adelaide_time())
            })
        if route_id and bus['id'] != route_id:
            continue
        if vehicle_type and vehicle_type != 'bus':
            continue
        
        waypoints = bus.get('waypoints', [(-34.9285, 138.6007)])
        
        # Increase bus count for better coverage
        for i in range(random.randint(3, 6)):
            progress = random.uniform(0, 1)
            lat, lon = interpolate_position(waypoints, progress)
            lat += random.uniform(-0.002, 0.002)
            lon += random.uniform(-0.002, 0.002)
            
            # Skip if not in Adelaide metro area
            if not is_in_adelaide(lat, lon):
                continue
            
            next_progress = min(1, progress + 0.01)
            next_lat, next_lon = interpolate_position(waypoints, next_progress)
            bearing = calculate_bearing(lat, lon, next_lat, next_lon)
            
            # Get actual next stop
            next_stop, arrival_mins = get_next_stop_for_position(
                lat, lon, waypoints, bus['destinations'], 'bus', bus['id']
            )
            
            vehicles.append({
                'id': f"{bus['id']}_{i}",
                'route_id': bus['id'],
                'route_name': bus['name'],
                'type': 'bus',
                'lat': lat,
                'lon': lon,
                'bearing': bearing,
                'speed': random.randint(30, 60),
                'destination': random.choice(bus['destinations']),
                'status': random.choice(['on-time', 'on-time', 'delayed', 'early']),
                'next_stop': next_stop,
                'arrival_minutes': arrival_mins,
                'updated_at': format_adelaide_time(get_adelaide_time())
            })
    
    return jsonify({
        'vehicles': vehicles,
        'count': len(vehicles),
        'source': 'simulation',
        'updated_at': format_adelaide_time(get_adelaide_time())
    })

@adelaide_metro_bp.route('/api/status')
def get_gtfs_status():
    """Check GTFS real-time status"""
    try:
        from adelaide_metro_gtfs_realtime import get_cached_vehicles, _last_fetch_time
        real_vehicles = get_cached_vehicles(max_age_seconds=120)
        
        if real_vehicles:
            return jsonify({
                'status': 'connected',
                'vehicles_cached': len(real_vehicles),
                'last_update': _last_fetch_time.isoformat() if _last_fetch_time else None,
                'source': 'gtfs-rt'
            })
        else:
            return jsonify({
                'status': 'disconnected',
                'vehicles_cached': 0,
                'source': 'simulation'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'source': 'simulation'
        })

@adelaide_metro_bp.route('/api/alerts')
def get_alerts():
    """Get service alerts"""
    route_id = request.args.get('route')
    
    # Mock alerts
    alerts = [
        {
            'id': '1',
            'route_id': None,
            'severity': 'info',
            'title': 'Weekend Schedule',
            'description': 'Sunday services operating on all lines.',
            'active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'id': '2',
            'route_id': 'Gawler',
            'severity': 'warning',
            'title': 'Minor Delays',
            'description': 'Gawler line experiencing minor delays due to signal fault.',
            'active': True,
            'created_at': datetime.now().isoformat()
        }
    ]
    
    if route_id:
        alerts = [a for a in alerts if a['route_id'] == route_id or a['route_id'] is None]
    
    return jsonify({
        'alerts': alerts,
        'count': len(alerts),
        'updated_at': datetime.now().isoformat()
    })

@adelaide_metro_bp.route('/api/trip-plan', methods=['POST'])
def trip_plan():
    """Plan a trip between two points"""
    data = request.get_json()
    
    from_stop = data.get('from')
    to_stop = data.get('to')
    time = data.get('time')
    
    # Mock trip planning result
    return jsonify({
        'trips': [
            {
                'duration': 25,
                'transfers': 0,
                'legs': [
                    {
                        'mode': 'train',
                        'route': 'Seaford',
                        'from': from_stop or 'Adelaide',
                        'to': to_stop or 'Seaford',
                        'departure': '14:30',
                        'arrival': '14:55'
                    }
                ]
            }
        ],
        'from': from_stop,
        'to': to_stop
    })

@adelaide_metro_bp.route('/api/stop/<stop_id>/times')
def get_stop_times(stop_id):
    """Get upcoming departures for a stop"""
    
    # Mock stop times
    import random
    times = []
    now = datetime.now()
    
    for i in range(5):
        departure = now + timedelta(minutes=random.randint(5, 60))
        route = random.choice(ADELAIDE_ROUTES['trains'] + ADELAIDE_ROUTES['trams'] + ADELAIDE_ROUTES['buses'])
        
        times.append({
            'route_id': route['id'],
            'route_name': route['name'],
            'destination': random.choice(route['destinations']),
            'scheduled_time': departure.strftime('%H:%M'),
            'estimated_time': (departure + timedelta(minutes=random.randint(-2, 5))).strftime('%H:%M'),
            'status': random.choice(['on-time', 'on-time', 'delayed', 'early']),
            'platform': random.choice(['1', '2', '3']) if route in ADELAIDE_ROUTES['trains'] else None
        })
    
    times.sort(key=lambda x: x['scheduled_time'])
    
    return jsonify({
        'stop_id': stop_id,
        'departures': times,
        'updated_at': datetime.now().isoformat()
    })

# Import send_from_directory for the index route
from flask import send_from_directory
