// MAZE の Service Worker: 一度開けば、通信なしでも起動できるようにする
// index.html やアイコンを変えたら CACHE の番号を上げる（古いキャッシュが消えて入れ替わる）
// 本番（kiyotake1229.github.io）はほかのアプリとキャッシュ置き場を共有しているので、
// 消すのも探すのも「maze-」で始まる自分のキャッシュだけにする
const CACHE = 'maze-v1';
const ASSETS = [
  './', './index.html', './manifest.json', './icon.svg',
  './icon-192.png', './icon-512.png', './icon-512-maskable.png', './apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith('maze-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

const fromCache = req => caches.open(CACHE).then(c => c.match(req));
const store = (req, resp) => { if (resp.ok) { const cp = resp.clone(); caches.open(CACHE).then(c => c.put(req, cp)); } return resp; };

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  if (e.request.mode === 'navigate') {
    // ページは毎回サーバーに最新を取りに行き、通信できないときだけキャッシュを使う
    e.respondWith(
      fetch(e.request, { cache: 'no-cache' }).then(resp => store(e.request, resp))
        .catch(() => fromCache(e.request).then(r => r || fromCache('./index.html')))
    );
    return;
  }
  // アイコンなどはキャッシュを優先する
  e.respondWith(fromCache(e.request).then(r => r || fetch(e.request).then(resp => store(e.request, resp))));
});
