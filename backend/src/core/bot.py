"""
Simple bot that learns anything the user tells it.
"""

import asyncio
from typing import Optional
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from .config import config
from ..tools.tool_manager import get_tools


class UserAuthenticatedBot:
    """Minimal bot: no owner/guest logic, just persistent memory."""

    def __init__(self, bot_owner_id: str | None = None):
        # owner id retained only for backward compatibility; unused in logic
        self.bot_owner_id = bot_owner_id or "user"
        self.session_service: Optional[DatabaseSessionService] = None
        self.agent: Optional[Agent] = None
        self.runner: Optional[Runner] = None
        self.current_user_id: Optional[str] = None
        
    async def initialize(self) -> bool:
        """Initialize the bot with database connection."""
        try:
            self.session_service = DatabaseSessionService(db_url=config.DB_URL)
            print("✅ Database session service created")
            
            # Create agent with simple instruction
            self.agent = Agent(
                name=f"memory_bot",
                model=config.ADK_MODEL,
                description="A friendly assistant with persistent memory.",
                instruction=(
                    "You are a helpful assistant that remembers anything the user says. "
                    "Use the learn_about_user(statement) tool to store facts, and feel free to recall them in future replies."
                ),
                tools=[],  # set per message
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
    
    def _get_tools(self):
        return get_tools()
    
    def create_initial_state(self, current_user_id: str) -> dict:
        return {"session_created": True}
    
    async def get_or_create_session(self, current_user_id: str) -> tuple[Optional[str], Optional[str]]:
        """Get or create a shared memory session."""
        try:
            # Single shared memory bucket
            shared_session_key = "memory::shared"
            
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
                initial_state = self.create_initial_state(current_user_id)
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
        """Chat with the bot; it can learn anything you say."""
        self.current_user_id = current_user_id

        if self.agent:
            self.agent.tools = self._get_tools()

            self.runner = Runner(
                agent=self.agent,
                app_name=config.APP_NAME,
                session_service=self.session_service,
            )

        user_key, session_id = await self.get_or_create_session(current_user_id)
        if not user_key or not session_id:
            return "Error: Could not create or access session"

        print(f"👤 User: {current_user_id} | 🤖 Bot: memory_bot | 🔄 Learning Mode")

        content = types.Content(role="user", parts=[types.Part(text=message)])

        try:
            async for event in self.runner.run_async(
                user_id=user_key,
                session_id=session_id,
                new_message=content,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        text_parts = []
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                text_parts.append(part.text)

                        if text_parts:
                            response_text = " ".join(text_parts)
                            return response_text
                        else:
                            return "I couldn't generate a reply this time. Try rephrasing."
            return "I couldn't generate a reply this time. Try rephrasing."

        except Exception as e:
            return f"Error: {e}"
