import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import SEO from '@/components/SEO';
import Layout from '@/components/Layout';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (password.length < 6) {
      setError('Passwort muss mindestens 6 Zeichen haben');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      } else {
        setError(data.detail || 'Registrierung fehlgeschlagen');
      }
    } catch (err) {
      setError('Verbindungsfehler. Bitte versuchen Sie es erneut.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="min-h-[80vh] bg-gray-100 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
        <SEO title="Registrieren | Welcome Link" description="Erstellen Sie Ihr Welcome Link Konto" />
        
        <div className="w-full max-w-md">
          {/* Register Card */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Konto erstellen
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Starten Sie kostenlos mit Welcome Link
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#F27C2C] focus:border-transparent"
                    placeholder="Ihr Name"
                  />
                </div>
              </div>

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
                    placeholder="Min. 6 Zeichen"
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
                {isLoading ? 'Wird registriert...' : 'Kostenlos registrieren'}
              </button>
            </form>

            {/* Terms */}
            <p className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
              Mit der Registrierung stimmen Sie unseren{' '}
              <Link to="/agb" className="text-[#F27C2C] hover:underline">AGB</Link> und{' '}
              <Link to="/datenschutz" className="text-[#F27C2C] hover:underline">Datenschutzrichtlinien</Link> zu.
            </p>

            {/* Login Link */}
            <p className="mt-6 text-center text-gray-600 dark:text-gray-400 text-sm">
              Bereits ein Konto?{' '}
              <Link to="/login" className="text-[#F27C2C] font-medium hover:underline">
                Anmelden
              </Link>
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
