import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

function GuestviewPage() {
    const { t } = useTranslation();
    const { token } = useParams<{ token: string }>();
    const [guestData, setGuestData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchGuestview = async () => {
            try {
                const response = await fetch(`/api/guestview/${token}`);
                if (response.ok) {
                    const data = await response.json();
                    setGuestData(data);
                } else {
                    setError(t('guestview.invalidToken'));
                }
            } catch (err) {
                setError(t('guestview.error'));
            } finally {
                setLoading(false);
            }
        };

        fetchGuestview();
    }, [token, t]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                    <p>{t('guestview.loading')}</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center max-w-md p-6 bg-card rounded-lg shadow-lg">
                    <h2 className="text-2xl font-bold mb-4 text-red-500">{t('guestview.errorTitle')}</h2>
                    <p className="mb-6 text-gray-700">{error}</p>
                    <a href="/" className="btn-primary">
                        {t('guestview.backToHome')}
                    </a>
                </div>
            </div>
        );
    }

    if (!guestData) {
        return null;
    }

    return (
        <div className="min-h-screen">
            {/* Header */}
            <header className="bg-white dark:bg-card shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="container mx-auto px-4 py-4">
                    <h1 className="text-2xl font-bold">{t('guestview.title')}</h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        {t('guestview.subtitle')}
                    </p>
                </div>
            </header>

            {/* Guest Info Section */}
            <section className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* User Info Card */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="bg-white dark:bg-card rounded-lg shadow-lg p-6">
                            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <i data-lucide="user"></i>
                                {t('guestview.userTitle')}
                            </h2>
                            <div className="space-y-2 text-sm">
                                <div>
                                    <span className="text-gray-500 dark:text-gray-400">{t('guestview.name')}</span>
                                    <p className="font-medium">{guestData.user.name}</p>
                                </div>
                                <div>
                                    <span className="text-gray-500 dark:text-gray-400">{t('guestview.email')}</span>
                                    <p className="font-medium">{guestData.user.email}</p>
                                </div>
                            </div>
                        </div>

                        {/* Invoice Info Card (if available) */}
                        {guestData.user.invoice_name && (
                            <div className="bg-white dark:bg-card rounded-lg shadow-lg p-6">
                                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                    <i data-lucide="file-text"></i>
                                    {t('guestview.invoiceTitle')}
                                </h2>
                                <div className="space-y-2 text-sm">
                                    <div>
                                        <span className="text-gray-500 dark:text-gray-400">{t('guestview.company')}</span>
                                        <p className="font-medium">{guestData.user.invoice_name}</p>
                                    </div>
                                    <div>
                                        <span className="text-gray-500 dark:text-gray-400">{t('guestview.address')}</span>
                                        <p className="font-medium">{guestData.user.invoice_address}</p>
                                    </div>
                                    <div>
                                        <span className="text-gray-500 dark:text-gray-400">{t('guestview.postcode')}</span>
                                        <p className="font-medium">{guestData.user.invoice_zip} {guestData.user.invoice_city}</p>
                                    </div>
                                    <div>
                                        <span className="text-gray-500 dark:text-gray-400">{t('guestview.country')}</span>
                                        <p className="font-medium">{guestData.user.invoice_country}</p>
                                    </div>
                                    {guestData.user.invoice_vat_id && (
                                        <div>
                                            <span className="text-gray-500 dark:text-gray-400">{t('guestview.vatId')}</span>
                                            <p className="font-medium">{guestData.user.invoice_vat_id}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Properties Section */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-white dark:bg-card rounded-lg shadow-lg p-6">
                            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <i data-lucide="home"></i>
                                {t('guestview.propertiesTitle')}
                                <span className="bg-primary text-white text-sm px-3 py-1 rounded-full ml-auto">
                                    {guestData.properties.length}
                                </span>
                            </h2>

                            {guestData.properties.length === 0 ? (
                                <div className="text-center py-12">
                                    <i data-lucide="inbox" className="mx-auto h-12 w-12 text-gray-400 mb-4"></i>
                                    <p className="text-gray-500 dark:text-gray-400">{t('guestview.noProperties')}</p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {guestData.properties.map((prop: any) => (
                                        <div key={prop.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                                            <h3 className="font-bold text-lg mb-2">{prop.name}</h3>
                                            {prop.description && (
                                                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">{prop.description}</p>
                                            )}
                                            {prop.address && (
                                                <div className="text-sm text-gray-500 dark:text-gray-400">
                                                    <i data-lucide="map-pin" className="inline w-4 h-4 mr-1"></i>
                                                    {prop.address}
                                                </div>
                                            )}
                                            {prop.created_at && (
                                                <div className="text-xs text-gray-400 mt-3">
                                                    {t('guestview.added', { date: new Date(prop.created_at).toLocaleDateString() })}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default GuestviewPage;
