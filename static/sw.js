const CACHE_NAME = 'luxious-beautyland-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/images/logo.png',
  '/static/images/favicon.png',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png'
];

// Installation du service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache ouvert');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Stratégie de cache : Network First, fallback to cache
self.addEventListener('fetch', event => {
  // Exclure les requêtes vers des APIs et les URLs dynamiques
  if (event.request.url.includes('/admin/') || 
      event.request.url.includes('/api/') ||
      event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Mettre en cache les nouvelles ressources
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseClone);
        });
        return response;
      })
      .catch(() => {
        // Retourner la ressource du cache si disponible
        return caches.match(event.request);
      })
  );
});

// Synchronisation en arrière-plan pour les formulaires hors ligne
self.addEventListener('sync', event => {
  if (event.tag === 'newsletter-sync') {
    event.waitUntil(syncNewsletter());
  }
});

async function syncNewsletter() {
  try {
    const db = await openDB();
    const offlineSubscriptions = await db.getAll('newsletter');
    
    for (const subscription of offlineSubscriptions) {
      try {
        const response = await fetch('/newsletter/subscribe/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: subscription.email })
        });
        
        if (response.ok) {
          await db.delete('newsletter', subscription.id);
        }
      } catch (error) {
        console.error('Erreur de synchronisation:', error);
      }
    }
  } catch (error) {
    console.error('Erreur d\'ouverture de la base de données:', error);
  }
}

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('LuxiousBeautylandDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('newsletter')) {
        db.createObjectStore('newsletter', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Notification push
self.addEventListener('push', event => {
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/badge.png',
    vibrate: [200, 100, 200],
    data: {
      url: data.url || '/'
    },
    actions: [
      {
        action: 'open',
        title: 'Ouvrir'
      },
      {
        action: 'close',
        title: 'Fermer'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});