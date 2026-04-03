'use client';

import { useEffect, useRef } from 'react';

interface Node {
  id: string;
  x: number;
  y: number;
  r: number;
  label: string;
  grad: string;
  delay: number;
}

interface Edge {
  from: Node;
  to: Node;
}

const NODES: Node[] = [
  { id: 'n0', x: 50,  y: 50,  r: 28, label: 'U1', grad: 'linear-gradient(135deg,#7C3AED,#06B6D4)', delay: 0 },
  { id: 'n1', x: 20,  y: 30,  r: 18, label: 'U2', grad: 'linear-gradient(135deg,#F97316,#FBBF24)', delay: 0.5 },
  { id: 'n2', x: 78,  y: 25,  r: 16, label: 'U3', grad: 'linear-gradient(135deg,#EC4899,#8B5CF6)', delay: 1 },
  { id: 'n3', x: 30,  y: 72,  r: 14, label: 'U4', grad: 'linear-gradient(135deg,#10B981,#34D399)', delay: 1.5 },
  { id: 'n4', x: 70,  y: 68,  r: 20, label: 'U5', grad: 'linear-gradient(135deg,#3B82F6,#06B6D4)', delay: 0.8 },
  { id: 'n5', x: 85,  y: 55,  r: 12, label: 'U6', grad: 'linear-gradient(135deg,#F59E0B,#EC4899)', delay: 1.2 },
  { id: 'n6', x: 15,  y: 60,  r: 10, label: 'U7', grad: 'linear-gradient(135deg,#8B5CF6,#EC4899)', delay: 0.3 },
];

const EDGES: [number, number][] = [
  [0, 1], [0, 2], [0, 3], [0, 4],
  [1, 6], [2, 5], [4, 5], [3, 6],
];

function getEdgeStyle(a: Node, b: Node) {
  const dx = (b.x - a.x);
  const dy = (b.y - a.y);
  const length = Math.sqrt(dx * dx + dy * dy);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  return { left: `${a.x}%`, top: `${a.y}%`, width: `${length}%`, transform: `rotate(${angle}deg)` };
}

export default function GraphVisualization() {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <div className="card-title-icon pink">🕸️</div>
          Graph Network Preview
        </div>
        <span className="card-badge purple">Live</span>
      </div>

      <div className="graph-canvas" style={{ padding: '0 12px 12px' }}>
        {/* Edges */}
        {EDGES.map(([ai, bi], i) => {
          const a = NODES[ai];
          const b = NODES[bi];
          const style = getEdgeStyle(a, b);
          return (
            <div
              key={i}
              className="graph-edge"
              style={style}
            />
          );
        })}

        {/* Nodes */}
        {NODES.map((node) => (
          <div
            key={node.id}
            className="graph-node"
            title={node.label}
            style={{
              left: `${node.x}%`,
              top: `${node.y}%`,
              width: node.r * 2,
              height: node.r * 2,
              background: node.grad,
              boxShadow: `0 0 ${node.r}px ${node.grad.includes('7C3AED') ? 'rgba(124,58,237,0.5)' : 'rgba(6,182,212,0.3)'}`,
              animationDelay: `${node.delay}s`,
              zIndex: 2,
            }}
          >
            {node.label}
          </div>
        ))}

        {/* Legend */}
        <div style={{
          position: 'absolute',
          bottom: 16,
          right: 16,
          display: 'flex',
          gap: 12,
          fontSize: '0.7rem',
          color: 'var(--text-muted)',
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--grad-primary)', display: 'inline-block' }} />
            High influence
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--bg-elevated)', border: '1px solid var(--border)', display: 'inline-block' }} />
            Normal
          </span>
        </div>
      </div>
    </div>
  );
}
