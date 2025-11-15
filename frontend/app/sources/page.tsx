'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import SourceList from '../../components/SourceList';
import AddSourceForm from '../../components/AddSourceForm';
import { fetchSources, createSource, deleteSource, testSource, triggerScrape, stopAllScraping } from '../../lib/api';

export default function SourcesPage() {
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [scrapingSourceId, setScrapingSourceId] = useState<string | null>(null);
  const [stoppingAll, setStoppingAll] = useState(false);

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      setLoading(true);
      const data = await fetchSources();
      setSources(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load sources');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSource = async (sourceData: { url: string; name?: string; autoScrape?: boolean }) => {
    try {
      await createSource(
        { url: sourceData.url, name: sourceData.name },
        sourceData.autoScrape ?? true
      );
      setShowAddForm(false);
      loadSources();
      if (sourceData.autoScrape) {
        alert('Source added! Scraping has started in the background. Articles will appear shortly.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to add source');
    }
  };

  const handleDeleteSource = async (sourceId: string) => {
    if (!confirm('Are you sure you want to delete this source?')) {
      return;
    }
    try {
      await deleteSource(sourceId);
      loadSources();
    } catch (err: any) {
      setError(err.message || 'Failed to delete source');
    }
  };

  const handleTestSource = async (sourceId: string) => {
    try {
      const result = await testSource(sourceId);
      alert(result.message || 'Test completed');
    } catch (err: any) {
      alert('Test failed: ' + (err.message || 'Unknown error'));
    }
  };

  const handleScrapeAll = async () => {
    if (!confirm('This will start scraping all active sources. This may take several minutes. Continue?')) {
      return;
    }

    setScraping(true);
    setError(null);
    try {
      const result = await triggerScrape();
      alert(result.message || `Scraping started for ${result.sources_queued || 0} sources. Articles will appear as they are processed.`);
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to start scraping';
      setError(errorMessage);
      alert('Failed to start scraping: ' + errorMessage);
      console.error('Scrape all error:', err);
    } finally {
      setScraping(false);
    }
  };

  const handleScrapeSource = async (sourceId: string) => {
    const source = sources.find(s => s.id === sourceId);
    const sourceName = source?.name || source?.domain || 'this source';
    
    if (!confirm(`Start scraping ${sourceName}? This will process all new articles and may take several minutes.`)) {
      return;
    }

    setScrapingSourceId(sourceId);
    setError(null);
    try {
      const result = await triggerScrape(sourceId);
      alert(result.message || `Scraping started for ${sourceName}. Articles will appear as they are processed.`);
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to start scraping';
      setError(errorMessage);
      alert('Failed to start scraping: ' + errorMessage);
      console.error('Scrape source error:', err);
    } finally {
      setScrapingSourceId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link href="/" className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">Cargo News Aggregator</h1>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-700 hover:text-gray-900">
                Articles
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-2xl font-bold text-gray-900">News Sources</h2>
            <div className="flex gap-3">
              <button
                onClick={handleScrapeAll}
                disabled={scraping || sources.filter(s => s.is_active).length === 0}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {scraping ? 'Scraping...' : 'Scrape All Sources'}
              </button>
              <button
                onClick={async () => {
                  if (confirm('Stop all running scraping tasks?')) {
                    setStoppingAll(true);
                    try {
                      await stopAllScraping();
                      alert('All scraping tasks stopped successfully');
                      // Reload sources to refresh status
                      loadSources();
                    } catch (err: any) {
                      alert(`Failed to stop scraping: ${err.message || 'Unknown error'}`);
                    } finally {
                      setStoppingAll(false);
                    }
                  }
                }}
                disabled={stoppingAll}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Stop all running scraping tasks"
              >
                {stoppingAll ? 'Stopping...' : '⏹ Stop All'}
              </button>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                {showAddForm ? 'Cancel' : 'Add Source'}
              </button>
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-600">
              Each air cargo news website has its own custom scraper script. The system automatically selects the appropriate scraper based on the URL domain.
            </p>
            <p className="text-xs text-gray-500">
              💡 Automatic scraping runs daily at 00:00 UTC. Use "Scrape All Sources" to manually trigger scraping now.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {showAddForm && (
          <div className="mb-6">
            <AddSourceForm onSubmit={handleAddSource} onCancel={() => setShowAddForm(false)} />
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading sources...</p>
          </div>
        ) : (
          <SourceList
            sources={sources}
            onDelete={handleDeleteSource}
            onTest={handleTestSource}
            onScrape={handleScrapeSource}
          />
        )}
      </main>
    </div>
  );
}

