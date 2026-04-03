'use client';

const EVENTS = [
  { id: 1, color: '#7C3AED', text: <><strong>User 42</strong> connected with <strong>User 17</strong> — score updated</>, time: '2s ago' },
  { id: 2, color: '#06B6D4', text: <><strong>PageRank</strong> recomputed for <strong>182 nodes</strong></>, time: '14s ago' },
  { id: 3, color: '#10B981', text: <><strong>Redis cache</strong> invalidated for user <strong>#5</strong></>, time: '31s ago' },
  { id: 4, color: '#F97316', text: <><strong>Stream event</strong> ingested — Kafka offset 1,204</>, time: '1m ago' },
  { id: 5, color: '#EC4899', text: <><strong>A/B</strong>: treatment variant CTR <strong>+3.2%</strong> vs control</>, time: '2m ago' },
  { id: 6, color: '#7C3AED', text: <><strong>Spark job</strong> finished — 3.4k recs written to PostgreSQL</>, time: '5m ago' },
];

export default function ActivityFeed() {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <div className="card-title-icon orange">📡</div>
          Live Activity Feed
        </div>
        <span className="card-badge green">● Streaming</span>
      </div>

      <div className="card-body" style={{ padding: '8px 22px 18px' }}>
        <div className="activity-list">
          {EVENTS.map((evt) => (
            <div key={evt.id} className="activity-item">
              <div className="activity-dot-wrap">
                <div
                  className="activity-dot"
                  style={{
                    background: evt.color,
                    boxShadow: `0 0 8px ${evt.color}80`,
                  }}
                />
              </div>
              <div className="activity-info">
                <div className="activity-text">{evt.text}</div>
                <div className="activity-time">{evt.time}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
