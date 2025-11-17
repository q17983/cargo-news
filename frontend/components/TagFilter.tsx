'use client';

import { useState, useMemo } from 'react';

interface TagFilterProps {
  tags: string[];
  selectedTags: string[];
  favoriteTags?: string[];
  onTagToggle: (tag: string) => void;
  onFavoriteToggle?: (tag: string) => void;
}

// Define tag categories - FOCUSED for cargo brokers (Special Cargo & Charter priority)
const TAG_CATEGORIES = {
  '特殊貨物與包機': [
    // Special Cargo - HIGH PRIORITY for cargo brokers
    '特殊貨物', 'Special Cargo', '冷鏈', 'Cold Chain', '冷鏈物流', '醫藥冷鏈', '溫控運輸',
    '活體動物', '危險品', '貴重物品', '醫療貨物', '花卉產業', 'Pharma', 'Pharmaceutical',
    'Perishable', 'Temperature Controlled', 'Live Animals', 'Dangerous Goods', 'Hazmat',
    // Charter - HIGH PRIORITY for cargo brokers
    '包機', 'Charter', '包機服務', 'Charter Service', 'ACMI', 'Wet Lease', 'Dry Lease',
    'Cargo Charter', 'Freight Charter', '空運包機', '貨運包機',
  ],
  '市場分析': [
    // Market & Analysis - ONLY specific analysis terms
    '市場分析', 'Market Analysis', '貨量報告', '市場預測', '貿易數據', '運費率', '費率管理',
    '收益率', '貨運量', '貨運量增長', '空運量', '運力', '運力限制', 'Market Data', 'Freight Rates',
  ],
  '公司動態': [
    // Company News - ONLY specific company-related terms
    '公司動態', 'Company News', '併購', '收購', '財務報告', '策略調整', '投資', 'IPO', '首次公開募股',
    'Merger', 'Acquisition', 'Financial', 'Strategy', 'Investment',
  ],
  '機場與基礎設施': [
    // Infrastructure - ONLY infrastructure terms (NOT generic logistics)
    '機場與基礎設施', 'Airports & Infrastructure', '基礎設施', 'Infrastructure', '物流基礎設施',
    '機場', '機場創新', '機場地面服務', '機場發展', '倉儲', 'Warehouse', 'Warehousing',
  ],
  '數位與科技': [
    // Digital & Tech - ONLY tech-specific terms
    '數位與科技', 'Digital & Tech', '數位化', '數位工具', '數位科技', '數位行銷', '數位轉型',
    'Digital', 'Tech', '人工智慧', 'AI', '自動化', '物聯網', '電子商務', 'e-commerce',
    'Automation', 'IoT', 'E-commerce', 'Platform', 'Software', 'System',
  ],
  '永續發展': [
    // Sustainability
    '永續發展', 'Sustainability', '永續', 'SAF', '減碳', '碳排放', '環保措施', '脫碳',
    'Carbon', 'Emissions', 'Green', 'ESG',
  ],
  '法規與安全': [
    // Regulation & Security
    '法規與安全', 'Regulation & Security', '法規', '安全', 'Security', '航空安全', '飛行安全', '跑道安全', '網路安全',
    '海關', '清關', '海關清關', '貿易協定', '貿易戰', '關稅', 'Customs', 'Clearance', 'Regulation',
  ],
  '人事任命': [
    // People & Appointments
    '人事任命', 'People & Appointments', '人事', '任命', '領導層變更', '領導變革', 'Appointment', 'Leadership',
  ],
  '地理區域': [
    '亞洲', 'Asia', 'Asian', '亞太地區', 'Asia Pacific', 'APAC',
    '歐洲', 'Europe', 'European',
    '北美', 'North America', 'North American', '美國', '美國市場', '加拿大',
    '中東', 'Middle East',
    '跨太平洋', 'Trans-Pacific', '跨大西洋', 'Trans-Atlantic', '大西洋', 'Atlantic',
    '亞歐貿易', 'Asia-Europe', '亞歐航線', '亞洲-歐洲', '亞洲內部',
    '南美', 'Latin America', '拉丁美洲', '非洲', 'Africa', '澳洲', 'Australia',
    '中國', '印度', '新加坡', '香港', '台灣', '韓國', '日本', '泰國', '馬來西亞',
    '英國', '德國', '法國', '瑞士', '波蘭', '土耳其', '埃及', '巴西', '墨西哥', '智利',
    '東南亞', '加勒比地區', '太平洋航線',
  ],
  '公司/機場': [
    // Major Airlines
    'FedEx', 'DHL', 'UPS', 'Lufthansa', 'IAG Cargo', 'Cathay Pacific', 'Singapore Airlines',
    'Emirates', 'Qatar Airways', 'British Airways', 'Air France', 'KLM', 'Turkish Airlines',
    'Korean Air', 'Japan Airlines', 'ANA', 'China Airlines', 'EVA Air', 'Thai Airways',
    'Air China', 'China Southern', 'China Eastern', 'United Airlines', 'American Airlines',
    'Delta Air Lines', 'Atlas Air', 'Kalitta Air', 'Cargolux', 'AirBridgeCargo',
    'Volga-Dnepr', 'Nippon Cargo', 'Polar Air Cargo', 'Southern Air', 'Western Global',
    // Additional Airlines (from "其他" category)
    'Airbus', 'Boeing', 'Amazon Air', 'Avianca', 'IndiGo', 'Iberia', 'Etihad', 'Etihad Airways',
    'Etihad Cargo', 'Royal Air Maroc', 'Royal Brunei', 'Kenya Airways', 'LOT Polish',
    'ITA Airways', 'Sun Country', 'WestJet', 'Cargojet', 'Central Airlines', 'Hungary Airlines',
    'Air Astana', 'Air Atlanta', 'Air Canada', 'Air Menzies', 'Ascend Airways', 'Astral Aviation',
    'Challenge Group', 'Magma Aviation', 'Mammoth Freighters', 'MNG Airlines', 'Swiftair',
    'One Air', 'Skye Air', 'Riyadh Air', 'Aerion', 'Eve Air Mobility', 'ZeroAvia',
    // Airports (English)
    'Heathrow', 'JFK', 'LAX', 'CDG', 'Frankfurt', 'Amsterdam', 'Dubai', 'Singapore Changi',
    'Hong Kong International', 'Narita', 'Haneda', 'Incheon', 'Miami', 'Chicago O\'Hare',
    'Atlanta', 'Dallas', 'Memphis', 'Louisville', 'Anchorage', 'Liege', 'Luxembourg',
    'Billund', 'Glasgow Prestwick', 'Halifax Stanfield', 'Hamilton', 'Salt Lake City',
    'Brussels Airport', 'Liege Airport', 'Gatwick', 'Luton',
    // Airports (Chinese) - MUST check these BEFORE topic keywords
    '上海浦東國際機場', '香港國際機場', '新加坡樟宜機場', '仁川國際機場', '廣州白雲國際機場',
    '廣州白雲機場', '深圳寶安國際機場', '北京首都', '成都', '重慶', '西安', '杭州', '南京',
    '法蘭克福機場', '希斯洛機場', '杜拜國際機場', '迪拜國際機場', '阿布達比國際機場',
    '阿布達比機場', '曼谷國際機場', '金邊國際機場', '馬尼拉國際機場', '雪梨機場',
    '維也納國際機場', '哥本哈根機場', '慕尼黑機場', '列日機場', '史基浦機場',
    '布魯塞爾機場', '東米德蘭機場', '格拉斯哥普雷斯蒂克機場', '哈利法克斯國際機場',
    '多倫多皮爾遜國際機場', '芝加哥歐海爾國際機場', '芝加哥羅克福德國際機場',
    '路易斯維爾國際機場', '路易斯維爾穆罕默德·阿里國際機場', '邁阿密國際機場',
    '鹽湖城國際機場', '鄂州花湖機場', '鄭州新鄭國際機場', '新千歲機場', '樟宜機場',
    '什里波特機場', '伊斯坦堡機場', '阿拉特國際機場', '阿勒馬克圖姆國際機場',
    '貨運機場', '機場', // Generic airport terms
    // Ground Handlers & Operators
    'WFS', 'Swissport', 'Menzies', 'Menzies Aviation', 'dnata', 'Celebi', 'SATS', 'SATS Ltd',
    'HACTL', 'Hactl', '香港空運貨站', 'G2 Secure Staff', 'Aviator Airport Alliance',
    'World Prime Services', 'AVS GSA', 'AVS GSA Services', 'ECS Group', 'GSA', 'GSSA',
    // Forwarders & Logistics
    'Kuehne+Nagel', 'DB Schenker', 'DSV', 'Expeditors', 'Panalpina', 'CEVA', 'Geodis',
    'Hellmann', 'Hellmann Worldwide', 'Bolloré', 'Agility', 'Nippon Express', 'Yusen',
    'Kerry Logistics', 'Rhenus', 'Rhenus Group', 'Morrison Express', 'Aramex', 'B&H Worldwide',
    'C.H. Robinson', 'Dimerco', 'Flexport', 'Alcott Global', 'OIA Global', 'XCF Global',
    'Berli Jucker', 'Eastway Global', 'MBS Logistics', 'SAL Logistics', 'Logistics UK',
    'U-Freight', 'U-Freight Group', 'Trans Global Projects', 'Nordisk', 'Ninatrans',
    'EFM Global', 'Frontier Scientific', 'World Central Kitchen',
    // Tech Platforms & Software
    'CargoAi', 'WebCargo', 'Freightos', 'Cargo.one', 'iCargo', 'myCargo', 'EzyCargo',
    'Amadeus', 'SITA', 'IBS Software', 'CHAMP Cargosystems', 'Nallian', 'FourKites',
    'Trackonomy', 'PayCargo', 'TAC Index', 'Xeneta', 'WorldACD', 'WorldACD Market Data',
    'Teleport', 'heyworld', 'reXtore',
    // Other Companies
    'Airforwarders Association', 'AfA', 'IATA', 'ICAO', 'TIACA', 'FIATA', 'BIFA', 'CILT UK',
    'UKWA', 'BARIG', 'BGMEA', 'NYNJFFFBA', 'Pharma.Aero', 'CargoTech', 'FL Technics',
    'Jeena & Company', 'Air Charter Service', 'Chapman Freeborn', 'Correios', 'Swiss Post',
    'SF Express', '順豐', '順豐航空', '順豐速運', 'DP World', 'GXO', 'Talma',
    'Unilode', 'Jettainer', 'ULD Care', 'Lödige Industries', 'LODDAutonomous',
    'ProGlove', 'Thales', 'Leonardo', 'Rolls-Royce', 'Neste', 'Exolum',
    'Hybrid Air Vehicles', 'Windracers', 'ST Engineering', 'Ontic Aerospace',
    'Titan Aviation', 'FAI Aviation', 'FlyUs Aviation', 'Avia Solutions', 'Abra Group',
    'TAM Group', 'CSC Group', 'ASR Cargo', 'CPK Airport', 'Fraport',
    '中國南方航空', '中國國際貨運航空', '中國東方航空', '國泰航空', '國泰貨運',
    '大韓航空', '日本航空', '泰國航空', '印度航空', '波蘭航空', '衣索比亞航空',
    '阿聯酋航空', '阿提哈德航空', '阿提哈德航空貨運', '阿曼航空', '蘇南航空', '蘇爾納航空',
    '北京首都航空', '加拿大航空 Transat',
  ],
};

// Helper function to detect if a tag is a company/airport/operator (English)
const isCompanyAirportOperator = (tag: string): boolean => {
  const tagLower = tag.toLowerCase();
  
  // Common company/airport patterns
  const patterns = [
    // Airlines (common suffixes)
    /airlines?$/i, /airways?$/i, /air cargo$/i, /cargo$/i,
    // Airports
    /airport$/i, /international$/i, /heathrow$/i, /jfk$/i, /lax$/i,
    // Companies (common words)
    /^(fedex|dhl|ups|wfs|swissport|menzies|sats)/i,
    // Ground handlers
    /(handler|handling|services|logistics|forwarder|forwarding)$/i,
    // Common company indicators
    /\b(inc|llc|ltd|corp|group|holdings|aviation|airlines|airways)\b/i,
  ];
  
  return patterns.some(pattern => pattern.test(tag));
};

// Helper function to detect if a tag is a geographic region (English)
const isGeographicRegion = (tag: string): boolean => {
  const tagLower = tag.toLowerCase();
  const regions = [
    'asia', 'europe', 'america', 'pacific', 'atlantic', 'middle east',
    'north', 'south', 'east', 'west', 'africa', 'australia', 'oceania',
    'trans-pacific', 'trans-atlantic', 'asia-pacific', 'apac', 'emea',
  ];
  
  return regions.some(region => tagLower.includes(region));
};

// Helper function to detect if a tag is a main topic (English)
const isMainTopic = (tag: string): boolean => {
  const tagLower = tag.toLowerCase();
  const topics = [
    'market', 'analysis', 'company', 'news', 'airport', 'infrastructure',
    'digital', 'tech', 'sustainability', 'saf', 'special', 'cargo',
    'regulation', 'security', 'people', 'appointment', 'merger', 'acquisition',
    'financial', 'strategy', 'e-commerce', 'cold chain', 'pharma',
  ];
  
  return topics.some(topic => tagLower.includes(topic));
};

export default function TagFilter({ tags, selectedTags, favoriteTags = [], onTagToggle, onFavoriteToggle }: TagFilterProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'categories' | 'search'>('categories');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['主要主題']));

  // Filter tags by search query
  const filteredTags = useMemo(() => {
    if (!searchQuery.trim()) return tags;
    const query = searchQuery.toLowerCase();
    return tags.filter(tag => tag.toLowerCase().includes(query));
  }, [tags, searchQuery]);

  // Group tags by category - STRICT matching for better categorization
  const categorizedTags = useMemo(() => {
    const categorized: { [key: string]: string[] } = {
      '特殊貨物與包機': [], // NEW: Priority category for cargo brokers
      '市場分析': [],
      '公司動態': [],
      '機場與基礎設施': [],
      '數位與科技': [],
      '永續發展': [],
      '法規與安全': [],
      '人事任命': [],
      '地理區域': [],
      '公司/機場': [],
      '其他': [],
    };

    tags.forEach(tag => {
      let found = false;
      const tagLower = tag.toLowerCase();
      
      // PRIORITY 1: Check 特殊貨物與包機 FIRST (cargo broker priority)
      const specialCargoKeywords = TAG_CATEGORIES['特殊貨物與包機'];
      if (specialCargoKeywords.some(keyword => {
        const keywordLower = keyword.toLowerCase();
        // Exact match preferred, but allow contains for compound terms
        return tagLower === keywordLower || tagLower.includes(keywordLower) || keywordLower.includes(tagLower);
      })) {
        categorized['特殊貨物與包機'].push(tag);
        found = true;
      }
      
      // PRIORITY 2: Check 公司/機場 (to catch airports before they match other categories)
      if (!found) {
        const companyKeywords = TAG_CATEGORIES['公司/機場'];
        if (companyKeywords.some(keyword => {
          const keywordLower = keyword.toLowerCase();
          return tagLower === keywordLower || tagLower.includes(keywordLower) || keywordLower.includes(tagLower);
        })) {
          categorized['公司/機場'].push(tag);
          found = true;
        }
      }
      
      // PRIORITY 3: Check 地理區域
      if (!found) {
        const regionKeywords = TAG_CATEGORIES['地理區域'];
        if (regionKeywords.some(keyword => {
          const keywordLower = keyword.toLowerCase();
          return tagLower === keywordLower || tagLower.includes(keywordLower);
        })) {
          categorized['地理區域'].push(tag);
          found = true;
        }
      }
      
      // PRIORITY 4: Check specific topic categories (STRICT - exact or very close match)
      if (!found) {
        // Skip if tag contains airport indicators
        const isAirport = tagLower.includes('airport') || 
                         tagLower.includes('機場') || 
                         tagLower.includes('國際機場') ||
                         /^(jfk|lax|cdg|heathrow|narita|haneda|incheon|dubai|singapore|hong kong|tokyo|seoul|shanghai|beijing|guangzhou|miami|chicago|atlanta|dallas|memphis|louisville|anchorage|liege|luxembourg|brussels|gatwick|luton|billund|glasgow|halifax|hamilton|salt lake)/i.test(tag);
        
        if (!isAirport) {
          // Check each topic category with STRICT matching
          for (const [category, keywords] of Object.entries(TAG_CATEGORIES)) {
            if (category === '公司/機場' || category === '地理區域' || category === '特殊貨物與包機') {
              continue; // Already checked
            }
            
            if (keywords.some(keyword => {
              const keywordLower = keyword.toLowerCase();
              // STRICT: Exact match or tag starts/ends with keyword (not just contains)
              return tagLower === keywordLower || 
                     tagLower.startsWith(keywordLower + ' ') ||
                     tagLower.endsWith(' ' + keywordLower) ||
                     tagLower.includes(' ' + keywordLower + ' ');
            })) {
              categorized[category].push(tag);
              found = true;
              break;
            }
          }
        }
      }
      
      // PRIORITY 5: Pattern matching for unrecognized tags (fallback)
      if (!found) {
        if (isCompanyAirportOperator(tag)) {
          categorized['公司/機場'].push(tag);
          found = true;
        } else if (isGeographicRegion(tag)) {
          categorized['地理區域'].push(tag);
          found = true;
        }
      }
      
      // If still not found, put in "其他"
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
                      const isFavorite = favoriteTags.includes(tag);
                      return (
                        <div key={tag} className="flex items-center gap-1 group">
                          <button
                            onClick={() => onTagToggle(tag)}
                            className={`flex-1 text-left px-2 py-1 rounded text-xs transition-colors ${
                              isSelected
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            {tag}
                          </button>
                          {onFavoriteToggle && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onFavoriteToggle(tag);
                              }}
                              className={`p-1 rounded transition-colors ${
                                isFavorite
                                  ? 'text-yellow-500 hover:text-yellow-600'
                                  : 'text-gray-400 hover:text-yellow-500 opacity-0 group-hover:opacity-100'
                              }`}
                              aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                            >
                              <svg className="w-4 h-4" fill={isFavorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                              </svg>
                            </button>
                          )}
                        </div>
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
                const isFavorite = favoriteTags.includes(tag);
                return (
                  <div key={tag} className="flex items-center gap-1 group">
                    <button
                      onClick={() => onTagToggle(tag)}
                      className={`flex-1 text-left px-3 py-2 rounded-md text-sm transition-colors ${
                        isSelected
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {tag}
                    </button>
                    {onFavoriteToggle && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onFavoriteToggle(tag);
                        }}
                        className={`p-1 rounded transition-colors ${
                          isFavorite
                            ? 'text-yellow-500 hover:text-yellow-600'
                            : 'text-gray-400 hover:text-yellow-500 opacity-0 group-hover:opacity-100'
                        }`}
                        aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                      >
                        <svg className="w-4 h-4" fill={isFavorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                        </svg>
                      </button>
                    )}
                  </div>
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
            const isFavorite = favoriteTags.includes(tag);
            return (
              <div key={tag} className="flex items-center gap-1 group">
                <button
                  onClick={() => onTagToggle(tag)}
                  className={`flex-1 text-left px-3 py-2 rounded-md text-sm transition-colors ${
                    isSelected
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {tag}
                </button>
                {onFavoriteToggle && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onFavoriteToggle(tag);
                    }}
                    className={`p-1 rounded transition-colors ${
                      isFavorite
                        ? 'text-yellow-500 hover:text-yellow-600'
                        : 'text-gray-400 hover:text-yellow-500 opacity-0 group-hover:opacity-100'
                    }`}
                    aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    <svg className="w-4 h-4" fill={isFavorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </button>
                )}
              </div>
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
