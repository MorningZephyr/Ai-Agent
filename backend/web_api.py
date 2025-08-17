"""
Simple FastAPI web interface for testing the ADK bot backend.
"""

import asyncio
import uuid
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import warnings

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from src.core.bot import ZhenBot
    from src.core.config import config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the backend directory")
    raise

# Suppress ADK framework warnings
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        config.validate()
        print("✅ Configuration validated successfully")
    except Exception as e:
        raise RuntimeError(f"Configuration error: {e}")
    
    yield
    
    # Shutdown (cleanup if needed)
    print("🔄 Server shutting down...")

app = FastAPI(title="Zhen's AI Representative API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active bot sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

class ChatMessage(BaseModel):
    message: str

class AuthRequest(BaseModel):
    user_id: str
    is_owner: bool = False

class ChatResponse(BaseModel):
    response: str
    session_id: str
    is_owner: bool



@app.post("/api/auth", response_model=dict)
async def authenticate_user(auth: AuthRequest):
    """Create or get a bot session for a user."""
    try:
        session_id = f"{auth.user_id}_{uuid.uuid4().hex[:8]}"
        print(f"Creating bot session: {session_id}")
        
        # Create new bot instance
        bot = ZhenBot()

        # Initialize the bot and verify success
        init_ok = await bot.initialize()
        if not init_ok:
            raise HTTPException(status_code=500, detail="Failed to initialize bot (DB/model configuration)")
        
        print("Bot created successfully.")
        
        # Store the session with user info
        active_sessions[session_id] = {
            "bot": bot,
            "user_id": auth.user_id,
            "is_owner": auth.is_owner
        }
        
        print(f"✅ Session stored: {session_id}")
        print(f"✅ Active sessions count: {len(active_sessions)}")
        print(f"✅ Session keys: {list(active_sessions.keys())}")
        
        owner_message = "as owner (can teach facts)" if auth.is_owner else "as visitor (can ask questions)"
        
        return {
            "session_id": session_id,
            "user_id": auth.user_id,
            "is_owner": auth.is_owner,
            "message": f"Connected {owner_message}"
        }
    
    except Exception as e:
        print(f"Error creating session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/api/chat/{session_id}", response_model=ChatResponse)
async def chat(session_id: str, chat_msg: ChatMessage):
    """Send a message to the bot and get a response."""
    try:
        print(f"Chat request for session: {session_id}")
        print(f"Active sessions: {list(active_sessions.keys())}")
        
        if session_id not in active_sessions:
            print(f"❌ Session {session_id} not found in active sessions")
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        bot = session["bot"]
        user_id = session["user_id"]
        is_owner = session["is_owner"]
        
        print(f"Processing message: {chat_msg.message}")
        print(f"User: {user_id}, Is owner: {is_owner}")
        
        # Get response from bot (simplified - no user_id or owner status needed)
        response = await bot.chat(chat_msg.message)
        # Ensure response is a string to satisfy ChatResponse schema
        if response is None or not isinstance(response, str) or response.strip() == "":
            response = "I couldn't generate a reply this time. Try rephrasing."
        
        print(f"Bot response (safe): {response!r}")
        
        return ChatResponse(
            response=str(response),
            session_id=session_id,
            is_owner=is_owner
        )
    
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/api/session/{session_id}/info")
async def get_session_info(session_id: str):
    """Get information about a session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return {
        "session_id": session_id,
        "current_user_id": session["user_id"],
        "is_owner": session["is_owner"]
    }

@app.delete("/api/session/{session_id}")
async def end_session(session_id: str):
    """End a bot session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del active_sessions[session_id]
    return {"message": "Session ended"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "active_sessions": len(active_sessions),
        "message": "AI Representative API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 