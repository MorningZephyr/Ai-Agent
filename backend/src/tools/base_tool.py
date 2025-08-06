"""
Base tool class for all bot tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext


class BaseTool(ABC):
    """Base class for all bot tools."""
    
    def __init__(self, bot_owner_id: str):
        self.bot_owner_id = bot_owner_id
        self.current_user_id: str = None
    
    def set_current_user(self, user_id: str) -> None:
        """Set the current user context."""
        self.current_user_id = user_id
    
    def is_owner(self) -> bool:
        """Check if current user is the bot owner."""
        return self.current_user_id == self.bot_owner_id
    
    @abstractmethod
    def execute(self, tool_context: ToolContext, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given context and parameters."""
        pass
