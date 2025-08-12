"""
Expose a single, simple learn tool for the bot.
"""

from typing import Dict, Any, List
from google.adk.tools.tool_context import ToolContext
from .user_info_tool import UserInfoTool


def get_tools() -> List:
    """
    Return the list of available tools for the bot to use.

    This function exposes all tool functions that the agent can call during reasoning.
    The returned list may include one or more tools, depending on the bot's capabilities.
    """
    tool = UserInfoTool()

    def learn_about_user(statement: str, tool_context: ToolContext) -> Dict[str, Any]:
        """
        Store a user statement as a key-value pair in persistent memory.

        The AI will attempt to extract a meaningful key name from the statement context
        (e.g., "My favorite color is blue" → key: "favorite_color", value: "blue").
        If no key-value can be extracted, a key name suggestion is returned for user approval.

        Args:
            statement (str): Any user fact or statement (e.g., "My favorite color is blue", "I work at Google").

        Returns:
            Dict[str, Any]:
                - status: 'learned' if fact stored, 'suggestion' if key name suggested, 'error' if invalid input
                - message: description of what was stored or suggested
                - extracted: dict of key-value pairs (if any)
                - suggested_key: key name suggestion (if applicable)
                - original_statement: the original input (if applicable)
        """
        return tool.learn_about_user(tool_context, statement)

    return [learn_about_user]
