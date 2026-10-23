"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Database,
  Cpu,
  Server,
  Clock,
  ShieldCheck,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { HealthResponse, ReadinessResponse } from "@/lib/types";
import { EngineBadge } from "@/components/ui/EngineBadge";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";

export default function SystemStatusPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [healthLatencyMs, setHealthLatencyMs] = useState<number | null>(null);
  const [readyLatencyMs, setReadyLatencyMs] = useState<number | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const probeStatus = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const t0 = performance.now();
      const healthData = await apiClient.getHealth();
      const t1 = performance.now();
      setHealthLatencyMs(Math.round(t1 - t0));
      setHealth(healthData);

      const t2 = performance.now();
      const readyData = await apiClient.getReadiness();
      const t3 = performance.now();
      setReadyLatencyMs(Math.round(t3 - t2));
      setReadiness(readyData);

      setLastChecked(new Date().toLocaleTimeString());
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "System health probe failed";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    probeStatus();
  }, []);

  const isFullyHealthy =
    (health?.status === "healthy" || health?.status === "ok") &&
    readiness?.status === "ready" &&
    (readiness?.neo4j?.status === "connected" || readiness?.database_readiness?.neo4j === true) &&
    (readiness?.monetdb?.status === "connected" || readiness?.database_readiness?.monetdb === true);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Activity className="h-6 w-6 text-indigo-400" />
              System Status & Diagnostics
            </h1>
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                isFullyHealthy
                  ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                  : "bg-amber-950 text-amber-400 border border-amber-800"
              }`}
            >
              {isFullyHealthy ? "All Engines Operational" : "System Degraded"}
            </span>
          </div>
          <p className="text-sm text-neutral-400 mt-1">
            Real-time liveness and readiness inspection for FastAPI, Neo4j Graph, and MonetDB Column-Store.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {lastChecked && (
            <span className="text-xs text-neutral-500 font-mono flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Checked {lastChecked}
            </span>
          )}
          <button
            type="button"
            onClick={probeStatus}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-800 bg-neutral-900 px-3 py-1.5 text-xs font-medium text-neutral-300 hover:border-neutral-700 hover:text-white transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Refresh Probes</span>
          </button>
        </div>
      </div>

      {isLoading && !health ? (
        <LoadingState message="Probing FastAPI, Neo4j, and MonetDB diagnostic endpoints..." />
      ) : error && !health ? (
        <ErrorState
          title="Backend Unavailable"
          message={error}
          onRetry={probeStatus}
        />
      ) : (
        <div className="space-y-8">
          {/* Dual Engine Connectivity Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Neo4j Status Card */}
            <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
                    <Database className="h-6 w-6" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-white">Neo4j Community Graph</h2>
                    <span className="text-xs text-neutral-400 font-mono">Port 7687 • Bolt Protocol</span>
                  </div>
                </div>
                <EngineBadge engine="neo4j" />
              </div>

              <div className="pt-2 border-t border-neutral-800/80 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-neutral-400">Readiness Probe</span>
                  {readiness?.neo4j?.status === "connected" || readiness?.database_readiness?.neo4j ? (
                    <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                      <CheckCircle2 className="h-4 w-4" />
                      CONNECTED
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 text-rose-400 font-semibold">
                      <XCircle className="h-4 w-4" />
                      DISCONNECTED
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-neutral-400">Responsibility</span>
                  <span className="text-neutral-200">Movie Topology & Collaborative Walks</span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-neutral-400">Ingested Sample</span>
                  <span className="font-mono text-neutral-200">2,500 Movies, 16,224 Graph Users</span>
                </div>
              </div>
            </div>

            {/* MonetDB Status Card */}
            <div className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
                    <Cpu className="h-6 w-6" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-white">MonetDB Analytical Columnar</h2>
                    <span className="text-xs text-neutral-400 font-mono">Port 50000 • MAPI Protocol</span>
                  </div>
                </div>
                <EngineBadge engine="monetdb" />
              </div>

              <div className="pt-2 border-t border-neutral-800/80 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-neutral-400">Readiness Probe</span>
                  {readiness?.monetdb?.status === "connected" || readiness?.database_readiness?.monetdb ? (
                    <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                      <CheckCircle2 className="h-4 w-4" />
                      CONNECTED
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 text-rose-400 font-semibold">
                      <XCircle className="h-4 w-4" />
                      DISCONNECTED
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-neutral-400">Responsibility</span>
                  <span className="text-neutral-200">Columnar Fact Scans & Distributions</span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-neutral-400">Ingested Sample</span>
                  <span className="font-mono text-neutral-200">119,689 Ratings, 25,999 Tags</span>
                </div>
              </div>
            </div>
          </div>

          {/* Service Endpoints Diagnostic Table */}
          <div className="rounded-2xl border border-neutral-800 bg-neutral-900/40 p-6 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Server className="h-4 w-4 text-indigo-400" />
              FastAPI Diagnostic Endpoints
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-neutral-950 text-neutral-400 border-b border-neutral-800">
                  <tr>
                    <th className="py-2.5 px-3">Endpoint Route</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Roundtrip Latency</th>
                    <th className="py-2.5 px-3">Response Payload Summary</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800/60">
                  <tr>
                    <td className="py-2.5 px-3 text-white">GET /api/v1/health</td>
                    <td className="py-2.5 px-3 text-neutral-400">Liveness</td>
                    <td className="py-2.5 px-3">
                      <span className="inline-flex items-center gap-1 text-emerald-400">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        {health?.status?.toUpperCase() ?? "OK"}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-neutral-300">
                      {healthLatencyMs !== null ? `${healthLatencyMs} ms` : "—"}
                    </td>
                    <td className="py-2.5 px-3 text-neutral-400 truncate max-w-xs font-sans">
                      {health?.app_name || "CineGraph Backend"} (v{health?.version || "1.0.0"})
                    </td>
                  </tr>

                  <tr>
                    <td className="py-2.5 px-3 text-white">GET /api/v1/ready</td>
                    <td className="py-2.5 px-3 text-neutral-400">Readiness</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-flex items-center gap-1 ${
                          readiness?.status === "ready" ? "text-emerald-400" : "text-amber-400"
                        }`}
                      >
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        {readiness?.status?.toUpperCase() ?? "READY"}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-neutral-300">
                      {readyLatencyMs !== null ? `${readyLatencyMs} ms` : "—"}
                    </td>
                    <td className="py-2.5 px-3 text-neutral-400 truncate max-w-xs font-sans">
                      Neo4j: {readiness?.database_readiness?.neo4j ? "true" : "false"}, MonetDB:{" "}
                      {readiness?.database_readiness?.monetdb ? "true" : "false"}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Academic Architecture Disclosure */}
          <div className="rounded-xl border border-neutral-800 bg-neutral-950 p-4 text-xs text-neutral-400 space-y-2">
            <div className="flex items-center gap-2 text-neutral-200 font-semibold">
              <ShieldCheck className="h-4 w-4 text-indigo-400" />
              <span>Architectural Verification Note</span>
            </div>
            <p className="leading-relaxed">
              CineGraph maintains strict database role separation. No credentials or connection
              strings are exposed to client-side code. All queries route through the authenticated
              FastAPI service layer at <code className="text-neutral-300">http://127.0.0.1:8000</code>.
              Database readiness checks run active protocol queries (`RETURN 1` in Cypher for Neo4j
              and `SELECT 1` in SQL for MonetDB) during each `/api/v1/ready` probe.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
