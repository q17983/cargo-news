'use client';

import { useState } from 'react';

interface AddSourceFormProps {
  onSubmit: (data: { url: string; name?: string; autoScrape?: boolean }) => void;
  onCancel: () => void;
}

export default function AddSourceForm({ onSubmit, onCancel }: AddSourceFormProps) {
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [autoScrape, setAutoScrape] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      alert('Please enter a URL');
      return;
    }

    setLoading(true);
    try {
      await onSubmit({
        url: url.trim(),
        name: name.trim() || undefined,
        autoScrape: autoScrape,
      });
      setUrl('');
      setName('');
    } catch (error) {
      // Error handling is done in parent
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Add News Source</h3>

      <div className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
            URL *
          </label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.aircargonews.net/news"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Enter the news website URL. The system will automatically detect which scraper to use.
          </p>
          <p className="mt-1 text-xs text-amber-600">
            ⚠️ Note: Only sites with custom scrapers are fully supported. See SUPPORTED_SITES.md for the list.
          </p>
        </div>

        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Name (Optional)
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Air Cargo News"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="autoScrape"
            checked={autoScrape}
            onChange={(e) => setAutoScrape(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="autoScrape" className="ml-2 block text-sm text-gray-700">
            Automatically start scraping after adding
          </label>
        </div>
      </div>

      <div className="mt-6 flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Adding...' : 'Add Source'}
        </button>
      </div>
    </form>
  );
}

