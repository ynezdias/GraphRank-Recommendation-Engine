'use client';

import { useState, useEffect, useCallback } from 'react';
import { Network, Users, Zap, Activity } from 'lucide-react';

import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import StatCard from '@/components/StatCard';
import InfluencerTable from '@/components/InfluencerTable';
import RecommendationsPanel from '@/components/RecommendationsPanel';
import GraphVisualization from '@/components/GraphVisualization';
import ActivityFeed from '@/components/ActivityFeed';
import ScoreChart from '@/components/ScoreChart';
import { api, type Influencer, type RecommendationsResponse } from '@/lib/api';

export default function DashboardPage() {
  const [apiOnline, setApiOnline] = useState(false);
  const [influencers, setInfluencers] = useState<Influencer[]>([]);
  const [recData, setRecData] = useState<RecommendationsResponse | null>(null);
  const [loadingInfluencers, setLoadingInfluencers] = useState(true);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [latency, setLatency] = useState<string | null>(null);
  const [currentUserId, setCurrentUserId] = useState(1);

  const fetchHealth = useCallback(async () => {
    try {
      await api.health();
      setApiOnline(true);
    } catch {
      setApiOnline(false);
    }
  }, []);

  const fetchInfluencers = useCallback(async () => {
    setLoadingInfluencers(true);
    try {
      const data = await api.topInfluencers(10);
      setInfluencers(data.top_influencers);
    } catch {
      setInfluencers([]);
    } finally {
      setLoadingInfluencers(false);
    }
  }, []);

  const fetchRecs = useCallback(async (userId: number) => {
    setLoadingRecs(true);
    const t0 = performance.now();
    try {
      const data = await api.recommendations(userId);
      const ms = performance.now() - t0;
      setLatency(`~${ms.toFixed(0)}ms`);
      setRecData(data);
    } catch {
      setRecData(null);
    } finally {
      setLoadingRecs(false);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    setIsRefreshing(true);
    await Promise.all([fetchHealth(), fetchInfluencers(), fetchRecs(currentUserId)]);
    setIsRefreshing(false);
  }, [fetchHealth, fetchInfluencers, fetchRecs, currentUserId]);

  // Initial load
  useEffect(() => {
    refreshAll();
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-refresh health + influencers every 10s
  useEffect(() => {
    const id = setInterval(() => {
      fetchHealth();
      fetchInfluencers();
    }, 10_000);
    return () => clearInterval(id);
  }, [fetchHealth, fetchInfluencers]);

  const handleRecSearch = (userId: number) => {
    setCurrentUserId(userId);
    fetchRecs(userId);
  };

  // Derived stats
  const totalNodes = 500;          // from data_gen defaults
  const totalEdges = 5000;
  const topScore = influencers[0]
    ? parseFloat(influencers[0].pagerank_score).toFixed(4)
    : '—';
  const cacheSource = recData?.source === 'redis_cache' ? 'Redis' : 'Postgres';

  return (
    <div className="layout">
      <Sidebar apiOnline={apiOnline} />

      <div className="main-content">
        <Header
          onRefresh={refreshAll}
          isRefreshing={isRefreshing}
          latency={latency}
        />

        {/* Gradient divider under header */}
        <div className="grad-divider" />

        <main className="page-body">
          {/* ── KPI Stats ── */}
          <div className="stats-grid">
            <StatCard
              icon={<Network size={20} />}
              label="Graph Nodes"
              value={totalNodes.toLocaleString()}
              trend={12}
              trendLabel="vs last run"
              color="purple"
            />
            <StatCard
              icon={<Activity size={20} />}
              label="Graph Edges"
              value={totalEdges.toLocaleString()}
              trend={8}
              trendLabel="connections"
              color="cyan"
            />
            <StatCard
              icon={<Users size={20} />}
              label="Top PR Score"
              value={topScore}
              trend={4}
              trendLabel="leading influencer"
              color="orange"
            />
            <StatCard
              icon={<Zap size={20} />}
              label="Cache Source"
              value={cacheSource}
              color="green"
              trendLabel={recData ? `User #${recData.user_id}` : 'waiting…'}
            />
          </div>

          {/* ── Main Grid: Table + Recommendations ── */}
          <div className="dashboard-grid">
            <InfluencerTable
              influencers={influencers}
              loading={loadingInfluencers}
            />
            <RecommendationsPanel
              data={recData}
              loading={loadingRecs}
              onSearch={handleRecSearch}
              latency={latency}
            />
          </div>

          {/* ── Bottom Grid: Chart + Graph + Activity ── */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 24 }}>
            <ScoreChart />
            <GraphVisualization />
            <ActivityFeed />
          </div>
        </main>
      </div>
    </div>
  );
}
