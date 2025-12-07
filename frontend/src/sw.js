/**
 * Service Worker for GitHub Spec Kit Demo
 * 
 * Provides offline capability and caching for the demo application.
 */

const CACHE_NAME = 'speckit-demo-v1';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/css/main.css',
  '/css/animations.css',
  '/css/components/workflow-stepper.css',
  '/css/components/artifact-viewer.css',
  '/css/components/constitution-panel.css',
  '/css/components/check-badge.css',
  '/css/components/custom-scenario.css',
  '/css/components/form-validation.css',
  '/css/components/presenter-notes.css',
  '/js/main.js',
  '/js/services/api-client.js',
  '/js/services/state-manager.js',
  '/js/components/workflow-stepper.js',
  '/js/components/artifact-viewer.js',
  '/js/components/constitution-panel.js',
  '/js/components/presenter-notes.js',
  '/js/utils/animation-helpers.js'
];

// CDN assets to cache
const CDN_ASSETS = [
  'https://unpkg.com/@primer/css@21.0.7/dist/primer.css',
  'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[ServiceWorker] Caching static assets');
        // Cache static assets (may fail if files don't exist)
        return Promise.allSettled([
          ...STATIC_ASSETS.map(url => 
            cache.add(url).catch(err => console.warn(`Failed to cache ${url}:`, err))
          ),
          ...CDN_ASSETS.map(url => 
            cache.add(url).catch(err => console.warn(`Failed to cache CDN ${url}:`, err))
          )
        ]);
      })
      .then(() => {
        console.log('[ServiceWorker] Installation complete');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => {
              console.log('[ServiceWorker] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[ServiceWorker] Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // API requests - network only (no caching)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .catch(() => {
          // Return cached API response if available
          return caches.match(request);
        })
    );
    return;
  }
  
  // Static assets - cache first, network fallback
  if (STATIC_ASSETS.includes(url.pathname) || url.hostname !== location.hostname) {
    event.respondWith(
      caches.match(request)
        .then((cachedResponse) => {
          if (cachedResponse) {
            // Return cached response, but also update cache in background
            fetchAndCache(request);
            return cachedResponse;
          }
          return fetchAndCache(request);
        })
    );
    return;
  }
  
  // Other requests - network first, cache fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        // Cache successful responses
        if (response.ok) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => cache.put(request, responseClone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(request);
      })
  );
});

// Helper function to fetch and cache
async function fetchAndCache(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.warn('[ServiceWorker] Fetch failed:', request.url);
    throw error;
  }
}

// Handle messages from main thread
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
  
  if (event.data === 'clearCache') {
    caches.delete(CACHE_NAME)
      .then(() => console.log('[ServiceWorker] Cache cleared'));
  }
});
