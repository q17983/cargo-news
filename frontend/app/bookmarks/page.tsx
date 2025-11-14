'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import ArticleList from '@/components/ArticleList';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function BookmarksPage() {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/bookmarks`);
      if (!response.ok) {
        throw new Error('Failed to load bookmarks');
      }
      const data = await response.json();
      
      // Extract articles from bookmark objects
      const bookmarkedArticles = data.map((bookmark: any) => ({
        ...bookmark.article,
        bookmark_id: bookmark.id,
        bookmarked_at: bookmark.created_at
      }));
      
      // Sort by bookmarked date (newest first)
      bookmarkedArticles.sort((a: any, b: any) => {
        const dateA = new Date(a.bookmarked_at).getTime();
        const dateB = new Date(b.bookmarked_at).getTime();
        return dateB - dateA;
      });
      
      setArticles(bookmarkedArticles);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load bookmarks');
    } finally {
      setLoading(false);
    }
  };

  const removeBookmark = async (articleId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/bookmarks/${articleId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        // Remove from local state
        setArticles(articles.filter(a => a.id !== articleId));
      }
    } catch (err) {
      console.error('Error removing bookmark:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-blue-600 hover:underline">
                ← Back to Articles
              </Link>
              <h1 className="text-xl font-bold text-gray-900">Bookmarked Articles</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading bookmarks...</p>
          </div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Saved Articles ({articles.length})
              </h2>
            </div>
            
            {articles.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow-md">
                <p className="text-gray-500 mb-4">No bookmarked articles yet.</p>
                <Link href="/" className="text-blue-600 hover:underline">
                  Browse articles to bookmark
                </Link>
              </div>
            ) : (
              <ArticleList articles={articles} />
            )}
          </>
        )}
      </main>
    </div>
  );
}

