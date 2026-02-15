# 🚌 Adelaide Metro Live Tracker

Real-time public transport tracking for Adelaide, Australia. Track buses, trains, and trams with live GPS positions, trip planning, and journey notifications.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Site-blue)](https://raya.li/adelaide-metro)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-orange)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

![Adelaide Metro Tracker Screenshot](docs/screenshot.png)

## ✨ Features

### 🗺️ Live Vehicle Tracking
- Real-time GPS positions of all Adelaide Metro vehicles
- Color-coded markers (🔵 Trains, 🟢 Buses, 🔴 Trams)
- Vehicle speed, next stop, and arrival times
- Filter by vehicle type

### 📍 Trip Planner
- Plan journeys between any two stops
- Multiple route options with walking directions
- Live vehicle matching for your route
- Estimated arrival times

### 🔔 Push Notifications
- Get alerts when your transport is approaching
- Notifications at 5 min, 2 min, and arrival
- Works in background on supported browsers

### 📱 Mobile-First Design
- Responsive glassmorphism UI
- Bottom navigation for easy thumb reach
- Swipe gestures between tabs
- Works on all screen sizes

### 🗺️ Journey Map
- Full-screen map view for tracking
- Animated vehicle markers
- Route visualization
- Real-time updates every 10 seconds

## 🗺️ Roadmap

### In Progress
- [ ] Better route matching algorithm
- [ ] Offline support / service worker
- [ ] Accessibility improvements (WCAG 2.1 AA)

### Planned
- [ ] Trip cost calculator
- [ ] Crowding indicators
- [ ] Weather integration
- [ ] Multiple language support
- [ ] Trip sharing via QR code

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for the full roadmap.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip
- (Optional) Virtual environment

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/adelaide-metro-tracking.git
cd adelaide-metro-tracking

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:5000`

### Environment Variables

Create a `.env` file:

```env
FLASK_ENV=development
FLASK_PORT=5000
# Optional: For production
# DATABASE_URL=postgresql://...
```

## 🏗️ Architecture

```
adelaide-metro-tracking/
├── app.py                      # Main Flask application
├── adelaide_metro_routes.py    # Route definitions & API endpoints
├── adelaide_metro_gtfs_realtime.py  # GTFS-RT data fetching
├── templates/
│   └── index.html             # Single-page application
├── static/
│   ├── adelaide-metro-stops.js # Stop database (2,900+ stops)
│   └── favicon.ico
├── docs/
│   ├── API.md                 # API documentation
│   └── CONTRIBUTING.md        # Contribution guide
├── requirements.txt
├── README.md
└── LICENSE
```

## 📡 Data Sources

This application uses the official Adelaide Metro GTFS-RT feeds:
- Vehicle Positions (real-time GPS)
- Trip Updates (delays, arrivals)
- Service Alerts (disruptions)

**Note:** This is an unofficial project and is not affiliated with Adelaide Metro.

## 🔌 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /adelaide-metro/api/vehicles` | Live vehicle positions |
| `GET /adelaide-metro/api/routes` | All route definitions |
| `GET /adelaide-metro/api/alerts` | Service alerts |
| `POST /adelaide-metro/api/plan` | Trip planning |

See [docs/API.md](docs/API.md) for detailed documentation.

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Frontend:** Vanilla JavaScript, Leaflet.js (maps)
- **Data:** GTFS-RT (General Transit Feed Specification - Realtime)
- **Styling:** CSS3 with glassmorphism effects
- **Notifications:** Browser Notifications API

## 📱 Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Live Tracking | ✅ | ✅ | ✅ | ✅ |
| Push Notifications | ✅ | ✅ | ⚠️* | ✅ |
| Background Sync | ✅ | ⚠️ | ❌ | ✅ |

*Safari requires adding to home screen for push notifications

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Adelaide Metro for providing GTFS-RT data
- OpenStreetMap contributors for map tiles
- The Flask and Leaflet.js communities

## 📮 Contact

- GitHub Issues: [Report bugs or request features](../../issues)
- Email: me@raya.li

---

Made with ❤️ for Adelaide commuters
