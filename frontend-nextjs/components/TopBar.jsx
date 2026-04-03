'use client';

function RefreshIcon({ spinning }) {
  return (
    <svg
      width="16" height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={spinning ? 'spin' : ''}
    >
      <polyline points="23 4 23 10 17 10"/>
      <polyline points="1 20 1 14 7 14"/>
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
    </svg>
  );
}

function BellIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
      <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
    </svg>
  );
}

export default function TopBar({ userId, onUserIdChange, onRefresh, isRefreshing }) {
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  return (
    <header className="topbar" id="main-topbar">
      <div className="topbar-left">
        <h1>Network Intelligence</h1>
        <p>{dateStr} &nbsp;·&nbsp; Real-time PageRank Analysis</p>
      </div>

      <div className="topbar-right">
        {/* Notification bell */}
        <button
          id="topbar-notifications"
          aria-label="Notifications"
          style={{
            background: 'var(--bg-glass)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-secondary)',
            width: 40, height: 40,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
        >
          <BellIcon />
        </button>

        {/* User ID selector */}
        <div className="user-selector" id="user-id-selector">
          <label htmlFor="user-id-input">User ID</label>
          <input
            id="user-id-input"
            type="number"
            min="1"
            value={userId}
            onChange={(e) => onUserIdChange(e.target.value)}
          />
        </div>

        {/* Refresh button */}
        <button
          id="refresh-btn"
          className="btn-primary"
          onClick={onRefresh}
          disabled={isRefreshing}
        >
          <RefreshIcon spinning={isRefreshing} />
          {isRefreshing ? 'Syncing…' : 'Refresh'}
        </button>
      </div>
    </header>
  );
}
