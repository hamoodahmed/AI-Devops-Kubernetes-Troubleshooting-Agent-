import json
from typing import Dict, Any

class PromptBuilder:
    @staticmethod
    def build(evidence: Dict[str, Any]) -> str:
        """
        Builds a structured prompt containing Kubernetes troubleshooting evidence.
        """
        # Extract evidence fields
        pods_info = evidence.get("pods", {})
        logs_info = evidence.get("logs", {})
        events_info = evidence.get("events", {})
        deployments_info = evidence.get("deployments", {})
        network_info = evidence.get("network", {})

        prompt = (
            "You are a Senior Kubernetes Site Reliability Engineer (SRE) helping troubleshoot cluster incidents.\n"
            "Analyze the Kubernetes diagnostics data provided below and diagnose the exact root cause, explanation, fix, action command, prevention steps, and a confidence score.\n\n"
            "### DIALOGUE RESTRICTIONS:\n"
            "- You MUST output ONLY valid JSON in your response.\n"
            "- DO NOT write any conversational introduction, codeblock indicators, or explanations outside the JSON block.\n"
            "- Keep your recommendations precise, actionable, and Kubernetes-specific. Avoid generic advice.\n\n"
            "### JSON OUTPUT FORMAT:\n"
            "{\n"
            "  \"root_cause\": \"A brief summary of the primary root cause\",\n"
            "  \"explanation\": \"A comprehensive explanation of what failed, how it occurred, and how it correlates to the logs and events\",\n"
            "  \"fix\": \"Step-by-step instructions to fix the issue (beginner-friendly)\",\n"
            "  \"kubectl_command\": \"The exact kubectl command that can be run to apply the fix or edit the configuration\",\n"
            "  \"prevention\": \"Specific recommendation on how to prevent this issue from recurring\",\n"
            "  \"confidence\": 92\n"
            "}\n\n"
            "### KUBERNETES DIAGNOSTICS EVIDENCE:\n\n"
        )

        # 1. Pod Status
        prompt += "#### 1. Pod status:\n"
        if pods_info.get("problematic_pods"):
            prompt += f"Problematic Pods detected: {json.dumps(pods_info['problematic_pods'], indent=2)}\n"
        else:
            prompt += "No explicitly problematic pods detected via status check. All running pods seem healthy.\n"
        prompt += f"Raw Pod list output:\n{pods_info.get('raw_output', 'No pods found')}\n\n"

        # 2. Logs
        prompt += "#### 2. Pod Logs (Tail/Filtered):\n"
        if logs_info:
            for pod_name, log_data in logs_info.items():
                prompt += f"Pod: {pod_name} (Namespace: {log_data.get('namespace')})\n"
                if log_data.get("success"):
                    log_lines = "\n".join(log_data.get("filtered_logs", []))
                    prompt += f"Logs:\n{log_lines}\n"
                else:
                    prompt += f"Log collection failure: {log_data.get('error')}\n"
                prompt += "-" * 40 + "\n"
        else:
            prompt += "No logs gathered.\n\n"

        # 3. Events
        prompt += "\n#### 3. Warning Events:\n"
        warnings = events_info.get("warnings", [])
        if warnings:
            prompt += "\n".join(warnings) + "\n\n"
        else:
            prompt += "No warning events gathered.\n\n"

        # 4. Deployments
        prompt += "#### 4. Deployment Status:\n"
        unhealthy_deps = deployments_info.get("unhealthy_deployments", [])
        if unhealthy_deps:
            for dep in unhealthy_deps:
                prompt += f"Deployment: {dep['name']} | Ready: {dep['ready']} | Available: {dep['available']}\n"
                prompt += f"Deployment details/conditions:\n{dep.get('details', '')}\n"
                prompt += "-" * 40 + "\n"
        else:
            prompt += "All deployments match desired replica counts.\n\n"

        # 5. Network (Services & Endpoints)
        prompt += "#### 5. Network and Endpoints Status:\n"
        network_issues = network_info.get("issues", [])
        if network_issues:
            prompt += "Network Issues Detected:\n"
            for issue in network_issues:
                prompt += f"Service: {issue['service_name']} | Issue: {issue['issue']} | Endpoints: {issue['endpoints']}\n"
        else:
            prompt += "No service endpoint or selection mismatch issues detected.\n"
        prompt += f"Raw Services output:\n{network_info.get('services', '')}\n"
        prompt += f"Raw Endpoints output:\n{network_info.get('endpoints', '')}\n\n"

        prompt += "Analyze these details carefully and return the diagnosis JSON output structure."
        return prompt
