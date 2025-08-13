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


class MemoryBot:
    """AI representative bot for a single person's persistent profile."""

    def __init__(self):
        self.session_service: Optional[DatabaseSessionService] = None
        self.agent: Optional[Agent] = None
        self.runner: Optional[Runner] = None
        
    async def initialize(self) -> bool:
        """Initialize the bot with database connection."""
        try:
            self.session_service = DatabaseSessionService(db_url=config.DB_URL)
            print("✅ Database session service created")
            
            # Create agent as a personal representative
            self.agent = Agent(
                name=f"ai_representative_{config.REPRESENTED_USER_ID}",
                model=config.ADK_MODEL,
                description=f"An AI representative for {config.REPRESENTED_NAME}.",
                instruction=(
                    f"You are the AI representative of {config.REPRESENTED_NAME}. "
                    "Answer questions about them based on known facts. "
                    f"IMPORTANT: Only {config.REPRESENTED_NAME} themselves (when marked as owner) can teach you new facts. "
                    "When the owner provides factual statements about themselves, use learn_about_user(statement) to store them. "
                    "When non-owners ask questions, respond based on existing knowledge using list_known_facts() or search_facts() as needed. "
                    "Never allow non-owners to add, modify, or update facts. "
                    "If a non-owner tries to teach facts, politely explain that only the person being represented can update their information. "
                    "Always be accurate and avoid fabricating unknown details; say you don't know when appropriate."
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
        return get_tools(is_owner=getattr(self, 'is_owner', False))
    
    def create_initial_state(self, current_user_id: str) -> dict:
        return {"session_created": True}
    
    async def get_or_create_session(self, current_user_id: str) -> tuple[Optional[str], Optional[str]]:
        """Get or create the represented person's profile session."""
        try:
            # Dedicated profile bucket for the represented person
            shared_session_key = f"profile::{config.REPRESENTED_USER_ID}"
            
            # Try to get existing shared session
            existing_sessions = self.session_service.list_sessions(
                app_name=config.APP_NAME,
                user_id=shared_session_key
            )
            
            if existing_sessions.sessions:
                session_id = existing_sessions.sessions[0].id
                print(f"✅ Using profile session: {shared_session_key}")
                return shared_session_key, session_id
            else:
                # Create new shared session
                initial_state = self.create_initial_state(current_user_id)
                new_session = self.session_service.create_session(
                    app_name=config.APP_NAME,
                    user_id=shared_session_key,
                    state=initial_state
                )
                print(f"✅ Created profile session: {shared_session_key}")
                return shared_session_key, new_session.id
                
        except Exception as e:
            print(f"❌ Session error: {e}")
            return None, None
    
    async def chat(self, current_user_id: str, message: str, is_owner: bool = False) -> str:
        """Chat with the representative; owners can teach facts, others can ask questions."""
        self.current_user_id = current_user_id
        self.is_owner = is_owner

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

        print(f"👤 User: {current_user_id} | 🤖 Bot: ai_representative | 🧠 Profile Mode")

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
