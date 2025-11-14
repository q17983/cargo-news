const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = 'Request failed';
    try {
      const error = await response.json();
      // Handle different error formats
      if (error.detail) {
        // FastAPI error format
        if (Array.isArray(error.detail)) {
          // Validation errors
          errorMessage = error.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        } else {
          errorMessage = JSON.stringify(error.detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      } else {
        errorMessage = JSON.stringify(error);
      }
    } catch {
      errorMessage = `HTTP error! status: ${response.status} ${response.statusText}`;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export async function fetchArticles(params?: {
  source_id?: string;
  tags?: string[];
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}) {
  const queryParams = new URLSearchParams();
  if (params?.source_id) queryParams.append('source_id', params.source_id);
  if (params?.tags) params.tags.forEach(tag => queryParams.append('tags', tag));
  if (params?.date_from) queryParams.append('date_from', params.date_from);
  if (params?.date_to) queryParams.append('date_to', params.date_to);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  return request<any[]>(`/api/articles?${queryParams.toString()}`);
}

export async function fetchArticle(id: string) {
  return request<any>(`/api/articles/${id}`);
}

export async function fetchTags() {
  return request<string[]>(`/api/articles/tags/list`);
}

export async function fetchSources(active_only?: boolean) {
  const query = active_only ? '?active_only=true' : '';
  return request<any[]>(`/api/sources${query}`);
}

export async function createSource(data: { url: string; name?: string }, autoScrape: boolean = false) {
  const query = autoScrape ? '?auto_scrape=true' : '';
  return request<any>(`/api/sources${query}`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteSource(id: string) {
  return request<void>(`/api/sources/${id}`, {
    method: 'DELETE',
  });
}

export async function testSource(id: string) {
  return request<any>(`/api/sources/${id}/test`, {
    method: 'POST',
  });
}

export async function triggerScrape(sourceId?: string) {
  const endpoint = sourceId ? `/api/scrape/${sourceId}` : '/api/scrape/all';
  return request<any>(endpoint, {
    method: 'POST',
  });
}

export async function getScrapingStatus(sourceId: string) {
  return request<any>(`/api/scrape/status/${sourceId}`);
}

export async function getScrapingLogs(sourceId: string, limit: number = 10) {
  return request<any[]>(`/api/scrape/logs/${sourceId}?limit=${limit}`);
}

