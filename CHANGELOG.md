# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-15

### Added
- **Offline Support** - Service Worker with caching for offline functionality
- **Favorites/Saved Trips** - Save trips with star button, view in Favorites tab
- **QR Code Sharing** - Generate and scan QR codes to share trips between devices
- **Service Alerts Tab** - Dedicated tab for active alerts and alert history
- **Smart Theme Toggle** - Auto mode switches theme based on time of day
- **High Contrast Mode** - Accessibility mode with enhanced contrast

### Accessibility (WCAG 2.1 AA)
- ARIA labels on all interactive elements
- Skip link for keyboard navigation
- Live region for screen reader announcements
- Focus-visible styles for keyboard users
- Proper tab panel semantics (role, aria-selected, aria-controls)

### Changed
- Enhanced tab navigation with Favorites and Alerts tabs
- Updated bottom navigation for mobile
- Improved offline indicator when network unavailable

### Technical
- Added Service Worker (`sw.js`) for offline caching
- Added QR code generation library (`qrcode.js`)
- localStorage for favorites and alert history
- Native Web Share API integration

## [1.0.0] - 2026-02-15

### Added
- Initial release of Adelaide Metro Live Tracker
- Real-time vehicle tracking with GPS positions
- Trip planner with multiple route options
- Live journey map with animated vehicle markers
- Push notifications for approaching vehicles (5min, 2min, arrival)
- Fullscreen map view
- Mobile-responsive glassmorphism UI
- 2,900+ stop database
- Support for buses, trains, and trams
- Route visualization with polylines
- Recent trips history
- Nearby stops based on GPS location

### Features
- 🗺️ Live vehicle tracking on interactive map
- 📍 Trip planning between any two stops
- 🔔 Browser push notifications
- 📱 Mobile-first responsive design
- 🌙 Dark/Light theme support
- 📊 Real-time arrival estimates
- 🚌 Vehicle type filtering
- 🗺️ Fullscreen map mode

### Technical
- Flask backend with GTFS-RT integration
- Leaflet.js for interactive maps
- Vanilla JavaScript frontend
- CSS3 with glassmorphism effects
- Browser Notifications API
- LocalStorage for trip history

## [0.1.0] - 2026-02-10

### Added
- Project initialization
- Basic Flask application structure
- GTFS-RT data fetching
- Initial map integration
- Basic stop database
