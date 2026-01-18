/**
 * Analytics Tracking Utilities
 * Wrapper für PostHog Events mit Type Safety
 */

// Check if PostHog is available
const isPostHogAvailable = () => {
  return typeof window !== 'undefined' && window.posthog;
};

/**
 * Track custom events
 */
export const trackEvent = (eventName, properties = {}) => {
  if (isPostHogAvailable()) {
    window.posthog.capture(eventName, properties);
  }
};

/**
 * Track page views
 */
export const trackPageView = (pageName, properties = {}) => {
  trackEvent('$pageview', {
    page_name: pageName,
    ...properties
  });
};

/**
 * Track conversions (e.g., sign-ups, purchases)
 */
export const trackConversion = (conversionType, value = null, properties = {}) => {
  trackEvent('conversion', {
    conversion_type: conversionType,
    value: value,
    ...properties
  });
};

/**
 * Track user actions
 */
export const trackAction = (actionName, category, properties = {}) => {
  trackEvent('user_action', {
    action: actionName,
    category: category,
    ...properties
  });
};

/**
 * Track errors
 */
export const trackError = (errorMessage, errorStack = null, properties = {}) => {
  trackEvent('error', {
    error_message: errorMessage,
    error_stack: errorStack,
    ...properties
  });
};

// Specific tracking functions for common events
export const analytics = {
  // Navigation
  clickedCTA: (ctaName, location) => 
    trackAction('cta_clicked', 'navigation', { cta_name: ctaName, location }),
  
  // Resources Page
  viewedGuide: (guideTitle, category) => 
    trackAction('guide_viewed', 'content', { guide_title: guideTitle, category }),
  
  clickedVideo: (videoTitle) => 
    trackAction('video_clicked', 'content', { video_title: videoTitle }),
  
  downloadedTemplate: (templateTitle, templateType) => 
    trackAction('template_downloaded', 'content', { 
      template_title: templateTitle, 
      template_type: templateType 
    }),
  
  viewedCaseStudy: (propertyName, location) => 
    trackAction('case_study_viewed', 'content', { 
      property_name: propertyName, 
      location 
    }),
  
  // Pricing & Conversion
  viewedPricingPlan: (planName) => 
    trackAction('pricing_plan_viewed', 'pricing', { plan_name: planName }),
  
  clickedPricingCTA: (planName, price) => 
    trackConversion('pricing_cta_clicked', price, { plan_name: planName }),
  
  startedRegistration: () => 
    trackConversion('registration_started'),
  
  completedRegistration: (planName = null) => 
    trackConversion('registration_completed', null, { plan_name: planName }),
  
  // Features
  viewedFeature: (featureName, category) => 
    trackAction('feature_viewed', 'features', { 
      feature_name: featureName, 
      category 
    }),
  
  // Integrations
  viewedIntegration: (integrationName) => 
    trackAction('integration_viewed', 'integrations', { 
      integration_name: integrationName 
    }),
  
  clickedIntegrationCTA: (integrationName) => 
    trackAction('integration_cta_clicked', 'integrations', { 
      integration_name: integrationName 
    }),
  
  // Support & Contact
  clickedSupport: (supportType, location) => 
    trackAction('support_clicked', 'support', { 
      support_type: supportType, 
      location 
    }),
  
  submittedContactForm: (formType) => 
    trackConversion('contact_form_submitted', null, { form_type: formType }),
  
  // Dark Mode
  toggledDarkMode: (enabled) => 
    trackAction('dark_mode_toggled', 'settings', { enabled }),
  
  // Errors
  encounteredError: (errorType, errorMessage) => 
    trackError(errorMessage, null, { error_type: errorType }),

  // Page Views
  trackPageView: (pageName, properties = {}) => trackPageView(pageName, properties),

  // QR Code
  generatedQRCode: (url, variant) =>
    trackAction('qr_code_generated', 'qr', { url, variant })
};

export default analytics;
