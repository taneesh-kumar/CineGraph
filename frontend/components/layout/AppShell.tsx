import { Suspense } from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen flex flex-col bg-neutral-950 text-neutral-100">
      <Suspense fallback={<div className="h-16 border-b border-neutral-800/80 bg-neutral-950" />}>
        <Navbar />
      </Suspense>
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 focus:outline-none">
        {children}
      </main>
      <Footer />
    </div>
  );
}
