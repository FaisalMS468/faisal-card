const CACHE='fahad-card-v7';
const FILES=['./','index.html','../logo.png','manifest.webmanifest','Fahad-Alherbeed-ar.vcf','Fahad-Alherbeed-en.vcf','../icons/apple-touch-icon.png','../icons/icon-192.png','../icons/icon-512.png',
  '../assets/tajawal/Iura6YBj_oCad4k1nzSBC5xLhLFw4Q.woff2','../assets/tajawal/Iura6YBj_oCad4k1nzGBC5xLhLE.woff2','../assets/tajawal/Iurf6YBj_oCad4k1l4qkHrRpiZtK6GwN9w.woff2','../assets/tajawal/Iurf6YBj_oCad4k1l4qkHrFpiZtK6Gw.woff2'];
// cache:'reload' skips the browser's HTTP cache so a new worker never stores a stale copy
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES.map(u=>new Request(u,{cache:'reload'})))).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
  const req=e.request;
  if(req.method!=='GET')return;
  // The page itself: always ask the network first (fresh copy), fall back to cache after 2s or when offline
  // Only handle this card's own page; another card in a subfolder has its own worker
  if(req.mode==='navigate'&&!['./','index.html'].some(x=>new URL(x,self.registration.scope).pathname===new URL(req.url).pathname))return;
  if(req.mode==='navigate'){
    e.respondWith(new Promise(resolve=>{
      let done=false;
      const fromCache=()=>caches.match('index.html').then(r=>{if(!done&&r){done=true;resolve(r);}});
      const t=setTimeout(fromCache,2000);
      fetch(req,{cache:'no-cache'}).then(res=>{clearTimeout(t);caches.open(CACHE).then(c=>c.put('index.html',res.clone()));if(!done){done=true;resolve(res);}})
        .catch(()=>{clearTimeout(t);fromCache().then(()=>{if(!done){done=true;resolve(Response.error());}});});
    }));
    return;
  }
  // Everything else (logo, fonts, icons) rarely changes: cache first
  e.respondWith(caches.match(req,{ignoreSearch:true}).then(hit=>hit||fetch(req).then(res=>{if(res.ok){const c=res.clone();caches.open(CACHE).then(x=>x.put(req,c));}return res;})));
});
