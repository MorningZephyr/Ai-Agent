"""
Simple bot that represents Zhen and learns about him.
"""

import asyncio
from typing import Optional
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from .config import config
from ..tools.learn_about_zhen import learn_about_zhen


class ZhenBot:
    """Simple AI representative bot for Zhen."""

    def __init__(self):
        self.session_service: Optional[DatabaseSessionService] = None
        self.agent: Optional[Agent] = None
        self.runner: Optional[Runner] = None
        
    async def initialize(self) -> bool:
        """Initialize the bot with database connection."""
        try:
            self.session_service = DatabaseSessionService(db_url=config.DB_URL)
            print("✅ Database session service created")
            
            # Create simple agent for Zhen
            self.agent = Agent(
                name="zhen_representative",
                model=config.ADK_MODEL,
                description="An AI representative for Zhen.",
                instruction=(
                    "You are Zhen's AI representative. "
                    "When Zhen tells you facts about himself, use learn_about_zhen to store them. "
                    "When asked about Zhen, share what you know from your stored facts. "
                    "Be helpful and conversational."
                ),
                tools=[learn_about_zhen],
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
    
    async def get_or_create_session(self) -> tuple[Optional[str], Optional[str]]:
        """Get or create Zhen's session."""
        try:
            user_key = "zhen"
            
            # Try to get existing session
            existing_sessions = self.session_service.list_sessions(
                app_name=config.APP_NAME,
                user_id=user_key
            )
            
            if existing_sessions.sessions:
                session_id = existing_sessions.sessions[0].id
                print(f"✅ Using existing session")
                return user_key, session_id
            else:
                # Create new session
                new_session = self.session_service.create_session(
                    app_name=config.APP_NAME,
                    user_id=user_key,
                    state={"facts": {}}
                )
                print(f"✅ Created new session")
                return user_key, new_session.id
                
        except Exception as e:
            print(f"❌ Session error: {e}")
            return None, None
    
    async def chat(self, message: str) -> str:
        """Simple chat with Zhen's representative."""
        user_key, session_id = await self.get_or_create_session()
        if not user_key or not session_id:
            return "Error: Could not create or access session"

        print(f"🤖 Zhen's AI Representative")

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

