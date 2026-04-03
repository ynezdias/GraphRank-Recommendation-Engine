'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
import type { RecommendationsResponse } from '@/lib/api';

const REC_GRADIENTS = [
  'linear-gradient(135deg,#7C3AED,#06B6D4)',
  'linear-gradient(135deg,#F97316,#FBBF24)',
  'linear-gradient(135deg,#EC4899,#8B5CF6)',
  'linear-gradient(135deg,#10B981,#34D399)',
  'linear-gradient(135deg,#3B82F6,#06B6D4)',
  'linear-gradient(135deg,#F59E0B,#EC4899)',
  'linear-gradient(135deg,#8B5CF6,#06B6D4)',
  'linear-gradient(135deg,#EF4444,#F97316)',
];

interface RecommendationsPanelProps {
  data: RecommendationsResponse | null;
  loading: boolean;
  onSearch: (userId: number) => void;
  latency: string | null;
}

export default function RecommendationsPanel({
  data,
  loading,
  onSearch,
  latency,
}: RecommendationsPanelProps) {
  const [inputVal, setInputVal] = useState('1');

  const handleSubmit = () => {
    const id = parseInt(inputVal, 10);
    if (!isNaN(id) && id > 0) onSearch(id);
  };

  const variant = data?.experiment_variant ?? 'control';

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-header">
        <div className="card-title">
          <div className="card-title-icon cyan">⚡</div>
          Recommendations
        </div>
        {latency && (
          <div className="latency-pill">
            {latency}
          </div>
        )}
      </div>

      <div className="card-body">
        {/* User search */}
        <div className="user-search">
          <input
            id="user-id-input"
            type="number"
            min={1}
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="Enter User ID…"
          />
          <button onClick={handleSubmit} aria-label="Search">
            <Search size={14} />
          </button>
        </div>

        {/* Experiment badge */}
        {data && (
          <div className={`experiment-tag ${variant}`} id="experiment-badge">
            <span>{variant === 'treatment' ? '🧪' : '🔬'}</span>
            {variant.toUpperCase()} variant
            {data.source === 'redis_cache' && (
              <span style={{ opacity: 0.7 }}> · cached</span>
            )}
          </div>
        )}

        {/* Rec cards */}
        {loading ? (
          <div className="rec-list">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="loading-shimmer"
                style={{ height: 56, borderRadius: 12 }}
              />
            ))}
          </div>
        ) : !data || data.recommendations.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🤝</div>
            <p>No recommendations for this user yet.</p>
          </div>
        ) : (
          <div className="rec-list">
            {data.recommendations.map((rec, idx) => {
              const initials = (rec.name || `U${rec.recommended_user_id}`)
                .substring(0, 2)
                .toUpperCase();
              const score = parseFloat(rec.score).toFixed(2);

              return (
                <div key={rec.recommended_user_id} className="rec-item">
                  <div
                    className="rec-avatar"
                    style={{ background: REC_GRADIENTS[idx % REC_GRADIENTS.length] }}
                  >
                    {initials}
                  </div>
                  <div className="rec-info">
                    <div className="rec-name">
                      {rec.name || `User ${rec.recommended_user_id}`}
                    </div>
                    <div className="rec-score">Match score: {score}</div>
                  </div>
                  <button className="btn-connect">Connect</button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
