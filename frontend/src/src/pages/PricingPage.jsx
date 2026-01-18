import { useEffect } from 'react';
import { Check, X, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import Layout from '@/components/Layout';
import SEO from '@/components/SEO';
import analytics from '@/lib/analytics';

export default function PricingPage() {
  useEffect(() => {
    analytics.trackPageView('Pricing');
  }, []);

  const plans = [
    {
      name: 'Starter',
      description: 'Perfekt für Hotels mit bis zu 3 Properties',
      price: '€299',
      priceDetail: 'Einmalige Setup-Gebühr',
      popular: false,
      features: [
        { text: 'Bis zu 3 Properties inklusive', included: true },
        { text: 'Digitale Gästemappen', included: true },
        { text: 'QR-Code Generator', included: true },
        { text: 'KI-Assistent (GPT-4)', included: true },
        { text: 'Basis Analytics', included: true },
        { text: 'Email Support', included: true },
        { text: 'Mobile App Zugang', included: true },
        { text: 'Erweiterte Analytics', included: false },
        { text: 'Priority Support', included: false },
        { text: 'Whitelabel Option', included: false },
      ]
    },
    {
      name: 'Professional',
      description: 'Für wachsende Unternehmen mit mehreren Properties',
      price: '€19.90',
      priceDetail: 'pro Property/Monat',
      priceNote: 'Erste 3 Properties gratis, ab der 4. Property €19.90/Monat',
      popular: true,
      features: [
        { text: 'Alles aus Starter', included: true },
        { text: 'Unbegrenzte Properties', included: true },
        { text: 'Upselling-System', included: true },
        { text: 'Paket-Management', included: true },
        { text: 'Affiliate-Programm', included: true },
        { text: 'DATEV Export', included: true },
        { text: 'Erweiterte Analytics', included: true },
        { text: 'Priority Email Support', included: true },
        { text: '10% Admin-Provision auf Upsells', included: true },
        { text: 'Whitelabel Option', included: false },
        { text: 'Dedizierter Account Manager', included: false },
      ]
    },
    {
      name: 'Enterprise',
      description: 'Für große Hotel-Ketten und Property-Management',
      price: 'Individuell',
      priceDetail: '',
      popular: false,
      features: [
        { text: 'Alles aus Professional', included: true },
        { text: 'Whitelabel-Option', included: true },
        { text: 'Custom Integrationen', included: true },
        { text: 'Dedizierter Account Manager', included: true },
        { text: '24/7 Priority Support', included: true },
        { text: 'SLA Garantie', included: true },
        { text: 'Schulungen & Onboarding', included: true },
        { text: 'API Zugang', included: true },
        { text: 'Individuelle Features', included: true },
        { text: 'Volume Rabatte', included: true },
      ]
    }
  ];

  const additionalServices = [
    {
      name: 'Premium Support',
      price: '€49/Monat',
      features: ['24/7 Phone Support', 'Response < 2h', 'Dedizierter Slack Channel']
    },
    {
      name: 'Custom Integrationen',
      price: '€299 einmalig',
      features: ['PMS Integration', 'Custom API', 'Technische Beratung']
    },
    {
      name: 'Whitelabel',
      price: '€199/Monat',
      features: ['Eigenes Branding', 'Custom Domain', 'Logo & Farben']
    }
  ];

  const faqs = [
    {
      question: 'Wie wird die Setup-Gebühr berechnet?',
      answer: 'Die einmalige Setup-Gebühr von €299 deckt die Einrichtung Ihres Accounts, die Integration und das initiale Onboarding ab. Diese Gebühr wird nur einmal fällig.'
    },
    {
      question: 'Was passiert nach den ersten 3 Properties?',
      answer: 'Die ersten 3 Properties sind im Setup-Preis enthalten. Ab der 4. Property zahlen Sie €19.90 pro Property und Monat. Sie können jederzeit Properties hinzufügen oder entfernen.'
    },
    {
      question: 'Gibt es versteckte Kosten?',
      answer: 'Nein! Unsere Preisgestaltung ist vollständig transparent. Die einzigen Kosten sind die Setup-Gebühr und die monatliche Gebühr pro Property (ab der 4. Property). Bei Upsells behalten wir 10% Provision.'
    },
    {
      question: 'Kann ich jederzeit kündigen?',
      answer: 'Ja, Sie können monatlich kündigen. Es gibt keine langfristigen Verträge oder Kündigungsfristen. Ihre Daten bleiben auch nach der Kündigung 90 Tage gespeichert.'
    },
    {
      question: 'Bieten Sie eine Testphase an?',
      answer: 'Ja! Sie können Welcome Link 14 Tage kostenlos testen mit vollem Funktionsumfang. Keine Kreditkarte erforderlich.'
    }
  ];

  return (
    <Layout>
      <SEO 
        title="Preise | Welcome Link - Digitale Gästekommunikation"
        description="Einfache, transparente Preise. Keine versteckten Kosten. Starten Sie noch heute mit Welcome Link."
      />
      
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 py-12 md:py-20 text-center">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-black dark:text-white mb-6">
            Einfache, transparente Preise
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-4 max-w-2xl mx-auto">
            Keine versteckten Kosten. Keine langfristigen Verträge. Starten Sie noch heute mit Welcome Link.
          </p>
          <p className="text-[#F27C2C] font-medium">14 Tage kostenlos testen</p>
        </section>

        {/* Pricing Cards */}
        <section className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, idx) => (
              <div 
                key={idx} 
                className={`bg-white dark:bg-slate-800 rounded-2xl p-8 relative ${
                  plan.popular ? 'ring-2 ring-[#F27C2C] shadow-xl' : 'border border-gray-200 dark:border-slate-700'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-[#F27C2C] text-white text-sm font-medium rounded-full">
                    🏆 Am beliebtesten
                  </div>
                )}
                
                <h3 className="text-xl font-bold text-black dark:text-white mb-2">{plan.name}</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-6">{plan.description}</p>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold text-black dark:text-white">{plan.price}</span>
                  {plan.priceDetail && (
                    <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">{plan.priceDetail}</span>
                  )}
                </div>
                
                {plan.priceNote && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-6">{plan.priceNote}</p>
                )}
                
                <Link 
                  to="/register"
                  className={`block w-full py-3 rounded-lg font-medium text-center mb-6 transition-colors ${
                    plan.popular
                      ? 'bg-[#F27C2C] text-white hover:bg-[#E06B1B]'
                      : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600'
                  }`}
                >
                  {plan.name === 'Enterprise' ? 'Kontakt aufnehmen' : plan.popular ? 'Beliebteste Wahl' : 'Jetzt starten'}
                </Link>
                
                <ul className="space-y-3">
                  {plan.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-start gap-3">
                      {feature.included ? (
                        <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-gray-300 dark:text-gray-600 flex-shrink-0 mt-0.5" />
                      )}
                      <span className={feature.included ? 'text-gray-700 dark:text-gray-300' : 'text-gray-400 dark:text-gray-500'}>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Additional Services */}
        <section className="max-w-7xl mx-auto px-4 py-16">
          <h2 className="text-2xl md:text-3xl font-bold text-center text-black dark:text-white mb-12">
            Zusätzliche Services
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {additionalServices.map((service, idx) => (
              <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                <h3 className="text-lg font-bold text-black dark:text-white mb-2">{service.name}</h3>
                <p className="text-2xl font-bold text-[#F27C2C] mb-4">{service.price}</p>
                <ul className="space-y-2">
                  {service.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-center gap-2 text-gray-600 dark:text-gray-400 text-sm">
                      <Check className="h-4 w-4 text-green-500" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* FAQs */}
        <section className="max-w-4xl mx-auto px-4 py-16">
          <h2 className="text-2xl md:text-3xl font-bold text-center text-black dark:text-white mb-12">
            Häufig gestellte Fragen
          </h2>
          <div className="space-y-6">
            {faqs.map((faq, idx) => (
              <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                <h3 className="text-lg font-semibold text-black dark:text-white mb-2">{faq.question}</h3>
                <p className="text-gray-600 dark:text-gray-400">{faq.answer}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-[#F27C2C] text-white py-20">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Bereit durchzustarten?
            </h2>
            <p className="text-xl mb-8">
              Testen Sie Welcome Link 14 Tage kostenlos. Keine Kreditkarte erforderlich.
            </p>
            <Link 
              to="/register" 
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-[#F27C2C] rounded-lg hover:bg-gray-100 font-semibold transition-colors"
            >
              Jetzt kostenlos testen
              <ChevronRight className="h-5 w-5" />
            </Link>
          </div>
        </section>
      </div>
    </Layout>
  );
}
