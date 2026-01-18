import { Helmet } from 'react-helmet-async';

/**
 * SEO Component für bessere Search Engine Optimization
 */
export default function SEO({ 
  title = "Welcome Link - Digitale Gästemappe für Hotels",
  description = "Professionelle digitale Gästemappe für Hotels und Ferienwohnungen. Weniger Rückfragen, mehr Umsatz durch intelligente Upsells.",
  keywords = "digitale Gästemappe, Hotel Software, Upselling, QR-Code, Welcome Link",
  ogImage = "https://www.welcome-link.de/og-image.jpg",
  ogType = "website",
  canonical,
  structuredData
}) {
  const url = canonical || window.location.href;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <link rel="canonical" href={url} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:site_name" content="Welcome Link" />

      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={url} />
      <meta property="twitter:title" content={title} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={ogImage} />

      {/* Structured Data (JSON-LD) */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
}

/**
 * Predefined Structured Data Schemas
 */
export const schemas = {
  // Organization Schema
  organization: {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Welcome Link",
    "applicationCategory": "BusinessApplication",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "EUR"
    },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.8",
      "ratingCount": "127"
    },
    "description": "Digitale Gästemappe für Hotels und Ferienwohnungen mit intelligentem Upselling-System"
  },

  // Product Schema (for Pricing Plans)
  product: (planName, price, currency = "EUR") => ({
    "@context": "https://schema.org",
    "@type": "Product",
    "name": planName,
    "description": `Welcome Link ${planName} Plan für Hotels und Ferienwohnungen`,
    "brand": {
      "@type": "Brand",
      "name": "Welcome Link"
    },
    "offers": {
      "@type": "Offer",
      "price": price,
      "priceCurrency": currency,
      "availability": "https://schema.org/InStock",
      "url": "https://www.welcome-link.de/pricing"
    }
  }),

  // FAQ Schema
  faq: (faqs) => ({
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  }),

  // Article Schema (for Guides/Resources)
  article: (title, description, author, datePublished, imageUrl) => ({
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": title,
    "description": description,
    "author": {
      "@type": "Person",
      "name": author
    },
    "datePublished": datePublished,
    "image": imageUrl,
    "publisher": {
      "@type": "Organization",
      "name": "Welcome Link",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.welcome-link.de/logo.png"
      }
    }
  }),

  // HowTo Schema (for Tutorials)
  howTo: (name, description, steps) => ({
    "@context": "https://schema.org",
    "@type": "HowTo",
    "name": name,
    "description": description,
    "step": steps.map((step, index) => ({
      "@type": "HowToStep",
      "position": index + 1,
      "name": step.name,
      "text": step.text,
      "url": step.url
    }))
  }),

  // Video Schema
  video: (name, description, thumbnailUrl, uploadDate, duration) => ({
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": name,
    "description": description,
    "thumbnailUrl": thumbnailUrl,
    "uploadDate": uploadDate,
    "duration": duration,
    "contentUrl": "https://www.welcome-link.de/videos",
    "embedUrl": "https://www.welcome-link.de/videos/embed"
  })
};
