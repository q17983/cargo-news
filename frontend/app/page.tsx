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
  const [favoriteTags, setFavoriteTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load favorite tags from localStorage on mount
  useEffect(() => {
    const savedFavorites = localStorage.getItem('favoriteTags');
    if (savedFavorites) {
      try {
        setFavoriteTags(JSON.parse(savedFavorites));
      } catch (e) {
        console.error('Failed to load favorite tags:', e);
      }
    }
  }, []);

  // Save favorite tags to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('favoriteTags', JSON.stringify(favoriteTags));
  }, [favoriteTags]);

  // Restore filter settings from sessionStorage on mount
  useEffect(() => {
    const savedSource = sessionStorage.getItem('selectedSource');
    const savedTags = sessionStorage.getItem('selectedTags');
    const savedScrollPosition = sessionStorage.getItem('articleListScrollPosition');
    
    if (savedSource && savedSource !== 'null') {
      setSelectedSource(savedSource);
    }
    
    if (savedTags) {
      try {
        const tags = JSON.parse(savedTags);
        if (Array.isArray(tags) && tags.length > 0) {
          setSelectedTags(tags);
        }
      } catch (e) {
        console.error('Failed to load selected tags:', e);
      }
    }
    
    // Restore scroll position after articles are loaded
    if (savedScrollPosition && !loading) {
      setTimeout(() => {
        window.scrollTo(0, parseInt(savedScrollPosition, 10));
      }, 200);
    }
  }, [loading]);

  // Save filter settings to sessionStorage whenever they change
  useEffect(() => {
    sessionStorage.setItem('selectedSource', selectedSource || 'null');
  }, [selectedSource]);

  useEffect(() => {
    sessionStorage.setItem('selectedTags', JSON.stringify(selectedTags));
  }, [selectedTags]);

  // Restore scroll position on mount
  useEffect(() => {
    const savedScrollPosition = sessionStorage.getItem('articleListScrollPosition');
    if (savedScrollPosition && !loading) {
      // Restore scroll position after articles are loaded
      setTimeout(() => {
        window.scrollTo(0, parseInt(savedScrollPosition, 10));
      }, 100);
    }
  }, [loading]);

  // Save scroll position before navigation
  useEffect(() => {
    const handleBeforeUnload = () => {
      sessionStorage.setItem('articleListScrollPosition', window.scrollY.toString());
    };
    
    const handleScroll = () => {
      // Throttle scroll position saving
      clearTimeout((window as any).scrollSaveTimeout);
      (window as any).scrollSaveTimeout = setTimeout(() => {
        sessionStorage.setItem('articleListScrollPosition', window.scrollY.toString());
      }, 500);
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  useEffect(() => {
    // Load data with error handling - optimized for speed
    const loadAll = async () => {
      try {
        // Load articles FIRST (most important) - show immediately
        loadArticles().catch(err => {
          console.error('Failed to load articles:', err);
          setError(`Failed to load articles: ${err.message}`);
        });
        
        // Load sources and tags in parallel (non-blocking)
        Promise.all([
          loadSources().catch(err => console.error('Failed to load sources:', err)),
          loadTags().catch(err => console.error('Failed to load tags:', err))
        ]);
      } catch (err: any) {
        console.error('Failed to load initial data:', err);
        setError(`Failed to load data: ${err.message}`);
        setLoading(false);
      }
    };
    
    loadAll();
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
      setError(null);
      
      // Check cache first - ALWAYS use cache if available (even with tags)
      const baseCacheKey = 'articles_all';
      const cached = sessionStorage.getItem(baseCacheKey);
      
      if (cached) {
        try {
          const cachedData = JSON.parse(cached);
          // Use cache if less than 10 minutes old (increased for better UX)
          if (Date.now() - cachedData.timestamp < 10 * 60 * 1000) {
            let articlesToShow = cachedData.data;
            
            // Filter by tags client-side if tags are selected
            if (selectedTags.length > 0) {
              articlesToShow = cachedData.data.filter((article: any) => {
                const articleTags = (article.tags || []).map((t: string) => t.toLowerCase());
                const selectedTagsLower = selectedTags.map(t => t.toLowerCase());
                return selectedTagsLower.some(tag => articleTags.includes(tag));
              });
            }
            
            // Show cached results IMMEDIATELY (instant)
            setAllArticles(articlesToShow);
            setError(null);
            setLoading(false);
            
            // Store article IDs
            const ids = articlesToShow.map((a: any) => a.id);
            sessionStorage.setItem('articleIds', JSON.stringify(ids));
            
            // Load fresh data in background (non-blocking)
            loadArticlesInBackground();
            return;
          }
        } catch (e) {
          console.warn('Failed to parse cache:', e);
          // Continue to fetch fresh data
        }
      }
      
      // If no cache, fetch fresh data
      const initialBatchSize = 300; // Load enough articles for filtering
      
      try {
        // Fetch WITHOUT tag filter - much faster
        const allArticlesData = await fetchArticles({ 
          limit: initialBatchSize,
          offset: 0
        });
        
        // Sort articles
        const sortedData = [...allArticlesData].sort((a, b) => {
          const dateA = a.published_date ? new Date(a.published_date).getTime() : new Date(a.created_at || a.scraped_at).getTime();
          const dateB = b.published_date ? new Date(b.published_date).getTime() : new Date(b.created_at || b.scraped_at).getTime();
          return dateB - dateA;
        });
        
        // Filter by tags client-side if tags are selected
        let filteredData = sortedData;
        if (selectedTags.length > 0) {
          filteredData = sortedData.filter(article => {
            const articleTags = (article.tags || []).map((t: string) => t.toLowerCase());
            const selectedTagsLower = selectedTags.map(t => t.toLowerCase());
            return selectedTagsLower.some(tag => articleTags.includes(tag));
          });
        }
        
        // Show results immediately
        setAllArticles(filteredData);
        setError(null);
        setLoading(false);
        
        // Store article IDs
        const ids = filteredData.map((a: any) => a.id);
        sessionStorage.setItem('articleIds', JSON.stringify(ids));
        
        // Cache all articles (without tag filter) for faster subsequent loads
        sessionStorage.setItem(baseCacheKey, JSON.stringify({
          data: sortedData,
          timestamp: Date.now()
        }));
        
        // Load remaining articles in background if needed
        if (allArticlesData.length >= initialBatchSize) {
          loadRemainingArticles(initialBatchSize);
        }
      } catch (err: any) {
        console.error('Error loading articles:', err);
        setError(err.message || 'Failed to load articles');
        setAllArticles([]);
        setLoading(false);
      }
    } catch (err: any) {
      console.error('Error in loadArticles:', err);
      setError(err.message || 'Failed to load articles');
      setAllArticles([]);
      setLoading(false);
    }
  };

  // Load remaining articles in background
  const loadRemainingArticles = async (startOffset: number) => {
    try {
      // Get current articles from state
      let allArticlesData: any[] = [];
      setAllArticles(currentArticles => {
        allArticlesData = [...currentArticles];
        return currentArticles;
      });
      
      let offset = startOffset;
      const batchSize = 200;
      let hasMore = true;
      const maxBatches = 20;
      let batchCount = 0;
      
      while (hasMore && batchCount < maxBatches) {
        try {
          // Fetch WITHOUT tag filter - filter client-side
          const batch = await fetchArticles({ 
            limit: batchSize,
            offset: offset
          });
          
          if (batch.length === 0) {
            hasMore = false;
          } else {
            // Add to all articles
            allArticlesData = [...allArticlesData, ...batch];
            offset += batchSize;
            batchCount++;
            
            // Filter by tags if needed
            let filteredData = allArticlesData;
            if (selectedTags.length > 0) {
              filteredData = allArticlesData.filter(article => {
                const articleTags = (article.tags || []).map((t: string) => t.toLowerCase());
                const selectedTagsLower = selectedTags.map(t => t.toLowerCase());
                return selectedTagsLower.some(tag => articleTags.includes(tag));
              });
            }
            
            // Sort and update state
            const sortedData = [...filteredData].sort((a, b) => {
              const dateA = a.published_date ? new Date(a.published_date).getTime() : new Date(a.created_at || a.scraped_at).getTime();
              const dateB = b.published_date ? new Date(b.published_date).getTime() : new Date(b.created_at || b.scraped_at).getTime();
              return dateB - dateA;
            });
            
            setAllArticles(sortedData);
            
            // Update article IDs
            const ids = sortedData.map((a: any) => a.id);
            sessionStorage.setItem('articleIds', JSON.stringify(ids));
            
            // Update base cache
            const sortedAll = [...allArticlesData].sort((a, b) => {
              const dateA = a.published_date ? new Date(a.published_date).getTime() : new Date(a.created_at || a.scraped_at).getTime();
              const dateB = b.published_date ? new Date(b.published_date).getTime() : new Date(b.created_at || b.scraped_at).getTime();
              return dateB - dateA;
            });
            sessionStorage.setItem('articles_all', JSON.stringify({
              data: sortedAll,
              timestamp: Date.now()
            }));
            
            if (batch.length < batchSize) {
              hasMore = false;
            }
          }
        } catch (err) {
          console.warn(`Failed to fetch batch at offset ${offset}:`, err);
          hasMore = false;
        }
      }
    } catch (err) {
      console.warn('Failed to load remaining articles:', err);
    }
  };

  // Load articles in background to refresh cache
  const loadArticlesInBackground = async () => {
    try {
      // Fetch WITHOUT tag filter - we'll filter client-side
      const batch = await fetchArticles({ 
        limit: 1000,
        offset: 0
      });
      
      if (batch.length > 0) {
        const sortedData = [...batch].sort((a, b) => {
          const dateA = a.published_date ? new Date(a.published_date).getTime() : new Date(a.created_at || a.scraped_at).getTime();
          const dateB = b.published_date ? new Date(b.published_date).getTime() : new Date(b.created_at || b.scraped_at).getTime();
          return dateB - dateA;
        });
        
        // Update base cache
        sessionStorage.setItem('articles_all', JSON.stringify({
          data: sortedData,
          timestamp: Date.now()
        }));
        
        // Filter and update current articles if tags are selected
        if (selectedTags.length > 0) {
          const filteredData = sortedData.filter(article => {
            const articleTags = (article.tags || []).map((t: string) => t.toLowerCase());
            const selectedTagsLower = selectedTags.map(t => t.toLowerCase());
            return selectedTagsLower.some(tag => articleTags.includes(tag));
          });
          
          setAllArticles(filteredData);
          const ids = filteredData.map((a: any) => a.id);
          sessionStorage.setItem('articleIds', JSON.stringify(ids));
        } else {
          setAllArticles(sortedData);
          const ids = sortedData.map((a: any) => a.id);
          sessionStorage.setItem('articleIds', JSON.stringify(ids));
        }
      }
    } catch (err) {
      // Silent fail for background refresh
      console.warn('Background refresh failed:', err);
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
    <div className="min-h-screen bg-white">
      {/* Mobile-First Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 safe-area-top">
        <div className="px-4 h-14 flex items-center justify-between">
          <h1 className="text-lg font-bold text-gray-900">Cargo News</h1>
          <div className="flex items-center gap-4">
            <Link 
              href="/bookmarks" 
              className="p-2 rounded-full active:bg-gray-100 transition-colors"
              aria-label="Bookmarks"
            >
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </Link>
            <Link 
              href="/sources" 
              className="p-2 rounded-full active:bg-gray-100 transition-colors"
              aria-label="Sources"
            >
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </Link>
          </div>
        </div>
      </header>

      <main className="pb-4">
        {/* Source Filter Tabs + Favorite Tags - Mobile Optimized */}
        <div className="sticky top-14 z-40 bg-white border-b border-gray-200">
          {/* Source Tabs */}
          <div className="px-4 py-3 overflow-x-auto border-b border-gray-100">
            <div className="flex items-center gap-2 min-w-max">
              <button
                onClick={() => setSelectedSource(null)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                  selectedSource === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 active:bg-gray-200'
                }`}
              >
                全部 ({allArticles.length})
              </button>
              {availableSources.map((sourceName) => {
                const count = allArticles.filter(
                  a => a.source?.name === sourceName || a.source?.domain === sourceName
                ).length;
                return (
                  <button
                    key={sourceName}
                    onClick={() => setSelectedSource(sourceName)}
                    className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                      selectedSource === sourceName
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 active:bg-gray-200'
                    }`}
                  >
                    {sourceName} ({count})
                  </button>
                );
              })}
            </div>
          </div>

          {/* Favorite Tags Quick Filter */}
          {favoriteTags.length > 0 && (
            <div className="px-4 py-2 overflow-x-auto bg-blue-50/50">
              <div className="flex items-center gap-2 min-w-max">
                <span className="text-xs font-medium text-gray-600 whitespace-nowrap">常用標籤:</span>
                {favoriteTags.map((tag) => {
                  const isSelected = selectedTags.includes(tag);
                  return (
                    <button
                      key={tag}
                      onClick={() => {
                        if (isSelected) {
                          setSelectedTags(prev => prev.filter(t => t !== tag));
                        } else {
                          setSelectedTags(prev => [...prev, tag]);
                        }
                      }}
                      className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 ${
                        isSelected
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-700 border border-gray-300 active:bg-gray-100'
                      }`}
                    >
                      {tag}
                      {isSelected && (
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Tag Filter - Mobile Drawer Style */}
        {selectedTags.length > 0 && (
          <div className="px-4 py-3 bg-blue-50 border-b border-blue-100">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-medium text-blue-700">已選標籤:</span>
              {selectedTags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => {
                    setSelectedTags(prev => prev.filter(t => t !== tag));
                  }}
                  className="px-3 py-1 bg-blue-600 text-white rounded-full text-xs font-medium active:bg-blue-700 flex items-center gap-1"
                >
                  {tag}
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              ))}
              <button
                onClick={() => setSelectedTags([])}
                className="text-xs text-blue-600 font-medium active:text-blue-700"
              >
                清除全部
              </button>
            </div>
          </div>
        )}

        {/* Articles List */}
        <div className="px-4">
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-500 text-sm">載入文章中...</p>
            </div>
          ) : (
            <>
              {selectedTags.length > 0 && (
                <div className="mt-4 mb-2 text-sm text-gray-600">
                  已篩選 {articles.length} 篇文章
                </div>
              )}
              <ArticleList articles={articles} />
            </>
          )}
        </div>

        {/* Tag Filter Button - Floating on Mobile */}
        {tags.length > 0 && (
          <div className="fixed bottom-20 right-4 z-30 sm:hidden">
            <button
              onClick={() => {
                const modal = document.getElementById('tag-filter-modal');
                if (modal) {
                  modal.classList.remove('hidden');
                }
              }}
              className="w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg active:bg-blue-700 flex items-center justify-center"
              aria-label="Filter by tags"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
            </button>
          </div>
        )}

        {/* Tag Filter Modal - Mobile Only */}
        <div 
          id="tag-filter-modal" 
          className="hidden sm:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              e.currentTarget.classList.add('hidden');
            }
          }}
        >
          <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl max-h-[80vh] overflow-hidden flex flex-col safe-area-bottom">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">篩選標籤</h3>
              <button
                onClick={() => {
                  const modal = document.getElementById('tag-filter-modal');
                  if (modal) {
                    modal.classList.add('hidden');
                  }
                }}
                className="p-2 rounded-full active:bg-gray-100"
                aria-label="Close"
              >
                <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <TagFilter
                tags={tags}
                selectedTags={selectedTags}
                favoriteTags={favoriteTags}
                onTagToggle={(tag) => {
                  setSelectedTags(prev =>
                    prev.includes(tag)
                      ? prev.filter(t => t !== tag)
                      : [...prev, tag]
                  );
                }}
                onFavoriteToggle={(tag) => {
                  setFavoriteTags(prev =>
                    prev.includes(tag)
                      ? prev.filter(t => t !== tag)
                      : [...prev, tag]
                  );
                }}
              />
            </div>
          </div>
        </div>

        {/* Tag Filter Section - Desktop Only */}
        <div className="hidden sm:block fixed top-14 right-0 w-80 h-[calc(100vh-3.5rem)] overflow-y-auto border-l border-gray-200 bg-white p-4">
          <TagFilter
            tags={tags}
            selectedTags={selectedTags}
            favoriteTags={favoriteTags}
            onTagToggle={(tag) => {
              setSelectedTags(prev =>
                prev.includes(tag)
                  ? prev.filter(t => t !== tag)
                  : [...prev, tag]
              );
            }}
            onFavoriteToggle={(tag) => {
              setFavoriteTags(prev =>
                prev.includes(tag)
                  ? prev.filter(t => t !== tag)
                  : [...prev, tag]
              );
            }}
          />
        </div>
      </main>
    </div>
  );
}
