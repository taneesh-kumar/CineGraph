export default function Home() {
  return (
    <main className="min-h-screen flex flex-col justify-between p-6 md:p-12 max-w-7xl mx-auto">
      {/* Header / Nav */}
      <header className="flex items-center justify-between border-b border-neutral-800 pb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-rose-500/20">
            CG
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">CineGraph</h1>
            <p className="text-xs text-neutral-400">Hybrid NoSQL Movie Analytics & Graph Engine</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Foundation Ready
          </span>
        </div>
      </header>

      {/* Hero / Placeholder UI */}
      <section className="my-auto py-16 flex flex-col items-center text-center">
        <div className="inline-block px-3 py-1 mb-6 text-xs font-semibold tracking-wider text-rose-400 uppercase bg-rose-950/40 border border-rose-800/50 rounded-full">
          NoSQL Course Project
        </div>
        <h2 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white max-w-4xl leading-tight">
          High-Velocity Graph Traversals Meets{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-400">
            Columnar Trend Analytics
          </span>
        </h2>
        <p className="mt-6 text-lg text-neutral-400 max-w-2xl leading-relaxed">
          CineGraph blends <strong className="text-neutral-200">Neo4j</strong> for rich entity relationships, co-acting networks, and personalized recommendations with <strong className="text-neutral-200">MonetDB</strong> for high-throughput OLAP aggregations across millions of movie ratings.
        </p>

        {/* Dual Engine Cards */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-3xl text-left">
          <div className="p-6 rounded-2xl bg-neutral-900/60 border border-neutral-800 backdrop-blur">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-amber-400">Graph Database</span>
              <span className="text-xs text-neutral-500 font-mono">Port 7687</span>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Neo4j Community</h3>
            <p className="text-sm text-neutral-400 mb-4">
              Powers topological traversals, collaborative filtering, actor/director paths, and collaborative recommendations.
            </p>
            <div className="text-xs font-mono text-neutral-400 bg-neutral-950 p-2.5 rounded-lg border border-neutral-850">
              Cypher: (:User)-[:RATED]-&gt;(:Movie)&lt;-[:ACTED_IN]-(:Actor)
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-neutral-900/60 border border-neutral-800 backdrop-blur">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Column Store</span>
              <span className="text-xs text-neutral-500 font-mono">Port 50000</span>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">MonetDB Analytics</h3>
            <p className="text-sm text-neutral-400 mb-4">
              Executes high-performance aggregations, release-year metrics, rating trends over time, and comparative benchmarks.
            </p>
            <div className="text-xs font-mono text-neutral-400 bg-neutral-950 p-2.5 rounded-lg border border-neutral-850">
              SQL: SELECT genre, AVG(rating) FROM ratings GROUP BY genre
            </div>
          </div>
        </div>

        {/* API Status Badge */}
        <div className="mt-10 p-4 rounded-xl bg-neutral-900/40 border border-neutral-800/80 max-w-md w-full flex items-center justify-between text-xs text-neutral-400">
          <span>Backend Target:</span>
          <code className="text-neutral-200 font-mono bg-neutral-950 px-2 py-0.5 rounded border border-neutral-800">
            http://127.0.0.1:8000/health
          </code>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-neutral-800 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-500">
        <p>© CineGraph Team. Academic NoSQL Evaluation System.</p>
        <p className="mt-2 sm:mt-0 font-mono">Status: Repository Foundation Initialized</p>
      </footer>
    </main>
  );
}
