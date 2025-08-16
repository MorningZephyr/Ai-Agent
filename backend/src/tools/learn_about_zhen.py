"""
Simple tool for learning facts about Zhen.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from google.genai import Client, types as genai_types


async def learn_about_zhen(statement: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Learn a fact about Zhen from a statement.

    Args:
        statement: What Zhen said about himself
        tool_context: ADK context for storing data

    Returns:
        Dict with status and message
    """
    if not statement or not statement.strip():
        return {"status": "error", "message": "Please tell me something about yourself."}

    # Make sure we have a place to store facts
    if "facts" not in tool_context.state:
        tool_context.state["facts"] = {}

    # Use the LLM to extract a key-value fact
    try:
        client = Client()
        prompt = f'''
Extract a fact from this statement: "{statement}"

Respond with JSON in this format:
{{"key": "descriptive_key", "value": "fact_value", "is_fact": true}}

Examples:
- "I like red" -> {{"key": "favorite_color", "value": "red", "is_fact": true}}
- "I work at Google" -> {{"key": "job", "value": "works at Google", "is_fact": true}}
- "How are you?" -> {{"key": "", "value": "", "is_fact": false}}

Only extract clear facts. Set is_fact=false for questions or non-facts.
'''

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=prompt)]
            )]
        )

        if response.candidates and response.candidates[0].content.parts:
            response_text = response.candidates[0].content.parts[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                if result.get("is_fact") and result.get("key") and result.get("value"):
                    key = result["key"]
                    value = result["value"]
                    
                    # Store the fact
                    tool_context.state["facts"][key] = {
                        "value": value,
                        "learned_at": datetime.now().isoformat(),
                        "from_statement": statement
                    }
                    
                    return {
                        "status": "learned",
                        "message": f"Got it! I learned that {key} = {value}",
                        "key": key,
                        "value": value
                    }
                else:
                    return {
                        "status": "not_factual",
                        "message": "That doesn't seem to be a fact I can store about you."
                    }

    except Exception as e:
        print(f"Error extracting fact: {e}")
        
    return {
        "status": "error", 
        "message": "I couldn't understand what to learn from that."
    }
