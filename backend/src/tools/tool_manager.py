"""
Expose a single, simple learn tool for the bot.
"""

from typing import Dict, Any, List
from google.adk.tools.tool_context import ToolContext
from .user_info_tool import UserInfoTool


def get_tools() -> List:
    """Return the minimal toolset: learn_about_user(statement, tool_context).

    The tool teaches the bot anything the user says. It stores the raw statement
    and attempts a simple key/value extraction for patterns like "my X is Y".
    """
    tool = UserInfoTool()

    def learn_about_user(statement: str, tool_context: ToolContext) -> Dict[str, Any]:
        """Learn a fact or statement about the user.

        Args:
            statement (str): e.g., "My favorite color is blue", "I work at Google".
            tool_context (ToolContext): Provided by ADK to persist state.

        Returns:
            Dict[str, Any]: status in {'learned','stored','error'} with message and extracted pairs.
        """
        return tool.learn_about_user(tool_context, statement)

    return [learn_about_user]
