// AnnApp offline cache: app shell up front, instrument samples as they are used.
const V='annapp-v11';
const SHELL=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png','icon-180.png',
  's/C2.mp3','s/Ds2.mp3','s/Fs2.mp3','s/A2.mp3','s/C3.mp3','s/Ds3.mp3','s/Fs3.mp3','s/A3.mp3','s/C4.mp3','s/Ds4.mp3','s/Fs4.mp3','s/A4.mp3','s/C5.mp3','s/Ds5.mp3','s/Fs5.mp3','s/A5.mp3','s/C6.mp3','s/Ds6.mp3','s/Fs6.mp3','s/A6.mp3','s/C7.mp3'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const u=new URL(r.url);
  if(u.origin!==self.location.origin&&!/cdnjs|fonts\.g/.test(u.host))return;
  const page=r.mode==='navigate'||u.pathname.endsWith('/index.html');
  if(page){ // network first, so updates arrive; cache when offline
    e.respondWith(fetch(r).then(res=>{const c=res.clone();caches.open(V).then(x=>x.put('index.html',c));return res}).catch(()=>caches.match('index.html')));return}
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{
    if(res.ok||res.type==='opaque'){const c=res.clone();caches.open(V).then(x=>x.put(r,c))}return res})));
});
