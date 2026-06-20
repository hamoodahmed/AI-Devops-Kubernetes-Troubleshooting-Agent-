# backend/index.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Devops Backend")

# ✅ CORS - Allow frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-devops-frontend.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "mistralai/mistral-7b-instruct:free"

@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "Backend is running"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")

        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-devops-frontend.vercel.app",
                    "X-Title": "AI Devops Agent"
                },
                json={
                    "model": request.model,
                    "messages": messages,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="OpenRouter API error")
            
            data = response.json()
            return {
                "response": data["choices"][0]["message"]["content"],
                "model": request.model
            }
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Devops Backend API", "status": "running"}

# Vercel handler
async def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
