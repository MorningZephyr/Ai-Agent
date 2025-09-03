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
        self.read_write_agent: Optional[Agent] = None
        self.read_only_agent: Optional[Agent] = None
        self.read_write_runner: Optional[Runner] = None
        self.read_only_runner: Optional[Runner] = None
        self.client: Optional[Client] = None
    
    async def initialize(self) -> bool:
        """Initialize the AI system with database and agent."""
        try:
            # Initialize database session service for persistent memory
            self.session_service = DatabaseSessionService(db_url=self.db_url)
            print("✅ Database session service initialized")
            
            # Initialize Gemini client for knowledge extraction
            self.client = Client()
            
            # Create the AI agent with learning capabilities
            smart_retrieval_tool = self._create_smart_retrieval_tool()
            representation_tool = self._create_representation_tool()
            learning_tool = self._create_learning_tool()
            
            print(f"🔧 Created tools:")
            print(f"   - Learning Tool (for owners)")
            print(f"   - Smart Retrieval Tool (for everyone)")
            print(f"   - Representation Tool (for everyone)")
            
            # Agent for owners to train their AI (includes learning tool)
            self.read_write_agent = Agent(
                name="ai_representative_read_write",
                model=self.model_name,
                description="An intelligent AI that learns about users and can represent them.",
                instruction=self._get_system_instruction(),
                tools=[learning_tool, smart_retrieval_tool, representation_tool],
            )

            # Agent for others to talk to an AI (does NOT include learning tool)
            self.read_only_agent = Agent(
                name="ai_representative_read_only",
                model=self.model_name,
                description="An intelligent AI that represents a user to others.",
                instruction=self._get_system_instruction(read_only=True),
                tools=[smart_retrieval_tool, representation_tool],
            )
            
            # Initialize runner with session management
            self.read_write_runner = Runner(
                agent=self.read_write_agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
            self.read_only_runner = Runner(
                agent=self.read_only_agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
            
            print("✅ AI Representative System initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing AI system: {e}")
            return False
    
    def _get_system_instruction(self, read_only: bool = False) -> str:
        """Get the system instruction for the AI agent."""
        
        if read_only:
            return """
        You are an intelligent AI representative that represents a user to others.
        Your goal is to answer questions and provide information about the user you represent, based on what they have taught you.

        IMPORTANT: You CANNOT learn new information. Your knowledge is strictly read-only.
        
        CRITICAL RULES:
        - If a user tries to tell you new information about the person you represent, you MUST politely refuse.
        - Example refusal: "Thank you for sharing, but I can only learn new information from [User's Name] directly." or "My knowledge about [User's Name] is read-only and cannot be updated by others."
        - Do not pretend to record or learn new information.
        - You MUST use your tools (`smart_answer_about_user` and `represent_user`) to answer questions.
        - Do not ask for new information.
        - Answer only based on the information you have been provided by the user you represent.
        """

        return """
        You are an intelligent AI representative that learns about users and can represent them to others.
        
        IMPORTANT: You MUST use the available tools for learning and retrieval. Do not just respond conversationally.
        
        Your capabilities and WHEN to use tools:
        
        1. LEARN: When users share ANY information about themselves, you MUST use the extract_and_learn tool.
           - This tool applies to the user you are currently interacting with.
        
        2. SMART RETRIEVAL: When asked questions about a specific user, you MUST use the `smart_answer_about_user` tool:
           - You must provide the `target_user_id` for whom the question is about.
           - Example: If the user asks "What does Jane like?", you must call the tool with `target_user_id='Jane'`.
           - ALWAYS call `smart_answer_about_user` when asked about user information.
        
        3. REPRESENT: When asked to represent a user, use the `represent_user` tool:
           - You must provide the `target_user_id` of the user to represent.
           - Example: If the user says "Represent Jane", call the tool with `target_user_id='Jane'`.
           - ALWAYS call `represent_user` when asked to speak as a specific user.
        
        4. REMEMBER: Use persistent conversation memory to:
           - Build comprehensive user profiles over time
           - Reference past conversations and learned facts
           - Continuously update and refine user models
        
        CRITICAL RULES:
        - NEVER respond without using tools when users share information about themselves
        - ALWAYS use extract_and_learn for personal information
        - ALWAYS use smart_answer_about_user for questions about users
        - Tools are mandatory, not optional
        
        Always be helpful, accurate, and respectful when learning about and representing users.
        """
    
    def _create_learning_tool(self):
        """Create the automated knowledge extraction tool."""
        
        async def extract_and_learn(user_message: str, tool_context: ToolContext) -> Dict[str, Any]:
            """
            Automatically extract knowledge from user messages and update their profile.
            
            Args:
                user_message: The user's message to analyze
                tool_context: ADK context for accessing session state
            
            Returns:
                Dict with extraction results and updated profile info
            """
            print(f"🔧 [FUNCTION CALL] extract_and_learn() - Analyzing message for knowledge extraction")
            print(f"   📝 Message: '{user_message[:100]}{'...' if len(user_message) > 100 else ''}'")
            
            try:
                # Get or create user profile in session state
                if "user_profile" not in tool_context.state:
                    # In read-write mode, the session belongs to the user who is learning
                    # Get the user_id from the invocation context (which has the session info)
                    user_id = tool_context.invocation_context.user_id
                    empty_profile = UserProfile.create_empty(user_id)
                    tool_context.state["user_profile"] = empty_profile.to_dict()
                    print(f"   📊 Created new user profile for {user_id}")
                else:
                    print(f"   📊 Using existing user profile")
                
                # Use LLM to extract structured information
                extraction_prompt = f"""
                Analyze this user message and extract structured information: "{user_message}"
                
                Extract and return JSON with these fields:
                {{
                    "interests": {{"interest_name": "description", ...}},
                    "personality_traits": ["trait1", "trait2", ...],
                    "communication_style": "description",
                    "factual_information": {{"fact_type": "fact_value", ...}},
                    "has_extractable_info": true/false
                }}
                
                Examples:
                - "I love hiking and photography" → interests: {{"hiking": "outdoor activity", "photography": "creative hobby"}}
                - "I'm pretty introverted but love deep conversations" → personality_traits: ["introverted", "thoughtful"]
                - "I work as a software engineer at Google" → factual_information: {{"job": "software engineer", "company": "Google"}}
                
                Only extract clear, meaningful information. Set has_extractable_info=false for casual messages.
                """
                
                print(f"   🤖 Calling Gemini AI for knowledge extraction...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[genai_types.Content(
                        role="user", 
                        parts=[genai_types.Part.from_text(text=extraction_prompt)]
                    )]
                )
                
                if response.candidates and response.candidates[0].content.parts:
                    response_text = response.candidates[0].content.parts[0].text
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        extracted_info = json.loads(json_match.group())
                        
                        if extracted_info.get("has_extractable_info", False):
                            print(f"   ✅ Extracted information: {extracted_info}")
                            
                            # Update user profile with extracted information
                            profile = tool_context.state["user_profile"]
                            
                            # Update interests
                            if extracted_info.get("interests"):
                                profile["interests"].update(extracted_info["interests"])
                                print(f"   🎯 Updated interests: {list(extracted_info['interests'].keys())}")
                            
                            # Update personality traits
                            if extracted_info.get("personality_traits"):
                                new_traits = extracted_info["personality_traits"]
                                existing_traits = set(profile["personality_traits"])
                                profile["personality_traits"] = list(existing_traits.union(set(new_traits)))
                                print(f"   🧠 Updated personality traits: {new_traits}")
                            
                            # Update communication style
                            if extracted_info.get("communication_style"):
                                profile["communication_style"] = extracted_info["communication_style"]
                                print(f"   💬 Updated communication style: {extracted_info['communication_style']}")
                            
                            # Update factual information
                            if extracted_info.get("factual_information"):
                                for fact_type, fact_value in extracted_info["factual_information"].items():
                                    profile["learned_facts"][fact_type] = {
                                        "value": fact_value,
                                        "learned_at": datetime.now().isoformat(),
                                        "source_message": user_message
                                    }
                                print(f"   📚 Updated facts: {list(extracted_info['factual_information'].keys())}")
                            
                            profile["last_updated"] = datetime.now().isoformat()
                            
                            # Update the session state through tool_context
                            # This will automatically persist to the sessions table
                            tool_context.state["user_profile"] = profile
                            print(f"   💾 Profile updated in session state - will be persisted automatically")
                            
                            result = {
                                "status": "learned", 
                                "message": "I've updated my understanding of you based on what you shared.",
                                "extracted_info": extracted_info,
                                "profile_summary": {
                                    "interests_count": len(profile["interests"]),
                                    "traits_count": len(profile["personality_traits"]),
                                    "facts_count": len(profile["learned_facts"])
                                }
                            }
                            print(f"   ✅ Function completed successfully: {result['status']}")
                            return result
                        else:
                            print(f"   ℹ️ No extractable information found")
                            return {
                                "status": "no_extraction",
                                "message": "Continuing our conversation..."
                            }
                
            except Exception as e:
                print(f"   ❌ Error in knowledge extraction: {e}")
            
            return {
                "status": "error",
                "message": "I'm having trouble processing that information right now."
            }
        
        # Return the function directly - ADK will handle tool registration
        return extract_and_learn
    
    def _create_smart_retrieval_tool(self):
        """Create intelligent data retrieval tool for answering questions about users."""
        async def smart_answer_about_user(question: str, tool_context: ToolContext) -> Dict[str, Any]:
            """
            Intelligently answer questions about a user by analyzing stored data and making inferences.
            
            Args:
                question: The question being asked about the user.
                tool_context: ADK context for accessing session state.
            
            Returns:
                Dict with intelligent answer based on stored data.
            """
            # Extract target_user_id from the temporary context in the session state
            temp_context = tool_context.state.get("_temp_context", {})
            target_user_id_from_context = temp_context.get("target_user_id", "unknown")

            print(f"🧠 [FUNCTION CALL] smart_answer_about_user() - Analyzing stored data for intelligent answers")
            print(f"   ❓ Question: '{question[:100]}{'...' if len(question) > 100 else ''}'")
            print(f"   🎯 Target User (from context): {target_user_id_from_context}")
            
            try:
                # Get user's profile data from the current session state.
                # NOTE: The session is for target_user_id, so tool_context is correct.
                if "user_profile" not in tool_context.state:
                    print(f"   ❌ No user profile found in session state for {target_user_id_from_context}")
                    return {
                        "status": "no_data",
                        "message": f"I don't have any information about {target_user_id_from_context} yet. If you are this user, please share something about yourself."
                    }
                
                profile = tool_context.state["user_profile"]
                print(f"   📊 Found user profile for analysis")
                print(f"      - Interests: {list(profile.get('interests', {}).keys())}")
                print(f"      - Personality Traits: {profile.get('personality_traits', [])}")
                print(f"      - Facts: {list(profile.get('learned_facts', {}).keys())}")
                
                # Check if the profile is actually empty (no real data learned yet)
                has_interests = bool(profile.get('interests', {}))
                has_traits = bool(profile.get('personality_traits', []))
                has_facts = bool(profile.get('learned_facts', {}))
                has_communication_style = bool(profile.get('communication_style', '').strip())
                
                if not (has_interests or has_traits or has_facts or has_communication_style):
                    print(f"   ℹ️ Profile exists but contains no learned data yet")
                    return {
                        "status": "no_data",
                        "message": "I don't have any information about you yet. Please share something about yourself so I can learn about you!"
                    }
                
                # Create comprehensive data summary for AI analysis
                user_data_summary = {
                    "interests": profile.get('interests', {}),
                    "personality_traits": profile.get('personality_traits', []),
                    "communication_style": profile.get('communication_style', 'unknown'),
                    "learned_facts": profile.get('learned_facts', {}),
                    "profile_updated": profile.get('last_updated', 'unknown')
                }
                
                # Use AI to analyze data and answer with inference
                analysis_prompt = f"""
                You are an intelligent assistant that can answer questions about a user based on their stored profile data.
                Use the available information to provide helpful answers, making reasonable inferences when appropriate.
                
                USER PROFILE DATA:
                {json.dumps(user_data_summary, indent=2)}
                
                QUESTION: "{question}"
                
                Instructions:
                1. Look through ALL the stored data for relevant information
                2. Make reasonable inferences based on the data (e.g., if they "play piano", piano is likely a favorite instrument)
                3. If you have relevant information, provide a confident answer with reasoning
                4. If the data is insufficient, say so honestly
                5. Always explain what data you're basing your answer on
                
                Examples of good inference:
                - "plays piano" → piano is probably their favorite/preferred instrument
                - "loves hiking" + "works outdoors" → they probably enjoy nature/outdoor activities
                - "software engineer" + "loves puzzles" → they probably enjoy problem-solving
                
                Respond in this format:
                {{
                    "answer": "Direct answer to the question",
                    "confidence": "high/medium/low",
                    "reasoning": "Explanation of what data supports this answer",
                    "supporting_data": ["list", "of", "relevant", "data", "points"],
                    "inference_made": true/false
                }}
                """
                
                print(f"   🤖 Calling Gemini AI for intelligent analysis...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[genai_types.Content(
                        role="user",
                        parts=[genai_types.Part.from_text(text=analysis_prompt)]
                    )]
                )
                
                if response.candidates and response.candidates[0].content.parts:
                    response_text = response.candidates[0].content.parts[0].text
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        analysis_result = json.loads(json_match.group())
                        
                        # Format the response nicely
                        answer = analysis_result.get("answer", "I couldn't determine an answer.")
                        confidence = analysis_result.get("confidence", "low")
                        reasoning = analysis_result.get("reasoning", "No clear reasoning available.")
                        supporting_data = analysis_result.get("supporting_data", [])
                        inference_made = analysis_result.get("inference_made", False)
                        
                        # Create response message
                        response_parts = [answer]
                        
                        if inference_made:
                            response_parts.append(f"(This is an inference based on: {reasoning})")
                        else:
                            response_parts.append(f"(Based on stored data: {reasoning})")
                        
                        if supporting_data:
                            response_parts.append(f"Supporting information: {', '.join(supporting_data)}")
                        
                        result = {
                            "status": "answered",
                            "message": " ".join(response_parts),
                            "answer": answer,
                            "confidence": confidence,
                            "inference_made": inference_made,
                            "supporting_data": supporting_data
                        }
                        
                        print(f"   ✅ Function completed successfully: {result['status']}")
                        return result
                
            except Exception as e:
                print(f"Error in smart retrieval: {e}")
            
            return {
                "status": "error",
                "message": "I'm having trouble analyzing the stored information right now."
            }
        
        # Return the function directly - ADK will handle tool registration
        return smart_answer_about_user
    
    def _create_representation_tool(self):
        """Create the user representation tool for cross-user interactions."""
        async def represent_user(context: str, tool_context: ToolContext) -> Dict[str, Any]:
            """
            Represent a user to someone else based on learned profile.
            
            Args:
                context: Context of the representation request.
                tool_context: ADK context for accessing session state.
            
            Returns:
                Dict with representation response.
            """
            # Extract target_user_id from the temporary context in the session state
            temp_context = tool_context.state.get("_temp_context", {})
            target_user_id_from_context = temp_context.get("target_user_id", "unknown")

            print(f"🎭 [FUNCTION CALL] represent_user() - Representing user to others")
            print(f"   🎯 Target User (from context): {target_user_id_from_context}")
            print(f"   📝 Context: '{context[:100]}{'...' if len(context) > 100 else ''}'")
            
            try:
                if "user_profile" not in tool_context.state:
                    print(f"   ❌ No user profile found in session state for {target_user_id_from_context}")
                    return {
                        "status": "no_profile",
                        "message": "I don't have enough information about that user yet."
                    }
                
                profile = tool_context.state["user_profile"]
                print(f"   📊 Found user profile for representation")
                print(f"      - Interests: {list(profile.get('interests', {}).keys())}")
                print(f"      - Personality Traits: {profile.get('personality_traits', [])}")
                print(f"      - Communication Style: {profile.get('communication_style', 'friendly')}")
                
                print(f"   🤖 Calling Gemini AI to generate user representation...")
                
                # Generate representation based on learned profile
                representation_prompt = f"""
                You are representing a user based on their learned profile. Respond as they would.
                
                User Profile:
                - Interests: {json.dumps(profile.get('interests', {}), indent=2)}
                - Personality Traits: {profile.get('personality_traits', [])}
                - Communication Style: {profile.get('communication_style', 'friendly')}
                - Known Facts: {json.dumps(profile.get('learned_facts', {}), indent=2)}
                
                Context/Question: {context}
                
                Respond as this user would respond, incorporating their interests, personality, and communication style.
                Be authentic to their profile while being helpful and appropriate.
                Make reasonable inferences from the available data (e.g., if they play piano, they probably prefer piano as an instrument).
                """
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[genai_types.Content(
                        role="user",
                        parts=[genai_types.Part.from_text(text=representation_prompt)]
                    )]
                )
                
                if response.candidates and response.candidates[0].content.parts:
                    representation_text = response.candidates[0].content.parts[0].text
                    print(f"   ✅ Generated representation: '{representation_text[:100]}{'...' if len(representation_text) > 100 else ''}'")
                    
                    result = {
                        "status": "represented",
                        "message": representation_text,
                        "represented_user": target_user_id_from_context
                    }
                    
                    print(f"   ✅ Function completed successfully: {result['status']}")
                    return result
                
            except Exception as e:
                print(f"   ❌ Error in user representation: {e}")
            
            return {
                "status": "error",
                "message": "I'm having trouble representing that user right now."
            }
        
        # Return the function directly - ADK will handle tool registration
        return represent_user
    
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

        if is_owner:
            print("   🔒 Mode: Read-Write (Owner is talking to their own AI)")
            runner = self.read_write_runner
        else:
            print("   👁️ Mode: Read-Only (Another user is talking to the AI)")
            runner = self.read_only_runner
            
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
