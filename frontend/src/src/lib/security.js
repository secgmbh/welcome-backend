/**
 * Content Security Policy Configuration
 */

export const CSP_DIRECTIVES = {
  defaultSrc: ["'self'"],
  scriptSrc: [
    "'self'",
    "'unsafe-inline'", // Required for React
    "'unsafe-eval'", // Required for development
    "https://us.i.posthog.com",
    "https://us-assets.i.posthog.com"
  ],
  styleSrc: [
    "'self'",
    "'unsafe-inline'", // Required for styled-components/emotion
    "https://fonts.googleapis.com"
  ],
  fontSrc: [
    "'self'",
    "https://fonts.gstatic.com",
    "data:"
  ],
  imgSrc: [
    "'self'",
    "data:",
    "https:",
    "https://images.unsplash.com",
    "https://www.welcome-link.de"
  ],
  connectSrc: [
    "'self'",
    "https://us.i.posthog.com",
    process.env.REACT_APP_BACKEND_URL || "http://localhost:8000"
  ],
  frameSrc: ["'none'"],
  objectSrc: ["'none'"],
  baseUri: ["'self'"],
  formAction: ["'self'"],
  frameAncestors: ["'none'"],
  upgradeInsecureRequests: []
};

/**
 * Generate CSP header string
 */
export const generateCSPHeader = () => {
  return Object.entries(CSP_DIRECTIVES)
    .map(([directive, sources]) => {
      const kebabDirective = directive.replace(/([A-Z])/g, '-$1').toLowerCase();
      return sources.length > 0
        ? `${kebabDirective} ${sources.join(' ')}`
        : kebabDirective;
    })
    .join('; ');
};

/**
 * Apply CSP via meta tag (fallback for static hosting)
 */
export const applyCSP = () => {
  const meta = document.createElement('meta');
  meta.httpEquiv = 'Content-Security-Policy';
  meta.content = generateCSPHeader();
  document.head.appendChild(meta);
};

/**
 * Security Headers Configuration for Render.com
 * Add these to render.yaml:
 * 
 * headers:
 *   - path: /*
 *     value:
 *       X-Frame-Options: DENY
 *       X-Content-Type-Options: nosniff
 *       X-XSS-Protection: 1; mode=block
 *       Referrer-Policy: strict-origin-when-cross-origin
 *       Permissions-Policy: geolocation=(), microphone=(), camera=()
 *       Content-Security-Policy: [use generateCSPHeader() output]
 */

export const SECURITY_HEADERS = {
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
};

export default {
  CSP_DIRECTIVES,
  generateCSPHeader,
  applyCSP,
  SECURITY_HEADERS
};
