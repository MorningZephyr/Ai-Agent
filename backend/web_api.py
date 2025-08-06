"""
Simple FastAPI web interface for testing the ADK bot backend.
"""

import asyncio
import uuid
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import warnings

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from src.core.bot import UserAuthenticatedBot
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the backend directory")
    raise

# Suppress ADK framework warnings
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")

app = FastAPI(title="Zhen Bot API", version="1.0.0")

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
    user_id: str = "user_001"  # Default user ID for testing

class AuthRequest(BaseModel):
    user_id: str
    bot_owner_id: str = "zhen"  # Default bot owner

class ChatResponse(BaseModel):
    response: str
    session_id: str
    is_owner: bool

@app.post("/api/auth", response_model=dict)
async def authenticate_user(auth: AuthRequest):
    """Create or get a bot session for a user."""
    try:
        session_id = f"{auth.user_id}_{auth.bot_owner_id}_{uuid.uuid4().hex[:8]}"
        
        print(f"Creating bot session: {session_id}")
        print(f"Bot owner: {auth.bot_owner_id}, User: {auth.user_id}")
        
        # Create new bot instance
        bot = UserAuthenticatedBot(bot_owner_id=auth.bot_owner_id)
        
        # Initialize the bot
        await bot.initialize()
        
        # Check if user is owner
        is_owner = (auth.user_id == auth.bot_owner_id)
        
        print(f"Bot created successfully. Is owner: {is_owner}")
        
        # Store the session with user info
        active_sessions[session_id] = {
            "bot": bot,
            "user_id": auth.user_id,
            "bot_owner_id": auth.bot_owner_id,
            "is_owner": is_owner
        }
        
        print(f"✅ Session stored: {session_id}")
        print(f"✅ Active sessions count: {len(active_sessions)}")
        print(f"✅ Session keys: {list(active_sessions.keys())}")
        
        return {
            "session_id": session_id,
            "user_id": auth.user_id,
            "bot_owner_id": auth.bot_owner_id,
            "is_owner": is_owner,
            "message": f"Connected as {'owner' if is_owner else 'visitor'}"
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
        
        print(f"Processing message: {chat_msg.message}")
        print(f"User: {user_id}, Is owner: {session['is_owner']}")
        
        # Get response from bot using user_id parameter
        response = await bot.chat(user_id, chat_msg.message)
        
        print(f"Bot response: {response}")
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            is_owner=session["is_owner"]
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
        "bot_owner_id": session["bot_owner_id"],
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
        "message": "Zhen Bot API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
