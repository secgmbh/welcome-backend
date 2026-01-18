import { useState, useMemo } from 'react';
import QRCodeGenerator from '@/components/QRCodeGenerator';
import analytics from '@/lib/analytics';
import Layout from '@/components/Layout';

export default function Dashboard() {
  const [propertyId, setPropertyId] = useState('demo');
  const [customUrl, setCustomUrl] = useState('');

  const qrUrl = useMemo(() => {
    if (customUrl && customUrl.trim().length > 0) {
      return customUrl.trim();
    }
    return `${window.location.origin}/property/${propertyId}`;
  }, [propertyId, customUrl]);

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900 py-10">
        <div className="max-w-5xl mx-auto px-4">
          <h1 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-700 dark:text-gray-300 mb-8">
            Erzeuge einen einzigen, funktionierenden QR‑Code für deine Gästemappe.
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-6 border border-gray-100 dark:border-slate-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Ziel‑URL</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Property ID
                  </label>
                  <input
                    type="text"
                    value={propertyId}
                    onChange={(e) => setPropertyId(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-white px-3 py-2"
                    placeholder="z. B. 123"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Standard‑URL: {window.location.origin}/property/{"<ID>"}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Eigene URL (optional)
                  </label>
                  <input
                    type="text"
                    value={customUrl}
                    onChange={(e) => setCustomUrl(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-gray-900 dark:text-white px-3 py-2"
                    placeholder="https://deine-domain.de/gaestemappe"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Wenn gesetzt, wird diese URL für den QR‑Code verwendet.
                  </p>
                </div>

                <div className="mt-4 p-3 bg-gray-50 dark:bg-slate-700 rounded-lg text-sm text-gray-800 dark:text-gray-100">
                  Aktuelle Ziel‑URL:
                  <div className="mt-1 font-mono break-all">{qrUrl}</div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-6 border border-gray-100 dark:border-slate-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">QR‑Code</h2>
              <QRCodeGenerator 
                value={qrUrl} 
                size={256}
                level="H"
                includeDownload={true}
                includeImage={false}
              />

              <div className="mt-4 text-sm text-gray-600 dark:text-gray-300">
                Dieser QR‑Code ersetzt Varianten A und B und leitet Gäste direkt zur digitalen Gästemappe.
              </div>

              <button
                onClick={() => analytics.generatedQRCode(qrUrl, 'single_variant')}
                className="mt-6 px-4 py-2 bg-[#F27C2C] text-white rounded-lg hover:bg-[#E06B1B] transition-colors"
              >
                Nutzung erfassen
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
