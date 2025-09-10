"""
Core AI system service for the AI Representative System.
Contains the main AIRepresentativeSystem class with all business logic.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import Client, types as genai_types

from config import get_settings
from models import UserProfile, ExtractedInfo
from .tools import create_learning_tool, create_smart_retrieval_tool, create_representation_tool


class AIRepresentativeSystem:
    """
    Intelligent conversational AI system that learns from users and can represent them.
    Uses PostgreSQL for persistent conversation memory and ADK's session framework.
    """
    
    def __init__(self):
        # Get configuration from our new settings system
        self.settings = get_settings()
        self.db_url = self.settings.db_url
        self.google_api_key = self.settings.google_api_key
        self.app_name = self.settings.app_name
        self.model_name = self.settings.model_name
        
        self.session_service: Optional[DatabaseSessionService] = None
        self.client: Optional[Client] = None
    
    async def initialize(self) -> bool:
        """Initialize the AI system with database and agent."""
        try:
            # Initialize database session service for persistent memory
            self.session_service = DatabaseSessionService(db_url=self.db_url)
            print("✅ Database session service initialized")
            
            # Initialize Gemini client for knowledge extraction
            self.client = Client()
            
            print(f"🔧 Tools will be created dynamically per user:")
            print(f"   - Learning Tool (for owners)")
            print(f"   - Smart Retrieval Tool (for everyone)")
            print(f"   - Representation Tool (for everyone)")
            
            print("✅ AI Representative System initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing AI system: {e}")
            return False
    
    def _get_system_instruction(self, target_user_id: str, read_only: bool = False) -> str:
        """Get the system instruction for the AI agent."""
        
        if read_only:
            return f"""
        You are an intelligent AI representative that represents {target_user_id} to others.
        Your goal is to answer questions and provide information about {target_user_id}, based on what they have taught you.

        IMPORTANT: You CANNOT learn new information. Your knowledge is strictly read-only.
        
        CRITICAL RULES:
        - If a user tries to tell you new information about {target_user_id}, you MUST politely refuse.
        - Example refusal: "Thank you for sharing, but I can only learn new information from {target_user_id} directly." or "My knowledge about {target_user_id} is read-only and cannot be updated by others."
        - Do not pretend to record or learn new information.
        - You MUST use your tools (`smart_answer_about_user` and `represent_user`) to answer questions.
        - Do not ask for new information.
        - Answer only based on the information you have been provided by {target_user_id}.
        """

        return f"""
        You are an intelligent AI representative that learns about {target_user_id} and can represent {target_user_id} to others.
        
        IMPORTANT: You MUST use the available tools for learning and retrieval. Do not just respond conversationally.
        
        Your capabilities and WHEN to use tools:
        
        1. LEARN: When {target_user_id} shares ANY information about themselves, you MUST use the extract_and_learn tool.
           - This tool applies to {target_user_id} (the user you are currently interacting with).
        
        2. SMART RETRIEVAL: When asked questions about {target_user_id}, you MUST use the `smart_answer_about_user` tool:
           - You must provide the `target_user_id` for whom the question is about.
           - Example: If the user asks "What does {target_user_id} like?", you must call the tool with `target_user_id='{target_user_id}'`.
           - ALWAYS call `smart_answer_about_user` when asked about {target_user_id}'s information.
        
        3. REPRESENT: When asked to represent {target_user_id}, use the `represent_user` tool:
           - You must provide the `target_user_id` of the user to represent.
           - Example: If the user says "Represent {target_user_id}", call the tool with `target_user_id='{target_user_id}'`.
           - ALWAYS call `represent_user` when asked to speak as {target_user_id}.
        
        4. REMEMBER: Use persistent conversation memory to:
           - Build comprehensive user profiles over time for {target_user_id}
           - Reference past conversations and learned facts about {target_user_id}
           - Continuously update and refine {target_user_id}'s user model
        
        CRITICAL RULES:
        - NEVER respond without using tools when {target_user_id} shares information about themselves
        - ALWAYS use extract_and_learn for personal information from {target_user_id}
        - ALWAYS use smart_answer_about_user for questions about {target_user_id}
        - Tools are mandatory, not optional
        
        Always be helpful, accurate, and respectful when learning about and representing {target_user_id}.
        """
    
    def _create_read_write_agent(self, target_user_id: str) -> Agent:
        """Create a read-write agent for the target user."""
        smart_retrieval_tool = create_smart_retrieval_tool(self.client, self.model_name)
        representation_tool = create_representation_tool(self.client, self.model_name)
        learning_tool = create_learning_tool(self.client, self.model_name)
        
        return Agent(
            name=f"ai_representative_read_write_{target_user_id}",
            model=self.model_name,
            description=f"An intelligent AI that learns about {target_user_id} and can represent {target_user_id}.",
            instruction=self._get_system_instruction(target_user_id, read_only=False),
            tools=[learning_tool, smart_retrieval_tool, representation_tool],
        )
    
    def _create_read_only_agent(self, target_user_id: str) -> Agent:
        """Create a read-only agent for the target user."""
        smart_retrieval_tool = create_smart_retrieval_tool(self.client, self.model_name)
        representation_tool = create_representation_tool(self.client, self.model_name)
        
        return Agent(
            name=f"ai_representative_read_only_{target_user_id}",
            model=self.model_name,
            description=f"An intelligent AI that represents {target_user_id} to others.",
            instruction=self._get_system_instruction(target_user_id, read_only=True),
            tools=[smart_retrieval_tool, representation_tool],
        )
    
    async def get_or_create_session(self, user_id: str) -> tuple[Optional[str], Optional[str]]:
        """Get or create a session for the user with persistent memory."""
        try:
            # Try to get existing session for persistent memory
            existing_sessions = self.session_service.list_sessions(
                app_name=self.app_name,
                user_id=user_id
            )
            
            if existing_sessions.sessions:
                session_id = existing_sessions.sessions[0].id
                print(f"✅ Using existing session with persistent memory")
                return user_id, session_id
            else:
                # Create new session with initial user profile
                # Use the refactored UserProfile.create_empty method
                empty_profile = UserProfile.create_empty(user_id)
                new_session = self.session_service.create_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    state={
                        "user_profile": empty_profile.to_dict()
                    }
                )
                print(f"✅ Created new session with fresh user profile")
                return user_id, new_session.id
                
        except Exception as e:
            print(f"❌ Session error: {e}")
            return None, None
    
    async def chat(self, message: str, current_user_id: str, target_user_id: str) -> str:
        """
        Process a message with automated learning and representation capabilities.
        
        Args:
            message: User's message.
            current_user_id: The user who is sending the message.
            target_user_id: The user whose AI representative is being addressed.
        
        Returns:
            AI response incorporating learned information.
        """
        print(f"💬 [CHAT] User '{current_user_id}' is talking to '{target_user_id}'s AI.")
        print(f"   📝 Message: '{message[:100]}{'...' if len(message) > 100 else ''}'")
        
        # The session is always for the AI's owner (the target_user_id)
        user_key, session_id = await self.get_or_create_session(target_user_id)
        if not user_key or not session_id:
            return "Error: Could not create or access session for the AI's persistent memory."
        
        print(f"   📊 Using session '{session_id}' for user '{user_key}'")

        # Determine if the current user is the owner of the AI.
        is_owner = current_user_id == target_user_id
        
        # Add conversational context to the session state for the tools to use.
        # This is temporary and will not be persisted in the user's profile.
        session_state = self.session_service.get_session(
            app_name=self.app_name,
            user_id=target_user_id,
            session_id=session_id
        )
        if session_state:
            session_state.state["_temp_context"] = {
                "current_user_id": current_user_id,
                "target_user_id": target_user_id
            }

        # Create agents dynamically with the correct user context
        if is_owner:
            print("   🔒 Mode: Read-Write (Owner is talking to their own AI)")
            agent = self._create_read_write_agent(target_user_id)
            runner = Runner(
                agent=agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
        else:
            print("   👁️ Mode: Read-Only (Another user is talking to the AI)")
            agent = self._create_read_only_agent(target_user_id)
            runner = Runner(
                agent=agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
            
        content = genai_types.Content(
            role="user", 
            parts=[genai_types.Part(text=message)]
        )
        
        try:
            print(f"   🤖 Sending to ADK runner...")
            async for event in runner.run_async(
                user_id=user_key, # This is the target_user_id
                session_id=session_id,
                new_message=content,
            ):
                print(f"   📡 ADK Event: {type(event).__name__}")
                
                if event.is_final_response():
                    print(f"   ✅ Final response received")
                    if event.content and event.content.parts:
                        text_parts = []
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                text_parts.append(part.text)
                        
                        if text_parts:
                            response = " ".join(text_parts)
                            print(f"   💬 Response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
                            return response
                        else:
                            print(f"   ⚠️ No text parts in response")
                            return "I'm processing what you shared. Please continue our conversation."
            
            print(f"   ⚠️ No final response received")
            return "I'm learning from our conversation. Please tell me more about yourself."
            
        except Exception as e:
            print(f"   ❌ Error in chat processing: {e}")
            return f"Error: {e}"
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get the current learned profile for a user."""
        try:
            existing_sessions = self.session_service.list_sessions(
                app_name=self.app_name,
                user_id=user_id
            )
            
            if existing_sessions.sessions:
                session = existing_sessions.sessions[0]
                # Get session state to access user profile
                # Note: This would need to be implemented based on ADK session API
                profile_data = session.state.get("user_profile", {})
                
                # Use the refactored UserProfile.from_dict method
                profile_data["user_id"] = user_id
                return UserProfile.from_dict(profile_data)
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
        
        return None
