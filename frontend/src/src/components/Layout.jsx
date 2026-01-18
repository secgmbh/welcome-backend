import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { Menu, X, Moon, Sun } from 'lucide-react';

/**
 * Layout Component - Welcome Link Design (1:1 wie www.welcome-link.de)
 */
export default function Layout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark');
    }
    return false;
  });
  const location = useLocation();

  const navigation = [
    { name: 'Features', href: '/features' },
    { name: 'Preise', href: '/pricing' },
    { name: 'Integrationen', href: '/integrations' },
    { name: 'Ressourcen', href: '/resources' },
  ];

  const toggleDarkMode = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
    setIsDark(!isDark);
  };

  const isActive = (href) => {
    return location.pathname === href;
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Header - 1:1 wie welcome-link.de */}
      <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 py-4">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            {/* Logo - größer */}
            <Link to="/" className="flex items-center flex-shrink-0">
              <img 
                src="/logo.webp" 
                alt="Welcome Link" 
                className="h-14 w-auto"
              />
            </Link>

            {/* Desktop Navigation - mit grauem Border */}
            <div className="hidden md:flex items-center gap-3">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`px-5 py-2.5 rounded-lg text-sm font-medium border transition-all ${
                    isActive(item.href)
                      ? 'bg-gray-100 dark:bg-slate-800 text-gray-900 dark:text-white border-gray-300 dark:border-slate-600'
                      : 'bg-white dark:bg-slate-900 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-800'
                  }`}
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
              
              {/* Anmelden Button - gleiche Rundung wie Menüpunkte */}
              <Link 
                to="/login" 
                className="px-5 py-2.5 text-[#F27C2C] bg-white border-2 border-[#F27C2C] rounded-lg font-medium hover:bg-[#FEF3E7] transition-colors"
              >
                Anmelden
              </Link>
              
              {/* Registrieren Button - gleiche Rundung wie Menüpunkte */}
              <Link 
                to="/register" 
                className="px-5 py-2.5 bg-[#F27C2C] text-white rounded-lg font-medium hover:bg-[#E06B1B] transition-colors"
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
                {isDark ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </button>
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 text-gray-600 dark:text-gray-300"
              >
                {mobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
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
                    className={`px-4 py-3 rounded-lg text-base font-medium border ${
                      isActive(item.href)
                        ? 'bg-gray-100 dark:bg-slate-800 text-gray-900 dark:text-white border-gray-300'
                        : 'text-gray-600 dark:text-gray-300 border-gray-200 hover:bg-gray-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
                <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-slate-700">
                  <Link 
                    to="/login" 
                    className="flex-1 px-4 py-3 text-center text-[#F27C2C] border-2 border-[#F27C2C] rounded-lg font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Anmelden
                  </Link>
                  <Link 
                    to="/register" 
                    className="flex-1 px-4 py-3 text-center bg-[#F27C2C] text-white rounded-lg font-medium"
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
      <main>{children}</main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            {/* Brand */}
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

            {/* Product */}
            <div>
              <h4 className="font-semibold mb-4">Produkt</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link to="/pricing" className="hover:text-white transition-colors">Preise</Link></li>
                <li><Link to="/integrations" className="hover:text-white transition-colors">Integrationen</Link></li>
                <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>

            {/* Resources */}
            <div>
              <h4 className="font-semibold mb-4">Ressourcen</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/resources" className="hover:text-white transition-colors">Guides</Link></li>
                <li><Link to="/resources" className="hover:text-white transition-colors">Tutorials</Link></li>
                <li><Link to="/about" className="hover:text-white transition-colors">Über uns</Link></li>
                <li><Link to="/contact" className="hover:text-white transition-colors">Kontakt</Link></li>
              </ul>
            </div>

            {/* Legal */}
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
