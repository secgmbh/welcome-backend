/**
 * Performance Optimization Utilities
 */

/**
 * Lazy load images with Intersection Observer
 */
export const setupLazyLoading = () => {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          observer.unobserve(img);
        }
      });
    });

    document.querySelectorAll('img.lazy').forEach(img => {
      imageObserver.observe(img);
    });
  }
};

/**
 * Debounce function for performance
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function for performance
 */
export const throttle = (func, limit = 100) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * Preload critical assets
 */
export const preloadAssets = (urls) => {
  urls.forEach(url => {
    const link = document.createElement('link');
    link.rel = 'preload';
    
    if (url.match(/\.(woff2|woff|ttf|otf)$/)) {
      link.as = 'font';
      link.type = 'font/' + url.split('.').pop();
      link.crossOrigin = 'anonymous';
    } else if (url.match(/\.(jpg|jpeg|png|webp|svg)$/)) {
      link.as = 'image';
    } else if (url.match(/\.(css)$/)) {
      link.as = 'style';
    } else if (url.match(/\.(js)$/)) {
      link.as = 'script';
    }
    
    link.href = url;
    document.head.appendChild(link);
  });
};

/**
 * Optimize images (convert to WebP if supported)
 */
export const getOptimizedImageUrl = (url, width, quality = 80) => {
  const supportsWebP = document.createElement('canvas').toDataURL('image/webp').indexOf('data:image/webp') === 0;
  
  // If using Unsplash or similar CDN
  if (url.includes('unsplash.com')) {
    return `${url}?w=${width}&q=${quality}&fm=${supportsWebP ? 'webp' : 'jpg'}&fit=crop`;
  }
  
  // If using Cloudinary
  if (url.includes('cloudinary.com')) {
    return url.replace('/upload/', `/upload/w_${width},q_${quality},f_${supportsWebP ? 'webp' : 'jpg'}/`);
  }
  
  return url;
};

/**
 * Measure performance metrics
 */
export const measurePerformance = () => {
  if (window.performance && window.performance.timing) {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    const connectTime = perfData.responseEnd - perfData.requestStart;
    const renderTime = perfData.domComplete - perfData.domLoading;

    const metrics = {
      pageLoadTime: pageLoadTime / 1000, // Convert to seconds
      connectTime: connectTime / 1000,
      renderTime: renderTime / 1000
    };

    console.log('Performance Metrics:', metrics);

    // Track with analytics
    if (window.posthog) {
      window.posthog.capture('page_performance', metrics);
    }

    return metrics;
  }
  
  return null;
};

/**
 * Track Core Web Vitals
 */
export const trackWebVitals = () => {
  // Largest Contentful Paint (LCP)
  const observeLCP = () => {
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      
      console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
      
      if (window.posthog) {
        window.posthog.capture('web_vital_lcp', {
          value: lastEntry.renderTime || lastEntry.loadTime
        });
      }
    }).observe({ entryTypes: ['largest-contentful-paint'] });
  };

  // First Input Delay (FID)
  const observeFID = () => {
    new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        const delay = entry.processingStart - entry.startTime;
        console.log('FID:', delay);
        
        if (window.posthog) {
          window.posthog.capture('web_vital_fid', { value: delay });
        }
      });
    }).observe({ entryTypes: ['first-input'] });
  };

  // Cumulative Layout Shift (CLS)
  const observeCLS = () => {
    let clsValue = 0;
    new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });
      
      console.log('CLS:', clsValue);
      
      if (window.posthog) {
        window.posthog.capture('web_vital_cls', { value: clsValue });
      }
    }).observe({ entryTypes: ['layout-shift'] });
  };

  if ('PerformanceObserver' in window) {
    observeLCP();
    observeFID();
    observeCLS();
  }
};

/**
 * Initialize all performance optimizations
 */
export const initPerformanceOptimizations = () => {
  // Lazy load images
  setupLazyLoading();
  
  // Measure page load performance
  window.addEventListener('load', () => {
    setTimeout(measurePerformance, 0);
    trackWebVitals();
  });
  
  // Preload critical assets
  preloadAssets([
    // Add your critical assets here
  ]);
};

export default {
  setupLazyLoading,
  debounce,
  throttle,
  preloadAssets,
  getOptimizedImageUrl,
  measurePerformance,
  trackWebVitals,
  initPerformanceOptimizations
};
