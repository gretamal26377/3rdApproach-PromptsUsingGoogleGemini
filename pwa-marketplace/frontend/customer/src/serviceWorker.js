// Service worker setup (PWA functionality)
// Issue: I don't see self.addEventListener('install/fetch'...) to precache/use initial resources

/**
 * Determines if the current hostname corresponds to a localhost environment.
 *
 * This function checks if the hostname is one of the following:
 * - 'localhost'
 * - '[::1]' (IPv6 loopback address)
 * - An IPv4 address in the 127.x.x.x range (IPv4 loopback addresses)
 *
 * @constant {boolean} isLocalhost - True if the current hostname is a localhost address, false otherwise.
 */
const isLocalhost = Boolean(
  window.location.hostname === "localhost" ||
    window.location.hostname === "[::1]" ||
    window.location.hostname.match(
      /^127\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
      // /^127(?:\.(0|[1-9][0-9]{0,2})){3}$/ # This regex was wrong, it accepted for example 127.999.999.999 as valid. Modified it through vsCode Copilot
    )
);

/**
 * Registers a Service Worker to enable Progressive Web App (PWA) features.
 * This function checks if the environment is production and if the browser supports service workers.
 * It then registers the service worker to enable offline capabilities and cache-first behavior
 *
 * @param {Object} config - Optional configuration object for the Service Worker, meaning it might come or not
 * @returns {void}
 */
export function register(config) {
  // Proceed if in production environment and Service Workers are supported by the browser
  if (process.env.NODE_ENV === "production" && "serviceWorker" in navigator) {
    /**
     * Notice: "@" starting lines are JSDoc comments, which are used to document code and can also be used by documentation generators to produce API docs for your code
     * @const {URL} publicUrl - Creates a URL object representing the application's public URL, using environment variable PUBLIC_URL and the current window location as the base URL
     * PUBLIC_URL is typically set to the root of the application when running npm run build or npm start
     */
    const publicUrl = new URL(process.env.PUBLIC_URL, window.location.href);
    // Check if the Service Worker is being served from the same origin as the application.
    // This is important for security reasons, as Service Workers can only control pages that are served from the same origin
    if (publicUrl.origin !== window.location.origin) {
      return;
    }

    // The code inside the arrow function will be executed when the page has finished loading
    window.addEventListener("load", () => {
      // swUrl: Tells the browser where to find the Service Worker file
      const swUrl = `${process.env.PUBLIC_URL}/serviceWorker.js`;
      /**
       * Primary reason for having an isLocalhost check is to handle Service Worker registration differently in Development and Production environments.
       * During development, you're constantly making changes to your code. Service Workers can sometimes interfere with this process by caching older versions of your files. This can lead to unexpected behavior and make debugging difficult.
       * In Production, you want the Service Worker to be as reliable as possible. You want it to cache your assets and serve them even when the user is offline.
       * Caching Issues on Localhost: Browsers can sometimes be aggressive with Service Worker caching, especially on localhost. This can make it difficult to see the latest changes you've made to your application.
       * To avoid these caching issues, it's common to bypass the Service Worker or use a more lenient caching strategy during development
       */
      if (isLocalhost) {
        checkValidServiceWorker(swUrl, config);
      } else {
        registerValidSW(swUrl, config);
      }
    });
  } else {
    console.log(
      "Service Workers are not supported in this browser or it's been disabled to be in Development Mode"
    );
  }
}

/**
 * Registers a Service Worker at the given URL and handles updates and installation events
 * @param {string} swUrl - The URL of the Service Worker
 * @param {Object} config - An object containing optional callbacks for onUpdate and onSuccess
 * @param {Function} config.onUpdate - A callback function to be called when a new Service Worker is available. It receives the Service Worker registration object as an argument
 * @param {Function} config.onSuccess - A callback function to be called when the Service Worker is successfully installed. It receives the Service Worker registration object as an argument
 */
function registerValidSW(swUrl, config) {
  navigator.serviceWorker
    .register(swUrl)
    .then((registration) => {
      // This event is fired when a Service Worker is successfully registered for the 1st time and when it's updated
      registration.onupdatefound = () => {
        // installingWorker is a reference to the Service Worker that is currently being installed or updated.
        // This reference can be used to listen for changes in the Service Worker's state, such as when it's "installed", "activated", or fails to install
        const installingWorker = registration.installing;
        if (installingWorker == null) {
          // This should never happen if runtime reach this point, but it's a good practice to handle this case
          return;
        }
        // This event is fired when the state of the Service Worker changes. Eg: From Installing to Installed
        installingWorker.onstatechange = () => {
          if (installingWorker.state === "installed") {
            // Checks if there is an active previous Service Worker already controlling the page
            if (navigator.serviceWorker.controller) {
              // If there's previous Service Worker controller, it means this is a Service Worker update
              console.log(
                "New content is available and will be used when all " +
                  "tabs for this page are closed. See https://cra.link/PWA"
              );

              if (config && config.onUpdate) {
                /**
                 * This callback is called if the new Service Worker was successfully registered and a config object was provided.
                 * This object allows the application to perform custom actions when the Service Worker is successfully installed, such as displaying a notification to the user to reload the page in order to get new Service Worker content
                 */
                config.onUpdate(registration); // Pass the registration object to the callback
              }
              // If there's no previous controller, it means it's the first Service Worker installation
            } else {
              console.log(
                "Content was cached during previous Service Worker registration for offline use for the first time"
              );

              if (config && config.onSuccess) {
                /**
                 * This callback is called if the Service Worker was successfully registered and a config object was provided.
                 * This object allows the application to perform custom actions when the Service Worker is successfully installed, such as displaying a message for the user indicating it
                 */
                config.onSuccess(registration);
              }
            }
          } else if (installingWorker.state === "redundant") {
            console.error(
              "Service Worker became redundant. Installation failed or was replaced before completing"
            );
          } else {
            console.log(
              `Service Worker state changed to: ${installingWorker.state}`
            );
          }
        };
      };
    })
    .catch((error) => {
      console.error("Error during Service Worker registration:", error);
    });
}

/**
 * @function checkValidServiceWorker
 * @description Checks if the Service Worker at the given URL is valid.
 * If the service worker is not valid, it unregisters any existing Service Workers
 * @param {string} swUrl - The URL of the Service Worker
 * @param {object} config - Configuration options
 */
function checkValidServiceWorker(swUrl, config) {
  // Check if the Service Worker URL is valid by making a request to it
  fetch(swUrl, {
    headers: { "Service-Worker": "script" },
  })
    .then((response) => {
      const contentType = response.headers.get("content-type");

      if (!contentType || !contentType.includes("javascript")) {
        console.warn(
          "A Service Worker is expected to be found at " +
            `${swUrl}. Please check that this is the correct URL`
        );
        unregister();
        return;
      }
      console.log(
        "Service Worker found at " +
          `${swUrl} is valid to be registered when in Production Mode`
      );
    })
    .catch(() => {
      console.log(
        "Service Worker could not be fetched. This may be due to many reason such as no internet connection, file missing or corrupted, etc."
      );
    });
}

/**
 * Unregisters the Service Worker
 */
export function unregister() {
  if ("serviceWorker" in navigator) {
    // Before unregistering, we need to check if there's a Service Worker registered
    // and it has an unregister method in order to avoid errors
    if (registration && registration.unregister) {
      registration
        .unregister()
        .then(() => {
          console.log("Service Worker unregistered");
        })
        .catch((error) => {
          console.error("Error unregistering Service Worker:", error);
        });
    } else {
      console.log("There's no Service Worker to unregister");
    }
  }
}
