import Layout from '../components/Layout'
import { BookOpen, Video, FileText, TrendingUp, Users, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useEffect } from 'react'
import analytics from '../lib/analytics'
import SEO, { schemas } from '../components/SEO'

export default function ResourcesPage() {
  useEffect(() => {
    analytics.trackPageView('Resources Page');
  }, []);
  const guides = [
    {
      title: 'Der ultimative Guide zur digitalen Gästemappe',
      category: 'Guide',
      readTime: '10 min',
      description: 'Erfahren Sie, wie Sie eine professionelle digitale Gästemappe erstellen, die Ihre Gäste begeistert und Rückfragen reduziert.',
      icon: BookOpen,
      featured: true
    },
    {
      title: 'Upselling-Strategien für Hotels',
      category: 'Strategie',
      readTime: '8 min',
      description: 'Bewährte Methoden, um Ihren Zusatzumsatz um bis zu 40% zu steigern ohne aufdringlich zu wirken.',
      icon: TrendingUp,
      featured: true
    },
    {
      title: 'QR-Codes effektiv einsetzen',
      category: 'Tutorial',
      readTime: '5 min',
      description: 'Best Practices für die Platzierung und Nutzung von QR-Codes in Ihrer Unterkunft.',
      icon: FileText,
      featured: false
    }
  ]

  const videos = [
    {
      title: 'Welcome Link in 3 Minuten erklärt',
      duration: '3:24',
      thumbnail: 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=400&h=250&fit=crop'
    },
    {
      title: 'Setup-Tutorial: Ihre erste Property',
      duration: '7:15',
      thumbnail: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=250&fit=crop'
    },
    {
      title: 'Upsells konfigurieren',
      duration: '5:42',
      thumbnail: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=250&fit=crop'
    }
  ]

  const caseStudies = [
    {
      property: 'Alpenhotel Sonnenhof',
      location: 'Österreich',
      result: '+65% weniger Anfragen',
      quote: 'Welcome Link hat unsere Gästekommunikation revolutioniert. Die Gäste lieben die digitale Mappe!',
      stats: [
        { label: 'Weniger Rückfragen', value: '65%' },
        { label: 'Höhere Gästezufriedenheit', value: '4.8/5' },
        { label: 'Zeitersparnis pro Woche', value: '8h' }
      ]
    },
    {
      property: 'Stadthotel Metropol',
      location: 'Deutschland',
      result: '+€2.400 Zusatzumsatz/Monat',
      quote: 'Das Upselling-System funktioniert fantastisch. Unsere Gäste buchen deutlich mehr Extras.',
      stats: [
        { label: 'Zusatzumsatz', value: '+€2.4k' },
        { label: 'Upsell-Rate', value: '34%' },
        { label: 'ROI', value: '450%' }
      ]
    }
  ]

  const templates = [
    {
      title: 'FAQ-Vorlage für Hotels',
      type: 'PDF Download',
      description: '50+ häufige Gästefragen mit Antwortvorschlägen'
    },
    {
      title: 'Upsell-Texte Sammlung',
      type: 'PDF Download',
      description: 'Bewährte Formulierungen für Ihre Zusatzangebote'
    },
    {
      title: 'Willkommens-Email Templates',
      type: 'PDF Download',
      description: 'Professionelle Email-Vorlagen für Check-in & Check-out'
    }
  ]

  return (
    <Layout>
      <SEO 
        title="Ressourcen & Guides | Welcome Link - Digitale Gästemappe"
        description="Kostenlose Guides, Tutorials und Success Stories für Hotels. Erfahren Sie, wie Sie mit Welcome Link mehr Umsatz generieren und Gäste begeistern."
        keywords="digitale Gästemappe Guide, Hotel Tutorials, Upselling Strategien, QR-Code Best Practices"
        structuredData={schemas.organization}
      />
      <div className="min-h-screen">
        {/* Hero */}
        <section className="bg-gradient-to-b from-blue-50 to-white dark:from-slate-900 dark:to-slate-800 py-20">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900 dark:text-white">
                Ressourcen & <span className="text-primary">Wissen</span>
              </h1>
              <p className="text-xl text-gray-900 dark:text-gray-200 max-w-3xl mx-auto">
                Entdecken Sie hilfreiche Guides, Tutorials und Success Stories, 
                um das Beste aus Welcome Link herauszuholen.
              </p>
            </div>
          </div>
        </section>

        {/* Featured Guides */}
        <section className="max-w-6xl mx-auto px-4 py-12">
          <h2 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Beliebte Guides</h2>
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            {guides.filter(g => g.featured).map((guide, idx) => {
              const Icon = guide.icon
              return (
                <div
                  key={idx}
                  onClick={() => analytics.viewedGuide(guide.title, guide.category)}
                  className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border-2 border-gray-100 dark:border-slate-700 hover:border-primary cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 bg-primary/10 dark:bg-primary/20 rounded-lg flex items-center justify-center">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <span className="text-sm text-primary font-medium bg-primary/10 dark:bg-primary/20 px-3 py-1 rounded-full">
                      {guide.readTime}
                    </span>
                  </div>
                  <span className="text-sm text-gray-700 dark:text-gray-300 mb-2 block">{guide.category}</span>
                  <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">{guide.title}</h3>
                  <p className="text-gray-700 dark:text-gray-200 mb-4">{guide.description}</p>
                  <div className="flex items-center gap-2 text-primary font-medium">
                    Jetzt lesen <ArrowRight className="h-4 w-4" />
                  </div>
                </div>
              )
            })}
          </div>

          {/* More Guides */}
          <div className="grid md:grid-cols-3 gap-6">
            {guides.filter(g => !g.featured).map((guide, idx) => {
              const Icon = guide.icon
              return (
                <div
                  key={idx}
                  className="bg-white dark:bg-slate-800 rounded-lg shadow dark:shadow-lg p-6 hover:shadow-lg dark:hover:shadow-xl transition-shadow cursor-pointer border border-gray-100 dark:border-slate-700"
                >
                  <div className="w-10 h-10 bg-primary/10 dark:bg-primary/20 rounded-lg flex items-center justify-center mb-3">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <span className="text-xs text-gray-700 dark:text-gray-300 mb-1 block">{guide.category}</span>
                  <h3 className="font-bold mb-2 text-gray-900 dark:text-white">{guide.title}</h3>
                  <p className="text-sm text-gray-700 dark:text-gray-200 mb-3">{guide.description}</p>
                  <span className="text-sm text-primary font-medium">{guide.readTime}</span>
                </div>
              )
            })}
          </div>
        </section>

        {/* Video Tutorials */}
        <section className="bg-gray-50 dark:bg-slate-900 py-20">
          <div className="max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3 text-gray-900 dark:text-white">
              <Video className="h-8 w-8 text-primary" />
              Video-Tutorials
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              {videos.map((video, idx) => (
                <div
                  key={idx}
                  onClick={() => analytics.clickedVideo(video.title)}
                  className="bg-white dark:bg-slate-800 rounded-lg overflow-hidden shadow-lg dark:shadow-xl hover:shadow-xl dark:hover:shadow-2xl transition-shadow cursor-pointer group border border-gray-100 dark:border-slate-700"
                >
                  <div className="relative">
                    <img
                      src={video.thumbnail}
                      alt={video.title}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform"
                    />
                    <div className="absolute inset-0 bg-black/40 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                      <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
                        <div className="w-0 h-0 border-l-[16px] border-l-primary border-t-[10px] border-t-transparent border-b-[10px] border-b-transparent ml-1"></div>
                      </div>
                    </div>
                    <div className="absolute bottom-3 right-3 bg-black/80 text-white text-xs px-2 py-1 rounded">
                      {video.duration}
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-bold text-gray-900 dark:text-white">{video.title}</h3>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Case Studies */}
        <section className="py-20 bg-white dark:bg-slate-800">
          <div className="max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3 text-gray-900 dark:text-white">
              <Users className="h-8 w-8 text-primary" />
              Erfolgsgeschichten
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              {caseStudies.map((study, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-br from-blue-50 to-white dark:from-slate-700 dark:to-slate-800 rounded-xl p-8 border-2 border-gray-100 dark:border-slate-600 hover:border-primary transition-colors"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold mb-1 text-gray-900 dark:text-white">{study.property}</h3>
                      <p className="text-gray-700 dark:text-gray-300">{study.location}</p>
                    </div>
                    <span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-sm font-semibold px-3 py-1 rounded-full">
                      {study.result}
                    </span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-200 italic mb-6">"{study.quote}"</p>
                  <div className="grid grid-cols-3 gap-4">
                    {study.stats.map((stat, sidx) => (
                      <div key={sidx} className="text-center">
                        <div className="text-2xl font-bold text-primary">{stat.value}</div>
                        <div className="text-xs text-gray-700 dark:text-gray-300 mt-1">{stat.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Templates */}
        <section className="bg-primary dark:bg-primary text-white py-20">
          <div className="max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold mb-8">Kostenlose Vorlagen</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {templates.map((template, idx) => (
                <div
                  key={idx}
                  onClick={() => analytics.downloadedTemplate(template.title, template.type)}
                  className="bg-white/10 dark:bg-white/5 backdrop-blur rounded-lg p-6 hover:bg-white/20 dark:hover:bg-white/10 transition-colors cursor-pointer border border-white/20"
                >
                  <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center mb-3">
                    <FileText className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="font-bold mb-2 text-white">{template.title}</h3>
                  <p className="text-sm text-white/80 mb-4">{template.description}</p>
                  <div className="flex items-center gap-2 text-sm font-medium text-white">
                    Download {template.type} <ArrowRight className="h-4 w-4" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 bg-gray-50 dark:bg-slate-900">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900 dark:text-white">
              Haben Sie noch Fragen?
            </h2>
            <p className="text-xl text-gray-700 dark:text-gray-200 mb-8">
              Unser Team hilft Ihnen gerne weiter
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                onClick={() => analytics.clickedCTA('Kostenlos starten', 'Resources Page Footer')}
                className="px-8 py-4 bg-primary text-white rounded-lg hover:bg-primary-dark font-semibold"
              >
                Kostenlos starten
              </Link>
              <button 
                onClick={() => analytics.clickedSupport('contact', 'Resources Page Footer')}
                className="px-8 py-4 border-2 border-primary text-primary dark:text-primary dark:border-primary rounded-lg hover:bg-primary hover:text-white dark:hover:bg-primary dark:hover:text-white font-semibold transition-colors bg-white dark:bg-slate-800">
                Support kontaktieren
              </button>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  )
}
