'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import ArticleList from '../components/ArticleList';
import TagFilter from '../components/TagFilter';
import { fetchArticles, fetchTags, fetchSources } from '../lib/api';

export default function Home() {
  const [articles, setArticles] = useState<any[]>([]);
  const [allArticles, setAllArticles] = useState<any[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadArticles();
    loadTags();
    loadSources();
  }, [selectedTags]);

  useEffect(() => {
    // Filter articles by selected source
    if (selectedSource) {
      const filtered = allArticles.filter(
        article => article.source?.name === selectedSource || article.source?.domain === selectedSource
      );
      setArticles(filtered);
    } else {
      setArticles(allArticles);
    }
  }, [selectedSource, allArticles]);

  const loadArticles = async () => {
    try {
      setLoading(true);
      
      // Check cache first (for faster loading)
      const cacheKey = `articles_${selectedTags.join(',')}`;
      const cached = sessionStorage.getItem(cacheKey);
      if (cached) {
        const cachedData = JSON.parse(cached);
        // Use cache if less than 2 minutes old
        if (Date.now() - cachedData.timestamp < 2 * 60 * 1000) {
          setAllArticles(cachedData.data);
          setError(null);
          setLoading(false);
          
          // Store article IDs for navigation
          const ids = cachedData.data.map((a: any) => a.id);
          sessionStorage.setItem('articleIds', JSON.stringify(ids));
          
          // Load fresh data in background
          loadArticlesInBackground();
          return;
        }
      }
      
      // Fetch all articles (up to 1000 limit) - load in batches if needed
      let allArticlesData: any[] = [];
      let offset = 0;
      const batchSize = 1000; // Increased to load more articles per batch
      let hasMore = true;
      
      while (hasMore) {
        const batch = await fetchArticles({ 
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          limit: batchSize,
          offset: offset
        });
        
        if (batch.length === 0) {
          hasMore = false;
        } else {
          allArticlesData = [...allArticlesData, ...batch];
          offset += batchSize;
          
          // Stop if we got fewer articles than requested (last batch)
          if (batch.length < batchSize) {
            hasMore = false;
          }
        }
      }
      
      // Sort by published_date (newest first), fallback to created_at
      const sortedData = [...allArticlesData].sort((a, b) => {
        const dateA = a.published_date ? new Date(a.published_date).getTime() : new Date(a.created_at || a.scraped_at).getTime();
        const dateB = b.published_date ? new Date(b.published_date).getTime() : new Date(b.created_at || b.scraped_at).getTime();
        return dateB - dateA; // Newest first
      });
      
      setAllArticles(sortedData);
      
      // Cache the results
      sessionStorage.setItem(cacheKey, JSON.stringify({
        data: sortedData,
        timestamp: Date.now()
      }));
      
      // Store article IDs for navigation
      const ids = sortedData.map((a: any) => a.id);
      sessionStorage.setItem('articleIds', JSON.stringify(ids));
      
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  // Load articles in background to refresh cache
  const loadArticlesInBackground = async () => {
    try {
      const batch = await fetchArticles({ 
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        limit: 1000,
        offset: 0
      });
      
      if (batch.length > 0) {
        const sortedData = [...batch].sort((a, b) => {
          const dateA = a.published_date ? new Date(a.published_date).getTime() : new Date(a.created_at || a.scraped_at).getTime();
          const dateB = b.published_date ? new Date(b.published_date).getTime() : new Date(b.created_at || b.scraped_at).getTime();
          return dateB - dateA;
        });
        
        const cacheKey = `articles_${selectedTags.join(',')}`;
        sessionStorage.setItem(cacheKey, JSON.stringify({
          data: sortedData,
          timestamp: Date.now()
        }));
        
        const ids = sortedData.map((a: any) => a.id);
        sessionStorage.setItem('articleIds', JSON.stringify(ids));
      }
    } catch (err) {
      // Silent fail for background refresh
    }
  };

  const loadTags = async () => {
    try {
      const data = await fetchTags();
      setTags(data);
    } catch (err) {
      console.error('Failed to load tags:', err);
    }
  };

  const loadSources = async () => {
    try {
      const data = await fetchSources(true); // Only active sources
      setSources(data);
    } catch (err) {
      console.error('Failed to load sources:', err);
    }
  };

  // Get unique source names from articles
  const availableSources = Array.from(
    new Set(
      allArticles
        .map(a => a.source?.name || a.source?.domain)
        .filter(Boolean)
    )
  ).sort();

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
              <Link href="/bookmarks" className="text-gray-700 hover:text-gray-900">
                Bookmarks
              </Link>
              <Link href="/sources" className="text-gray-700 hover:text-gray-900">
                Sources
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Source Filter Tabs at Top */}
        <div className="mb-6 bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-gray-700 mr-2">Filter by Source:</span>
            <button
              onClick={() => setSelectedSource(null)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedSource === null
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All Sources ({allArticles.length})
            </button>
            {availableSources.map((sourceName) => {
              const count = allArticles.filter(
                a => a.source?.name === sourceName || a.source?.domain === sourceName
              ).length;
              return (
                <button
                  key={sourceName}
                  onClick={() => setSelectedSource(sourceName)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    selectedSource === sourceName
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {sourceName} ({count})
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex gap-8">
          <aside className="w-80 flex-shrink-0">
            <TagFilter
              tags={tags}
              selectedTags={selectedTags}
              onTagToggle={(tag) => {
                setSelectedTags(prev =>
                  prev.includes(tag)
                    ? prev.filter(t => t !== tag)
                    : [...prev, tag]
                );
              }}
            />
          </aside>

          <div className="flex-1">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {loading ? (
              <div className="text-center py-12">
                <p className="text-gray-500">Loading articles...</p>
              </div>
            ) : (
              <>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-900">
                    Articles ({articles.length})
                  </h2>
                  {selectedTags.length > 0 && (
                    <span className="text-sm text-gray-600">
                      Filtered by {selectedTags.length} tag{selectedTags.length !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>
                <ArticleList articles={articles} />
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
