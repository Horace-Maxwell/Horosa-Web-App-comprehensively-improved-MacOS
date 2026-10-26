
const CACHE_NAME = 'ziwei-offline-v2';

// Core assets to pre-cache immediately
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json'
];

// Install: Cache core app shell
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    })
  );
});

// Activate: Clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch: Hybrid Strategy
self.addEventListener('fetch', (event) => {
  // Only handle GET
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  
  // 1. Strategy for Third-Party CDNs (esm.sh, tailwindcss, unpkg etc.) -> Cache First
  // These are versioned or static, so we prefer cache to save bandwidth and ensure offline speed.
  if (url.hostname.includes('esm.sh') || url.hostname.includes('tailwindcss.com') || url.hostname.includes('cdn')) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then((networkResponse) => {
          // Check valid response
          if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic' && networkResponse.type !== 'cors') {
            return networkResponse;
          }
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
          return networkResponse;
        }).catch(() => {
           // If offline and not in cache, nothing we can do for external resource unless fallback exists
           return new Response('Offline', { status: 503 });
        });
      })
    );
    return;
  }

  // 2. Strategy for Local App Files -> Network First
  // Try to get latest version from server, fallback to cache if offline.
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200) {
           return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});
