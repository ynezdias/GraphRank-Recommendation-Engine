'use client';

import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts';

// Mock sparkline data — in production wire to a real timeseries endpoint
const DATA = [
  { t: '00:00', score: 0.18 },
  { t: '02:00', score: 0.22 },
  { t: '04:00', score: 0.19 },
  { t: '06:00', score: 0.31 },
  { t: '08:00', score: 0.45 },
  { t: '10:00', score: 0.52 },
  { t: '12:00', score: 0.48 },
  { t: '14:00', score: 0.61 },
  { t: '16:00', score: 0.74 },
  { t: '18:00', score: 0.68 },
  { t: '20:00', score: 0.83 },
  { t: '22:00', score: 0.91 },
];

interface CustomTooltipProps {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border)',
      borderRadius: 8,
      padding: '8px 12px',
      fontSize: '0.78rem',
      color: 'var(--text-primary)',
    }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: 2 }}>{label}</div>
      <div style={{ fontWeight: 700, color: '#A78BFA' }}>
        Score: {payload[0].value.toFixed(3)}
      </div>
    </div>
  );
}

export default function ScoreChart() {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <div className="card-title-icon cyan">📈</div>
          PageRank Score — 24h Trend
        </div>
        <span className="card-badge purple">Top Influencer</span>
      </div>

      <div style={{ padding: '16px 12px 12px' }}>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={DATA} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#7C3AED" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="t"
              tick={{ fill: '#475569', fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: '#475569', fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              domain={[0, 1]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="score"
              stroke="url(#strokeGrad)"
              fill="url(#scoreGrad)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5, fill: '#7C3AED', stroke: '#06B6D4', strokeWidth: 2 }}
            />
            {/* Gradient stroke via SVG trick */}
            <defs>
              <linearGradient id="strokeGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%"   stopColor="#7C3AED" />
                <stop offset="100%" stopColor="#06B6D4" />
              </linearGradient>
            </defs>
          </AreaChart>
        </ResponsiveContainer>

        {/* Mini metrics row */}
        <div className="metrics-row" style={{ marginTop: 12 }}>
          <div className="metric-block">
            <div className="metric-block-label">Peak Score</div>
            <div className="metric-block-value" style={{ background: 'var(--grad-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              0.910
            </div>
            <div className="metric-block-sub">at 22:00 UTC</div>
          </div>
          <div className="metric-block">
            <div className="metric-block-label">Avg Score</div>
            <div className="metric-block-value" style={{ background: 'var(--grad-warm)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              0.513
            </div>
            <div className="metric-block-sub">last 24h</div>
          </div>
          <div className="metric-block">
            <div className="metric-block-label">Δ Change</div>
            <div className="metric-block-value" style={{ background: 'var(--grad-success)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              +4.7%
            </div>
            <div className="metric-block-sub">vs yesterday</div>
          </div>
        </div>
      </div>
    </div>
  );
}
