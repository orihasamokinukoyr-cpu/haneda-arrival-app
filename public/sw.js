self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', () => self.clients.claim());
self.addEventListener('fetch', event => {
  // ネットワーク優先（常に最新データを取得）
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
