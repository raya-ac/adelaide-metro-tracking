# API Documentation

## Base URL
```
http://localhost:5000/adelaide-metro/api
```

## Endpoints

### GET /vehicles
Returns live vehicle positions and status.

**Response:**
```json
{
  "vehicles": [
    {
      "id": "vehicle_123",
      "route_id": "174",
      "route_name": "Route 174",
      "type": "bus",
      "lat": -34.9285,
      "lon": 138.6007,
      "speed": 35,
      "heading": 180,
      "destination": "City",
      "next_stop": "Stop 45 Pimpala Rd",
      "arrival_minutes": 3,
      "status": "on_time"
    }
  ],
  "updated_at": "2026-02-15T11:45:00Z"
}
```

### GET /routes
Returns all transit routes.

**Response:**
```json
{
  "routes": [
    {
      "id": "Gawler",
      "name": "Gawler Line",
      "type": "train",
      "color": "#e31837",
      "destinations": ["Gawler Central", "Adelaide"],
      "waypoints": [[-34.92, 138.59], ...]
    }
  ]
}
```

### GET /alerts
Returns active service alerts.

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_1",
      "title": "Bus Replacement",
      "description": "Buses replacing trains between X and Y",
      "severity": "warning",
      "active": true,
      "start_time": "2026-02-15T06:00:00Z",
      "end_time": "2026-02-15T18:00:00Z"
    }
  ]
}
```

### POST /plan
Plan a trip between two stops.

**Request:**
```json
{
  "from": "Stop 45 Pimpala Rd",
  "to": "Adelaide Railway Station",
  "departure_time": "11:45"
}
```

**Response:**
```json
{
  "routes": [
    {
      "type": "transit",
      "totalTime": 25,
      "transfers": 0,
      "walkingDistance": 0,
      "legs": [
        {
          "type": "transit",
          "mode": "bus",
          "route": "Route 174",
          "from": "Stop 45 Pimpala Rd",
          "to": "Adelaide Railway Station",
          "departure": "11:45",
          "arrival": "12:10",
          "duration": 25,
          "stops": [...]
        }
      ]
    }
  ]
}
```

### GET /nearby
Find stops near a location.

**Query Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude  
- `radius` (optional): Search radius in meters (default: 500)
- `limit` (optional): Max results (default: 5)

**Response:**
```json
{
  "stops": [
    {
      "n": "Stop 45 Pimpala Rd - North side",
      "i": "North side",
      "lat": -35.1041,
      "lon": 138.549,
      "distance": 150
    }
  ]
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error description",
  "code": 400
}
```

Common HTTP codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Server Error

## Rate Limits

- 100 requests per minute per IP
- No authentication required for public endpoints
