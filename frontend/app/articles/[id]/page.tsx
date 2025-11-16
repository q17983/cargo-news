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
    // Save scroll position before navigating
    sessionStorage.setItem('articleListScrollPosition', window.scrollY.toString());
    router.push(`/articles/${articleId}`);
  };

  // Swipe handlers - improved to prevent false triggers during vertical scrolling
  const touchStartY = useRef<number>(0);
  const touchEndY = useRef<number>(0);
  const isScrolling = useRef<boolean>(false);

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
    touchStartY.current = e.touches[0].clientY;
    isScrolling.current = false;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX;
    touchEndY.current = e.touches[0].clientY;
    
    // Check if user is scrolling vertically (more vertical movement than horizontal)
    const verticalDistance = Math.abs(touchStartY.current - touchEndY.current);
    const horizontalDistance = Math.abs(touchStartX.current - touchEndX.current);
    
    // If vertical movement is significantly more than horizontal, it's a scroll
    if (verticalDistance > horizontalDistance * 1.5) {
      isScrolling.current = true;
    }
  };

  const handleTouchEnd = () => {
    if (!touchStartX.current || !touchEndX.current) return;
    
    // Don't trigger swipe if user was scrolling vertically
    if (isScrolling.current) {
      touchStartX.current = 0;
      touchEndX.current = 0;
      return;
    }
    
    const distance = touchStartX.current - touchEndX.current;
    const minSwipeDistance = 100; // Increased threshold for more intentional swipes

    if (distance > minSwipeDistance && nextArticleId) {
      // Swipe left - next article
      navigateToArticle(nextArticleId);
    } else if (distance < -minSwipeDistance && prevArticleId) {
      // Swipe right - previous article
      navigateToArticle(prevArticleId);
    }
    
    // Reset
    touchStartX.current = 0;
    touchEndX.current = 0;
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
    <div className="min-h-screen bg-white">
      {/* Mobile-First News App Style Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 safe-area-top">
        <div className="flex items-center justify-between h-14 px-4">
          <div className="flex items-center gap-3">
            <Link 
              href="/" 
              onClick={() => {
                // Save scroll position before going back
                sessionStorage.setItem('articleListScrollPosition', window.scrollY.toString());
              }}
              className="p-2 -ml-2 rounded-full active:bg-gray-100 transition-colors"
              aria-label="Back to articles"
            >
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Link>
            {currentIndex >= 0 && (
              <span className="text-xs text-gray-500 font-medium">
                {currentIndex + 1} / {articleIds.length}
              </span>
            )}
          </div>
          
          <button
            onClick={toggleBookmark}
            disabled={bookmarkLoading}
            className={`p-2 rounded-full transition-colors ${
              isBookmarked
                ? 'text-yellow-500 active:bg-yellow-50'
                : 'text-gray-400 active:bg-gray-100'
            } disabled:opacity-50`}
            aria-label={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
          >
            <svg className="w-6 h-6" fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>
        </div>
      </header>

      {/* Article Content - News App Style */}
      <article
        ref={articleRef}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        className="max-w-3xl mx-auto px-4 pb-20"
      >
        {/* 1. Translated Title (Chinese) */}
        <div className="pt-6 pb-4">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight mb-3">
            {article.title}
          </h1>
          
          {/* Date under title */}
          {(article.published_date || dateFromSummary) && (
            <div className="text-sm text-gray-500 mb-4">
              {article.published_date 
                ? format(new Date(article.published_date), 'yyyy年MM月dd日')
                : dateFromSummary}
            </div>
          )}
        </div>

        {/* 2. Summary Content */}
        {article.summary && (
          <div className="mb-6 pb-6 border-b border-gray-200">
            <div 
              className="prose prose-sm sm:prose-base max-w-none text-gray-700 leading-relaxed"
              style={{
                fontSize: '16px',
                lineHeight: '1.75',
              }}
              dangerouslySetInnerHTML={{ __html: article.summary.replace(/\n/g, '<br />') }}
            />
          </div>
        )}

        {/* 3. Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="mb-6 pb-6 border-b border-gray-200">
            <div className="flex flex-wrap gap-2">
              {article.tags.map((tag: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-xs font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 4. Website URL */}
        {article.url && (
          <div className="mb-6 pb-6 border-b border-gray-200">
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl active:bg-gray-100 transition-colors group"
            >
              <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 mb-1">原始文章</p>
                <p className="text-sm font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                  {article.url.replace(/^https?:\/\//, '').replace(/\/$/, '')}
                </p>
              </div>
              <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </a>
          </div>
        )}

        {/* 5. English Title */}
        {originalTitle && (
          <div className="mb-6 pb-6 border-b border-gray-200">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Original Title
            </h2>
            <h3 className="text-lg sm:text-xl font-semibold text-gray-900 leading-tight">
              {originalTitle}
            </h3>
          </div>
        )}

        {/* 6. Original Content */}
        {article.content && (
          <div className="mb-8">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">
              Full Article
            </h2>
            <div 
              className="prose prose-sm sm:prose-base max-w-none text-gray-700 leading-relaxed whitespace-pre-line"
              style={{
                fontSize: '15px',
                lineHeight: '1.75',
              }}
            >
              {article.content}
            </div>
          </div>
        )}

        {/* Swipe Hint */}
        <div className="fixed bottom-20 left-0 right-0 flex justify-center pointer-events-none">
          <div className="bg-black/70 text-white text-xs px-4 py-2 rounded-full backdrop-blur-sm">
            {prevArticleId && nextArticleId && '左右滑動切換文章'}
            {!prevArticleId && nextArticleId && '向左滑動查看下一篇文章'}
            {prevArticleId && !nextArticleId && '向右滑動查看上一篇文章'}
          </div>
        </div>
      </article>

      {/* Bottom Navigation Bar - Mobile Optimized */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-bottom z-40">
        <div className="max-w-3xl mx-auto flex items-center justify-between h-16 px-4">
          <button
            onClick={() => prevArticleId && navigateToArticle(prevArticleId)}
            disabled={!prevArticleId}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              prevArticleId
                ? 'text-gray-700 active:bg-gray-100'
                : 'text-gray-300 cursor-not-allowed'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="text-sm font-medium hidden sm:inline">上一則</span>
          </button>
          
          <div className="text-xs text-gray-500">
            {currentIndex >= 0 && `${currentIndex + 1} / ${articleIds.length}`}
          </div>
          
          <button
            onClick={() => nextArticleId && navigateToArticle(nextArticleId)}
            disabled={!nextArticleId}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              nextArticleId
                ? 'text-gray-700 active:bg-gray-100'
                : 'text-gray-300 cursor-not-allowed'
            }`}
          >
            <span className="text-sm font-medium hidden sm:inline">下一則</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </nav>
    </div>
  );
}
