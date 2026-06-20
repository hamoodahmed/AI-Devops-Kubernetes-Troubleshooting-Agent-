export interface ClusterInfo {
  name: string;
  is_active: boolean;
  is_simulated?: boolean;
  server?: string;
}

export interface PodInfo {
  name: string;
  namespace: string;
  ready: string;
  status: string;
  restarts: string;
  age: string;
}

export interface PodInspectorResult {
  healthy: boolean;
  problematic_pods: PodInfo[];
  error?: string;
  raw_output?: string;
}

export interface LogInfo {
  pod_name: string;
  namespace: string;
  success: boolean;
  error?: string;
  filtered_logs?: string[];
  total_lines_read?: number;
}

export interface EventsAnalyzerResult {
  success: boolean;
  warnings: string[];
  error?: string;
  raw_output?: string;
}

export interface DeploymentInfo {
  name: string;
  namespace: string;
  ready: string;
  up_to_date: string;
  available: string;
  age: string;
  details?: string;
}

export interface DeploymentInspectorResult {
  success: boolean;
  unhealthy_deployments: DeploymentInfo[];
  error?: string;
  raw_output?: string;
}

export interface NetworkIssue {
  service_name: string;
  namespace: string;
  issue: string;
  endpoints: string;
}

export interface NetworkInspectorResult {
  success: boolean;
  error?: string;
  services?: string;
  endpoints?: string;
  issues: NetworkIssue[];
}

export interface InvestigationEvidence {
  pods: PodInspectorResult;
  logs: Record<string, LogInfo>;
  events: EventsAnalyzerResult;
  deployments: DeploymentInspectorResult;
  network: NetworkInspectorResult;
}

export interface Diagnosis {
  root_cause: string;
  explanation: string;
  fix: string;
  kubectl_command: string;
  prevention: string;
  confidence: number;
}

export interface InvestigationResult {
  status: string;
  cluster: string;
  namespace: string;
  is_simulated: boolean;
  evidence: InvestigationEvidence;
  diagnosis: Diagnosis;
  error?: string;
}

// Progress Event interface for SSE stream
export interface ProgressEvent {
  type: "progress" | "result";
  step?: "pods" | "logs" | "events" | "deployments" | "network" | "ai";
  message?: string;
  status?: "running" | "completed" | "failed";
  data?: any;
}

// InsForge History item schema
export interface InvestigationHistoryItem {
  id: string;
  user_id?: string;
  timestamp: string;
  cluster: string;
  namespace: string;
  root_cause: string;
  confidence: number;
  status: string;
  diagnosis?: Diagnosis;
}
