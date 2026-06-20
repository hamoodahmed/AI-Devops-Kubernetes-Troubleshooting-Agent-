from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class ClusterInfo(BaseModel):
    name: str
    is_active: bool
    is_simulated: bool = False
    server: Optional[str] = None

class ClustersResponse(BaseModel):
    clusters: List[ClusterInfo]

class InvestigateRequest(BaseModel):
    cluster: str = Field(..., description="Target cluster context name")
    namespace: str = Field("default", description="Kubernetes namespace to investigate")
    scenario: Optional[str] = Field(None, description="Force a specific simulation scenario (e.g., CrashLoopBackOff, ImagePullBackOff, OOMKilled, SelectorMismatch)")

class Diagnosis(BaseModel):
    root_cause: str = Field(..., description="Root cause of the failure")
    explanation: str = Field(..., description="Details and explanation of the failure")
    fix: str = Field(..., description="Step-by-step fix recommendation")
    kubectl_command: str = Field(..., description="Actionable kubectl command to fix or verify")
    prevention: str = Field(..., description="How to prevent this issue in the future")
    confidence: int = Field(..., description="Confidence score between 0 and 100")

class InvestigationEvidence(BaseModel):
    pods: Dict[str, Any] = Field(default_factory=dict)
    logs: Dict[str, Any] = Field(default_factory=dict)
    events: Dict[str, Any] = Field(default_factory=dict)
    deployments: Dict[str, Any] = Field(default_factory=dict)
    network: Dict[str, Any] = Field(default_factory=dict)

class InvestigateResponse(BaseModel):
    status: str
    cluster: str
    namespace: str
    is_simulated: bool
    evidence: InvestigationEvidence
    diagnosis: Optional[Diagnosis] = None
    error: Optional[str] = None
