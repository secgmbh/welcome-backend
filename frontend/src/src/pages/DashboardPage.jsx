import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Home, Building2, QrCode, Package, Users, Settings, LogOut, 
  Plus, Eye, Edit, Trash2, BarChart3, MessageSquare, Bell,
  ChevronRight, Menu, X, Moon, Sun, Search
} from 'lucide-react';
import SEO from '@/components/SEO';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [properties, setProperties] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Check auth
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      navigate('/login');
      return;
    }

    setUser(JSON.parse(userData));
    
    // Check dark mode
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }

    // Fetch properties
    fetchProperties(token);
  }, [navigate]);

  const fetchProperties = async (token) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/properties`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProperties(data);
      }
    } catch (err) {
      console.error('Error fetching properties:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('isDemo');
    navigate('/login');
  };

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

  const navigation = [
    { name: 'Übersicht', icon: Home, id: 'overview' },
    { name: 'Properties', icon: Building2, id: 'properties' },
    { name: 'QR-Codes', icon: QrCode, id: 'qrcodes' },
    { name: 'Pakete & Upsells', icon: Package, id: 'packages' },
    { name: 'Analytics', icon: BarChart3, id: 'analytics' },
    { name: 'Gäste', icon: Users, id: 'guests' },
    { name: 'Nachrichten', icon: MessageSquare, id: 'messages' },
  ];

  const stats = [
    { label: 'Properties', value: properties.length, change: '+2 diese Woche', color: 'bg-blue-500' },
    { label: 'QR-Code Scans', value: '1.247', change: '+12% vs. Vormonat', color: 'bg-green-500' },
    { label: 'Upsell-Umsatz', value: '€2.840', change: '+28% vs. Vormonat', color: 'bg-[#F27C2C]' },
    { label: 'Rückfragen reduziert', value: '68%', change: 'Ziel: 70%', color: 'bg-purple-500' },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-xl text-gray-600 dark:text-gray-300">Lädt...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <SEO title="Dashboard | Welcome Link" description="Verwalten Sie Ihre Properties und Gästemappen" />

      {/* Mobile Sidebar Overlay */}
      {mobileSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full bg-white dark:bg-slate-800 border-r border-gray-200 dark:border-slate-700 z-50 transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-20'
      } ${mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-slate-700">
          {sidebarOpen && (
            <Link to="/">
              <img src="/logo.webp" alt="Welcome Link" className="h-8" />
            </Link>
          )}
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 hidden lg:block"
          >
            <Menu className="h-5 w-5 text-gray-500" />
          </button>
          <button 
            onClick={() => setMobileSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 lg:hidden"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => { setActiveTab(item.id); setMobileSidebarOpen(false); }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  activeTab === item.id
                    ? 'bg-[#F27C2C] text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                }`}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {sidebarOpen && <span className="font-medium">{item.name}</span>}
              </button>
            );
          })}
        </nav>

        {/* Bottom Section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-slate-700">
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors mb-2 ${
              activeTab === 'settings'
                ? 'bg-[#F27C2C] text-white'
                : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
            }`}
          >
            <Settings className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span className="font-medium">Einstellungen</span>}
          </button>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span className="font-medium">Abmelden</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-20'}`}>
        {/* Top Bar */}
        <header className="h-16 bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between px-4 lg:px-6">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setMobileSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 lg:hidden"
            >
              <Menu className="h-5 w-5 text-gray-500" />
            </button>
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Suchen..."
                className="pl-10 pr-4 py-2 bg-gray-100 dark:bg-slate-700 rounded-lg text-sm w-64 focus:outline-none focus:ring-2 focus:ring-[#F27C2C]"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 relative">
              <Bell className="h-5 w-5 text-gray-500" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700"
            >
              {isDark ? <Sun className="h-5 w-5 text-yellow-500" /> : <Moon className="h-5 w-5 text-gray-500" />}
            </button>
            <div className="flex items-center gap-3 pl-3 border-l border-gray-200 dark:border-slate-700">
              <div className="w-8 h-8 bg-[#F27C2C] rounded-full flex items-center justify-center text-white font-medium">
                {user?.name?.[0]?.toUpperCase() || 'D'}
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.name || 'Demo'}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="p-4 lg:p-6">
          {/* Demo Banner */}
          {user?.is_demo && (
            <div className="mb-6 p-4 bg-[#F27C2C]/10 border border-[#F27C2C]/30 rounded-lg flex items-center justify-between">
              <div>
                <p className="font-medium text-[#F27C2C]">🎉 Sie nutzen den Demo-Zugang</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Testen Sie alle Funktionen kostenlos. Für ein eigenes Konto registrieren Sie sich.</p>
              </div>
              <Link to="/register" className="px-4 py-2 bg-[#F27C2C] text-white rounded-lg font-medium hover:bg-[#E06B1B] transition-colors">
                Jetzt registrieren
              </Link>
            </div>
          )}

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Willkommen zurück, {user?.name?.split(' ')[0] || 'Demo'}! 👋
              </h1>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {stats.map((stat, idx) => (
                  <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-10 h-10 ${stat.color} rounded-lg flex items-center justify-center`}>
                        <span className="text-white font-bold text-lg">{stat.value.toString()[0]}</span>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
                        <p className="text-sm text-gray-500">{stat.label}</p>
                      </div>
                    </div>
                    <p className="text-xs text-green-600">{stat.change}</p>
                  </div>
                ))}
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Schnellaktionen</h2>
                  <div className="grid grid-cols-2 gap-3">
                    <button 
                      onClick={() => setActiveTab('properties')}
                      className="p-4 bg-gray-50 dark:bg-slate-700 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-600 transition-colors text-left"
                    >
                      <Building2 className="h-6 w-6 text-[#F27C2C] mb-2" />
                      <p className="font-medium text-gray-900 dark:text-white">Neue Property</p>
                      <p className="text-xs text-gray-500">Property anlegen</p>
                    </button>
                    <button 
                      onClick={() => setActiveTab('qrcodes')}
                      className="p-4 bg-gray-50 dark:bg-slate-700 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-600 transition-colors text-left"
                    >
                      <QrCode className="h-6 w-6 text-[#F27C2C] mb-2" />
                      <p className="font-medium text-gray-900 dark:text-white">QR-Code</p>
                      <p className="text-xs text-gray-500">Code generieren</p>
                    </button>
                    <button 
                      onClick={() => setActiveTab('packages')}
                      className="p-4 bg-gray-50 dark:bg-slate-700 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-600 transition-colors text-left"
                    >
                      <Package className="h-6 w-6 text-[#F27C2C] mb-2" />
                      <p className="font-medium text-gray-900 dark:text-white">Upsell</p>
                      <p className="text-xs text-gray-500">Paket erstellen</p>
                    </button>
                    <button 
                      onClick={() => setActiveTab('analytics')}
                      className="p-4 bg-gray-50 dark:bg-slate-700 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-600 transition-colors text-left"
                    >
                      <BarChart3 className="h-6 w-6 text-[#F27C2C] mb-2" />
                      <p className="font-medium text-gray-900 dark:text-white">Analytics</p>
                      <p className="text-xs text-gray-500">Statistiken ansehen</p>
                    </button>
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Letzte Aktivitäten</h2>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 pb-3 border-b border-gray-100 dark:border-slate-700">
                      <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                        <QrCode className="h-4 w-4 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900 dark:text-white">QR-Code gescannt</p>
                        <p className="text-xs text-gray-500">Boutique Hotel Alpenblick</p>
                      </div>
                      <span className="text-xs text-gray-400">vor 5 Min.</span>
                    </div>
                    <div className="flex items-center gap-3 pb-3 border-b border-gray-100 dark:border-slate-700">
                      <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                        <Package className="h-4 w-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900 dark:text-white">Upsell gebucht</p>
                        <p className="text-xs text-gray-500">Frühstückspaket - €15,00</p>
                      </div>
                      <span className="text-xs text-gray-400">vor 2 Std.</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                        <Users className="h-4 w-4 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900 dark:text-white">Neuer Gast</p>
                        <p className="text-xs text-gray-500">Ferienwohnung Seeblick</p>
                      </div>
                      <span className="text-xs text-gray-400">vor 1 Tag</span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Properties Tab */}
          {activeTab === 'properties' && (
            <>
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Properties</h1>
                <button className="flex items-center gap-2 px-4 py-2 bg-[#F27C2C] text-white rounded-lg font-medium hover:bg-[#E06B1B] transition-colors">
                  <Plus className="h-5 w-5" />
                  Neue Property
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {properties.map((property) => (
                  <div key={property.id} className="bg-white dark:bg-slate-800 rounded-xl overflow-hidden border border-gray-200 dark:border-slate-700">
                    <div className="h-40 bg-gradient-to-br from-[#F27C2C]/20 to-[#F27C2C]/5 flex items-center justify-center">
                      <Building2 className="h-16 w-16 text-[#F27C2C]/50" />
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{property.name}</h3>
                      <p className="text-sm text-gray-500 mb-3 line-clamp-2">{property.description}</p>
                      <p className="text-xs text-gray-400 mb-4">{property.address}</p>
                      <div className="flex items-center gap-2">
                        <button className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gray-100 dark:bg-slate-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors">
                          <Eye className="h-4 w-4" />
                          Ansehen
                        </button>
                        <button className="flex items-center justify-center gap-1 px-3 py-2 bg-gray-100 dark:bg-slate-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors">
                          <Edit className="h-4 w-4" />
                        </button>
                        <button className="flex items-center justify-center gap-1 px-3 py-2 bg-red-50 dark:bg-red-900/20 rounded-lg text-sm text-red-600 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Add New Property Card */}
                <div className="bg-white dark:bg-slate-800 rounded-xl border-2 border-dashed border-gray-300 dark:border-slate-600 flex items-center justify-center min-h-[280px] hover:border-[#F27C2C] hover:bg-[#F27C2C]/5 transition-colors cursor-pointer">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-gray-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-3">
                      <Plus className="h-6 w-6 text-gray-400" />
                    </div>
                    <p className="font-medium text-gray-600 dark:text-gray-400">Neue Property hinzufügen</p>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* QR Codes Tab */}
          {activeTab === 'qrcodes' && (
            <>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">QR-Code Generator</h1>
              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Wählen Sie eine Property aus, um einen QR-Code zu generieren:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {properties.map((property) => (
                    <button 
                      key={property.id}
                      className="p-4 bg-gray-50 dark:bg-slate-700 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-600 transition-colors text-left flex items-center gap-4"
                    >
                      <div className="w-12 h-12 bg-[#F27C2C]/10 rounded-lg flex items-center justify-center">
                        <QrCode className="h-6 w-6 text-[#F27C2C]" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{property.name}</p>
                        <p className="text-sm text-gray-500">QR-Code generieren</p>
                      </div>
                      <ChevronRight className="h-5 w-5 text-gray-400 ml-auto" />
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Packages Tab */}
          {activeTab === 'packages' && (
            <>
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Pakete & Upsells</h1>
                <button className="flex items-center gap-2 px-4 py-2 bg-[#F27C2C] text-white rounded-lg font-medium hover:bg-[#E06B1B] transition-colors">
                  <Plus className="h-5 w-5" />
                  Neues Paket
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Example Packages */}
                {[
                  { name: 'Frühstückspaket', price: '€15,00', description: 'Reichhaltiges Frühstücksbuffet für 2 Personen', bookings: 24 },
                  { name: 'Spa-Zugang', price: '€25,00', description: 'Ganztägiger Zugang zum Wellness-Bereich', bookings: 18 },
                  { name: 'Late Checkout', price: '€20,00', description: 'Abreise bis 14:00 Uhr statt 11:00 Uhr', bookings: 32 },
                ].map((pkg, idx) => (
                  <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{pkg.name}</h3>
                      <span className="text-lg font-bold text-[#F27C2C]">{pkg.price}</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-4">{pkg.description}</p>
                    <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-slate-700">
                      <span className="text-xs text-gray-400">{pkg.bookings} Buchungen</span>
                      <button className="text-sm text-[#F27C2C] font-medium hover:underline">Bearbeiten</button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Analytics</h1>
              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                <div className="text-center py-12">
                  <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Analytics Dashboard</h3>
                  <p className="text-gray-500">Detaillierte Statistiken und Berichte zu Ihren Properties</p>
                </div>
              </div>
            </>
          )}

          {/* Other Tabs */}
          {(activeTab === 'guests' || activeTab === 'messages' || activeTab === 'settings') && (
            <>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                {activeTab === 'guests' && 'Gäste'}
                {activeTab === 'messages' && 'Nachrichten'}
                {activeTab === 'settings' && 'Einstellungen'}
              </h1>
              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-gray-200 dark:border-slate-700">
                <div className="text-center py-12">
                  <p className="text-gray-500">Diese Funktion ist in der Demo-Version verfügbar.</p>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
