"""
Learning tool for the AI Representative System.
Handles automated knowledge extraction from user messages.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any

from google.adk.tools.tool_context import ToolContext
from google.genai import Client, types as genai_types

from models import UserProfile


def create_learning_tool(client: Client, model_name: str):
    """
    Create the automated knowledge extraction tool.
    
    Args:
        client: Gemini client for AI processing
        model_name: Name of the model to use
    
    Returns:
        The learning tool function
    """
    
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
            response = client.models.generate_content(
                model=model_name,
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
