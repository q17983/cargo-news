'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { fetchArticle } from '../../../lib/api';
import { format } from 'date-fns';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ArticleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [article, setArticle] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [bookmarkLoading, setBookmarkLoading] = useState(false);
  const [articleIds, setArticleIds] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [nextArticleId, setNextArticleId] = useState<string | null>(null);
  const [prevArticleId, setPrevArticleId] = useState<string | null>(null);
  const [prefetching, setPrefetching] = useState(false);
  
  // Swipe detection
  const touchStartX = useRef<number>(0);
  const touchEndX = useRef<number>(0);
  const articleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (params.id) {
      loadArticleIds();
      loadArticle(params.id as string);
      checkBookmark(params.id as string);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  // Load article IDs from sessionStorage or fetch from API
  const loadArticleIds = async () => {
    try {
      // Try to get from sessionStorage first (fast)
      const stored = sessionStorage.getItem('articleIds');
      if (stored) {
        const ids = JSON.parse(stored);
        setArticleIds(ids);
        const index = ids.indexOf(params.id as string);
        setCurrentIndex(index);
        if (index >= 0) {
          setNextArticleId(index < ids.length - 1 ? ids[index + 1] : null);
          setPrevArticleId(index > 0 ? ids[index - 1] : null);
        } else {
          // Article not in cached list, reload all IDs
          console.log('Article not in cached list, reloading...');
          // Continue to fetch all IDs below
        }
        // Only return if article was found in cache
        if (index >= 0) {
          return;
        }
      }

      // If not in sessionStorage, fetch ALL article IDs (in batches if needed)
      let allIds: string[] = [];
      let offset = 0;
      const batchSize = 1000; // Match the API limit
      let hasMore = true;

      while (hasMore) {
        const response = await fetch(`${API_URL}/api/articles?limit=${batchSize}&offset=${offset}`);
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const articles = await response.json();
        if (articles.length === 0) {
          hasMore = false;
        } else {
          const ids = articles.map((a: any) => a.id);
          allIds = [...allIds, ...ids];
          offset += batchSize;
          
          // Stop if we got fewer articles than requested (last batch)
          if (articles.length < batchSize) {
            hasMore = false;
          }
        }
      }

      // Store all IDs in sessionStorage
      sessionStorage.setItem('articleIds', JSON.stringify(allIds));
      setArticleIds(allIds);
      
      const index = allIds.indexOf(params.id as string);
      setCurrentIndex(index);
      if (index >= 0) {
        setNextArticleId(index < allIds.length - 1 ? allIds[index + 1] : null);
        setPrevArticleId(index > 0 ? allIds[index - 1] : null);
      } else {
        // Article not found in list, try to find it anyway
        setNextArticleId(null);
        setPrevArticleId(null);
      }
    } catch (err: any) {
      console.error('Error loading article IDs:', err);
      // Show error but don't break the page
      setError(err.message || 'Failed to load article navigation');
    }
  };

  const loadArticle = async (id: string) => {
    try {
      setLoading(true);
      
      // Check cache first
      const cached = sessionStorage.getItem(`article_${id}`);
      if (cached) {
        const cachedData = JSON.parse(cached);
        // Check if cache is fresh (less than 5 minutes old)
        if (Date.now() - cachedData.timestamp < 5 * 60 * 1000) {
          setArticle(cachedData.data);
          setLoading(false);
          // Prefetch next article in background
          prefetchNextArticle();
          return;
        }
      }
      
      const data = await fetchArticle(id);
      setArticle(data);
      
      // Cache the article
      sessionStorage.setItem(`article_${id}`, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
      
      setError(null);
      
      // Prefetch next article in background
      prefetchNextArticle();
    } catch (err: any) {
      setError(err.message || 'Failed to load article');
    } finally {
      setLoading(false);
    }
  };

  const prefetchNextArticle = async () => {
    if (nextArticleId && !prefetching) {
      setPrefetching(true);
      try {
        const response = await fetch(`${API_URL}/api/articles/${nextArticleId}`);
        if (response.ok) {
          const data = await response.json();
          // Cache the next article
          sessionStorage.setItem(`article_${nextArticleId}`, JSON.stringify({
            data,
            timestamp: Date.now()
          }));
        }
      } catch (err) {
        // Silent fail for prefetch
      } finally {
        setPrefetching(false);
      }
    }
  };

  const checkBookmark = async (articleId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/bookmarks/${articleId}`);
      if (response.ok) {
        const data = await response.json();
        setIsBookmarked(data.is_bookmarked || false);
      } else {
        setIsBookmarked(false);
      }
    } catch (err) {
      setIsBookmarked(false);
    }
  };

  const toggleBookmark = async () => {
    if (!article) return;
    
    setBookmarkLoading(true);
    try {
      if (isBookmarked) {
        const response = await fetch(`${API_URL}/api/bookmarks/${article.id}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          setIsBookmarked(false);
        }
      } else {
        const response = await fetch(`${API_URL}/api/bookmarks`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ article_id: article.id }),
        });
        if (response.ok) {
          setIsBookmarked(true);
        }
      }
    } catch (err: any) {
      console.error('Error toggling bookmark:', err);
      alert('Failed to update bookmark');
    } finally {
      setBookmarkLoading(false);
    }
  };

  const navigateToArticle = (articleId: string) => {
    router.push(`/articles/${articleId}`);
  };

  // Swipe handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX;
  };

  const handleTouchEnd = () => {
    if (!touchStartX.current || !touchEndX.current) return;
    
    const distance = touchStartX.current - touchEndX.current;
    const minSwipeDistance = 50;

    if (distance > minSwipeDistance && nextArticleId) {
      // Swipe left - next article
      navigateToArticle(nextArticleId);
    } else if (distance < -minSwipeDistance && prevArticleId) {
      // Swipe right - previous article
      navigateToArticle(prevArticleId);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft' && prevArticleId) {
        navigateToArticle(prevArticleId);
      } else if (e.key === 'ArrowRight' && nextArticleId) {
        navigateToArticle(nextArticleId);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [prevArticleId, nextArticleId]);

  // Extract original English title from summary
  const extractOriginalTitle = (summary: string): string | null => {
    if (!summary) return null;
    const match = summary.match(/標題[：:]\s*([^\n]+)/);
    if (match && match[1]) {
      const allMatches = [...summary.matchAll(/標題[：:]\s*([^\n]+)/g)];
      if (allMatches.length >= 2) {
        return allMatches[1][1].trim();
      }
    }
    return null;
  };

  // Extract date from summary
  const extractDateFromSummary = (summary: string): string | null => {
    if (!summary) return null;
    const match = summary.match(/新聞日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日|日期未標示)/);
    return match ? match[1] : null;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading article...</p>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Article not found'}</p>
          <Link href="/" className="text-blue-600 hover:underline">
            Back to Articles
          </Link>
        </div>
      </div>
    );
  }

  const originalTitle = extractOriginalTitle(article.summary || '');
  const dateFromSummary = extractDateFromSummary(article.summary || '');

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-blue-600 hover:underline">
                ← Back
              </Link>
              {currentIndex >= 0 && (
                <span className="text-sm text-gray-500">
                  {currentIndex + 1} / {articleIds.length}
                </span>
              )}
            </div>
            <button
              onClick={toggleBookmark}
              disabled={bookmarkLoading}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isBookmarked
                  ? 'bg-yellow-500 text-white hover:bg-yellow-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              } disabled:opacity-50`}
            >
              {bookmarkLoading ? '...' : isBookmarked ? '★ Bookmarked' : '☆ Bookmark'}
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Buttons */}
        <div className="mb-4 flex justify-between items-center">
          <button
            onClick={() => prevArticleId && navigateToArticle(prevArticleId)}
            disabled={!prevArticleId}
            className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              prevArticleId
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <span>←</span>
            <span>Previous</span>
          </button>
          
          <div className="text-sm text-gray-500">
            {prevArticleId || nextArticleId ? 'Use ← → arrow keys or swipe' : ''}
          </div>
          
          <button
            onClick={() => nextArticleId && navigateToArticle(nextArticleId)}
            disabled={!nextArticleId}
            className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              nextArticleId
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <span>Next</span>
            <span>→</span>
          </button>
        </div>

        <article
          ref={articleRef}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          className="bg-white rounded-lg shadow-md p-8"
        >
          {/* Chinese Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{article.title}</h1>

          {/* News Date under Chinese title */}
          {article.published_date ? (
            <div className="mb-6 text-sm text-gray-600">
              <span className="font-medium">發布日期：</span>
              {format(new Date(article.published_date), 'yyyy年MM月dd日')}
            </div>
          ) : dateFromSummary ? (
            <div className="mb-6 text-sm text-gray-600">
              <span className="font-medium">發布日期：</span>
              {dateFromSummary}
            </div>
          ) : null}

          {/* Website URL */}
          {article.url && (
            <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline font-medium flex items-center gap-2"
              >
                <span>🔗</span>
                <span className="truncate">{article.url}</span>
                <span className="text-xs text-blue-500">(在新視窗開啟)</span>
              </a>
            </div>
          )}

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="mb-6 flex flex-wrap gap-2">
              {article.tags.map((tag: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Summary */}
          {article.summary && (
            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">摘要</h2>
              <div
                className="prose max-w-none text-gray-700 whitespace-pre-line"
                dangerouslySetInnerHTML={{ __html: article.summary.replace(/\n/g, '<br />') }}
              />
            </div>
          )}

          {/* Full Content */}
          {article.content && (
            <div className="mb-8">
              {/* English Title above full content */}
              {originalTitle && (
                <div className="mb-4 p-4 bg-gray-50 border-l-4 border-gray-400 rounded">
                  <h3 className="text-lg font-semibold text-gray-700 mb-1">Original Title (English)</h3>
                  <p className="text-gray-900">{originalTitle}</p>
                </div>
              )}
              
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Full Content</h2>
              <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                {article.content}
              </div>
            </div>
          )}
        </article>

        {/* Bottom Navigation */}
        <div className="mt-6 flex justify-between items-center">
          <button
            onClick={() => prevArticleId && navigateToArticle(prevArticleId)}
            disabled={!prevArticleId}
            className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              prevArticleId
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <span>←</span>
            <span>Previous</span>
          </button>
          
          <button
            onClick={() => nextArticleId && navigateToArticle(nextArticleId)}
            disabled={!nextArticleId}
            className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              nextArticleId
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <span>Next</span>
            <span>→</span>
          </button>
        </div>
      </main>
    </div>
  );
}
