import { createClient } from "@insforge/sdk";
import { InvestigationHistoryItem } from "../types";

const INSFORGE_URL = process.env.NEXT_PUBLIC_INSFORGE_URL || "";
const INSFORGE_ANON_KEY = process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY || "";

// Initialize the real client only if both keys are provided
export const insforgeClient = INSFORGE_URL && INSFORGE_ANON_KEY
  ? createClient({ baseUrl: INSFORGE_URL, anonKey: INSFORGE_ANON_KEY })
  : null;

const GUEST_EMAIL = "guest@simulation.local";

// Abstraction layer for Authentication
export const insforgeAuth = {
  async signUp(email: string, password: string) {
    if (insforgeClient) {
      try {
        const { data, error } = await insforgeClient.auth.signUp({ email, password });
        if (error) throw error;
        return { data, error: null };
      } catch (err: any) {
        return { data: null, error: err.message || "Sign up failed" };
      }
    } else {
      const users = JSON.parse(localStorage.getItem("sim_users") || "{}");
      if (users[email]) {
        return { data: null, error: "User already exists. Please sign in instead." };
      }
      users[email] = { email, password };
      localStorage.setItem("sim_users", JSON.stringify(users));
      const mockSession = { user: { email }, access_token: "sim-token-" + Date.now() };
      localStorage.setItem("sim_session", JSON.stringify(mockSession));
      return { data: mockSession, error: null };
    }
  },

  async signIn(email: string, password: string) {
    if (insforgeClient) {
      try {
        const { data, error } = await insforgeClient.auth.signInWithPassword({ email, password });
        if (error) throw error;
        return { data, error: null };
      } catch (err: any) {
        return { data: null, error: err.message || "Authentication failed" };
      }
    } else {
      const users = JSON.parse(localStorage.getItem("sim_users") || "{}");
      const user = users[email];
      if (!user || user.password !== password) {
        return { data: null, error: "Invalid email or password" };
      }
      const mockSession = { user: { email }, access_token: "sim-token-" + Date.now() };
      localStorage.setItem("sim_session", JSON.stringify(mockSession));
      return { data: mockSession, error: null };
    }
  },

  // ✅ FIX: Guest access bypasses password validation entirely — directly sets session
  async signInAsGuest() {
    if (insforgeClient) {
      // With real InsForge, try anonymous/guest sign-in if supported, else fallback
      try {
        const { data, error } = await insforgeClient.auth.signInWithPassword({
          email: GUEST_EMAIL,
          password: "guest-simulation-mode",
        });
        if (!error && data) return { data, error: null };
      } catch (_) {}
    }
    // Always works: directly write a guest session to localStorage
    const guestSession = {
      user: { email: GUEST_EMAIL },
      access_token: "guest-sim-token-" + Date.now(),
      is_guest: true,
    };
    localStorage.setItem("sim_session", JSON.stringify(guestSession));
    return { data: guestSession, error: null };
  },

  async signOut() {
    if (insforgeClient) {
      try { await insforgeClient.auth.signOut(); } catch (_) {}
    }
    localStorage.removeItem("sim_session");
  },

  async getSession() {
    if (insforgeClient) {
      try {
        const { data } = await (insforgeClient.auth as any).getSession();
        if (data?.session) return data.session;
      } catch (_) {}
    }
    // Fallback: read from localStorage (works for both real+guest simulation)
    if (typeof window === "undefined") return null;
    const sessionStr = localStorage.getItem("sim_session");
    return sessionStr ? JSON.parse(sessionStr) : null;
  },
};

// Abstraction layer for History database
export const insforgeDb = {
  async saveInvestigation(item: Omit<InvestigationHistoryItem, "id" | "timestamp">) {
    const timestamp = new Date().toISOString();
    const id = Math.random().toString(36).substring(2, 9);
    const newItem: InvestigationHistoryItem = { ...item, id, timestamp };

    if (insforgeClient) {
      try {
        const { data, error } = await (insforgeClient as any)
          .from("investigations")
          .insert([newItem])
          .select();
        if (error) throw error;
        return data ? data[0] : newItem;
      } catch (err) {
        console.error("InsForge DB write error, falling back to localStorage:", err);
        this._saveLocal(newItem);
        return newItem;
      }
    } else {
      this._saveLocal(newItem);
      return newItem;
    }
  },

  async getHistory(): Promise<InvestigationHistoryItem[]> {
    if (insforgeClient) {
      try {
        const { data, error } = await (insforgeClient as any)
          .from("investigations")
          .select("*")
          .order("timestamp", { ascending: false });
        if (error) throw error;
        return data || [];
      } catch (err) {
        console.error("InsForge DB read error, loading from localStorage:", err);
        return this._getLocal();
      }
    } else {
      return this._getLocal();
    }
  },

  _saveLocal(item: InvestigationHistoryItem) {
    const history = this._getLocal();
    history.unshift(item);
    // Keep max 50 entries
    localStorage.setItem("sim_history", JSON.stringify(history.slice(0, 50)));
  },

  _getLocal(): InvestigationHistoryItem[] {
    if (typeof window === "undefined") return [];
    const historyStr = localStorage.getItem("sim_history");
    return historyStr ? JSON.parse(historyStr) : [];
  },
};
