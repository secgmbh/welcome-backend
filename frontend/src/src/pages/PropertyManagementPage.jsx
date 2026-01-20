import { useState, useEffect } from 'react';
import { Building2, Link2, BarChart3, QrCode, Download, Copy, Eye, Edit, Trash2, Plus } from 'lucide-react';
import Layout from '@/components/Layout';
import QRCodeGenerator from '@/components/QRCodeGenerator';
import analytics from '@/lib/analytics';

export default function PropertyManagementPage() {
  const [activeTab, setActiveTab] = useState('properties');
  const [properties, setProperties] = useState([
    { id: 1, name: 'Berghotel Alpenblick', location: 'Österreich' },
    { id: 2, name: 'Strandvilla Ostsee', location: 'Deutschland' },
  ]);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [qrVariant, setQrVariant] = useState('A');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (selectedProperty === null && properties.length > 0) {
      setSelectedProperty(properties[0]);
    }
  }, [properties, selectedProperty]);

  const tabs = [
    { id: 'properties', name: 'Unterkünfte', icon: Building2 },
    { id: 'qrcodes', name: 'Links & QR Codes', icon: Link2 },
    { id: 'analytics', name: 'Analyse', icon: BarChart3 },
  ];

  const getQRUrl = () => {
    if (!selectedProperty) return '';
    return `${window.location.origin}/property/${selectedProperty.id}`;
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(getQRUrl());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    analytics.clickedCTA('Link kopiert', 'PropertyManagement');
  };

  const handleAddProperty = () => {
    analytics.clickedCTA('Property hinzugefügt', 'PropertyManagement');
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900 py-8">
        <div className="max-w-7xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Verwaltungs-Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Verwalten Sie Ihre Unterkünfte, Links und analysieren Sie die Nutzung
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-8 border-b border-gray-200 dark:border-slate-700">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors ${
                    isActive
                      ? 'text-[#F27C2C] border-b-2 border-[#F27C2C]'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {tab.name}
                </button>
              );
            })}
          </div>

          {/* Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Sidebar */}
            <div className="lg:col-span-1">
              {activeTab === 'properties' && (
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Deine Unterkünfte</h2>
                  <div className="space-y-3">
                    {properties.map((prop) => (
                      <button
                        key={prop.id}
                        onClick={() => setSelectedProperty(prop)}
                        className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                          selectedProperty?.id === prop.id
                            ? 'border-[#F27C2C] bg-orange-50 dark:bg-orange-900/20'
                            : 'border-gray-200 dark:border-slate-700 hover:border-[#F27C2C]'
                        }`}
                      >
                        <div className="font-medium text-gray-900 dark:text-white">{prop.name}</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">{prop.location}</div>
                      </button>
                    ))}
                  </div>
                  <button
                    onClick={handleAddProperty}
                    className="w-full mt-4 px-4 py-2 bg-[#F27C2C] text-white rounded-lg hover:bg-[#E06B1B] transition-colors flex items-center justify-center gap-2 font-medium"
                  >
                    <Plus className="h-4 w-4" />
                    Neue Unterkunft
                  </button>
                </div>
              )}

              {activeTab === 'qrcodes' && selectedProperty && (
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">QR-Code Varianten</h2>
                  <div className="space-y-3">
                    <button
                      onClick={() => {
                        setQrVariant('A');
                        analytics.generatedQRCode(getQRUrl(), 'variant_a');
                      }}
                      className={`w-full p-3 rounded-lg border-2 transition-all ${
                        qrVariant === 'A'
                          ? 'border-[#F27C2C] bg-orange-50 dark:bg-orange-900/20'
                          : 'border-gray-200 dark:border-slate-700'
                      }`}
                    >
                      <div className="font-medium text-gray-900 dark:text-white">Variante A</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">Standard QR-Code</div>
                    </button>
                    <button
                      onClick={() => {
                        setQrVariant('B');
                        analytics.generatedQRCode(getQRUrl(), 'variant_b');
                      }}
                      className={`w-full p-3 rounded-lg border-2 transition-all ${
                        qrVariant === 'B'
                          ? 'border-[#F27C2C] bg-orange-50 dark:bg-orange-900/20'
                          : 'border-gray-200 dark:border-slate-700'
                      }`}
                    >
                      <div className="font-medium text-gray-900 dark:text-white">Variante B</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">QR-Code mit Logo</div>
                    </button>
                  </div>

                  {/* QR-Code Link */}
                  <div className="mt-6 p-4 bg-gray-50 dark:bg-slate-700 rounded-lg">
                    <div className="text-sm text-gray-600 dark:text-gray-300 mb-2">Link zur Gästemappe:</div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={getQRUrl()}
                        readOnly
                        className="flex-1 px-3 py-2 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded text-sm"
                      />
                      <button
                        onClick={handleCopyLink}
                        className="px-3 py-2 bg-[#F27C2C] text-white rounded hover:bg-[#E06B1B] transition-colors"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                    {copied && <div className="text-xs text-green-600 dark:text-green-400 mt-1">✓ Kopiert!</div>}
                  </div>
                </div>
              )}

              {activeTab === 'analytics' && (
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Metriken</h2>
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">QR-Code Scans</div>
                      <div className="text-3xl font-bold text-[#F27C2C]">247</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">+12% diese Woche</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Links besucht</div>
                      <div className="text-3xl font-bold text-blue-600">1.842</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">+8% diese Woche</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Main Content */}
            <div className="lg:col-span-2">
              {activeTab === 'properties' && selectedProperty && (
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-8">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">{selectedProperty.name}</h2>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name</label>
                      <input
                        type="text"
                        defaultValue={selectedProperty.name}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Ort</label>
                      <input
                        type="text"
                        defaultValue={selectedProperty.location}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>
                  <div className="mt-6 flex gap-4">
                    <button className="px-4 py-2 bg-[#F27C2C] text-white rounded-lg hover:bg-[#E06B1B] transition-colors">
                      <Edit className="h-4 w-4 mr-2 inline" /> Bearbeiten
                    </button>
                    <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                      <Trash2 className="h-4 w-4 mr-2 inline" /> Löschen
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'qrcodes' && selectedProperty && (
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-8">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                    QR-Code Variante {qrVariant}
                  </h2>
                  <div className="flex flex-col items-center gap-6">
                    <QRCodeGenerator
                      value={getQRUrl()}
                      size={256}
                      level="H"
                      includeDownload={true}
                      includeImage={qrVariant === 'B'}
                    />
                    <div className="w-full p-4 bg-gray-50 dark:bg-slate-700 rounded-lg">
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        {qrVariant === 'A'
                          ? 'Standard QR-Code ohne Logo. Perfekt für Druck und universelle Nutzung.'
                          : 'QR-Code mit Ihrem Logo im Mittelpunkt. Professioneller Look, erhöhte Erkennbarkeit.'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'analytics' && (
                <div className="space-y-6">
                  <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-8">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Trend (letzte 30 Tage)</h2>
                    <div className="h-64 bg-gray-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
                      <p className="text-gray-500 dark:text-gray-400">Chart-Platzhalter</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white dark:bg-slate-800 rounded-lg p-4">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Durchschn. Scans/Tag</div>
                      <div className="text-2xl font-bold text-[#F27C2C]">8.2</div>
                    </div>
                    <div className="bg-white dark:bg-slate-800 rounded-lg p-4">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Conversion Rate</div>
                      <div className="text-2xl font-bold text-blue-600">34%</div>
                    </div>
                    <div className="bg-white dark:bg-slate-800 rounded-lg p-4">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Top Geräte</div>
                      <div className="text-2xl font-bold text-green-600">Mobile</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
