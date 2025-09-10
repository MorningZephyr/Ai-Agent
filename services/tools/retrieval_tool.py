"""
Smart retrieval tool for the AI Representative System.
Handles intelligent data retrieval and answering questions about users.
"""

import json
import re
from typing import Dict, Any

from google.adk.tools.tool_context import ToolContext
from google.genai import Client, types as genai_types


def create_smart_retrieval_tool(client: Client, model_name: str):
    """
    Create intelligent data retrieval tool for answering questions about users.
    
    Args:
        client: Gemini client for AI processing
        model_name: Name of the model to use
    
    Returns:
        The smart retrieval tool function
    """
    
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
            response = client.models.generate_content(
                model=model_name,
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
