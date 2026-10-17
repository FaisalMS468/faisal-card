const CACHE='faisal-card-v3';
const FILES=['./','index.html','logo.png','manifest.webmanifest','Faisal-Alshammari-ar.vcf','Faisal-Alshammari-en.vcf','icons/apple-touch-icon.png','icons/icon-192.png','icons/icon-512.png',
  'assets/tajawal/Iura6YBj_oCad4k1nzSBC5xLhLFw4Q.woff2','assets/tajawal/Iura6YBj_oCad4k1nzGBC5xLhLE.woff2','assets/tajawal/Iurf6YBj_oCad4k1l4qkHrRpiZtK6GwN9w.woff2','assets/tajawal/Iurf6YBj_oCad4k1l4qkHrFpiZtK6Gw.woff2'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
// Serve from cache instantly, refresh the cache in the background; updates show on the next open
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(caches.open(CACHE).then(async c=>{
    const hit=await c.match(e.request,{ignoreSearch:true});
    const net=fetch(e.request).then(res=>{if(res.ok)c.put(e.request,res.clone());return res;}).catch(()=>hit);
    if(hit){e.waitUntil(net);return hit;}
    return net;
  }));
});
