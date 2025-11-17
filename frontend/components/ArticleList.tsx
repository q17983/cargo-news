'use client';

import Link from 'next/link';
import { format } from 'date-fns';
import { useEffect, useRef } from 'react';

interface Article {
  id: string;
  title: string;
  summary?: string;
  tags?: string[];
  published_date?: string;
  scraped_at: string;
  url?: string;
  source?: {
    id: string;
    name: string;
    url: string;
    domain: string;
  };
}

interface ArticleListProps {
  articles: Article[];
}

export default function ArticleList({ articles }: ArticleListProps) {
  const listRef = useRef<HTMLDivElement>(null);

  // Save scroll position when clicking an article
  const handleArticleClick = () => {
    sessionStorage.setItem('articleListScrollPosition', window.scrollY.toString());
  };

  // Force layout recalculation when articles change
  useEffect(() => {
    // Trigger a reflow to fix layout issues
    if (listRef.current) {
      void listRef.current.offsetHeight;
    }
  }, [articles]);

  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No articles found.</p>
      </div>
    );
  }

  // Display articles in news app style (mobile-first)
  return (
    <div ref={listRef} key={articles.length} className="space-y-3 py-4">
      {articles.map((article) => (
        <Link
          key={article.id}
          href={`/articles/${article.id}`}
          onClick={handleArticleClick}
          className="block bg-white rounded-2xl p-4 active:bg-gray-50 transition-colors border border-gray-100"
          prefetch={true}
        >
          {/* Source and Date Row */}
          <div className="flex items-center justify-between mb-2">
            {article.source && (
              <span className="text-xs font-medium text-gray-500">
                {article.source.name || article.source.domain}
              </span>
            )}
            <span className="text-xs text-gray-400">
              {article.published_date 
                ? format(new Date(article.published_date), 'MMM d')
                : 'No date'}
            </span>
          </div>

          {/* Title */}
          <h3 className="text-base font-bold text-gray-900 mb-2 line-clamp-2 leading-snug">
            {article.title}
          </h3>

          {/* Summary Preview */}
          {article.summary && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2 leading-relaxed">
              {article.summary.replace(/標題[：:].*?\n/g, '').replace(/來源[：:].*?\n/g, '').substring(0, 120)}...
            </p>
          )}

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {article.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-md text-xs font-medium"
                >
                  {tag}
                </span>
              ))}
              {article.tags.length > 3 && (
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-xs">
                  +{article.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}
