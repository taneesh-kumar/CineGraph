import Link from "next/link";
import { Database, GitFork, Cpu, ShieldCheck } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-neutral-900 bg-neutral-950 text-neutral-400">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Purpose */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-base tracking-tight">CineGraph</span>
              <span className="text-xs text-neutral-500 font-mono">NoSQL Dual-Engine Architecture</span>
            </div>
            <p className="text-sm text-neutral-400 max-w-md leading-relaxed">
              Academic demonstration pairing <strong className="text-neutral-200">Neo4j</strong> (graph traversal, community detection, collaborative filtering) with <strong className="text-neutral-200">MonetDB</strong> (columnar aggregations, rating distributions, and analytical querying) over the MovieLens dataset.
            </p>
            <div className="inline-flex items-center gap-2 rounded-md bg-neutral-900/90 px-3 py-1.5 text-xs text-neutral-400 border border-neutral-800">
              <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" />
              <span>Dataset sample: 2,500 movies (2020–2023), 18,327 users, 119,689 ratings ingested.</span>
            </div>
          </div>

          {/* Dual Database Architecture */}
          <div className="space-y-2.5">
            <h3 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">
              Engine Attribution
            </h3>
            <ul className="space-y-2 text-xs">
              <li className="flex items-start gap-2">
                <Database className="h-3.5 w-3.5 text-indigo-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-neutral-200 font-medium">Neo4j (Bolt 7687):</span>
                  <p className="text-neutral-500">Movie graph, genres, user collaborative walks.</p>
                </div>
              </li>
              <li className="flex items-start gap-2">
                <Cpu className="h-3.5 w-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-neutral-200 font-medium">MonetDB (MAPI 50000):</span>
                  <p className="text-neutral-500">Columnar aggregations, top-rated ranking, rating distributions.</p>
                </div>
              </li>
            </ul>
          </div>

          {/* Quick Links */}
          <div className="space-y-2.5">
            <h3 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">
              Navigation
            </h3>
            <ul className="space-y-1.5 text-sm">
              <li>
                <Link href="/movies" className="hover:text-white transition-colors">
                  Movie Explorer
                </Link>
              </li>
              <li>
                <Link href="/recommendations" className="hover:text-white transition-colors">
                  Graph Recommendations
                </Link>
              </li>
              <li>
                <Link href="/analytics" className="hover:text-white transition-colors">
                  Columnar Analytics
                </Link>
              </li>
              <li>
                <Link href="/system" className="hover:text-white transition-colors">
                  System Health & Readiness
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 pt-8 border-t border-neutral-900 flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-500 gap-4">
          <p>© 2026 CineGraph Academic Project. Built with Next.js, FastAPI, Neo4j & MonetDB.</p>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1">
              <GitFork className="h-3 w-3" />
              REST API v1
            </span>
            <span className="font-mono">FastAPI :8000</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
