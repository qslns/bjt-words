/* BJT 빈출 단어장 — 오프라인 캐시 (서비스 워커) */
const VERSION = '9d349d05b6';
const CORE = 'bjt-core-' + VERSION;
const FONTS = 'bjt-fonts-v1';
const AUDIO = 'bjt-audio-v1';   // 녹음 음성: 앱을 업데이트해도 지우지 않음
const BASE = new URL('./', self.location).href;            // 앱이 놓인 폴더 (루트든 하위 경로든)
const SCOPE_PATH = new URL('./', self.location).pathname;
const CORE_FILES = ['./', './manifest.webmanifest', './icons/apple-touch-icon.png', './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CORE)
      .then(cache => cache.addAll(CORE_FILES.map(u => new Request(new URL(u, BASE).href, {cache: 'reload'}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('bjt-core-') && k !== CORE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* 페이지: 인터넷 먼저(최신 버전), 3초 안에 안 오거나 끊겨 있으면 저장본 */
function page(event) {
  const net = fetch(event.request, {cache: 'no-cache'}).then(res => {
    if (res && res.ok && res.type === 'basic') {
      const copy = res.clone();
      caches.open(CORE).then(c => c.put(BASE, copy));
    }
    return res;
  });
  event.waitUntil(net.then(() => {}, () => {}));
  return caches.open(CORE).then(c => c.match(BASE)).then(cached => {
    if (!cached) return net;
    const fallback = net.then(r => (r && r.ok) ? r : cached, () => cached);
    const timer = new Promise(resolve => setTimeout(() => resolve(cached), 3000));
    return Promise.race([fallback, timer]);
  });
}

/* 글꼴: 저장본 먼저, 뒤에서 새로 받아 둠 */
function font(event) {
  return caches.open(FONTS).then(cache => cache.match(event.request).then(hit => {
    const net = fetch(event.request).then(res => {
      if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); cache.put(event.request, copy); }
      return res;
    });
    event.waitUntil(net.then(() => {}, () => {}));
    return hit || net;
  }));
}

/* 녹음 음성: 저장본 먼저. 사파리는 음성을 구간(Range) 단위로 요청하므로 206 응답으로 잘라서 줌 */
async function audio(event) {
  const req = event.request;
  const url = req.url.split('#')[0];
  const cache = await caches.open(AUDIO);
  let res = await cache.match(url);
  if (!res) {
    const net = await fetch(url);
    if (!net.ok) return net;
    await cache.put(url, net.clone());
    res = net;
  }
  const range = req.headers.get('range');
  if (!range) return res;
  const buf = await res.arrayBuffer();
  const size = buf.byteLength;
  const type = res.headers.get('Content-Type') || 'audio/mpeg';
  const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
  if (!m || (m[1] === '' && m[2] === '')) {
    return new Response(buf, {status: 200, headers: {'Content-Type': type, 'Content-Length': String(size), 'Accept-Ranges': 'bytes'}});
  }
  let start, end;
  if (m[1] === '') { start = Math.max(0, size - Number(m[2])); end = size - 1; }
  else { start = Number(m[1]); end = m[2] === '' ? size - 1 : Math.min(Number(m[2]), size - 1); }
  if (start >= size || start > end) return new Response(null, {status: 416, headers: {'Content-Range': 'bytes */' + size}});
  const part = buf.slice(start, end + 1);
  return new Response(part, {status: 206, statusText: 'Partial Content', headers: {'Content-Type': type, 'Content-Range': 'bytes ' + start + '-' + end + '/' + size, 'Content-Length': String(part.byteLength), 'Accept-Ranges': 'bytes'}});
}

/* 그 밖의 앱 파일(아이콘·매니페스트): 저장본 먼저 */
function asset(event) {
  return caches.match(event.request).then(hit => hit || fetch(event.request).then(res => {
    if (res && res.ok && res.type === 'basic') { const copy = res.clone(); caches.open(CORE).then(c => c.put(event.request, copy)); }
    return res;
  }));
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const same = url.origin === self.location.origin;
  if (req.mode === 'navigate' || (same && (url.pathname === SCOPE_PATH || url.pathname === SCOPE_PATH + 'index.html'))) {
    event.respondWith(page(event));
    return;
  }
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(font(event));
    return;
  }
  if (same && url.pathname.startsWith(SCOPE_PATH + 'audio/')) {
    event.respondWith(audio(event).catch(() => fetch(req)));
    return;
  }
  if (same && url.pathname.startsWith(SCOPE_PATH) && url.pathname !== SCOPE_PATH + 'sw.js') {
    event.respondWith(asset(event));
  }
});
