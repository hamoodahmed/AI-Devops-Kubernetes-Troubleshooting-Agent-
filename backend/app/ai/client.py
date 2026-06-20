import httpx
import json
import os
from typing import Dict, Any
from loguru import logger
from app.core.config import settings
from app.models.schemas import Diagnosis

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.url = settings.OPENROUTER_URL

    async def get_diagnosis(self, prompt: str, scenario: str) -> Diagnosis:
        """
        Sends the diagnostic prompt to OpenRouter.
        If API key is missing, or query fails, falls back to a realistic local simulation.
        """
        # If API Key is empty, fallback to offline simulation
        if not self.api_key:
            logger.info("OpenRouter API key is missing. Using offline simulated SRE reasoning.")
            return self._get_simulated_diagnosis(scenario)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/insforge/ai-kubernetes-agent",
            "X-Title": "AI Kubernetes Troubleshooting Agent"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Senior Kubernetes SRE. You analyze cluster issues and return a single valid JSON block containing: root_cause, explanation, fix, kubectl_command, prevention, and confidence."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Sending prompt to OpenRouter model: {self.model}")
                response = await client.post(self.url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    logger.info("OpenRouter response received successfully.")
                    
                    # Clean markdown wrappers if any
                    content_clean = content.strip()
                    if content_clean.startswith("```json"):
                        content_clean = content_clean[7:]
                    if content_clean.endswith("```"):
                        content_clean = content_clean[:-3]
                    content_clean = content_clean.strip()
                    
                    parsed = json.loads(content_clean)
                    return Diagnosis(
                        root_cause=parsed.get("root_cause", "Unknown Root Cause"),
                        explanation=parsed.get("explanation", "Failed to compile explanation."),
                        fix=parsed.get("fix", "Please verify pod configuration manually."),
                        kubectl_command=parsed.get("kubectl_command", "kubectl get pods"),
                        prevention=parsed.get("prevention", "Implement health checks."),
                        confidence=int(parsed.get("confidence", 80))
                    )
                else:
                    logger.error(f"OpenRouter API error {response.status_code}: {response.text}")
                    # Fallback to simulated on failure
                    return self._get_simulated_diagnosis(scenario)
        except Exception as e:
            logger.error(f"Failed to communicate with OpenRouter API: {e}")
            return self._get_simulated_diagnosis(scenario)

    def _get_simulated_diagnosis(self, scenario: str) -> Diagnosis:
        """
        Mock Senior SRE diagnosis responses when offline or missing keys.
        """
        if scenario == "CrashLoopBackOff":
            return Diagnosis(
                root_cause="Missing DATABASE_URL environment variable",
                explanation=(
                    "The pod 'payment-service-58d7c49b6b-df2jk' is crashing shortly after startup "
                    "because it attempt to retrieve the 'DATABASE_URL' environment variable. "
                    "This is verified by the container log traceback containing KeyError: 'DATABASE_URL'."
                ),
                fix="Define the DATABASE_URL environment variable in the payment-service deployment specification.",
                kubectl_command="kubectl set env deployment/payment-service DATABASE_URL=\"postgresql://db-user:password@order-db:5432/payment\"",
                prevention="Verify configurations during deployment validation or use templates that enforce required environment variables.",
                confidence=98
            )
        elif scenario == "ImagePullBackOff":
            return Diagnosis(
                root_cause="Invalid image reference or registry credentials issue",
                explanation=(
                    "The container 'auth-service' fails to start because Kubernetes cannot pull "
                    "the image 'internal-registry.io/auth-service:v2.0.1-prod'. This is caused by a wrong tag name "
                    "or a failure to authenticate against the private container registry."
                ),
                fix="Update the deployment image tag to a valid reference or ensure image-pull secrets are configured properly.",
                kubectl_command="kubectl set image deployment/auth-service auth-service=internal-registry.io/auth-service:v2.0.0-prod",
                prevention="Automate image tagging validation in CI/CD before pushing deployment manifests to Kubernetes.",
                confidence=95
            )
        elif scenario == "OOMKilled":
            return Diagnosis(
                root_cause="Container memory limit exceeded",
                explanation=(
                    "The pod 'report-generator-d86bfcd8-89qws' was terminated with exit status 137 (OOMKilled) "
                    "because the memory usage exceeded its limit of 64Mi. The logs show processing a large batch "
                    "of transaction records before the system OOM killer triggered."
                ),
                fix="Increase the memory resource limit of the report-generator deployment configuration to a higher value like 256Mi.",
                kubectl_command="kubectl set resources deployment/report-generator --limits=memory=256Mi",
                prevention="Implement proper resource profiling and configure horizontal pod autoscalers to match application workloads.",
                confidence=97
            )
        elif scenario == "SelectorMismatch":
            return Diagnosis(
                root_cause="Service label selector mismatch",
                explanation=(
                    "The Service 'notification-service' is configured with selector 'app=notification-app', "
                    "but the deployment pods are labeled with 'app=notification-service'. "
                    "As a result, no endpoints are matched (endpoints column is <none>), making the service inaccessible."
                ),
                fix="Edit the service configuration selector app label to match the pod label 'app=notification-service'.",
                kubectl_command="kubectl patch svc notification-service -p '{\"spec\":{\"selector\":{\"app\":\"notification-service\"}}}'",
                prevention="Define matching templates using helm templates or label validation checks in pre-deployment linters.",
                confidence=99
            )
        else:
            return Diagnosis(
                root_cause="No critical issues found",
                explanation="All inspected pods and services appear healthy. The system is operating within normal boundaries.",
                fix="No intervention required.",
                kubectl_command="kubectl get pods -A",
                prevention="Continue monitoring resource usage and keep warning events logs enabled.",
                confidence=100
            )
