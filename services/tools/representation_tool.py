"""
Representation tool for the AI Representative System.
Handles representing users to others based on learned profiles.
"""

import json
from typing import Dict, Any

from google.adk.tools.tool_context import ToolContext
from google.genai import Client, types as genai_types


def create_representation_tool(client: Client, model_name: str):
    """
    Create the user representation tool for cross-user interactions.
    
    Args:
        client: Gemini client for AI processing
        model_name: Name of the model to use
    
    Returns:
        The representation tool function
    """
    
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
            
            response = client.models.generate_content(
                model=model_name,
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
