import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, Sparkles } from 'lucide-react';
import SEO from '@/components/SEO';
import Layout from '@/components/Layout';

export default function LoginPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showMagicLink, setShowMagicLink] = useState(false);
  const [magicLinkEmail, setMagicLinkEmail] = useState('');
  const [magicLinkSent, setMagicLinkSent] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
        setError(data.detail || 'Anmeldung fehlgeschlagen');
      }
    } catch (err) {
      setError('Verbindungsfehler. Bitte versuchen Sie es erneut.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      // Demo credentials
      const demoEmail = 'demo@welcome-link.de';
      const demoPassword = 'demo123';

      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: demoEmail, password: demoPassword }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('isDemo', 'true');
        navigate('/dashboard');
      } else {
        // If demo login fails, show a message
        setError('Demo-Zugang momentan nicht verfügbar. Bitte registrieren Sie sich.');
      }
    } catch (err) {
      setError('Verbindungsfehler. Bitte versuchen Sie es erneut.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMagicLink = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/magic-link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: magicLinkEmail }),
      });

      if (response.ok) {
        setMagicLinkSent(true);
      } else {
        const data = await response.json();
        setError(data.detail || 'Fehler beim Senden des Magic Links');
      }
    } catch (err) {
      setError('Verbindungsfehler. Bitte versuchen Sie es erneut.');
    } finally {
      setIsLoading(false);
    }
  };

  if (showMagicLink) {
    return (
      <Layout>
        <div className="min-h-[80vh] bg-gray-100 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
          <SEO title="Magic Link | Welcome Link" description="Anmeldung ohne Passwort" />
          
          <div className="w-full max-w-md">
            {/* Magic Link Card */}
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
              {magicLinkSent ? (
                <div className="text-center">
                  <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Mail className="h-8 w-8 text-green-600 dark:text-green-400" />
                  </div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    E-Mail gesendet!
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Wir haben Ihnen einen Magic Link an <strong>{magicLinkEmail}</strong> gesendet. 
                    Klicken Sie auf den Link in der E-Mail, um sich anzumelden.
                  </p>
                  <button
                    onClick={() => { setMagicLinkSent(false); setMagicLinkEmail(''); }}
                    className="text-[#F27C2C] font-medium hover:underline"
                  >
                    Andere E-Mail verwenden
                  </button>
                </div>
              ) : (
                <>
                  <div className="text-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      Willkommen zurück
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                      Anmeldung ohne Passwort - einfach und sicher
                    </p>
                  </div>

                  {error && (
                    <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
                      {error}
                    </div>
                  )}

                  <form onSubmit={handleMagicLink} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        E-Mail-Adresse
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                        <input
                          type="email"
                          value={magicLinkEmail}
                          onChange={(e) => setMagicLinkEmail(e.target.value)}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#F27C2C] focus:border-transparent"
                          placeholder="ihre@email.de"
                          required
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full py-3 bg-[#F27C2C] text-white rounded-lg font-medium hover:bg-[#E06B1B] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {isLoading ? 'Wird gesendet...' : 'Magic Link senden →'}
                    </button>
                  </form>

                  <div className="mt-6 text-center space-y-3">
                    <button
                      onClick={() => setShowMagicLink(false)}
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-sm"
                    >
                      Haben Sie noch ein altes Passwort? <span className="text-[#F27C2C] font-medium">Klassisch anmelden</span>
                    </button>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      Noch kein Konto?{' '}
                      <Link to="/register" className="text-[#F27C2C] font-medium hover:underline">
                        Jetzt registrieren
                      </Link>
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-[80vh] bg-gray-100 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
        <SEO title="Anmelden | Welcome Link" description="Melden Sie sich bei Welcome Link an" />
        
        <div className="w-full max-w-md">
          {/* Login Card */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Anmelden
              </h1>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  E-Mail
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#F27C2C] focus:border-transparent"
                    placeholder="ihre@email.de"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Passwort
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-12 py-3 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#F27C2C] focus:border-transparent"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-[#F27C2C] text-white rounded-lg font-medium hover:bg-[#E06B1B] transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Wird angemeldet...' : 'Anmelden'}
              </button>
            </form>

            {/* Demo Access Button */}
            <button
              onClick={handleDemoLogin}
              disabled={isLoading}
              className="w-full mt-4 py-3 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Sparkles className="h-5 w-5 text-[#F27C2C]" />
              Demo-Zugang verwenden
            </button>

            {/* Magic Link Option */}
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-300 mb-2">
                <strong>Neu:</strong> Anmeldung ohne Passwort
              </p>
              <button
                onClick={() => setShowMagicLink(true)}
                className="text-sm text-[#F27C2C] font-medium hover:underline"
              >
                Mit Magic Link anmelden →
              </button>
            </div>

            {/* Register Link */}
            <p className="mt-6 text-center text-gray-600 dark:text-gray-400 text-sm">
              Noch kein Konto?{' '}
              <Link to="/register" className="text-[#F27C2C] font-medium hover:underline">
                Registrieren
              </Link>
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
