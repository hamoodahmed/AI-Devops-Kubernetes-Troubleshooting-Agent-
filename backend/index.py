# backend/index.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Devops Kubernetes Agent API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "mistralai/mistral-7b-instruct:free"

class ChatResponse(BaseModel):
    response: str
    model: str

# Health Check Endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "Backend is running"}

# Chat Endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            logger.error("OPENROUTER_API_KEY not configured")
            raise HTTPException(status_code=500, detail="API key not configured")

        # Prepare messages for OpenRouter
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Call OpenRouter API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv("VERCEL_URL", "http://localhost:3000"),
                    "X-Title": "AI Devops Agent"
                },
                json={
                    "model": request.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.text}")
                raise HTTPException(status_code=response.status_code, detail="OpenRouter API error")
            
            data = response.json()
            
            if data.get("choices") and len(data["choices"]) > 0:
                return ChatResponse(
                    response=data["choices"][0]["message"]["content"],
                    model=request.model
                )
            else:
                raise HTTPException(status_code=500, detail="No response from OpenRouter")
                
    except httpx.TimeoutException:
        logger.error("OpenRouter API timeout")
        raise HTTPException(status_code=504, detail="API timeout")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Devops Kubernetes Agent API", "status": "running"}

# Vercel serverless handler
async def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
