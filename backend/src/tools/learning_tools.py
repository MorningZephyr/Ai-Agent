"""
Learning tools for storing information about the bot owner.
"""

from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from .base_tool import BaseTool


class LearnAboutUserTool(BaseTool):
    """Tool for learning and storing facts about the bot owner."""
    
    def execute(self, tool_context: ToolContext, key: str, value: str) -> Dict[str, Any]:
        """Store personal facts about the bot owner for future conversations.
        
        Use this when the bot owner shares personal information that should be remembered.
        Examples: favorite color, job, hobbies, preferences, family details, interests.
        Only works when talking directly to the bot owner (is_owner=True).
        
        Args:
            key: Category of information (e.g., 'favorite_color', 'job', 'hobby')  
            value: The actual information to store
        
        Returns:
            Dict with status and confirmation message
        """
        
        # Check if the current user is the bot owner
        if not self.is_owner():
            return {
                "status": "unauthorized",
                "message": f"I can only learn about {self.bot_owner_id} when talking to {self.bot_owner_id} directly. You are logged in as '{self.current_user_id}'."
            }
        
        # Get the old value if it exists
        old_value = tool_context.state.get(key)
        
        # Store the new information in session state (this persists with DatabaseSessionService!)
        tool_context.state[key] = value
        
        # Create response message
        is_update = old_value is not None
        if is_update:
            message = f"Updated: {key.replace('_', ' ')} = '{value}' (was: '{old_value}')"
            status = "updated"
        else:
            message = f"Learned: {key.replace('_', ' ')} = '{value}'"
            status = "learned"
        
        return {
            "status": status,
            "message": message,
            "key": key,
            "value": value,
            "previous_value": old_value
        }


def learn_about_user_wrapper(bot_owner_id: str, current_user_id: str):
    """Create a wrapper function for the learn_about_user tool."""
    tool = LearnAboutUserTool(bot_owner_id)
    tool.set_current_user(current_user_id)
    
    def learn_about_user(key: str, value: str, tool_context: ToolContext) -> Dict[str, Any]:
        return tool.execute(tool_context, key, value)
    
    return learn_about_user
