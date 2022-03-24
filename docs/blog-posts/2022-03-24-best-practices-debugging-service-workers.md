# Best Practices for Debugging Service Workers

Service Workers are a great way to add offline functionality to your app, as well as speed up subsequent page loads (especially with the app shell model).

I recently encountered many issues while debugging, and to save myself and others the hassle, here are some of the best practices I recommend when debugging service workers.

## 1. Use Chrome Private Browsing

In private browsing, each time you close and open the window, all existing service workers are terminated. This avoids issues with older service workers persisting despite a new service worker available.

Firefox's private browsing, as of 24/3/22, does not support service workers.

## 2. Ensure `npm` modules are all up-to-date

I had a bizzare issue where the `update()` method of `ServiceWorkerRegistration` would refuse to update, if it encountered a single failed network request for the `service-worker.js` file. After spending a lot of time trying `127.0.0.1`, `localhost`, and switching between WSL and Windows, an update of the `node_modules` folder fixed everything.