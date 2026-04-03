'use client';

import { TrendingUp, TrendingDown } from 'lucide-react';

type AccentColor = 'purple' | 'cyan' | 'orange' | 'green';

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  trend?: number;        // positive = up, negative = down
  trendLabel?: string;
  color: AccentColor;
}

const gradMap: Record<AccentColor, string> = {
  purple: 'grad-purple',
  cyan: 'grad-cyan',
  orange: 'grad-orange',
  green: 'grad-green',
};

export default function StatCard({ icon, label, value, trend, trendLabel, color }: StatCardProps) {
  const isUp = trend !== undefined && trend >= 0;

  return (
    <div className={`stat-card ${color}`}>
      <div className="stat-header">
        <div className={`stat-icon ${color}`}>{icon}</div>
        {trend !== undefined && (
          <div className={`stat-trend ${isUp ? 'up' : 'down'}`}>
            {isUp ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>

      <div className={`stat-value ${gradMap[color]}`}>{value}</div>
      <div className="stat-label">{label}</div>
      {trendLabel && (
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
          {trendLabel}
        </div>
      )}
    </div>
  );
}
