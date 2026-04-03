'use client';

import { useEffect, useRef } from 'react';
import type { Influencer } from '@/lib/api';

const AVATAR_GRADIENTS = [
  'linear-gradient(135deg,#7C3AED,#06B6D4)',
  'linear-gradient(135deg,#F97316,#FBBF24)',
  'linear-gradient(135deg,#EC4899,#8B5CF6)',
  'linear-gradient(135deg,#10B981,#34D399)',
  'linear-gradient(135deg,#3B82F6,#06B6D4)',
  'linear-gradient(135deg,#F59E0B,#EF4444)',
];

function rankBadgeClass(rank: number) {
  if (rank === 1) return 'r1';
  if (rank === 2) return 'r2';
  if (rank === 3) return 'r3';
  return 'rn';
}

interface InfluencerTableProps {
  influencers: Influencer[];
  loading: boolean;
}

export default function InfluencerTable({ influencers, loading }: InfluencerTableProps) {
  const barRefs = useRef<(HTMLDivElement | null)[]>([]);

  const maxScore = influencers.length
    ? Math.max(...influencers.map((i) => parseFloat(i.pagerank_score)))
    : 1;

  // Animate bars after render
  useEffect(() => {
    barRefs.current.forEach((el, idx) => {
      if (!el) return;
      const pct =
        maxScore > 0
          ? (parseFloat(influencers[idx]?.pagerank_score ?? '0') / maxScore) * 100
          : 0;
      setTimeout(() => {
        if (el) el.style.width = `${pct}%`;
      }, 80 + idx * 60);
    });
  }, [influencers, maxScore]);

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-header">
        <div className="card-title">
          <div className="card-title-icon purple">🏆</div>
          Top Influencers
        </div>
        <span className="card-badge purple">{influencers.length} users</span>
      </div>

      <div className="card-body" style={{ padding: '12px 22px 18px' }}>
        {loading ? (
          <>
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="loading-shimmer"
                style={{ height: 48, marginBottom: 8 }}
              />
            ))}
          </>
        ) : influencers.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <p>No influencers found. Run the Graph Engine.</p>
          </div>
        ) : (
          <table className="influencer-table">
            <thead>
              <tr>
                <th style={{ width: 40 }}>#</th>
                <th>User</th>
                <th style={{ textAlign: 'right' }}>PageRank Score</th>
              </tr>
            </thead>
            <tbody>
              {influencers.map((user, idx) => {
                const rank = idx + 1;
                const initials = (user.name || `U${user.user_id}`)
                  .substring(0, 2)
                  .toUpperCase();

                return (
                  <tr key={user.user_id}>
                    {/* Rank */}
                    <td className="rank-cell">
                      <div className={`rank-badge ${rankBadgeClass(rank)}`}>
                        {rank}
                      </div>
                    </td>

                    {/* User */}
                    <td>
                      <div className="user-cell">
                        <div
                          className="user-avatar-sm"
                          style={{ background: AVATAR_GRADIENTS[idx % AVATAR_GRADIENTS.length] }}
                        >
                          {initials}
                        </div>
                        <div>
                          <div className="user-name">
                            {user.name || `User ${user.user_id}`}
                          </div>
                          <div className="user-handle">
                            @{user.username || `user${user.user_id}`}
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Score */}
                    <td className="score-cell">
                      <span className="score-value">
                        {parseFloat(user.pagerank_score).toFixed(4)}
                      </span>
                      <div className="score-bar-wrap">
                        <div
                          className="score-bar-fill"
                          ref={(el) => { barRefs.current[idx] = el; }}
                          style={{ width: '0%' }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
