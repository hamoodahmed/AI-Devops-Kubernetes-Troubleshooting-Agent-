"use client";

import React, { useState, useEffect } from "react";
import { Server, Settings, Terminal, RefreshCw } from "lucide-react";
import { ClusterInfo } from "../types";
import { api } from "../services/api";

interface ClusterSelectorProps {
  onInvestigate: (cluster: string, namespace: string, scenario: string | null) => void;
  loading: boolean;
}

export function ClusterSelector({ onInvestigate, loading }: ClusterSelectorProps) {
  const [clusters, setClusters] = useState<ClusterInfo[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>("");
  const [namespace, setNamespace] = useState<string>("default");
  const [scenario, setScenario] = useState<string>("CrashLoopBackOff");
  const [fetching, setFetching] = useState<boolean>(false);

  const loadClusters = async () => {
    setFetching(true);
    try {
      const data = await api.getClusters();
      setClusters(data.clusters);
      
      // Select the active context by default
      const active = data.clusters.find((c: any) => c.is_active);
      if (active) {
        setSelectedCluster(active.name);
      } else if (data.clusters.length > 0) {
        setSelectedCluster(data.clusters[0].name);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    loadClusters();
  }, []);

  const currentClusterObj = clusters.find(c => c.name === selectedCluster);
  const showScenarioSelect = currentClusterObj?.is_simulated || selectedCluster.startsWith("simulation-");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCluster) return;
    onInvestigate(selectedCluster, namespace, showScenarioSelect ? scenario : null);
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div className="flex items-center space-x-2">
          <Settings className="h-5 w-5 text-indigo-400" />
          <h2 className="text-md font-bold text-white uppercase tracking-wider">Configure Investigation</h2>
        </div>
        <button
          onClick={loadClusters}
          disabled={fetching || loading}
          className="rounded-md p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition disabled:opacity-50"
          title="Reload Cluster Contexts"
        >
          <RefreshCw className={`h-4 w-4 ${fetching ? "animate-spin" : ""}`} />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Cluster Selector */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Target Cluster Context
          </label>
          <div className="relative">
            <select
              value={selectedCluster}
              onChange={(e) => setSelectedCluster(e.target.value)}
              disabled={loading || fetching}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white shadow-inner outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-60"
            >
              {clusters.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name} {c.is_simulated ? " (Simulated)" : " (Local)"}
                </option>
              ))}
            </select>
          </div>
          {currentClusterObj?.server && (
            <p className="mt-2 text-xs text-slate-500 truncate flex items-center">
              <Server className="h-3 w-3 mr-1 inline" />
              API Server: {currentClusterObj.server}
            </p>
          )}
        </div>

        {/* Namespace Input */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Kubernetes Namespace
          </label>
          <input
            type="text"
            value={namespace}
            onChange={(e) => setNamespace(e.target.value)}
            disabled={loading}
            placeholder="e.g. default, kube-system"
            className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-60"
          />
          <div className="mt-2 flex space-x-2">
            <button
              type="button"
              onClick={() => setNamespace("default")}
              disabled={loading}
              className="rounded-md border border-slate-800/80 bg-slate-950 px-2 py-1 text-[10px] font-semibold text-slate-400 hover:text-white transition"
            >
              default
            </button>
            <button
              type="button"
              onClick={() => setNamespace("all-namespaces")}
              disabled={loading}
              className="rounded-md border border-slate-800/80 bg-slate-950 px-2 py-1 text-[10px] font-semibold text-slate-400 hover:text-white transition"
            >
              all-namespaces
            </button>
          </div>
        </div>

        {/* Simulation Scenario (Conditionally Shown) */}
        {showScenarioSelect && (
          <div className="rounded-lg border border-indigo-950 bg-indigo-950/10 p-4 border-dashed">
            <label className="block text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">
              Select Troubleshooting Scenario (Simulation)
            </label>
            <select
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              disabled={loading}
              className="w-full rounded-lg border border-indigo-900 bg-slate-950 px-3 py-2.5 text-xs text-white outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option value="CrashLoopBackOff">CrashLoopBackOff (Missing environment variable)</option>
              <option value="ImagePullBackOff">ImagePullBackOff (Incorrect image tag reference)</option>
              <option value="OOMKilled">OOMKilled (Low memory resource limits configured)</option>
              <option value="SelectorMismatch">SelectorMismatch (Service selector labels mismatch)</option>
              <option value="Healthy">Healthy (No failures detected)</option>
            </select>
            <p className="mt-2 text-[11px] text-indigo-400/80 leading-relaxed">
              * This scenario will inject specific Kubernetes container failures for the AI agent to diagnose.
            </p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !selectedCluster}
          className="flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-indigo-500/25 transition hover:from-violet-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:pointer-events-none"
        >
          <Terminal className="h-4 w-4" />
          <span>{loading ? "Investigating Cluster..." : "Investigate Cluster"}</span>
        </button>
      </form>
    </div>
  );
}
