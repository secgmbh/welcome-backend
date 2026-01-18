/**
 * PWA Installation & Service Worker Registration
 */

// Check if service workers are supported
export const isPWASupported = () => {
  return 'serviceWorker' in navigator;
};

// Register Service Worker
export const registerServiceWorker = async () => {
  if (!isPWASupported()) {
    console.log('Service Workers not supported');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/service-worker.js', {
      scope: '/'
    });

    console.log('Service Worker registered:', registration);

    // Check for updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;
      console.log('New Service Worker found');

      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          // New service worker available
          console.log('New content available, please refresh');
          
          // Notify user about update
          if (window.confirm('Neue Version verfügbar! Seite neu laden?')) {
            newWorker.postMessage({ type: 'SKIP_WAITING' });
            window.location.reload();
          }
        }
      });
    });

    return registration;
  } catch (error) {
    console.error('Service Worker registration failed:', error);
    return null;
  }
};

// Unregister Service Worker
export const unregisterServiceWorker = async () => {
  if (!isPWASupported()) return;

  const registration = await navigator.serviceWorker.ready;
  await registration.unregister();
  console.log('Service Worker unregistered');
};

// Check if app is installed as PWA
export const isInstalledPWA = () => {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true
  );
};

// PWA Install Prompt
let deferredPrompt = null;

export const setupInstallPrompt = () => {
  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent default install prompt
    e.preventDefault();
    deferredPrompt = e;
    console.log('Install prompt ready');
    
    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('pwa-installable'));
  });

  window.addEventListener('appinstalled', () => {
    console.log('PWA installed');
    deferredPrompt = null;
    
    // Track installation
    if (window.posthog) {
      window.posthog.capture('pwa_installed');
    }
  });
};

export const showInstallPrompt = async () => {
  if (!deferredPrompt) {
    console.log('Install prompt not available');
    return false;
  }

  // Show install prompt
  deferredPrompt.prompt();
  
  // Wait for user response
  const { outcome } = await deferredPrompt.userChoice;
  console.log(`Install prompt outcome: ${outcome}`);
  
  deferredPrompt = null;
  return outcome === 'accepted';
};

export const canInstallPWA = () => {
  return deferredPrompt !== null;
};

// Push Notifications
export const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    console.log('Notifications not supported');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  return false;
};

export const subscribeToPushNotifications = async (registration) => {
  try {
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: process.env.REACT_APP_VAPID_PUBLIC_KEY
    });

    console.log('Push subscription:', subscription);
    
    // Send subscription to server
    await fetch('/api/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription)
    });

    return subscription;
  } catch (error) {
    console.error('Push subscription failed:', error);
    return null;
  }
};

// Offline Detection
export const setupOfflineDetection = () => {
  const updateOnlineStatus = () => {
    const isOnline = navigator.onLine;
    document.body.classList.toggle('offline', !isOnline);
    
    // Dispatch event
    window.dispatchEvent(new CustomEvent('online-status-changed', { 
      detail: { isOnline } 
    }));

    if (isOnline) {
      console.log('Back online');
    } else {
      console.log('Offline');
    }
  };

  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  
  // Initial check
  updateOnlineStatus();
};

// Initialize PWA features
export const initPWA = async () => {
  // Register service worker
  const registration = await registerServiceWorker();
  
  // Setup install prompt
  setupInstallPrompt();
  
  // Setup offline detection
  setupOfflineDetection();
  
  // Request notification permission if already installed
  if (isInstalledPWA() && registration) {
    await requestNotificationPermission();
    await subscribeToPushNotifications(registration);
  }

  return registration;
};

export default {
  isPWASupported,
  registerServiceWorker,
  unregisterServiceWorker,
  isInstalledPWA,
  setupInstallPrompt,
  showInstallPrompt,
  canInstallPWA,
  requestNotificationPermission,
  subscribeToPushNotifications,
  setupOfflineDetection,
  initPWA
};
