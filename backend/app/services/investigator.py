import json
import asyncio
import os
from typing import AsyncGenerator, Dict, Any, Optional
from loguru import logger

from app.kubernetes.executor import KubectlExecutor
from app.kubernetes.pod_inspector import PodInspector
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.network_inspector import NetworkInspector
from app.ai.analyzer import AIKubernetesAgent

class InvestigationService:
    def __init__(self):
        self.executor = KubectlExecutor()
        self.pod_inspector = PodInspector(self.executor)
        self.logs_collector = LogsCollector(self.executor)
        self.events_analyzer = EventsAnalyzer(self.executor)
        self.deployment_inspector = DeploymentInspector(self.executor)
        self.network_inspector = NetworkInspector(self.executor)
        self.ai_agent = AIKubernetesAgent()

    async def run_investigation_stream(
        self, cluster: str, namespace: str, scenario: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Runs the investigation components sequentially and yields realtime progress updates as SSE strings.
        """
        # Set active scenario for simulation (in thread/process env)
        if scenario:
            os.environ["ACTIVE_SIMULATION_SCENARIO"] = scenario
        else:
            # default simulation scenario if none provided
            os.environ["ACTIVE_SIMULATION_SCENARIO"] = "CrashLoopBackOff"

        evidence = {}
        
        # Step 1: Checking Pods
        yield self._event("progress", "pods", "Checking Pods status...", "running")
        await asyncio.sleep(0.8) # simulate short delay for visual realism
        pods_result = self.pod_inspector.inspect(cluster, namespace)
        evidence["pods"] = pods_result
        yield self._event("progress", "pods", "Pods status checked.", "completed", pods_result)

        # Step 2: Reading Logs
        yield self._event("progress", "logs", "Reading Logs for unhealthy containers...", "running")
        await asyncio.sleep(0.8)
        problematic_pods = pods_result.get("problematic_pods", [])
        logs_result = self.logs_collector.collect(cluster, problematic_pods)
        evidence["logs"] = logs_result
        yield self._event("progress", "logs", f"Logs collected for {len(problematic_pods)} pods.", "completed", logs_result)

        # Step 3: Analyzing Events
        yield self._event("progress", "events", "Analyzing Cluster Events...", "running")
        await asyncio.sleep(0.8)
        events_result = self.events_analyzer.analyze(cluster, namespace)
        evidence["events"] = events_result
        yield self._event("progress", "events", "Cluster events analyzed.", "completed", events_result)

        # Step 4: Inspecting Deployments
        yield self._event("progress", "deployments", "Inspecting Deployment replicas & conditions...", "running")
        await asyncio.sleep(0.8)
        deployments_result = self.deployment_inspector.inspect(cluster, namespace)
        evidence["deployments"] = deployments_result
        yield self._event("progress", "deployments", "Deployments checked.", "completed", deployments_result)

        # Step 5: Checking Networking
        yield self._event("progress", "network", "Checking Service endpoint selectors...", "running")
        await asyncio.sleep(0.8)
        network_result = self.network_inspector.inspect(cluster, namespace)
        evidence["network"] = network_result
        yield self._event("progress", "network", "Networking and endpoints verified.", "completed", network_result)

        # Step 6: AI Reasoning
        yield self._event("progress", "ai", "AI SRE Engine running root cause analysis...", "running")
        await asyncio.sleep(1.0)
        
        try:
            diagnosis_res = await self.ai_agent.diagnose(evidence, os.getenv("ACTIVE_SIMULATION_SCENARIO", "CrashLoopBackOff"))
            diagnosis = diagnosis_res.model_dump()
            yield self._event("progress", "ai", "AI SRE diagnostics complete.", "completed", diagnosis)
        except Exception as e:
            logger.error(f"Error during AI reasoning: {e}")
            diagnosis = {
                "root_cause": "AI reasoning analysis failure",
                "explanation": f"AI model invocation failed: {str(e)}",
                "fix": "Manually inspect logs and events listed in evidence.",
                "kubectl_command": "kubectl get pods",
                "prevention": "Ensure OpenRouter API key and model config are correct.",
                "confidence": 0
            }
            yield self._event("progress", "ai", f"AI SRE diagnostics failed: {e}", "failed", diagnosis)

        # Step 7: Done - return final investigation payload
        payload = {
            "status": "success",
            "cluster": cluster,
            "namespace": namespace,
            "is_simulated": cluster.startswith("simulation-") or not self.executor.has_kubectl,
            "evidence": evidence,
            "diagnosis": diagnosis
        }
        
        yield f"data: {json.dumps({'type': 'result', 'data': payload})}\n\n"

    def _event(self, type_: str, step: str, message: str, status: str, data: Optional[Any] = None) -> str:
        return f"data: {json.dumps({'type': type_, 'step': step, 'message': message, 'status': status, 'data': data})}\n\n"
