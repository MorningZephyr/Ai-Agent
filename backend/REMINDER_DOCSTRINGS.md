# Reminder: Importance of Docstrings in ADK Functions

## Why Docstrings Matter
- **Clarity for Developers:** Docstrings explain what a function does, its arguments, return values, and side effects. This is crucial for anyone using or maintaining ADK-based agents and tools.
- **Tool Discovery:** ADK and similar frameworks often use docstrings to auto-generate documentation, help UIs, and guide agent orchestration.
- **LLM/Agent Guidance:** Well-written docstrings help the agent (and the underlying LLM) understand the intended use and constraints of a tool, improving reasoning and tool selection.
- **Testing & Debugging:** Docstrings clarify expected behavior, making it easier to write tests and debug issues.
- **Collaboration:** In multi-agent or team projects, docstrings ensure everyone understands the function's contract and usage.

## ADK Best Practices
- Every tool function should have a clear, descriptive docstring.
- Docstrings should specify:
  - What the function does
  - Expected input types and formats
  - Output structure and meaning
  - Any important side effects or persistence
- Use examples in docstrings for complex tools.

## Example
```python
    def search_google(query: str, tool_context: ToolContext) -> Dict[str, Any]:
        """
        Search Google for the given query and return top results.

        Args:
            query (str): The search query string.
            tool_context (ToolContext): Provided by ADK for context and persistence.

        Returns:
            Dict[str, Any]:
                - status: 'success' or 'error'
                - results: list of search results
        """
        ...
```

## Summary
**Always write and update docstrings for every function, especially ADK tools.**
This improves agent performance, developer experience, and project maintainability.
