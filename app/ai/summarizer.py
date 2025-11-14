"""Google Gemini API integration for article summarization."""
import logging
import re
import time
from typing import Dict, Optional, List
from datetime import datetime
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class Summarizer:
    """Summarizer using Google Gemini API."""
    
    # Rate limiting: minimum delay between API calls (seconds)
    MIN_DELAY_BETWEEN_CALLS = 1.0  # 1 second minimum delay
    _last_call_time = 0.0
    
    PROMPT_TEMPLATE = """你是一位專業的航空貨運新聞編輯。請根據我們提供的英文新聞文章，嚴格遵循以下所有指示和格式要求，將其處理成繁體中文新聞摘要。

【核心任務】
1. **翻譯與摘要**：閱讀完整文章，理解核心內容，翻譯標題並創建結構化摘要
2. **提取元數據**：識別來源、完整URL、原始標題、發布日期
3. **標籤分類**：生成至少5個相關標籤，必須包含公司/機場名稱和主要主題

【詳細指示】

### 1. 翻譯與摘要處理
- **標題翻譯**：將英文標題翻譯成流暢的繁體中文，保持專業性和準確性
- **內容摘要結構**：
  * 必須使用**子標題**（例如：市場動態、關鍵挑戰、未來展望、公司策略、行業影響）
  * 每個子標題下使用**項目符號**列出2-4個關鍵信息點
  * 重點提取：數據、關鍵人物/公司、重要決策、市場趨勢、時間表
  * 如果文章涉及多個主題，為每個主題創建子標題

### 2. 元數據提取（必須完整準確）
- **來源名稱**：識別新聞網站名稱（例如：Air Cargo News）
- **完整URL**：【關鍵】必須提取**完整且正確的URL路徑**，包括所有路徑參數
  * 格式範例：`https://www.aircargonews.net/news/smes-confident-about-asia-europe-trade-expansion/1080893.article`
  * 不要只提供主域名，必須包含完整路徑
- **原始標題**：保留英文原文標題
- **發布日期**：格式必須為 `YYYY年MM月DD日`（例如：2024年01月15日）
  * 如果文章未明確標示日期，標記為「日期未標示」

### 3. 標籤生成（【最重要】必須嚴格遵守）
**必須生成至少5個標籤，用逗號分隔**

標籤必須包含以下類別：

**A. 主要公司/機場/組織（必填，如果文章中出現）**
- 航空公司：FedEx, DHL, Lufthansa Cargo, IAG Cargo, Cathay Pacific Cargo, Singapore Airlines Cargo, Emirates SkyCargo, Qatar Airways Cargo 等
- 機場：CDG Airport, Heathrow, JFK, LAX, Hong Kong International Airport, Singapore Changi, Dubai International 等
- 貨運代理：Kuehne+Nagel, DB Schenker, DSV, Expeditors, Panalpina 等
- 地面服務：WFS (Worldwide Flight Services), Swissport, Menzies Aviation 等
- 如果文章明確提及主要公司/機場，必須包含在標籤中

**B. 主要主題分類（必填，選擇1-2個）**
從以下列表中選擇最相關的主題：
- 市場分析（Market Analysis）：運費、貨量報告、市場預測、貿易數據
- 公司動態（Company News）：併購、財務報告、策略調整、新服務
- 機場與基礎設施（Airports & Infrastructure）：機場運營、地面處理、倉儲設施、擴建項目
- 數位與科技（Digital & Tech）：電商平台、預訂系統、無人機、自動化、區塊鏈
- 永續發展（Sustainability）：SAF（永續航空燃料）、碳排放、環保措施
- 特殊貨物（Special Cargo）：醫藥冷鏈、危險品、活體動物、貴重物品
- 法規與安全（Regulation & Security）：海關、貿易協定、安全檢查、合規要求
- 人事任命（People & Appointments）：CEO變動、高層任命、組織架構調整

**C. 地理區域（如果適用）**
- 例如：亞洲-歐洲、北美、中東、亞太地區、跨太平洋、大西洋航線

**D. 其他關鍵詞（如果適用）**
- 例如：中小企業(SMEs)、供應鏈、運費率、電子商務、冷鏈物流、即時追蹤

**標籤格式範例：**
- 範例1：`Tag: 市場分析, 亞歐貿易, 中小企業, FedEx, 數位工具`
- 範例2：`Tag: 永續發展, 公司動態, IAG Cargo, British Airways, SAF, 減碳, 歐洲`
- 範例3：`Tag: 機場與基礎設施, 公司動態, WFS, 邁阿密國際機場, 倉儲, 北美`
- 範例4：`Tag: 特殊貨物, 醫藥冷鏈, DHL, 法規與安全, 溫控運輸, 亞太地區`

### 4. 嚴格輸出格式（必須完全遵守）

整個輸出必須使用繁體中文，格式必須完全符合以下模板：

```
標題：[繁體中文翻譯標題]

主要內容摘要：

[子標題1：繁體中文]
* [摘要要點1.1]
* [摘要要點1.2]
* [摘要要點1.3]

[子標題2：繁體中文]
* [摘要要點2.1]
* [摘要要點2.2]

（根據文章內容繼續添加更多子標題和要點）

來源：[來源名稱]
網址：[完整且正確的URL，例如：https://www.aircargonews.net/news/smes-confident-about-asia-europe-trade-expansion/1080893.article]
標題: [原始英文標題]
新聞日期：[發布日期，格式：YYYY年MM月DD日，如果未標示則寫「日期未標示」]

Tag: [至少5個標籤，用逗號分隔]
```

【重要提醒】
- 如果文章URL無法從內容中提取，請使用以下URL：{article_url}
- 如果文章日期無法確定，請使用以下日期：{article_date}
- 標籤必須具體且相關，避免過於籠統的詞彙
- 摘要要點應包含具體數據、時間、公司名稱等關鍵信息
- 保持專業術語的準確性，特別是航空貨運專業詞彙

現在請處理以下新聞文章：

{article_content}
"""
    
    def __init__(self):
        """Initialize the Gemini API client."""
        genai.configure(api_key=settings.gemini_api_key)
        # Use gemini-2.0-flash (fast and cost-effective) or fallback to latest
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-flash-latest')
            except:
                # Last resort: use pro-latest
                self.model = genai.GenerativeModel('gemini-pro-latest')
    
    def summarize(self, article_content: str, article_url: str, 
                  article_title: str, article_date: Optional[datetime] = None,
                  source_name: str = "Air Cargo News") -> Dict:
        """
        Summarize an article using Gemini API.
        
        Args:
            article_content: Full article text
            article_url: Article URL
            article_title: Original article title
            article_date: Publication date (optional)
            source_name: Source name
            
        Returns:
            Dictionary with summarized data
        """
        try:
            # Format date for prompt
            date_str = "日期未標示"
            if article_date:
                date_str = article_date.strftime("%Y年%m月%d日")
            
            # Build prompt
            prompt = self.PROMPT_TEMPLATE.format(
                article_content=article_content[:50000],  # Limit content length
                article_url=article_url,
                article_date=date_str
            )
            
            # Rate limiting: ensure minimum delay between API calls
            time_since_last_call = time.time() - Summarizer._last_call_time
            if time_since_last_call < Summarizer.MIN_DELAY_BETWEEN_CALLS:
                sleep_time = Summarizer.MIN_DELAY_BETWEEN_CALLS - time_since_last_call
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s before next API call")
                time.sleep(sleep_time)
            
            # Generate summary
            logger.info(f"Generating summary for article: {article_url}")
            Summarizer._last_call_time = time.time()
            
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
                
                summary_text = response.text
            except Exception as api_error:
                error_str = str(api_error).lower()
                # Check for quota errors
                if 'quota' in error_str or '429' in error_str or 'rate limit' in error_str:
                    logger.error(f"⚠️  GEMINI API QUOTA EXCEEDED: {str(api_error)}")
                    logger.error("Please wait before trying again or upgrade your API plan")
                    raise Exception(f"Gemini API quota exceeded. Please wait or upgrade your plan. Error: {str(api_error)}")
                # Re-raise other errors
                raise
            
            # Parse the structured output
            parsed = self._parse_summary(summary_text, article_url, article_title, article_date, source_name)
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error summarizing article {article_url}: {str(e)}")
            # Return fallback summary
            return {
                'translated_title': article_title,
                'summary': f"摘要生成失敗：{str(e)}",
                'source': source_name,
                'url': article_url,
                'original_title': article_title,
                'date': article_date.strftime("%Y年%m月%d日") if article_date else "日期未標示",
                'tags': ['新聞', '航空貨運', '摘要失敗']
            }
    
    def _parse_summary(self, summary_text: str, article_url: str, 
                      article_title: str, article_date: Optional[datetime],
                      source_name: str) -> Dict:
        """Parse the structured summary output from Gemini."""
        result = {
            'translated_title': article_title,
            'summary': '',
            'source': source_name,
            'url': article_url,
            'original_title': article_title,
            'date': article_date.strftime("%Y年%m月%d日") if article_date else "日期未標示",
            'tags': []
        }
        
        try:
            # Extract translated title
            title_match = re.search(r'標題[：:]\s*(.+?)(?:\n|主要內容)', summary_text, re.DOTALL)
            if title_match:
                result['translated_title'] = title_match.group(1).strip()
            
            # Extract summary (everything between "主要內容摘要：" and "來源：")
            summary_match = re.search(
                r'主要內容摘要[：:]\s*(.+?)(?=來源[：:]|$)',
                summary_text,
                re.DOTALL
            )
            if summary_match:
                result['summary'] = summary_match.group(1).strip()
            
            # Extract source
            source_match = re.search(r'來源[：:]\s*(.+?)(?:\n|網址)', summary_text)
            if source_match:
                result['source'] = source_match.group(1).strip()
            
            # Extract URL (prefer extracted, fallback to provided)
            url_match = re.search(r'網址[：:]\s*(https?://[^\s\n]+)', summary_text)
            if url_match:
                result['url'] = url_match.group(1).strip()
            
            # Extract original title
            orig_title_match = re.search(r'標題[：:]\s*(.+?)(?:\n|新聞日期)', summary_text)
            if orig_title_match:
                result['original_title'] = orig_title_match.group(1).strip()
            
            # Extract date
            date_match = re.search(r'新聞日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日|日期未標示)', summary_text)
            if date_match:
                result['date'] = date_match.group(1).strip()
            
            # Extract tags
            tag_match = re.search(r'Tag[：:]\s*(.+?)(?:\n|$)', summary_text)
            if tag_match:
                tags_str = tag_match.group(1).strip()
                # Split by comma and clean
                result['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            
            # Ensure at least 5 tags
            if len(result['tags']) < 5:
                # Add default tags if needed
                default_tags = ['新聞', '航空貨運']
                for tag in default_tags:
                    if tag not in result['tags']:
                        result['tags'].append(tag)
            
        except Exception as e:
            logger.error(f"Error parsing summary: {str(e)}")
            # Keep fallback values
        
        return result

