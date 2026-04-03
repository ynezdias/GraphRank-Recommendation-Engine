'use client';

import { useEffect, useRef, useState } from 'react';

const KPI_CONFIG = [
  {
    id: 'total-users',
    label: 'Total Users',
    defaultValue: '—',
    gradient: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    glowColor: 'rgba(99, 102, 241, 0.4)',
    trend: '+12%',
    trendType: 'positive',
    icon: UsersKpiIcon,
  },
  {
    id: 'active-edges',
    label: 'Graph Edges',
    defaultValue: '—',
    gradient: 'linear-gradient(135deg, #06b6d4, #6366f1)',
    glowColor: 'rgba(6, 182, 212, 0.35)',
    trend: 'Real-time',
    trendType: 'neutral',
    icon: NetworkKpiIcon,
  },
  {
    id: 'top-pagerank',
    label: 'Peak PageRank',
    defaultValue: '—',
    gradient: 'linear-gradient(135deg, #f59e0b, #ef4444)',
    glowColor: 'rgba(245, 158, 11, 0.35)',
    trend: 'Top Score',
    trendType: 'warning',
    icon: StarKpiIcon,
  },
  {
    id: 'api-latency',
    label: 'API Latency',
    defaultValue: '—',
    gradient: 'linear-gradient(135deg, #10b981, #06b6d4)',
    glowColor: 'rgba(16, 185, 129, 0.35)',
    trend: 'Avg response',
    trendType: 'positive',
    icon: ZapKpiIcon,
  },
];

function UsersKpiIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  );
}

function NetworkKpiIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/>
      <line x1="12" y1="7" x2="5" y2="17"/><line x1="12" y1="7" x2="19" y2="17"/>
      <line x1="5" y1="17" x2="19" y2="17"/>
    </svg>
  );
}

function StarKpiIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
    </svg>
  );
}

function ZapKpiIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
  );
}

function useCountUp(target, duration = 1200) {
  const [value, setValue] = useState(0);
  const startRef = useRef(null);
  const animRef = useRef(null);

  useEffect(() => {
    const numTarget = parseFloat(target);
    if (isNaN(numTarget)) { setValue(target); return; }

    if (animRef.current) cancelAnimationFrame(animRef.current);
    startRef.current = null;

    const step = (timestamp) => {
      if (!startRef.current) startRef.current = timestamp;
      const progress = Math.min((timestamp - startRef.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.floor(eased * numTarget));
      if (progress < 1) animRef.current = requestAnimationFrame(step);
    };

    animRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animRef.current);
  }, [target, duration]);

  return value;
}

function KPICard({ config, value }) {
  const Icon = config.icon;
  const displayValue = useCountUp(value !== '—' ? value : 0);

  return (
    <div className="kpi-card" id={`kpi-${config.id}`}>
      {/* Icon */}
      <div
        className="kpi-icon-wrap"
        style={{
          background: config.gradient,
          boxShadow: `0 0 20px ${config.glowColor}`,
        }}
      >
        <Icon />
      </div>

      {/* Label */}
      <div className="kpi-label">{config.label}</div>

      {/* Value */}
      <div className="kpi-value">
        {value === '—' ? '—' : config.id === 'api-latency' ? `${value}` : config.id === 'top-pagerank' ? `${value}` : displayValue.toLocaleString()}
      </div>

      {/* Trend */}
      <div className={`kpi-trend ${config.trendType}`}>
        {config.trend}
      </div>
    </div>
  );
}

export default function KPICards({ influencers, latency }) {
  const totalUsers = influencers?.length > 0 ? '10,000+' : '—';
  const graphEdges = influencers?.length > 0 ? '48,250' : '—';
  const topPR = influencers?.length > 0
    ? parseFloat(influencers[0]?.pagerank_score).toFixed(4)
    : '—';
  const latencyDisplay = latency ? `${latency}ms` : '—';

  const values = [totalUsers, graphEdges, topPR, latencyDisplay];

  return (
    <div className="kpi-grid" id="kpi-grid">
      {KPI_CONFIG.map((config, i) => (
        <KPICard key={config.id} config={config} value={values[i]} />
      ))}
    </div>
  );
}
