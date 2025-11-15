'use client';

import { format } from 'date-fns';
import { useState, useEffect } from 'react';
import { getScrapingStatus } from '../lib/api';

interface Source {
  id: string;
  url: string;
  name?: string;
  is_active: boolean;
  created_at: string;
  listing_url?: string;
  scraper_type?: string;
  domain?: string;
  has_custom_scraper?: boolean;
}

interface ScrapingStatus {
  status: string;
  articles_found: number;
  created_at?: string;
  error_message?: string;
}

interface SourceListProps {
  sources: Source[];
  onDelete: (id: string) => void;
  onTest: (id: string) => void;
  onScrape: (id: string) => void;
}

export default function SourceList({ sources, onDelete, onTest, onScrape }: SourceListProps) {
  const [statuses, setStatuses] = useState<Record<string, ScrapingStatus>>({});
  const [loadingStatuses, setLoadingStatuses] = useState<Record<string, boolean>>({});

  // Load scraping statuses for all sources
  useEffect(() => {
    const loadStatuses = async () => {
      // Load statuses in parallel with timeout protection
      const statusPromises = sources.map(async (source) => {
        try {
          const status = await getScrapingStatus(source.id);
          return { sourceId: source.id, status };
        } catch (err) {
          console.error(`Error loading status for ${source.id}:`, err);
          return null;
        }
      });
      
      const results = await Promise.all(statusPromises);
      results.forEach(result => {
        if (result) {
          setStatuses(prev => ({ ...prev, [result.sourceId]: result.status }));
        }
      });
    };
    
    if (sources.length > 0) {
      loadStatuses();
      // Refresh status every 10 seconds
      const interval = setInterval(loadStatuses, 10000);
      return () => clearInterval(interval);
    }
  }, [sources]);

  if (sources.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No sources found. Add your first source to get started.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-x-auto w-full">
      <table className="w-full divide-y divide-gray-200" style={{ minWidth: '1000px' }}>
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Source URL
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Scraping URL
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Scraper
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sources.map((source) => (
            <tr key={source.id}>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">
                  {source.name || 'Unnamed Source'}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm text-gray-500 truncate max-w-xs" title={source.url}>
                  {source.url}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm text-blue-600 truncate max-w-xs" title={source.listing_url || source.url}>
                  {source.listing_url || source.url}
                </div>
                {source.listing_url && source.listing_url !== source.url && (
                  <div className="text-xs text-gray-400 mt-1">
                    (transformed)
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center">
                    <span className={`text-xs px-2 py-1 rounded ${
                      source.has_custom_scraper 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {source.scraper_type || 'Unknown'}
                    </span>
                    {!source.has_custom_scraper && (
                      <span className="ml-2 text-xs text-gray-500" title="Generic scraper may not work well">
                        ⚠️
                      </span>
                    )}
                  </div>
                  {statuses[source.id] && (
                    <div className="text-xs">
                      <div className="text-gray-500">
                        Last: {statuses[source.id].status === 'success' ? '✅' : statuses[source.id].status === 'failed' ? '❌' : '⚠️'} 
                        {statuses[source.id].articles_found} articles
                        {statuses[source.id].created_at && (
                          <span className="ml-1">
                            ({format(new Date(statuses[source.id].created_at!), 'MMM d, HH:mm')})
                          </span>
                        )}
                      </div>
                      {statuses[source.id].error_message && (
                        <div className="mt-1 text-red-600 text-xs max-w-xs truncate" title={statuses[source.id].error_message}>
                          ⚠️ {statuses[source.id].error_message}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    source.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {source.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {format(new Date(source.created_at), 'MMM d, yyyy')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium min-w-[200px]">
                <div className="flex items-center justify-end gap-2 flex-shrink-0">
                  <button
                    onClick={() => onScrape(source.id)}
                    className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded hover:bg-green-700 transition-colors shadow-sm"
                    title="Scrape this source now"
                  >
                    Scrape
                  </button>
                  <button
                    onClick={() => onTest(source.id)}
                    className="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors shadow-sm"
                    title="Test connection"
                  >
                    Test
                  </button>
                  <button
                    onClick={() => onDelete(source.id)}
                    className="px-3 py-1.5 bg-red-600 text-white text-xs font-medium rounded hover:bg-red-700 transition-colors shadow-sm"
                    title="Delete source"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

