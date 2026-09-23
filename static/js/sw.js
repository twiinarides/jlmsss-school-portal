/**
 * JLMSSS Admissions Portal — Service Worker
 * Provides offline support and caching for the PWA
 */

const CACHE_NAME = 'jlmsss-v1';
const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
];

// Install: pre-cache static assets
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(() => {});
    })
  );
});

// Activate: clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  return self.clients.claim();
});

// Fetch: network-first with cache fallback for navigation
self.addEventListener('fetch', event => {
  const req = event.request;
  // Only handle GET requests for same-origin
  if (req.method !== 'GET') return;
  if (!req.url.startsWith(self.location.origin)) return;

  // For navigation requests: network first, cache fallback
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() =>
        caches.match('/').then(r => r || new Response('Offline', { status: 503 }))
      )
    );
    return;
  }

  // For static assets: cache first
  if (req.url.includes('/static/')) {
    event.respondWith(
      caches.match(req).then(cached => {
        if (cached) return cached;
        return fetch(req).then(resp => {
          if (resp && resp.status === 200) {
            caches.open(CACHE_NAME).then(cache => cache.put(req, resp.clone()));
          }
          return resp;
        }).catch(() => cached);
      })
    );
  }
});
