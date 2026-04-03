import { Inter, Outfit } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' });

export const metadata = {
  title: 'GraphRank — Network Intelligence Dashboard',
  description: 'Real-time graph-based recommendation engine powered by PageRank. Monitor influencers, recommendations, and system performance.',
  keywords: 'GraphRank, PageRank, recommendation engine, network analysis, influencers',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
      <body>{children}</body>
    </html>
  );
}
