'use client';

import { useState, useMemo } from 'react';

interface TagFilterProps {
  tags: string[];
  selectedTags: string[];
  onTagToggle: (tag: string) => void;
}

// Define tag categories based on the Gemini prompt structure
const TAG_CATEGORIES = {
  '主要主題': [
    '市場分析',
    '公司動態',
    '機場與基礎設施',
    '數位與科技',
    '永續發展',
    '特殊貨物',
    '法規與安全',
    '人事任命',
  ],
  '地理區域': [
    '亞洲',
    '歐洲',
    '北美',
    '中東',
    '亞太地區',
    '跨太平洋',
    '大西洋',
    '亞歐貿易',
  ],
  '公司/機場': [
    'FedEx',
    'DHL',
    'Lufthansa',
    'IAG Cargo',
    'Cathay Pacific',
    'Singapore Airlines',
    'Emirates',
    'Qatar Airways',
    'WFS',
    'Swissport',
  ],
};

export default function TagFilter({ tags, selectedTags, onTagToggle }: TagFilterProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'categories' | 'search'>('categories');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['主要主題']));

  // Filter tags by search query
  const filteredTags = useMemo(() => {
    if (!searchQuery.trim()) return tags;
    const query = searchQuery.toLowerCase();
    return tags.filter(tag => tag.toLowerCase().includes(query));
  }, [tags, searchQuery]);

  // Group tags by category
  const categorizedTags = useMemo(() => {
    const categorized: { [key: string]: string[] } = {
      '主要主題': [],
      '地理區域': [],
      '公司/機場': [],
      '其他': [],
    };

    tags.forEach(tag => {
      let found = false;
      for (const [category, keywords] of Object.entries(TAG_CATEGORIES)) {
        if (keywords.some(keyword => tag.includes(keyword))) {
          if (!categorized[category]) categorized[category] = [];
          categorized[category].push(tag);
          found = true;
          break;
        }
      }
      if (!found) {
        categorized['其他'].push(tag);
      }
    });

    // Sort each category
    Object.keys(categorized).forEach(key => {
      categorized[key].sort();
    });

    return categorized;
  }, [tags]);

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  return (
    <div className="bg-white">
      <h3 className="text-lg font-semibold text-gray-900 mb-2 hidden sm:block">Filter by Tags</h3>
      <p className="text-xs text-gray-500 mb-4 hidden sm:block">({tags.length} total tags)</p>

      {/* Tab Selection */}
      <div className="flex gap-2 mb-4 border-b">
        <button
          onClick={() => setActiveTab('categories')}
          className={`px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === 'categories'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Categories
        </button>
        <button
          onClick={() => setActiveTab('search')}
          className={`px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === 'search'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Search
        </button>
        <button
          onClick={() => setActiveTab('all')}
          className={`px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === 'all'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          All
        </button>
      </div>

      {/* Solution 1: Category-based filtering */}
      {activeTab === 'categories' && (
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {Object.entries(categorizedTags).map(([category, categoryTags]) => {
            if (categoryTags.length === 0) return null;
            
            const isExpanded = expandedCategories.has(category);
            
            return (
              <div key={category} className="border rounded-lg">
                <button
                  onClick={() => toggleCategory(category)}
                  className="w-full px-3 py-2 text-left font-medium text-gray-900 bg-gray-50 hover:bg-gray-100 flex items-center justify-between"
                >
                  <span>{category} ({categoryTags.length})</span>
                  <span className="text-gray-500">{isExpanded ? '▼' : '▶'}</span>
                </button>
                
                {isExpanded && (
                  <div className="p-2 space-y-1 max-h-48 overflow-y-auto">
                    {categoryTags.map((tag) => {
                      const isSelected = selectedTags.includes(tag);
                      return (
                        <button
                          key={tag}
                          onClick={() => onTagToggle(tag)}
                          className={`w-full text-left px-2 py-1 rounded text-xs transition-colors ${
                            isSelected
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {tag}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Solution 2: Search-based filtering */}
      {activeTab === 'search' && (
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Search tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          <div className="space-y-1 max-h-[500px] overflow-y-auto">
            {filteredTags.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-4">No tags found</p>
            ) : (
              filteredTags.map((tag) => {
                const isSelected = selectedTags.includes(tag);
                return (
                  <button
                    key={tag}
                    onClick={() => onTagToggle(tag)}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                      isSelected
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {tag}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* All tags view (scrollable) */}
      {activeTab === 'all' && (
        <div className="space-y-1 max-h-[600px] overflow-y-auto">
          {tags.map((tag) => {
            const isSelected = selectedTags.includes(tag);
            return (
              <button
                key={tag}
                onClick={() => onTagToggle(tag)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                  isSelected
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tag}
              </button>
            );
          })}
        </div>
      )}

      {/* Selected tags summary */}
      {selectedTags.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {selectedTags.length} selected
            </span>
            <button
              onClick={() => selectedTags.forEach(onTagToggle)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Clear all
            </button>
          </div>
          <div className="flex flex-wrap gap-1">
            {selectedTags.slice(0, 5).map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
              >
                {tag}
              </span>
            ))}
            {selectedTags.length > 5 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                +{selectedTags.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
