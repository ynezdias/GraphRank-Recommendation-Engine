import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GraphRank — Recommendation Engine Dashboard',
  description: 'Real-time graph-based social influence and recommendation analytics powered by PageRank.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
