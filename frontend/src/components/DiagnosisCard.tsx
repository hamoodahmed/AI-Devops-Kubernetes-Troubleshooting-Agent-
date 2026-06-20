"use client";

import React, { useState } from "react";
import { 
  CheckCircle, 
  AlertTriangle, 
  Terminal, 
  Copy, 
  Check, 
  FileText, 
  Activity, 
  Layout, 
  Network,
  HelpCircle,
  ShieldCheck,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { InvestigationResult } from "../types";

interface DiagnosisCardProps {
  result: InvestigationResult;
}

export function DiagnosisCard({ result }: DiagnosisCardProps) {
  const { diagnosis, evidence, cluster, namespace } = result;
  const [activeTab, setActiveTab] = useState<"diagnosis" | "pods" | "logs" | "events" | "deployments" | "network">("diagnosis");
  const [copied, setCopied] = useState(false);

  const copyCommand = () => {
    navigator.clipboard.writeText(diagnosis.kubectl_command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Get color based on confidence score
  const getConfidenceColor = (score: number) => {
    if (score >= 90) return "text-emerald-400 bg-emerald-950/30 border-emerald-900/50";
    if (score >= 70) return "text-amber-400 bg-amber-950/30 border-amber-900/50";
    return "text-rose-400 bg-rose-950/30 border-rose-900/50";
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/30 shadow-xl overflow-hidden backdrop-blur-sm">
      {/* Top Banner */}
      <div className="border-b border-slate-800 bg-slate-900/60 px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-md font-bold text-white uppercase tracking-wider">Troubleshooting Diagnosis Report</h2>
          <p className="text-xs text-slate-400 mt-1">
            Cluster Context: <span className="text-slate-300 font-semibold">{cluster}</span> &bull; Namespace: <span className="text-slate-300 font-semibold">{namespace}</span>
          </p>
        </div>
        <div className={`flex items-center space-x-2 rounded-full border px-3.5 py-1 text-xs font-semibold ${getConfidenceColor(diagnosis.confidence)}`}>
          <ShieldCheck className="h-4 w-4" />
          <span>SRE Confidence: {diagnosis.confidence}%</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-950 overflow-x-auto scrollbar-thin scrollbar-thumb-slate-800">
        {[
          { id: "diagnosis", label: "AI SRE Diagnosis", icon: ShieldCheck },
          { id: "pods", label: "Pods Status", icon: Activity },
          { id: "logs", label: "Containers Logs", icon: FileText },
          { id: "events", label: "Cluster Events", icon: AlertTriangle },
          { id: "deployments", label: "Deployments", icon: Layout },
          { id: "network", label: "Network status", icon: Network },
        ].map((tab) => {
          const Icon = tab.icon;
          const isSelected = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 border-b-2 px-5 py-4 text-xs font-semibold tracking-wider uppercase transition whitespace-nowrap focus:outline-none ${
                isSelected
                  ? "border-indigo-500 bg-slate-900/50 text-indigo-400"
                  : "border-transparent text-slate-400 hover:bg-slate-900/20 hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Panel Content */}
      <div className="p-6">
        
        {/* Diagnosis Tab */}
        {activeTab === "diagnosis" && (
          <div className="space-y-6">
            {/* Root Cause Card */}
            <div className="rounded-lg border border-red-950 bg-red-950/10 p-5">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 shrink-0" />
                <div>
                  <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider">Primary Root Cause</h3>
                  <p className="mt-2 text-base font-semibold text-white leading-relaxed">
                    {diagnosis.root_cause}
                  </p>
                </div>
              </div>
            </div>

            {/* Explanation */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Technical Analysis</h3>
              <div className="text-sm text-slate-300 bg-slate-950/50 rounded-lg p-4 leading-relaxed border border-slate-800">
                {diagnosis.explanation}
              </div>
            </div>

            {/* Suggested Fix */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Suggested Correction Steps</h3>
              <div className="text-sm text-slate-300 bg-slate-950/50 rounded-lg p-4 leading-relaxed border border-slate-800 space-y-2">
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-indigo-400 mt-0.5 shrink-0" />
                  <span>{diagnosis.fix}</span>
                </div>
              </div>
            </div>

            {/* Actionable kubectl command */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Resolution kubectl Command</h3>
              <div className="relative flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-indigo-300">
                <span className="break-all select-all pr-8">{diagnosis.kubectl_command}</span>
                <button
                  onClick={copyCommand}
                  className="absolute right-3 rounded bg-slate-900 border border-slate-800 p-1.5 text-slate-400 hover:text-white transition focus:outline-none"
                  title="Copy command"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                </button>
              </div>
            </div>

            {/* Prevention Recommendation */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Prevention recommendation</h3>
              <div className="text-sm text-slate-300 bg-slate-950/50 rounded-lg p-4 leading-relaxed border border-slate-800 flex items-start space-x-2">
                <HelpCircle className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
                <span>{diagnosis.prevention}</span>
              </div>
            </div>
          </div>
        )}

        {/* Pods Status Tab */}
        {activeTab === "pods" && (
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Pods Inventory Overview</h3>
            <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-300 leading-relaxed">
              {evidence.pods.raw_output || "No pod details gathered."}
            </pre>
            {evidence.pods.problematic_pods.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-2">Unhealthy Resources Pinpointed</h4>
                <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/20">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-950/60 font-semibold text-slate-400">
                        <th className="p-3">Name</th>
                        <th className="p-3">Namespace</th>
                        <th className="p-3">Ready</th>
                        <th className="p-3">Status</th>
                        <th className="p-3">Restarts</th>
                        <th className="p-3">Age</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50 text-slate-300">
                      {evidence.pods.problematic_pods.map((pod, i) => (
                        <tr key={i} className="hover:bg-slate-900/30">
                          <td className="p-3 font-semibold text-white">{pod.name}</td>
                          <td className="p-3">{pod.namespace}</td>
                          <td className="p-3">{pod.ready}</td>
                          <td className="p-3">
                            <span className="rounded bg-red-950/40 border border-red-900/40 px-2 py-0.5 text-[10px] font-bold text-red-400">
                              {pod.status}
                            </span>
                          </td>
                          <td className="p-3 text-red-400 font-semibold">{pod.restarts}</td>
                          <td className="p-3">{pod.age}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Containers Logs Tab */}
        {activeTab === "logs" && (
          <div className="space-y-6">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Troubled Containers Logs Summary</h3>
            {Object.keys(evidence.logs).length === 0 ? (
              <p className="text-sm text-slate-400 italic">No container logs were collected (all active resources are operational).</p>
            ) : (
              Object.entries(evidence.logs).map(([podName, logData]) => (
                <div key={podName} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white bg-slate-800 px-2 py-1 rounded">Pod: {podName}</span>
                    <span className="text-[10px] text-slate-500 font-medium">Namespace: {logData.namespace}</span>
                  </div>
                  <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-red-300/90 leading-relaxed max-h-[300px]">
                    {logData.success 
                      ? (logData.filtered_logs?.join("\n") || "No exceptions/error patterns detected in log trace.") 
                      : `Log Collection Failed: ${logData.error}`
                    }
                  </pre>
                </div>
              ))
            )}
          </div>
        )}

        {/* Cluster Events Tab */}
        {activeTab === "events" && (
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Recent Warning / Exception Events</h3>
            {evidence.events.warnings.length === 0 ? (
              <p className="text-sm text-slate-400 italic">No warning events detected within namespace.</p>
            ) : (
              <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-4 divide-y divide-slate-800/60 font-mono text-[11px] text-amber-300/90 space-y-2 max-h-[350px] overflow-y-auto">
                {evidence.events.warnings.map((evt, i) => (
                  <div key={i} className="py-2.5 first:pt-0 last:pb-0 break-words leading-relaxed">
                    {evt}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Deployments Tab */}
        {activeTab === "deployments" && (
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Deployments Conditions Overview</h3>
            <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-300 leading-relaxed">
              {evidence.deployments.raw_output || "No deployments detected."}
            </pre>
            {evidence.deployments.unhealthy_deployments.length > 0 && (
              <div className="mt-4 space-y-4">
                <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Unhealthy Rollout Details</h4>
                {evidence.deployments.unhealthy_deployments.map((dep, i) => (
                  <div key={i} className="space-y-2 border border-amber-900/40 bg-amber-950/5 rounded-lg p-4">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-white uppercase">{dep.name}</span>
                      <span className="text-amber-400 font-semibold">Ready: {dep.ready} (Available: {dep.available})</span>
                    </div>
                    <pre className="overflow-x-auto rounded border border-slate-900 bg-slate-950/80 p-3 font-mono text-[11px] text-slate-300 leading-relaxed max-h-[200px]">
                      {dep.details || "No describe info available."}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Network status Tab */}
        {activeTab === "network" && (
          <div className="space-y-6">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Kubernetes services status</h3>
              <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-300 leading-relaxed">
                {evidence.network.services || "No services detected."}
              </pre>
            </div>
            
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Active Endpoints inventory</h3>
              <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-300 leading-relaxed">
                {evidence.network.endpoints || "No endpoints detected."}
              </pre>
            </div>

            {evidence.network.issues.length > 0 && (
              <div>
                <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">Endpoints Selection Incidents</h3>
                <div className="space-y-2">
                  {evidence.network.issues.map((issue, i) => (
                    <div key={i} className="rounded-lg border border-rose-950 bg-rose-950/15 p-4 text-xs">
                      <div className="font-bold text-white">Service: {issue.service_name} (Namespace: {issue.namespace})</div>
                      <div className="mt-2 text-rose-300 font-semibold leading-relaxed">{issue.issue}</div>
                      <div className="mt-1 font-mono text-slate-400">Endpoints matches: {issue.endpoints}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
