import axios from "axios";
import { ClustersResponse, ProgressEvent } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  async getClusters(): Promise<ClustersResponse> {
    try {
      const response = await apiClient.get<ClustersResponse>("/api/clusters");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch clusters from backend:", error);
      // Return simulated backup list to make sure app runs locally
      return {
        clusters: [
          { name: "simulation-minikube-dev", is_active: true, is_simulated: true, server: "https://127.0.0.1:8443 (Simulated Developer Cluster)" },
          { name: "simulation-eks-production", is_active: false, is_simulated: true, server: "https://aws-eks.prod.k8s.local (Simulated Production Cluster)" }
        ]
      };
    }
  },

  async startInvestigation(
    cluster: string,
    namespace: string,
    scenario: string | null,
    onProgress: (event: ProgressEvent) => void,
    onComplete: (result: any) => void,
    onError: (err: any) => void
  ) {
    try {
      const url = `${API_BASE_URL}/api/investigate?stream=true`;
      
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          cluster,
          namespace,
          scenario,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("ReadableStream is not supported by backend response.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        
        // Save the incomplete last line back to buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data: ")) continue;

          try {
            const rawJson = trimmed.slice(6);
            const parsed: ProgressEvent = JSON.parse(rawJson);
            
            if (parsed.type === "result") {
              onComplete(parsed.data);
            } else {
              onProgress(parsed);
            }
          } catch (e) {
            console.error("Failed to parse SSE stream chunk:", trimmed, e);
          }
        }
      }
    } catch (err: any) {
      console.error("Error reading investigation stream:", err);
      onError(err.message || "Failed to establish investigation stream connection.");
    }
  }
};
