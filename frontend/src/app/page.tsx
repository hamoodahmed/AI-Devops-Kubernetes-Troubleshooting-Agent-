"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Terminal, Lock, Mail, AlertCircle, ArrowRight } from "lucide-react";
import { insforgeAuth } from "../services/insforge";

export default function LoginPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if session already exists
  useEffect(() => {
    const checkSession = async () => {
      const session = await insforgeAuth.getSession();
      if (session) {
        router.push("/dashboard");
      }
    };
    checkSession();
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    setError(null);

    const action = isSignUp 
      ? insforgeAuth.signUp(email, password)
      : insforgeAuth.signIn(email, password);

    const { data, error: err } = await action;

    if (err) {
      setError(err);
      setLoading(false);
    } else {
      router.push("/dashboard");
    }
  };

  const handleGuestAccess = async () => {
    setLoading(true);
    // ✅ Use dedicated guest method that bypasses password validation
    await insforgeAuth.signInAsGuest();
    router.push("/dashboard");
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-slate-950 px-4 py-12 text-slate-100 overflow-hidden">
      {/* Decorative Blur Background Circles */}
      <div className="absolute top-1/4 left-1/4 h-80 w-80 rounded-full bg-violet-600/10 blur-[100px]" />
      <div className="absolute bottom-1/4 right-1/4 h-80 w-80 rounded-full bg-indigo-500/10 blur-[100px]" />

      <div className="relative w-full max-w-md space-y-8 rounded-2xl border border-slate-800 bg-slate-900/30 p-8 shadow-2xl backdrop-blur-md">
        {/* Brand Icon & Heading */}
        <div className="flex flex-col items-center text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 shadow-xl shadow-indigo-500/20">
            <Terminal className="h-6 w-6 text-white" />
          </div>
          <h2 className="mt-6 text-2xl font-bold tracking-tight text-white sm:text-3xl">
            AI Kubernetes Agent
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Troubleshoot cluster outages and container failures in seconds
          </p>
        </div>

        {error && (
          <div className="flex items-center space-x-2.5 rounded-lg border border-red-900/50 bg-red-950/20 p-4 text-xs font-semibold text-red-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Email Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500">
                <Mail className="h-4 w-4" />
              </span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                placeholder="you@example.com"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 pl-10 pr-4 py-3 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-60"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500">
                <Lock className="h-4 w-4" />
              </span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 pl-10 pr-4 py-3 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-60"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-3 text-sm font-bold text-white shadow-lg transition hover:from-violet-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50"
          >
            <span>{loading ? "Authenticating..." : isSignUp ? "Sign Up" : "Sign In"}</span>
          </button>
        </form>

        <div className="flex flex-col space-y-4 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            disabled={loading}
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            {isSignUp ? "Already have an account? Sign In" : "Need an account? Sign Up"}
          </button>

          <div className="relative flex py-2 items-center">
            <div className="flex-grow border-t border-slate-800/80"></div>
            <span className="flex-shrink mx-4 text-xs font-semibold uppercase tracking-wider text-slate-600">Or</span>
            <div className="flex-grow border-t border-slate-800/80"></div>
          </div>

          <button
            onClick={handleGuestAccess}
            disabled={loading}
            className="flex w-full items-center justify-center space-x-2 rounded-lg border border-slate-800 bg-slate-950 px-4 py-3 text-xs font-bold text-slate-300 transition hover:bg-slate-900 hover:text-white"
          >
            <span>Continue as Guest (Simulation Mode)</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
