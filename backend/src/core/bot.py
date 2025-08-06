"""
Core bot implementation with authentication-based learning control.
"""

import asyncio
from typing import Optional
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from .config import config
from ..tools.learning_tools import learn_about_user_wrapper
from ..tools.retrieval_tools import get_user_info_wrapper, list_known_facts_wrapper


class UserAuthenticatedBot:
    """Multi-user AI bot with authentication-based learning mode."""
    
    def __init__(self, bot_owner_id: str):
        self.bot_owner_id = bot_owner_id
        self.session_service: Optional[DatabaseSessionService] = None
        self.agent: Optional[Agent] = None
        self.runner: Optional[Runner] = None
        self.current_user_id: Optional[str] = None
        
    async def initialize(self) -> bool:
        """Initialize the bot with database connection."""
        try:
            self.session_service = DatabaseSessionService(db_url=config.DB_URL)
            print("✅ Database session service created")
            
            # Create agent with dynamic owner name
            self.agent = Agent(
                name=f"{self.bot_owner_id}_bot",
                model=config.ADK_MODEL,
                description=f"Digital representative of {self.bot_owner_id} with persistent memory.",
                instruction=f"""
                You are {self.bot_owner_id}-Bot, a digital representative of {self.bot_owner_id} with persistent memory.
                
                IMPORTANT: Only learn new facts when talking to {self.bot_owner_id} directly (is_owner=True).
                When talking to others (is_owner=False), share what you know but don't learn new information.
                
                Available tools:
                - learn_about_user(key, value): Store facts about {self.bot_owner_id} (only when is_owner=True)
                - get_user_info(key): Retrieve specific facts about {self.bot_owner_id}
                - list_known_facts(): Show all known facts about {self.bot_owner_id}
                
                When is_owner=True: You're talking to the real {self.bot_owner_id} - learn and store facts
                When is_owner=False: You're {self.bot_owner_id}'s representative talking to others - share knowledge but don't learn
                
                Be natural, friendly, and conversational. Represent {self.bot_owner_id} well!
                """,
                tools=[]  # Tools will be set dynamically per conversation
            )
            
            self.runner = Runner(
                agent=self.agent,
                app_name=config.APP_NAME,
                session_service=self.session_service
            )
            
            return True
        except Exception as e:
            print(f"❌ Error initializing bot: {e}")
            return False
    
    def _get_tools_for_user(self, current_user_id: str):
        """Get tools configured for the current user."""
        return [
            learn_about_user_wrapper(self.bot_owner_id, current_user_id),
            get_user_info_wrapper(self.bot_owner_id, current_user_id),
            list_known_facts_wrapper(self.bot_owner_id, current_user_id)
        ]
    
    def create_initial_state(self, current_user_id: str) -> dict:
        """Create initial session state with user authentication info."""
        is_owner = (current_user_id == self.bot_owner_id)
        
        return {
            "is_owner": is_owner,
            "current_user": current_user_id,
            "bot_owner_id": self.bot_owner_id,
            "session_created": True
        }
    
    async def get_or_create_session(self, current_user_id: str) -> tuple[Optional[str], Optional[str]]:
        """Get existing session or create new one for the current user."""
        try:
            # All users share the same bot session for shared knowledge
            # But we track who's currently talking
            shared_session_key = f"{self.bot_owner_id}_bot_shared_knowledge"
            
            # Try to get existing shared session
            existing_sessions = self.session_service.list_sessions(
                app_name=config.APP_NAME,
                user_id=shared_session_key
            )
            
            if existing_sessions.sessions:
                session_id = existing_sessions.sessions[0].id
                print(f"✅ Using shared session: {shared_session_key}")
                return shared_session_key, session_id
            else:
                # Create new shared session
                initial_state = self.create_initial_state(self.bot_owner_id)  # Initialize as owner
                new_session = self.session_service.create_session(
                    app_name=config.APP_NAME,
                    user_id=shared_session_key,
                    state=initial_state
                )
                print(f"✅ Created shared session: {shared_session_key}")
                return shared_session_key, new_session.id
                
        except Exception as e:
            print(f"❌ Session error: {e}")
            return None, None
    
    async def chat(self, current_user_id: str, message: str) -> str:
        """Handle a chat message from a user."""
        # Set current user for this conversation
        self.current_user_id = current_user_id
        
        # Update agent tools for current user context
        if self.agent:
            self.agent.tools = self._get_tools_for_user(current_user_id)
        
        user_key, session_id = await self.get_or_create_session(current_user_id)
        if not user_key or not session_id:
            return "Error: Could not create or access session"
        
        # Determine if this is the owner or someone else
        is_owner = (current_user_id == self.bot_owner_id)
        mode = "Learning Mode" if is_owner else "Representative Mode"
        
        print(f"👤 User: {current_user_id} | 🤖 Bot: {self.bot_owner_id}-Bot | 🔄 {mode}")
        
        content = types.Content(role="user", parts=[types.Part(text=message)])
        
        try:
            async for event in self.runner.run_async(
                user_id=user_key,
                session_id=session_id,
                new_message=content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        text_parts = []
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        
                        if text_parts:
                            response_text = ' '.join(text_parts)
                            return response_text
                        else:
                            return "[Processing...]"
                            
        except Exception as e:
            return f"Error: {e}"
