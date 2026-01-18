import { useState, useEffect } from 'react';
import { BookOpen, QrCode, Bot, Sparkles, TrendingUp, Settings, Check } from 'lucide-react';
import Layout from '@/components/Layout';
import SEO from '@/components/SEO';
import analytics from '@/lib/analytics';

export default function FeaturesPage() {
  const [activeTab, setActiveTab] = useState('communication');

  useEffect(() => {
    analytics.trackPageView('Features');
  }, []);

  const stats = [
    { value: '70%', label: 'Weniger Rückfragen' },
    { value: '24/7', label: 'KI-Support' },
    { value: '38%', label: 'Mehr Upsells' },
    { value: '<2min', label: 'Setup-Zeit' }
  ];

  const tabs = [
    { id: 'communication', label: 'Gästekommunikation' },
    { id: 'revenue', label: 'Umsatzsteigerung' },
    { id: 'management', label: 'Verwaltung' }
  ];

  const features = {
    communication: [
      {
        icon: BookOpen,
        title: 'Interaktive Gästemappen',
        description: 'Erstellen Sie ansprechende digitale Gästemappen mit Bildern, Videos und wichtigen Informationen für Ihre Gäste.',
        benefits: ['Mehrsprachig (DE/EN)', 'Unbegrenzte Inhalte', 'Einfache Aktualisierung']
      },
      {
        icon: QrCode,
        title: 'QR-Code System',
        description: 'Generieren Sie einzigartige QR-Codes für jede Unterkunft. Gäste scannen und erhalten sofort alle relevanten Informationen.',
        benefits: ['Automatische Generierung', 'Trackbare Scans', 'Print-optimiert']
      },
      {
        icon: Bot,
        title: 'KI-Assistent',
        description: 'Intelligenter Chat-Bot beantwortet Gästefragen 24/7 basierend auf Ihren FAQs und property-spezifischen Informationen.',
        benefits: ['GPT-4 powered', 'Automatisch trainiert', '24/7 verfügbar']
      }
    ],
    revenue: [
      {
        icon: TrendingUp,
        title: 'Upselling-System',
        description: 'Verkaufen Sie Zusatzleistungen wie Frühstück, Spa-Behandlungen oder Late-Checkout automatisch an Ihre Gäste.',
        benefits: ['Automatische Empfehlungen', 'Einfache Buchung', 'Mehr Umsatz']
      },
      {
        icon: Sparkles,
        title: 'Paket-Management',
        description: 'Erstellen Sie attraktive Pakete und Bundles, die Ihren Gästen Mehrwert bieten.',
        benefits: ['Flexible Pakete', 'Rabatt-Optionen', 'Saisonale Angebote']
      }
    ],
    management: [
      {
        icon: Settings,
        title: 'Property-Verwaltung',
        description: 'Verwalten Sie alle Ihre Properties zentral an einem Ort mit übersichtlichem Dashboard.',
        benefits: ['Multi-Property Support', 'Zentrale Verwaltung', 'Übersichtliches Dashboard']
      }
    ]
  };

  const integrations = [
    { name: 'Airbnb', logo: '🏠' },
    { name: 'Booking.com', logo: '📗' },
    { name: 'Stripe', logo: '💳' },
    { name: 'DATEV', logo: '📊' },
    { name: 'Google Analytics', logo: '📈' }
  ];

  return (
    <Layout>
      <SEO 
        title="Features | Welcome Link - Digitale Gästekommunikation"
        description="Entdecken Sie alle Features von Welcome Link: Digitale Gästemappen, QR-Codes, KI-Assistent und mehr."
      />
      
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 py-12 md:py-20">
          <div className="text-center mb-12">
            <p className="text-[#F27C2C] font-medium mb-2">Alle Features im Überblick</p>
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-black dark:text-white mb-6">
              Alles, was Sie für erfolgreiche<br />Gästekommunikation brauchen
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Welcome Link vereint digitale Gästemappen, Upselling-Tools und intelligente Automatisierung in einer benutzerfreundlichen Plattform.
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
            {stats.map((stat, idx) => (
              <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center shadow-sm">
                <p className="text-3xl md:text-4xl font-bold text-[#F27C2C] mb-1">{stat.value}</p>
                <p className="text-gray-600 dark:text-gray-400 text-sm">{stat.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features Tabs */}
        <section className="max-w-7xl mx-auto px-4 py-12">
          {/* Tab Navigation */}
          <div className="flex justify-center gap-2 mb-12">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 rounded-lg font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-[#F27C2C] text-white'
                    : 'bg-white dark:bg-slate-800 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-center text-black dark:text-white mb-4">
              {activeTab === 'communication' && 'Digitale Gästekommunikation'}
              {activeTab === 'revenue' && 'Umsatzsteigerung'}
              {activeTab === 'management' && 'Verwaltung'}
            </h2>
            <p className="text-center text-gray-600 dark:text-gray-400 mb-8">
              {activeTab === 'communication' && 'Reduzieren Sie Rückfragen um bis zu 70%'}
              {activeTab === 'revenue' && 'Steigern Sie Ihren Umsatz mit intelligenten Tools'}
              {activeTab === 'management' && 'Verwalten Sie alles an einem Ort'}
            </p>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features[activeTab]?.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-slate-700">
                  <div className="w-12 h-12 bg-[#F27C2C]/10 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="h-6 w-6 text-[#F27C2C]" />
                  </div>
                  <h3 className="text-xl font-semibold text-black dark:text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">{feature.description}</p>
                  <ul className="space-y-2">
                    {feature.benefits.map((benefit, bidx) => (
                      <li key={bidx} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                        <Check className="h-4 w-4 text-green-500" />
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </section>

        {/* Integrations Section */}
        <section className="max-w-7xl mx-auto px-4 py-16">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 md:p-12 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-black dark:text-white mb-4">
              Nahtlose Integration
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
              Welcome Link integriert sich mit Ihren bestehenden Systemen. Von PMS über Buchungssysteme bis hin zu Payment-Providern.
            </p>
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              {integrations.map((integration, idx) => (
                <div key={idx} className="flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-slate-700 rounded-lg">
                  <span className="text-2xl">{integration.logo}</span>
                  <span className="text-gray-700 dark:text-gray-300 font-medium">{integration.name}</span>
                </div>
              ))}
            </div>
            <a href="/integrations" className="text-[#F27C2C] font-medium hover:underline">
              Alle Integrationen ansehen →
            </a>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-[#F27C2C] text-white py-20">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Bereit, Ihre Gästekommunikation zu revolutionieren?
            </h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto">
              Starten Sie noch heute mit Welcome Link und erleben Sie den Unterschied
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="/register" 
                className="px-8 py-4 bg-white text-[#F27C2C] rounded-lg hover:bg-gray-100 font-semibold transition-colors"
              >
                Jetzt kostenlos starten
              </a>
              <a 
                href="/login" 
                className="px-8 py-4 border-2 border-white text-white rounded-lg hover:bg-white/10 font-semibold transition-colors"
              >
                Demo ansehen
              </a>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
