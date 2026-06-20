import { useState, useCallback } from "react";
import { ProgressEvent, InvestigationResult } from "../types";
import { api } from "../services/api";
import { insforgeDb } from "../services/insforge";

export interface ProgressStep {
  id: "pods" | "logs" | "events" | "deployments" | "network" | "ai";
  label: string;
  status: "idle" | "running" | "completed" | "failed";
  message: string;
}

const INITIAL_STEPS: ProgressStep[] = [
  { id: "pods", label: "Checking Pods", status: "idle", message: "Waiting to start..." },
  { id: "logs", label: "Reading Logs", status: "idle", message: "Waiting to start..." },
  { id: "events", label: "Analyzing Events", status: "idle", message: "Waiting to start..." },
  { id: "deployments", label: "Inspecting Deployments", status: "idle", message: "Waiting to start..." },
  { id: "network", label: "Checking Networking", status: "idle", message: "Waiting to start..." },
  { id: "ai", label: "AI Reasoning", status: "idle", message: "Waiting to start..." },
];

export function useInvestigation() {
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState<ProgressStep[]>(INITIAL_STEPS);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setLoading(false);
    setSteps(INITIAL_STEPS);
    setResult(null);
    setError(null);
  }, []);

  const run = useCallback(async (cluster: string, namespace: string, scenario: string | null) => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    // Reset steps to idle/running status
    setSteps(INITIAL_STEPS.map(s => s.id === "pods" ? { ...s, status: "running", message: "In progress..." } : s));

    await api.startInvestigation(
      cluster,
      namespace,
      scenario,
      (progressEvent: ProgressEvent) => {
        const { step, message, status, data } = progressEvent;
        if (!step) return;

        setSteps((currentSteps) =>
          currentSteps.map((s) => {
            if (s.id === step) {
              return {
                ...s,
                status: status || "running",
                message: message || s.message,
              };
            }
            // If this step completed, start the next one
            if (step === "pods" && s.id === "logs" && status === "completed") return { ...s, status: "running", message: "Starting log collector..." };
            if (step === "logs" && s.id === "events" && status === "completed") return { ...s, status: "running", message: "Analyzing warn events..." };
            if (step === "events" && s.id === "deployments" && status === "completed") return { ...s, status: "running", message: "Verifying deployment replicas..." };
            if (step === "deployments" && s.id === "network" && status === "completed") return { ...s, status: "running", message: "Checking network endpoints..." };
            if (step === "network" && s.id === "ai" && status === "completed") return { ...s, status: "running", message: "Spinning up Senior SRE model..." };
            return s;
          })
        );
      },
      async (investigationResult: InvestigationResult) => {
        setResult(investigationResult);
        setLoading(false);

        // Mark all steps as complete
        setSteps((currentSteps) =>
          currentSteps.map((s) => ({
            ...s,
            status: "completed",
            message: s.id === "ai" ? "Analysis complete." : "Checked successfully."
          }))
        );

        // Write the outcome of this investigation to InsForge Database History
        try {
          await insforgeDb.saveInvestigation({
            cluster: investigationResult.cluster,
            namespace: investigationResult.namespace,
            root_cause: investigationResult.diagnosis.root_cause,
            confidence: investigationResult.diagnosis.confidence,
            status: "completed",
            diagnosis: investigationResult.diagnosis
          });
        } catch (dbErr) {
          console.error("Failed to save investigation result to history:", dbErr);
        }
      },
      (errMessage: string) => {
        setError(errMessage);
        setLoading(false);
        setSteps((currentSteps) =>
          currentSteps.map((s) => 
            s.status === "running" 
              ? { ...s, status: "failed", message: errMessage } 
              : s
          )
        );
      }
    );
  }, []);

  return {
    loading,
    steps,
    result,
    error,
    run,
    reset,
  };
}
