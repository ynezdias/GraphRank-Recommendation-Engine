'use client';

import { RefreshCw, Bell, Search } from 'lucide-react';

interface HeaderProps {
  onRefresh: () => void;
  isRefreshing: boolean;
  latency: string | null;
}

export default function Header({ onRefresh, isRefreshing, latency }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-left">
        <h1>Analytics Dashboard</h1>
        <p>Real-time social graph influence &amp; recommendations</p>
      </div>

      <div className="header-right">
        {latency && (
          <div className="latency-pill">
            <span>⚡</span>
            {latency} latency
          </div>
        )}

        <button className="header-btn" aria-label="Search">
          <Search size={14} />
          Search
        </button>

        <button className="header-btn" aria-label="Notifications">
          <Bell size={14} />
        </button>

        <button
          id="refresh-btn"
          className={`header-btn primary ${isRefreshing ? 'spinning' : ''}`}
          onClick={onRefresh}
          aria-label="Refresh data"
        >
          <RefreshCw size={14} />
          {isRefreshing ? 'Refreshing…' : 'Refresh'}
        </button>

        <div className="user-avatar" title="Admin">A</div>
      </div>
    </header>
  );
}
