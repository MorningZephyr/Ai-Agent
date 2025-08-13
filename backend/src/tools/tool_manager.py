"""
Enhanced tool manager with fact learning, retrieval, and search capabilities.
"""

import asyncio
from typing import Dict, Any, List
from google.adk.tools.tool_context import ToolContext
from .user_info_tool import UserInfoTool


def get_tools(is_owner: bool = False) -> List:
    """
    Return the list of available tools for the AI representative agent.

    Args:
        is_owner: Whether the current user is the person being represented
        
    Returns:
        List of tools based on user permissions:
        - Owners: can learn facts, list facts, and search facts
        - Non-owners: can only list facts and search facts (no learning)
    """
    tool = UserInfoTool()

    async def learn_about_user(statement: str, tool_context: ToolContext) -> Dict[str, Any]:
        """
        Learn facts about the represented person using LLM-driven extraction.
        
        PERMISSION REQUIRED: Only available to the person being represented (owner).

        Uses advanced natural language processing to extract structured facts from statements
        about the person. Handles multiple facts per statement, confidence scoring, and
        intelligent key normalization with collision detection.

        Args:
            statement (str): Statement about the person (e.g., "I work at Google as a software engineer", 
                           "My favorite color is blue and I love hiking").

        Returns:
            Dict[str, Any]:
                - status: 'learned', 'not_factual', 'no_facts', 'validation_failed', 'permission_denied', or 'error'
                - message: Human-readable description of the outcome
                - extracted: Dict of successfully stored key-value pairs (if any)
                - reasoning: LLM's explanation of extraction decisions (if available)

        Side Effects:
            - Writes to tool_context.state['profile']['facts']: structured fact storage
            - Updates tool_context.state['profile']['audit']: audit trail of changes
            - Maintains tool_context.state['profile']['keys']: index of known keys
        """
        # Check if this tool should be available (only for owners)
        if not is_owner:
            return {
                "status": "permission_denied",
                "message": "Only the person being represented can teach new facts. Others can ask questions about existing knowledge."
            }
        return await tool.learn_about_user(tool_context, statement)

    def list_known_facts(tool_context: ToolContext) -> Dict[str, Any]:
        """
        List all stored facts about the represented person.

        Provides a comprehensive view of everything known about the person, including
        confidence levels and when each fact was learned.

        Args:
            tool_context (ToolContext): ADK context for accessing stored facts.

        Returns:
            Dict[str, Any]:
                - status: 'success' or 'empty'
                - message: Summary of facts found
                - facts: Dict mapping fact keys to {value, confidence, learned} objects
                - fact_count: Total number of stored facts

        Side Effects:
            - Reads from tool_context.state['profile']['facts']
        """
        return tool.list_known_facts(tool_context)

    async def search_facts(query: str, tool_context: ToolContext) -> Dict[str, Any]:
        """
        Search stored facts by keyword or topic.

        Enables the agent to find specific information about the person based on
        topic queries (e.g., "work", "hobbies", "personal preferences").

        Args:
            query (str): Search query or topic (e.g., "work", "favorite", "hobbies").
            tool_context (ToolContext): ADK context for accessing stored facts.

        Returns:
            Dict[str, Any]:
                - status: 'found', 'not_found', 'empty', or 'error'
                - message: Description of search results
                - matches: Dict of matching facts with metadata
                - query: The original search query

        Side Effects:
            - Reads from tool_context.state['profile']['facts']
        """
        return await tool.search_facts(tool_context, query)

    # Return tools based on permissions
    tools = [list_known_facts, search_facts]
    if is_owner:
        tools.insert(0, learn_about_user)  # Add learning capability for owners
    
    return tools
