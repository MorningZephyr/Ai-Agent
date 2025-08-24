"""
Web API for AI Representative System
Simple FastAPI interface for the intelligent conversational AI system.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import AIRepresentativeSystem

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    user_id: str
    learning_summary: Optional[Dict[str, Any]] = None

class ProfileResponse(BaseModel):
    user_id: str
    interests_count: int
    traits_count: int
    facts_count: int
    communication_style: str
    last_updated: str

# Global AI system instance
ai_system: Optional[AIRepresentativeSystem] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the AI system."""
    global ai_system
    
    # Startup
    print("🔄 Initializing AI Representative System...")
    ai_system = AIRepresentativeSystem()
    
    if not await ai_system.initialize():
        raise RuntimeError("Failed to initialize AI Representative System")
    
    print("✅ AI Representative System ready for web requests")
    yield
    
    # Shutdown
    print("🔄 Shutting down AI Representative System...")

# Create FastAPI app
app = FastAPI(
    title="AI Representative System API",
    description="Intelligent conversational AI with automated knowledge extraction and user representation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "name": "AI Representative System",
        "description": "Intelligent conversational AI with automated knowledge extraction and smart inference",
        "features": [
            "Automated knowledge extraction from conversations",
            "Smart data retrieval with intelligent inference",
            "Dynamic user interest modeling",
            "Persistent conversation memory with PostgreSQL",
            "Cross-user representation capabilities"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "ask": "/api/ask",
            "represent": "/api/represent", 
            "profile": "/api/profile/{user_id}",
            "health": "/api/health"
        },
        "example_inference": {
            "user_says": "I love playing piano",
            "someone_asks": "What's their favorite instrument?",
            "ai_infers": "Piano is likely their favorite instrument based on them loving to play it"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_msg: ChatMessage):
    """
    Chat with the AI system. Automatically extracts knowledge and learns about users.
    
    Args:
        chat_msg: Message containing text and user_id
    
    Returns:
        AI response with learning summary if applicable
    """
    try:
        if not ai_system:
            raise HTTPException(status_code=500, detail="AI system not initialized")
        
        # Process the message with automated learning
        response = await ai_system.chat(chat_msg.message, chat_msg.user_id)
        
        if not response or response.strip() == "":
            response = "I'm processing what you shared. Please continue our conversation."
        
        return ChatResponse(
            response=response,
            user_id=chat_msg.user_id,
            learning_summary={
                "message": "Continuously learning from our conversation",
                "persistent_memory": "Enabled via PostgreSQL + ADK sessions"
            }
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.get("/api/profile/{user_id}", response_model=ProfileResponse)
async def get_user_profile(user_id: str):
    """
    Get the learned profile for a specific user.
    
    Args:
        user_id: Unique identifier for the user
    
    Returns:
        User profile summary with learned information
    """
    try:
        if not ai_system:
            raise HTTPException(status_code=500, detail="AI system not initialized")
        
        profile = await ai_system.get_user_profile(user_id)
        
        if not profile:
            return ProfileResponse(
                user_id=user_id,
                interests_count=0,
                traits_count=0,
                facts_count=0,
                communication_style="Unknown",
                last_updated="Never"
            )
        
        return ProfileResponse(
            user_id=profile.user_id,
            interests_count=len(profile.interests),
            traits_count=len(profile.personality_traits),
            facts_count=len(profile.learned_facts),
            communication_style=profile.communication_style,
            last_updated=profile.last_updated
        )
        
    except Exception as e:
        print(f"Profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Profile retrieval error: {str(e)}")

class QuestionRequest(BaseModel):
    question: str
    target_user_id: str

class QuestionResponse(BaseModel):
    answer: str
    confidence: str
    inference_made: bool
    supporting_data: list
    reasoning: str

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_about_user(question_req: QuestionRequest):
    """
    Ask a question about a user. The AI will analyze stored data and make intelligent inferences.
    
    Example: "What's John's favorite instrument?" → AI finds "John plays piano" → infers piano is favorite
    
    Args:
        question_req: Question and target user ID
    
    Returns:
        Intelligent answer with confidence level and supporting data
    """
    try:
        if not ai_system:
            raise HTTPException(status_code=500, detail="AI system not initialized")
        
        # Use smart retrieval to answer the question with inference
        smart_query = f"Answer this question about {question_req.target_user_id}: {question_req.question}"
        response = await ai_system.chat(smart_query, question_req.target_user_id)
        
        # For now, return a structured response - in a full implementation, 
        # we'd parse the tool output for structured data
        return QuestionResponse(
            answer=response,
            confidence="medium",
            inference_made=True,
            supporting_data=["Based on stored user profile data"],
            reasoning="AI analyzed stored information and made reasonable inferences"
        )
        
    except Exception as e:
        print(f"Question answering error: {e}")
        raise HTTPException(status_code=500, detail=f"Question answering error: {str(e)}")

@app.post("/api/represent")
async def represent_user(
    target_user_id: str,
    context: str,
    representing_user_id: str = "system"
):
    """
    Have the AI represent a user to someone else based on learned profile.
    
    Args:
        target_user_id: User to represent
        context: Context or question for representation
        representing_user_id: Who is requesting the representation
    
    Returns:
        Response as the target user would respond
    """
    try:
        if not ai_system:
            raise HTTPException(status_code=500, detail="AI system not initialized")
        
        # This would use the representation tool - simplified for now
        representation_message = f"Please represent user {target_user_id} in this context: {context}"
        response = await ai_system.chat(representation_message, representing_user_id)
        
        return {
            "represented_user": target_user_id,
            "context": context,
            "representation": response,
            "note": "AI representation based on learned user profile with intelligent inference"
        }
        
    except Exception as e:
        print(f"Representation error: {e}")
        raise HTTPException(status_code=500, detail=f"Representation error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        system_status = "healthy" if ai_system else "not_initialized"
        
        return {
            "status": system_status,
            "message": "AI Representative System API",
            "features": {
                "automated_knowledge_extraction": True,
                "persistent_memory": True,
                "user_representation": True,
                "cross_user_modeling": True
            },
            "technology": {
                "ai_framework": "Google ADK",
                "model": "Gemini 2.0 Flash",
                "database": "PostgreSQL",
                "memory": "ADK Session Framework"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
