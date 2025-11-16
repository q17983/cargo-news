# Tag Categorization Analysis

## Current Status
- **Total Tags**: 669
- **主要主題**: 81 tags (12.1%)
- **地理區域**: 15 tags (2.2%)
- **公司/機場**: 116 tags (17.3%)
- **其他**: 457 tags (68.3%) ⚠️ **TOO MANY**

## Problems Identified

### 1. Missing Company Names in "其他"
Many well-known companies are not being recognized:
- **Airlines**: Airbus, Boeing, Amazon Air, Avianca, IndiGo, Iberia, etc.
- **Forwarders**: Aramex, B&H Worldwide, C.H. Robinson, Dimerco, Flexport, Morrison Express, etc.
- **Tech/Platforms**: Amadeus, SITA, IBS Software, CargoAi, WebCargo, Freightos, etc.
- **Airports**: Many Chinese airport names (上海浦東國際機場, 香港國際機場, etc.) are in 主要主題 instead of 公司/機場

### 2. Missing Topic Keywords
Many Chinese topic tags aren't being matched:
- 併購, 收購 (M&A)
- 財務報告 (Financial reports)
- 策略調整 (Strategy)
- 電子商務 (E-commerce)
- 供應鏈 (Supply chain)
- etc.

### 3. Pattern Matching Issues
- Company names with spaces or special characters aren't matched
- Chinese company names need better recognition
- Airport names in Chinese need better categorization

## Current Filtering Logic

### Step 1: Keyword Matching
- Checks if tag contains any keyword from `TAG_CATEGORIES`
- Case-insensitive matching
- Uses `includes()` - so "FedEx" matches "FedEx Express"

### Step 2: Pattern Matching (if keyword match fails)
- **Company/Airport**: Regex patterns for `*Airlines`, `*Airport`, `*Handler`, etc.
- **Geographic**: Checks for region keywords (asia, europe, etc.)
- **Topic**: Checks for topic keywords (market, analysis, etc.)

### Step 3: Default to "其他"
- If no match found, goes to "其他"

## Issues with Current Logic

1. **Exact company names not in keyword list** → Go to "其他"
2. **Chinese airport names** → Often matched to 主要主題 (because they contain "機場")
3. **Pattern matching too strict** → Only matches suffixes, not full company names
4. **Missing many common companies** → Need to expand keyword list significantly

## Recommended Fixes

1. **Expand company keyword list** with all companies found in "其他"
2. **Improve Chinese airport recognition** - separate from topic keywords
3. **Add more topic keywords** (Chinese and English)
4. **Better pattern matching** for company names (not just suffixes)
5. **Add acronym recognition** (IATA, ICAO, etc. should be categorized)

