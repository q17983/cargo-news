'use client';

import Link from 'next/link';
import { format } from 'date-fns';

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
  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No articles found.</p>
      </div>
    );
  }

  // Display articles in a simple list (source filtering is done at page level)
  return (
    <div className="space-y-4">
      {articles.map((article) => (
        <Link
          key={article.id}
          href={`/articles/${article.id}`}
          className="block bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border-l-4 border-blue-500"
          prefetch={true}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              {/* Source badge */}
              {article.source && (
                <span className="inline-block px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs mb-2">
                  {article.source.name || article.source.domain}
                </span>
              )}
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {article.title}
              </h3>

              {article.summary && (
                <p className="text-gray-600 mb-3 line-clamp-2 text-sm">
                  {article.summary.substring(0, 200)}...
                </p>
              )}

              <div className="flex flex-wrap gap-2 mb-2">
                {article.tags && article.tags.slice(0, 5).map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                  >
                    {tag}
                  </span>
                ))}
                {article.tags && article.tags.length > 5 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                    +{article.tags.length - 5} more
                  </span>
                )}
              </div>
            </div>

            <div className="text-sm text-gray-500 whitespace-nowrap">
              {article.published_date ? (
                <span>{format(new Date(article.published_date), 'MMM d, yyyy')}</span>
              ) : (
                <span className="text-gray-400">No date</span>
              )}
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
