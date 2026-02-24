"""
Haystack Backend Server
AI SDK: Haystack
Tech Stack: FastAPI + Python
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional

app = FastAPI(
    title="Haystack API",
    version="1.0.0",
    description="Haystack AI SDK backend service"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "haystack-api",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Haystack API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "api": "/api"
        }
    }

# AI endpoint (placeholder for now)
class AIRequest(BaseModel):
    prompt: str
    parameters: Optional[dict] = None

@app.post("/api/ai")
async def ai_endpoint(request: AIRequest):
    """AI endpoint - placeholder implementation"""
    return {
        "response": f"Mock AI response for: {request.prompt}",
        "status": "success",
        "framework": "Haystack"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
