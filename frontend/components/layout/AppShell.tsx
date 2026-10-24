import { Suspense } from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen flex flex-col bg-neutral-950 text-neutral-100 relative overflow-x-hidden selection:bg-indigo-500 selection:text-white">
      {/* Ambient background glows */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-indigo-600/10 rounded-full blur-[100px]" />
        <div className="absolute top-1/4 -right-32 w-[28rem] h-[28rem] bg-purple-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-emerald-600/8 rounded-full blur-[100px]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-10%,rgba(99,102,241,0.08),rgba(255,255,255,0))]" />
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        <Suspense fallback={<div className="h-16 border-b border-neutral-800/80 bg-neutral-950/80" />}>
          <Navbar />
        </Suspense>
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 focus:outline-none">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );
}
