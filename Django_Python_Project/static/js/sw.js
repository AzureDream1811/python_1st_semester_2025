/**
 * Service Worker for ElectroShop PWA
 * Handles caching, offline support, and push notifications
 */

const CACHE_NAME = 'electroshop-v1';
const STATIC_CACHE = 'electroshop-static-v1';
const DYNAMIC_CACHE = 'electroshop-dynamic-v1';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/offline/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/images/logo.png',
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('[SW] Installing Service Worker...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[SW] Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating Service Worker...');
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
                    .map((key) => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') return;
    
    // Skip WebSocket and API requests
    if (url.pathname.startsWith('/ws/') || url.pathname.startsWith('/api/')) return;
    
    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                
                return fetch(request)
                    .then((networkResponse) => {
                        // Cache successful responses
                        if (networkResponse.ok) {
                            const responseClone = networkResponse.clone();
                            caches.open(DYNAMIC_CACHE)
                                .then((cache) => cache.put(request, responseClone));
                        }
                        return networkResponse;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (request.mode === 'navigate') {
                            return caches.match('/offline/');
                        }
                    });
            })
    );
});

// Push notification event
self.addEventListener('push', (event) => {
    console.log('[SW] Push notification received');
    
    let data = { title: 'ElectroShop', body: 'Bạn có thông báo mới!' };
    
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }
    
    const options = {
        body: data.body,
        icon: '/static/images/icon-192.png',
        badge: '/static/images/badge.png',
        vibrate: [100, 50, 100],
        data: data.data || {},
        actions: [
            { action: 'open', title: 'Xem chi tiết' },
            { action: 'close', title: 'Đóng' }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    if (event.action === 'open' || !event.action) {
        const url = event.notification.data.url || '/';
        event.waitUntil(
            clients.openWindow(url)
        );
    }
});

// Background sync event
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);
    
    if (event.tag === 'sync-cart') {
        event.waitUntil(syncCart());
    }
});

async function syncCart() {
    // Sync offline cart changes
    const cache = await caches.open(DYNAMIC_CACHE);
    const pendingActions = await cache.match('/pending-cart-actions');
    
    if (pendingActions) {
        const actions = await pendingActions.json();
        for (const action of actions) {
            try {
                await fetch('/api/cart/', {
                    method: 'POST',
                    body: JSON.stringify(action),
                    headers: { 'Content-Type': 'application/json' }
                });
            } catch (e) {
                console.error('[SW] Failed to sync cart action:', e);
            }
        }
        await cache.delete('/pending-cart-actions');
    }
}
