"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Film, Compass, Sparkles, BarChart3, Activity, Menu, X, Database } from "lucide-react";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Overview", icon: Compass, description: "System summary & quick entry" },
  { href: "/movies", label: "Movies", icon: Film, description: "Discover & search 2,500 movies" },
  { href: "/recommendations", label: "Recommendations", icon: Sparkles, description: "Neo4j graph & collaborative engine" },
  { href: "/analytics", label: "Analytics", icon: BarChart3, description: "MonetDB columnar aggregations" },
  { href: "/system", label: "System Status", icon: Activity, description: "Neo4j & MonetDB health" },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-neutral-800/80 bg-neutral-950/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-emerald-500 text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Film className="h-5 w-5" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-bold tracking-tight text-white text-lg">CineGraph</span>
              <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-[10px] font-medium tracking-wide text-neutral-300 border border-neutral-700/60 uppercase">
                v1.0
              </span>
            </div>
            <span className="text-[10px] text-neutral-400 font-medium">Neo4j + MonetDB NoSQL</span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? "bg-neutral-800 text-white shadow-sm"
                    : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-indigo-400" : "text-neutral-500"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* System Pill & Mobile Trigger */}
        <div className="flex items-center gap-2">
          <Link
            href="/system"
            className="hidden sm:inline-flex items-center gap-2 rounded-full border border-neutral-800 bg-neutral-900/90 px-3 py-1 text-xs text-neutral-300 hover:border-neutral-700 hover:text-white transition-colors"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-[11px] text-neutral-400 flex items-center gap-1">
              <Database className="h-3 w-3 text-neutral-400" />
              Dual DB Active
            </span>
          </Link>

          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
            className="md:hidden rounded-lg p-2 text-neutral-400 hover:bg-neutral-900 hover:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-neutral-800 bg-neutral-950 px-4 pt-2 pb-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium ${
                  isActive
                    ? "bg-neutral-800 text-white font-semibold"
                    : "text-neutral-300 hover:bg-neutral-900"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4 w-4 ${isActive ? "text-indigo-400" : "text-neutral-500"}`} />
                  <span>{item.label}</span>
                </div>
                <span className="text-[11px] text-neutral-500">{item.description}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
}
