// Typed API helpers — all calls go through Next.js proxy → FastAPI

export interface Influencer {
  user_id: number;
  name: string | null;
  username: string | null;
  pagerank_score: string;
}

export interface TopInfluencersResponse {
  top_influencers: Influencer[];
}

export interface Recommendation {
  recommended_user_id: number;
  name: string | null;
  username: string | null;
  score: string;
}

export interface RecommendationsResponse {
  user_id: number;
  experiment_variant: 'control' | 'treatment';
  source: 'redis_cache' | 'postgres';
  recommendations: Recommendation[];
}

export interface HealthResponse {
  status: string;
  service: string;
}

const BASE = '/api';

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json();
}

export const api = {
  health: () => apiFetch<HealthResponse>('/health'),
  topInfluencers: (limit = 10) =>
    apiFetch<TopInfluencersResponse>(`/top-influencers?limit=${limit}`),
  recommendations: (userId: number) =>
    apiFetch<RecommendationsResponse>(`/recommendations/${userId}`),
};
