"use client";

import React from "react";
import { History, Calendar, ShieldCheck, CheckCircle2, ChevronRight } from "lucide-react";
import { InvestigationHistoryItem } from "../types";

interface HistoryListProps {
  history: InvestigationHistoryItem[];
  onSelect: (item: InvestigationHistoryItem) => void;
  selectedId?: string;
}

export function HistoryList({ history, onSelect, selectedId }: HistoryListProps) {
  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-4 mb-6">
        <History className="h-5 w-5 text-indigo-400" />
        <h2 className="text-md font-bold text-white uppercase tracking-wider">Investigation History</h2>
      </div>

      {history.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <History className="h-8 w-8 text-slate-700 mb-3" />
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">No Investigations Yet</p>
          <p className="text-xs text-slate-600 mt-1">Run an investigation to store results here.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-800">
          {history.map((item) => {
            const isSelected = selectedId === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelect(item)}
                className={`w-full text-left rounded-lg border p-4 transition-all duration-200 flex items-center justify-between group ${
                  isSelected
                    ? "bg-indigo-950/20 border-indigo-500/80 shadow-md shadow-indigo-500/5"
                    : "bg-slate-950/40 border-slate-800/80 hover:bg-slate-900/40 hover:border-slate-700"
                }`}
              >
                <div className="space-y-1.5 min-w-0 pr-2">
                  <div className="flex items-center space-x-2">
                    <span className="rounded bg-indigo-950/60 border border-indigo-900/50 px-1.5 py-0.5 text-[9px] font-bold text-indigo-400 tracking-wide uppercase">
                      {item.cluster.replace("simulation-", "sim:")}
                    </span>
                    <span className="text-[10px] text-slate-500 font-medium">
                      ns: {item.namespace}
                    </span>
                  </div>
                  <h3 className="text-xs font-bold text-white truncate group-hover:text-indigo-400 transition-colors">
                    {item.root_cause}
                  </h3>
                  <div className="flex items-center text-[10px] text-slate-500 space-x-3">
                    <span className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      {formatDate(item.timestamp)}
                    </span>
                    <span className="flex items-center text-indigo-400 font-semibold">
                      <ShieldCheck className="h-3 w-3 mr-0.5" />
                      {item.confidence}%
                    </span>
                  </div>
                </div>
                <ChevronRight className={`h-4 w-4 shrink-0 transition-transform ${
                  isSelected ? "text-indigo-400 translate-x-0.5" : "text-slate-600 group-hover:text-slate-400"
                }`} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
