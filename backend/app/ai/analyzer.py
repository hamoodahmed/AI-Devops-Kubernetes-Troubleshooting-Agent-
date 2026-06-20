from typing import Dict, Any
from app.ai.prompt_builder import PromptBuilder
from app.ai.client import OpenRouterClient
from app.models.schemas import Diagnosis

class AIKubernetesAgent:
    def __init__(self):
        self.client = OpenRouterClient()

    async def diagnose(self, evidence: Dict[str, Any], scenario: str) -> Diagnosis:
        """
        Coordinates generating prompt and fetching diagnosis from OpenRouter.
        """
        prompt = PromptBuilder.build(evidence)
        return await self.client.get_diagnosis(prompt, scenario)
