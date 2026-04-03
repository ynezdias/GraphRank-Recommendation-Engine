'use client';

const NAV_ITEMS = [
  {
    section: 'Overview',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: GridIcon, badge: null },
      { id: 'influencers', label: 'Influencers', icon: TrendingUpIcon, badge: 'Live' },
      { id: 'recommendations', label: 'Recommendations', icon: UsersIcon, badge: null },
    ],
  },
  {
    section: 'Analytics',
    items: [
      { id: 'graph', label: 'Graph Engine', icon: ShareIcon, badge: null },
      { id: 'experiments', label: 'A/B Testing', icon: FlaskIcon, badge: '2' },
      { id: 'metrics', label: 'Performance', icon: ActivityIcon, badge: null },
    ],
  },
  {
    section: 'System',
    items: [
      { id: 'pipeline', label: 'Spark Pipeline', icon: ZapIcon, badge: null },
      { id: 'settings', label: 'Settings', icon: SettingsIcon, badge: null },
    ],
  },
];

function GridIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
    </svg>
  );
}

function TrendingUpIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
      <polyline points="17 6 23 6 23 12"/>
    </svg>
  );
}

function UsersIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  );
}

function ShareIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
      <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
    </svg>
  );
}

function FlaskIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 3h6l3 7.5-7.5 9.5a1 1 0 0 1-1.5 0L2 10.5 9 3z"/>
      <path d="M9 3c0 3-1 5.5-2 7.5"/>
      <path d="M15 3c0 3 1 5.5 2 7.5"/>
    </svg>
  );
}

function ActivityIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
    </svg>
  );
}

function ZapIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
  );
}

function SettingsIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33..."/>
    </svg>
  );
}

function NetworkIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/>
      <line x1="12" y1="7" x2="5" y2="17"/><line x1="12" y1="7" x2="19" y2="17"/>
    </svg>
  );
}

export default function Sidebar({ apiStatus }) {
  const activeItem = 'dashboard';

  return (
    <aside className="sidebar" role="navigation" aria-label="Main navigation">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon">
          <NetworkIcon />
        </div>
        <span className="logo-text">GraphRank</span>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((section) => (
          <div key={section.section}>
            <div className="nav-section-label">{section.section}</div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive = item.id === activeItem;
              return (
                <div
                  key={item.id}
                  id={`nav-${item.id}`}
                  className={`nav-item${isActive ? ' active' : ''}`}
                  role="button"
                  tabIndex={0}
                >
                  <span className="nav-icon">
                    <Icon />
                  </span>
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="nav-badge">{item.badge}</span>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer Status */}
      <div className="sidebar-footer">
        <div className="status-pill" id="sidebar-api-status">
          <div className={`pulse-dot ${apiStatus === 'online' ? 'online' : 'offline'}`} />
          <div>
            <div className="status-text" style={{ color: apiStatus === 'online' ? 'var(--emerald-400)' : 'var(--rose-400)' }}>
              {apiStatus === 'online' ? 'API Online' : 'API Offline'}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '1px' }}>
              GraphRank Engine
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
