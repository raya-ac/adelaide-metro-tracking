# 🚌 Adelaide Metro Live Tracker

Real-time public transport tracking for Adelaide, Australia. Track buses, trains, and trams with live GPS positions, trip planning, and journey notifications.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Site-blue)](https://raya.li/adelaide-metro)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-orange)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![WCAG 2.1](https://img.shields.io/badge/WCAG%202.1-AA-brightgreen)](https://www.w3.org/WAI/WCAG21/quickref/)

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
- Save favorite trips for quick access

### 📡 Offline Support
- Service Worker caches assets for offline use
- Continue viewing cached data when offline
- Offline indicator shows connection status
- Background sync when connection returns

### 🔗 Trip Sharing
- Generate QR codes for any trip
- Share trips via native share API
- Scan QR codes to load shared trips
- URL-based trip sharing

### 🔔 Push Notifications
- Get alerts when your transport is approaching
- Notifications at 5 min, 2 min, and arrival
- Works in background on supported browsers

### 🌗 Smart Themes
- Dark mode (default)
- Light mode
- Auto mode (switches based on time of day)
- High contrast mode for accessibility

### ♿ Accessibility (WCAG 2.1 AA)
- Full keyboard navigation support
- Screen reader compatible with ARIA labels
- Skip links for quick navigation
- High contrast mode
- Focus indicators on all interactive elements

### 📱 Mobile-First Design
- Responsive glassmorphism UI
- Bottom navigation for easy thumb reach
- Swipe gestures between tabs
- Works on all screen sizes

### 🚨 Service Alerts
- Real-time service disruption alerts
- Alert history tracking
- Visual severity indicators
- Badge notifications for active alerts

### 🚦 Line Status Page
- Overview of all train lines (Belair, Seaford, Gawler, Flinders, Outer Harbor, Grange, Tonsley)
- Tram lines (Glenelg, Botanic, Entertainment Centre)
- Bus network status
- Color-coded status indicators (Good/Delayed/Disrupted)
- Click any line to filter the map

### 🕐 Next Departures
- Shows next 3 upcoming departures from nearby stops
- Route name, destination, and ETA
- Real-time countdown
- One-click to track specific departure

### 👥 Crowding Indicators
- Real-time occupancy levels (Quiet/Moderate/Busy)
- Color-coded (green/yellow/red)
- Displayed on vehicle cards and map popups
- Helps choose less crowded services

### 💰 Trip Cost Calculator
- Flat fare pricing (Adelaide Metro doesn't use zones)
- Peak fares: $4.55 regular / $2.25 concession
- Off-peak fares: $2.60 regular / $1.30 concession
- Peak hours: 3PM-9AM Mon-Fri, all day Saturday
- Off-peak: 9AM-3PM Mon-Fri, all day Sunday
- Displayed in trip results
- Updated for 2025-2026 fares

### 🌤️ Weather Integration
- Current weather at your location
- Temperature display
- Weather conditions (sunny, cloudy, rainy)
- Updates every 30 minutes
- Helps plan your journey

### 🌐 Multiple Language Support
- English (default)
- Chinese (Simplified) - 中文
- Arabic - العربية
- Language selector in header
- RTL support for Arabic
- Easy to add more languages

### 📊 Trip Analytics
- Track your trip history
- Most used routes
- Weekly trip statistics
- Total distance traveled
- Stored locally in your browser

### ❓ Help & Support
- FAQ section with common questions
- Quick help tips
- Contact form for feedback
- Report issues easily

### 🗺️ Journey Map
- Full-screen map view for tracking
- Animated vehicle markers
- Route visualization
- Real-time updates every 10 seconds

## 🗺️ Roadmap

### Recently Completed ✅
- [x] Offline support / service worker
- [x] Accessibility improvements (WCAG 2.1 AA)
- [x] Trip sharing via QR code
- [x] Favorite/saved trips
- [x] Auto theme toggle
- [x] Service disruption alerts
- [x] **Line Status page** - Train/tram/bus line status overview
- [x] **Next Departures** - Upcoming departures from nearby stops
- [x] **Crowding Indicators** - Real-time occupancy levels
- [x] **Trip Cost Calculator** - Zone-based fare estimation
- [x] **Weather Integration** - Current weather display
- [x] **Multiple Language Support** - English, Chinese (中文), Arabic (العربية)
- [x] **Trip Analytics** - Track and analyze your trips
- [x] **Help & Support** - FAQ and contact system

### In Progress
- [ ] Better route matching algorithm

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
│   ├── index.html             # Single-page application
│   ├── sw.js                  # Service Worker for offline support
│   └── qrcode.js              # QR code generation library
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
- **Offline:** Service Worker with Cache API
- **QR Codes:** Custom lightweight QR generator

## 📱 Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Live Tracking | ✅ | ✅ | ✅ | ✅ |
| Offline Support | ✅ | ✅ | ✅ | ✅ |
| Push Notifications | ✅ | ✅ | ⚠️* | ✅ |
| Background Sync | ✅ | ⚠️ | ❌ | ✅ |
| QR Code Sharing | ✅ | ✅ | ✅ | ✅ |

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
