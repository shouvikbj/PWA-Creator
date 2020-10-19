//install service worker
self.addEventListener("install", (evt) => {
  console.log("service worker has been installed");
});

//activation of service worker
self.addEventListener("install", (evt) => {
  console.log("service worker has is activated");
});

//fetch event
self.addEventListener("fetch", (evt) => {
  //console.log('fetch event', evt);
});
