// Service Worker for Adelaide Metro Tracker
// Provides offline support and API response caching

const CACHE_NAME = 'adelaide-metro-v1';
const STATIC_ASSETS = [
    '/templates/adelaide-metro/index.html',
    '/static/adelaide-metro-stops.js',
    '/static/adelaide-metro-enhanced.js',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    '/adelaide-metro/api/routes',
    '/adelaide-metro/api/vehicles',
    '/adelaide-metro/api/alerts'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        }).then(() => {
            self.skipWaiting();
        }).catch((err) => {
            console.log('[SW] Cache install error:', err);
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((name) => {
                    if (name !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    }
                })
            );
        }).then(() => {
            self.clients.claim();
        })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Handle API requests with stale-while-revalidate strategy
    if (API_CACHE_PATTERNS.some(pattern => url.pathname.includes(pattern))) {
        event.respondWith(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.match(request).then((cachedResponse) => {
                    // Return cached response immediately if available
                    const fetchPromise = fetch(request).then((networkResponse) => {
                        // Update cache with fresh data
                        if (networkResponse && networkResponse.status === 200) {
                            cache.put(request, networkResponse.clone());
                        }
                        return networkResponse;
                    }).catch(() => {
                        // Network failed - return cached if available
                        console.log('[SW] Network failed for API, using cache');
                        return cachedResponse;
                    });

                    return cachedResponse || fetchPromise;
                });
            })
        );
        return;
    }

    // Handle static assets with cache-first strategy
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
                // Return cached response
                return cachedResponse;
            }

            // Fetch from network
            return fetch(request).then((networkResponse) => {
                // Cache successful responses
                if (networkResponse && networkResponse.status === 200) {
                    const responseToCache = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, responseToCache);
                    });
                }
                return networkResponse;
            }).catch((err) => {
                console.log('[SW] Fetch failed:', err);
                // Return offline fallback for HTML requests
                if (request.headers.get('accept').includes('text/html')) {
                    return caches.match('/templates/adelaide-metro/index.html');
                }
            });
        })
    );
});

// Handle background sync for offline form submissions
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-favorites') {
        event.waitUntil(syncFavorites());
    }
});

// Handle push notifications (for future service alerts)
self.addEventListener('push', (event) => {
    const data = event.data?.json() || {};
    const options = {
        body: data.body || 'New service alert available',
        icon: '/static/favicon.ico',
        badge: '/static/favicon.ico',
        tag: data.tag || 'service-alert',
        requireInteraction: data.requireInteraction || false,
        data: data.data || {}
    };

    event.waitUntil(
        self.registration.showNotification(
            data.title || 'Adelaide Metro Alert',
            options
        )
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    const url = event.notification.data?.url || '/templates/adelaide-metro/index.html';
    
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then((clientList) => {
            // Focus existing window if open
            for (const client of clientList) {
                if (client.url === url && 'focus' in client) {
                    return client.focus();
                }
            }
            // Open new window
            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});

async function syncFavorites() {
    // Future: sync favorites with server when online
    console.log('[SW] Syncing favorites...');
}

// Message handling from main thread
self.addEventListener('message', (event) => {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }
});
