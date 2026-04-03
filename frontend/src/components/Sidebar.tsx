'use client';

import {
  LayoutDashboard, Network, Users, FlaskConical,
  Zap, Settings, ChevronRight, Activity
} from 'lucide-react';

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  badge?: string;
  active?: boolean;
}

function NavItem({ icon, label, badge, active }: NavItemProps) {
  return (
    <div className={`nav-item ${active ? 'active' : ''}`}>
      <span className="nav-icon">{icon}</span>
      <span className="nav-label">{label}</span>
      {badge && <span className="nav-badge">{badge}</span>}
      {active && <ChevronRight size={12} style={{ marginLeft: 'auto', opacity: 0.5 }} />}
    </div>
  );
}

interface SidebarProps {
  apiOnline: boolean;
}

export default function Sidebar({ apiOnline }: SidebarProps) {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-mark">GR</div>
        <div className="logo-text">
          <span className="logo-name">GraphRank</span>
          <span className="logo-sub">Recommendation Engine</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <span className="nav-section-label">Main</span>

        <NavItem
          icon={<LayoutDashboard size={16} />}
          label="Dashboard"
          active
        />
        <NavItem
          icon={<Network size={16} />}
          label="Graph Explorer"
          badge="β"
        />
        <NavItem
          icon={<Users size={16} />}
          label="Influencers"
        />
        <NavItem
          icon={<Zap size={16} />}
          label="Recommendations"
        />

        <span className="nav-section-label">Experiments</span>

        <NavItem
          icon={<FlaskConical size={16} />}
          label="A/B Testing"
          badge="Live"
        />
        <NavItem
          icon={<Activity size={16} />}
          label="Stream Events"
        />

        <span className="nav-section-label">System</span>
        <NavItem
          icon={<Settings size={16} />}
          label="Settings"
        />
      </nav>

      {/* Footer status */}
      <div className="sidebar-footer">
        <div className="status-pill">
          <div className={`status-dot ${apiOnline ? '' : 'offline'}`} />
          <span style={{ color: 'var(--text-secondary)', flex: 1 }}>
            {apiOnline ? 'API Online' : 'API Offline'}
          </span>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
            v1.0
          </span>
        </div>
      </div>
    </aside>
  );
}
