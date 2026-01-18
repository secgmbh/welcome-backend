import { Link } from 'react-router-dom';
import { Check, Moon, Sun, Sparkles, BookOpen, QrCode, TrendingUp, TestTube, Home, BarChart3, ChevronRight, Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import SEO from '@/components/SEO';
import analytics from '@/lib/analytics';

export default function HomePage() {
  const [isDark, setIsDark] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Features', href: '/features' },
    { name: 'Preise', href: '/pricing' },
    { name: 'Integrationen', href: '/integrations' },
    { name: 'Ressourcen', href: '/resources' },
  ];

  useEffect(() => {
    analytics.trackPageView('Homepage');
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const features = [
    {
      icon: BookOpen,
      title: 'Digitale Gästemappen',
      description: 'Interaktive Inhalte mit Bildern, Videos und Anleitungen'
    },
    {
      icon: QrCode,
      title: 'QR-Code-Generator',
      description: 'Individuelle QR-Codes für jeden Gast und jede Unterkunft'
    },
    {
      icon: TrendingUp,
      title: 'Upselling-System',
      description: 'Verkaufen Sie Extras automatisch und erhöhen Sie Ihren Umsatz'
    },
    {
      icon: TestTube,
      title: 'A/B-Testing',
      description: 'Testen Sie verschiedene Angebote und optimieren Sie'
    },
    {
      icon: Home,
      title: 'Airbnb-Integration',
      description: 'Automatischer Import von Listings und Buchungen'
    },
    {
      icon: BarChart3,
      title: 'Analytics',
      description: 'Detaillierte Einblicke in Ihre Performance'
    }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-slate-900">
      <SEO 
        title="Welcome Link - Digitale Gästekommunikation"
        description="Bis zu 70% weniger Gäste-Rückfragen. Erstellen Sie interaktive, digitale Gästemappen und steigern Sie Ihren Umsatz."
      />
      
      {/* Header - 1:1 wie welcome-link.de */}
      <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 py-4">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            {/* Logo - größer */}
            <Link to="/" className="flex items-center flex-shrink-0">
              <img 
                src="/logo.webp" 
                alt="Welcome Link" 
                className="h-12 w-auto"
              />
            </Link>

            {/* Desktop Navigation - mit grauem Border */}
            <div className="hidden md:flex items-center gap-3">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="px-5 py-2.5 rounded-lg text-sm font-medium bg-white dark:bg-slate-900 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-800 transition-all"
                >
                  {item.name}
                </Link>
              ))}
            </div>

            {/* Right Side - Dark Mode, Login, Register */}
            <div className="hidden md:flex items-center gap-4">
              {/* Dark Mode Toggle - einfaches Icon */}
              <button
                onClick={toggleDarkMode}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
                aria-label="Toggle dark mode"
              >
                {isDark ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </button>
              
              {/* Anmelden Button - Pill shape */}
              <Link 
                to="/login" 
                className="px-6 py-2.5 text-[#F27C2C] bg-white border-2 border-[#F27C2C] rounded-full font-medium hover:bg-[#FEF3E7] transition-colors"
              >
                Anmelden
              </Link>
              
              {/* Registrieren Button - Pill shape */}
              <Link 
                to="/register" 
                className="px-6 py-2.5 bg-[#F27C2C] text-white rounded-full font-medium hover:bg-[#E06B1B] transition-colors"
                onClick={() => analytics.clickedCTA('Register', 'Header')}
              >
                Registrieren
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="flex md:hidden items-center gap-3">
              <button
                onClick={toggleDarkMode}
                className="p-2 text-gray-500 dark:text-gray-400"
              >
                {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 text-gray-600 dark:text-gray-300"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden mt-4 py-4 border-t border-gray-200 dark:border-slate-700">
              <div className="flex flex-col gap-2">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="px-4 py-3 rounded-lg text-base font-medium text-gray-600 dark:text-gray-300 border border-gray-200 hover:bg-gray-50 dark:hover:bg-slate-800"
                  >
                    {item.name}
                  </Link>
                ))}
                <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-slate-700">
                  <Link 
                    to="/login" 
                    className="flex-1 px-4 py-3 text-center text-[#F27C2C] border-2 border-[#F27C2C] rounded-full font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Anmelden
                  </Link>
                  <Link 
                    to="/register" 
                    className="flex-1 px-4 py-3 text-center bg-[#F27C2C] text-white rounded-full font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Registrieren
                  </Link>
                </div>
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
          {/* Hero Section */}
          <section className="max-w-7xl mx-auto px-4 py-8 md:py-20">
            <div className="grid md:grid-cols-2 gap-8 md:gap-12 items-center">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-2 rounded-full bg-[#F27C2C]/10 text-[#F27C2C] text-xs md:text-sm font-medium mb-4">
                  <Sparkles className="h-4 w-4" />
                  Innovative Gästekommunikation
                </div>
                
                <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6 text-black dark:text-white leading-tight">
                  Bis zu <span className="text-[#F27C2C]">70% weniger</span> Gäste-Rückfragen
                </h1>
                
                <p className="text-base md:text-lg lg:text-xl text-gray-900 dark:text-gray-200 mb-6 md:mb-8 leading-relaxed">
                  Erstellen Sie interaktive, digitale Gästemappen, automatisieren Sie den Verkauf von Extras und steigern Sie Ihren Umsatz – alles an einem Ort.
                </p>

                <div className="flex flex-col sm:flex-row gap-3 md:gap-4 mb-6 md:mb-8">
                  <Link 
                    to="/register" 
                    className="px-6 py-4 bg-[#F27C2C] text-white rounded-lg hover:bg-[#E06B1B] flex items-center justify-center gap-2 transition-colors font-semibold text-base md:text-lg shadow-lg"
                    onClick={() => analytics.clickedCTA('Jetzt kostenlos starten', 'Hero')}
                  >
                    Jetzt kostenlos starten
                    <ChevronRight className="h-5 w-5" />
                  </Link>
                  <Link 
                    to="/login" 
                    className="px-6 py-4 border-2 border-[#F27C2C] text-[#F27C2C] rounded-lg hover:bg-[#F27C2C] hover:text-white transition-colors font-semibold text-base md:text-lg"
                    onClick={() => analytics.clickedCTA('Demo ansehen', 'Hero')}
                  >
                    Demo ansehen
                  </Link>
                </div>

                <div className="flex flex-col sm:flex-row sm:flex-wrap items-start sm:items-center gap-3 md:gap-6 text-sm md:text-base text-gray-900 dark:text-gray-200">
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-[#F27C2C] flex-shrink-0" />
                    <span>Keine Installation nötig</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-[#F27C2C] flex-shrink-0" />
                    <span>Sofort einsatzbereit</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-[#F27C2C] flex-shrink-0" />
                    <span>Kostenlos testen</span>
                  </div>
                </div>
              </div>

              {/* Right Image */}
              <div className="relative flex items-center">
                <div className="relative rounded-2xl overflow-hidden shadow-2xl max-h-[500px]">
                  <img 
                    src="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=700&h=500&fit=crop"
                    alt="Moderne Hotel-Lobby mit digitaler Gästekommunikation"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#F27C2C]/20 to-transparent"></div>
                </div>
                <div className="absolute -top-4 -right-4 w-24 h-24 bg-[#F27C2C]/10 rounded-full blur-2xl"></div>
                <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-[#F27C2C]/10 rounded-full blur-2xl"></div>
              </div>
            </div>
          </section>

          {/* Features Section */}
          <section className="max-w-7xl mx-auto px-4 py-12 md:py-20 bg-gray-50 dark:bg-slate-800">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-center mb-8 md:mb-12 text-black dark:text-white">
                Alles, was Sie brauchen, in einem Tool
              </h2>
              
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-8">
                {features.map((feature, idx) => {
                  const Icon = feature.icon;
                  return (
                    <div 
                      key={idx} 
                      className="p-5 md:p-6 bg-white dark:bg-slate-700 rounded-xl border-2 border-gray-200 dark:border-slate-600 hover:border-[#F27C2C] hover:shadow-xl transition-all group"
                    >
                      <div className="w-12 h-12 md:w-14 md:h-14 bg-[#F27C2C]/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-[#F27C2C] transition-colors">
                        <Icon className="h-6 w-6 md:h-7 md:w-7 text-[#F27C2C] group-hover:text-white transition-colors" />
                      </div>
                      <h3 className="text-base md:text-lg font-semibold mb-2 text-black dark:text-white">
                        {feature.title}
                      </h3>
                      <p className="text-sm md:text-base text-gray-800 dark:text-gray-300 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>

          {/* CTA Section */}
          <section className="bg-[#F27C2C] text-white py-20">
            <div className="max-w-7xl mx-auto px-4 text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Bereit, Ihre Gästekommunikation zu revolutionieren?
              </h2>
              <p className="text-xl mb-8 max-w-2xl mx-auto font-medium">
                Starten Sie noch heute und erleben Sie, wie Welcome Link Ihr Hotel-Management vereinfacht
              </p>
              <Link 
                to="/register" 
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-[#F27C2C] rounded-lg hover:bg-gray-100 font-semibold transition-colors"
                onClick={() => analytics.clickedCTA('Kostenlos starten', 'CTA Section')}
              >
                Jetzt kostenlos starten
                <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div>
              <div className="mb-4">
                <img 
                  src="/logo.webp" 
                  alt="Welcome Link" 
                  className="h-10 w-auto"
                />
              </div>
              <p className="text-gray-400 text-sm">
                Die digitale Gästemappe für Hotels und Ferienwohnungen.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Produkt</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link to="/pricing" className="hover:text-white transition-colors">Preise</Link></li>
                <li><Link to="/integrations" className="hover:text-white transition-colors">Integrationen</Link></li>
                <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Ressourcen</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/resources" className="hover:text-white transition-colors">Guides</Link></li>
                <li><Link to="/resources" className="hover:text-white transition-colors">Tutorials</Link></li>
                <li><Link to="/about" className="hover:text-white transition-colors">Über uns</Link></li>
                <li><Link to="/contact" className="hover:text-white transition-colors">Kontakt</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Rechtliches</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/impressum" className="hover:text-white transition-colors">Impressum</Link></li>
                <li><Link to="/datenschutz" className="hover:text-white transition-colors">Datenschutz</Link></li>
                <li><Link to="/agb" className="hover:text-white transition-colors">AGB</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
            © {new Date().getFullYear()} Welcome Link. Alle Rechte vorbehalten.
          </div>
        </div>
      </footer>
    </div>
  );
}
