"use client";

import React from "react";
import { Terminal, LogOut, ShieldAlert } from "lucide-react";
import { insforgeAuth } from "../services/insforge";

interface HeaderProps {
  userEmail: string | null;
  onLogout: () => void;
}

export function Header({ userEmail, onLogout }: HeaderProps) {
  const handleLogout = async () => {
    await insforgeAuth.signOut();
    onLogout();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-500 shadow-lg shadow-indigo-500/30">
            <Terminal className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white sm:text-xl">
              AI Kubernetes <span className="bg-gradient-to-r from-violet-400 to-indigo-300 bg-clip-text text-transparent">Troubleshooting Agent</span>
            </h1>
          </div>
        </div>

        {userEmail && (
          <div className="flex items-center space-x-4">
            <div className="hidden rounded-full bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 border border-slate-800 sm:block">
              Connected: <span className="text-indigo-400 font-semibold">{userEmail}</span>
            </div>
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-300 transition hover:bg-red-950/30 hover:border-red-900/50 hover:text-red-400"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
