"""
Retrieval tools for accessing stored information about the bot owner.
"""

from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from .base_tool import BaseTool


class GetUserInfoTool(BaseTool):
    """Tool for retrieving specific information about the bot owner."""
    
    def execute(self, tool_context: ToolContext, key: str) -> Dict[str, Any]:
        """Retrieve specific information about the bot owner that was previously stored.
        
        Use this to look up facts about the bot owner when answering questions or providing context.
        Works for any stored information like preferences, background, interests, etc.
        Available to both the owner and others who interact with this bot.
        
        Args:
            key: The category of information to retrieve (e.g., 'favorite_color', 'job')
        
        Returns:
            Dict with the requested information or 'not found' message
        """
        
        # Access the session state to retrieve information
        value = tool_context.state.get(key)
        
        if value:
            return {
                "status": "found",
                "message": f"{self.bot_owner_id}'s {key.replace('_', ' ')}: {value}",
                "key": key,
                "value": value
            }
        else:
            if self.is_owner():
                suggestion = f"You can teach me by saying something like 'My {key.replace('_', ' ')} is ...'"
            else:
                suggestion = f"{self.bot_owner_id} hasn't shared that information with me yet."
            
            return {
                "status": "not_found",
                "message": f"I don't know {self.bot_owner_id}'s {key.replace('_', ' ')} yet. {suggestion}",
                "key": key
            }


class ListKnownFactsTool(BaseTool):
    """Tool for displaying all stored information about the bot owner."""
    
    def execute(self, tool_context: ToolContext) -> Dict[str, Any]:
        """Display all stored information about the bot owner in an organized summary.
        
        Use this to show everything the bot knows about the owner, useful for:
        - Providing a complete overview when asked "what do you know about me?" (by owner)
        - Showing what information is available when others ask about the owner
        - Giving context in conversations about the bot owner
        
        Returns:
            Dict with all stored facts formatted as a readable list
        """
        
        # Get all non-system keys from state
        facts = {}
        system_keys = {"is_owner", "current_user", "bot_owner_id", "session_created"}
        
        # ADK State object doesn't support .items(), so we'll check known keys
        # This is a limitation - in a real app, you'd store facts in a structured way
        known_fact_keys = ["favorite_color", "job", "hobby", "work", "hobbies", "profession", "occupation", 
                          "age", "location", "education", "skills", "interests", "family", "pets"]
        
        for key in known_fact_keys:
            value = tool_context.state.get(key)
            if value is not None:
                facts[key.replace('_', ' ')] = value
        
        if facts:
            fact_list = "\n".join([f"- {key}: {value}" for key, value in facts.items()])
            if self.is_owner():
                message = f"Here's what I know about you:\n{fact_list}"
            else:
                message = f"Here's what I know about {self.bot_owner_id}:\n{fact_list}"
            
            return {
                "status": "found",
                "message": message,
                "facts": facts
            }
        else:
            if self.is_owner():
                message = "I don't have any specific facts about you yet. Start teaching me!"
            else:
                message = f"{self.bot_owner_id} hasn't shared much information with me yet."
            
            return {
                "status": "empty",
                "message": message,
                "facts": {}
            }


def get_user_info_wrapper(bot_owner_id: str, current_user_id: str):
    """Create a wrapper function for the get_user_info tool."""
    tool = GetUserInfoTool(bot_owner_id)
    tool.set_current_user(current_user_id)
    
    def get_user_info(key: str, tool_context: ToolContext) -> Dict[str, Any]:
        return tool.execute(tool_context, key)
    
    return get_user_info


def list_known_facts_wrapper(bot_owner_id: str, current_user_id: str):
    """Create a wrapper function for the list_known_facts tool."""
    tool = ListKnownFactsTool(bot_owner_id)
    tool.set_current_user(current_user_id)
    
    def list_known_facts(tool_context: ToolContext) -> Dict[str, Any]:
        return tool.execute(tool_context)
    
    return list_known_facts
