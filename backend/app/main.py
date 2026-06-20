import sys
import os
# Add parent directory of 'app' to sys.path to resolve module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger
from typing import List

from app.core.config import settings
from app.core.logging import setup_logging
from app.models.schemas import ClustersResponse, InvestigateRequest, InvestigateResponse, ClusterInfo
from app.services.investigator import InvestigationService

# Setup loguru logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend orchestration engine for AI Kubernetes Troubleshooting Agent."
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize investigation service
investigation_service = InvestigationService()

@app.get("/health")
def health_check():
    """
    Core health check endpoint.
    """
    logger.info("Health check triggered.")
    return {
        "status": "healthy",
        "service": "ai-kubernetes-agent"
    }

@app.get("/api/clusters", response_model=ClustersResponse)
def list_clusters():
    """
    Lists all available Kubernetes contexts from kubeconfig and mocks.
    """
    logger.info("Listing cluster contexts.")
    try:
        contexts = investigation_service.executor.get_available_contexts()
        return ClustersResponse(clusters=[ClusterInfo(**c) for c in contexts])
    except Exception as e:
        logger.error(f"Error fetching cluster contexts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/investigate")
async def investigate(
    request: InvestigateRequest,
    stream: bool = Query(True, description="Whether to stream the investigation progress in real-time")
):
    """
    Triggers a cluster investigation.
    Supports real-time streaming (SSE) and full synchronous JSON payload response.
    """
    logger.info(f"Triggering investigation for cluster '{request.cluster}' in namespace '{request.namespace}' (scenario: {request.scenario})")
    
    if stream:
        return StreamingResponse(
            investigation_service.run_investigation_stream(
                cluster=request.cluster,
                namespace=request.namespace,
                scenario=request.scenario
            ),
            media_type="text/event-stream"
        )
    
    # Non-streaming synchronous fallback
    try:
        full_data = None
        async for chunk in investigation_service.run_investigation_stream(
            cluster=request.cluster,
            namespace=request.namespace,
            scenario=request.scenario
        ):
            # Parse result line
            if chunk.startswith("data: "):
                data_str = chunk[6:].strip()
                if not data_str:
                    continue
                parsed = json.loads(data_str)
                if parsed.get("type") == "result":
                    full_data = parsed.get("data")
        
        if not full_data:
            raise HTTPException(status_code=500, detail="Investigation failed to produce a result.")
            
        return InvestigateResponse(**full_data)
    except Exception as e:
        logger.error(f"Sync investigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
