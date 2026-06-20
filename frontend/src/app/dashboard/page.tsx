"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2, CheckCircle2, AlertCircle, Activity } from "lucide-react";

import { Header } from "../../components/Header";
import { ClusterSelector } from "../../components/ClusterSelector";
import { DiagnosisCard } from "../../components/DiagnosisCard";
import { HistoryList } from "../../components/HistoryList";
import { useInvestigation } from "../../hooks/useInvestigation";
import { insforgeAuth, insforgeDb } from "../../services/insforge";
import { InvestigationHistoryItem, InvestigationResult } from "../../types";

export default function DashboardPage() {
  const router = useRouter();
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [history, setHistory] = useState<InvestigationHistoryItem[]>([]);
  const [historyResult, setHistoryResult] = useState<InvestigationResult | null>(null);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | undefined>(undefined);

  const { loading, steps, result, error, run, reset } = useInvestigation();

  // ✅ Auth check: redirect to login if no session
  useEffect(() => {
    const checkAuth = async () => {
      const session = await insforgeAuth.getSession();
      if (!session) {
        router.push("/");
        return;
      }
      setUserEmail(session.user?.email || "guest@simulation.local");
      setAuthLoading(false);
      loadHistory();
    };
    checkAuth();
  }, [router]);

  const loadHistory = async () => {
    try {
      const data = await insforgeDb.getHistory();
      setHistory(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const handleInvestigate = async (cluster: string, namespace: string, scenario: string | null) => {
    setHistoryResult(null);
    setSelectedHistoryId(undefined);
    reset();
    await run(cluster, namespace, scenario);
    await loadHistory();
  };

  // ✅ Fixed: store history item as proper InvestigationResult state
  const handleSelectHistoryItem = (item: InvestigationHistoryItem) => {
    if (!item.diagnosis) return;
    setSelectedHistoryId(item.id);
    reset();
    setHistoryResult({
      status: "success",
      cluster: item.cluster,
      namespace: item.namespace,
      is_simulated: true,
      evidence: {
        pods: { healthy: true, problematic_pods: [], raw_output: "Historical record — rerun investigation for live pod data." },
        logs: {},
        events: { success: true, warnings: [] },
        deployments: { success: true, unhealthy_deployments: [] },
        network: { success: true, issues: [] },
      },
      diagnosis: item.diagnosis,
    });
  };

  const handleLogout = async () => {
    await insforgeAuth.signOut();
    setUserEmail(null);
    router.push("/");
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  // Active result = live investigation OR selected history item
  const activeResult: InvestigationResult | null = result || historyResult;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header userEmail={userEmail} onLogout={handleLogout} />

      <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">

          {/* Left Column */}
          <div className="space-y-8 lg:col-span-1">
            <ClusterSelector onInvestigate={handleInvestigate} loading={loading} />
            <HistoryList
              history={history}
              onSelect={handleSelectHistoryItem}
              selectedId={selectedHistoryId}
            />
          </div>

          {/* Right Column */}
          <div className="lg:col-span-2 space-y-6">

            {/* Progress checklist while loading */}
            {loading && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 shadow-xl backdrop-blur-sm space-y-6">
                <div>
                  <h2 className="text-md font-bold text-white uppercase tracking-wider flex items-center">
                    <Loader2 className="mr-2 h-4 w-4 animate-spin text-indigo-500" />
                    Investigating Kubernetes Cluster...
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">Collecting evidence for AI SRE analysis.</p>
                </div>

                <div className="space-y-4">
                  {steps.map((step) => (
                    <div
                      key={step.id}
                      className={`flex items-start space-x-3.5 p-3 rounded-lg border transition ${
                        step.status === "running"
                          ? "bg-indigo-950/15 border-indigo-500/30 text-white"
                          : step.status === "completed"
                          ? "bg-slate-900/40 border-slate-800/80 text-slate-300"
                          : step.status === "failed"
                          ? "bg-red-950/10 border-red-900/30 text-red-400"
                          : "bg-slate-950/20 border-slate-900/20 text-slate-600"
                      }`}
                    >
                      <div className="mt-0.5">
                        {step.status === "running" && <Loader2 className="h-4 w-4 animate-spin text-indigo-400" />}
                        {step.status === "completed" && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
                        {step.status === "failed" && <AlertCircle className="h-4 w-4 text-red-500" />}
                        {step.status === "idle" && <div className="h-4 w-4 rounded-full border border-slate-800 bg-slate-950" />}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="text-xs font-bold uppercase tracking-wider">{step.label}</div>
                        <div className="text-xs text-slate-400 mt-0.5 truncate">{step.message}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Error state */}
            {error && !loading && (
              <div className="rounded-xl border border-red-950 bg-red-950/10 p-6 shadow-xl">
                <div className="flex items-start space-x-3">
                  <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 shrink-0" />
                  <div>
                    <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider">Investigation Failure</h3>
                    <p className="mt-2 text-sm text-slate-300 leading-relaxed">{error}</p>
                    <div className="mt-4 rounded-lg bg-slate-950 border border-slate-900 p-4 text-xs text-slate-400 space-y-1.5 leading-relaxed">
                      <div className="font-semibold text-white">Please check:</div>
                      <div>&bull; Verify the FastAPI backend is running on port 8000.</div>
                      <div>&bull; Ensure kubeconfig path is correct or use a simulation cluster.</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Diagnosis card */}
            {activeResult && !loading && (
              <DiagnosisCard result={activeResult} />
            )}

            {/* Empty state */}
            {!loading && !error && !activeResult && (
              <div className="rounded-xl border border-slate-800 border-dashed bg-slate-900/10 p-12 text-center flex flex-col items-center justify-center min-h-[300px]">
                <Activity className="h-10 w-10 text-slate-700 mb-4" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Troubleshooter Ready</h3>
                <p className="text-xs text-slate-400 mt-2 max-w-sm leading-relaxed">
                  Select a cluster context on the left, choose a failure scenario, then click <strong>Investigate Cluster</strong> to get AI root cause analysis.
                </p>
              </div>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}
