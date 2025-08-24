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

## ADK Usage Best Practices (for this repo)

- Agent and runner
  - Define an `Agent` with clear `name`, `model`, `description`, and a single source of truth for `instruction`.
  - Keep `Agent` construction separate from request handling; reuse a `Runner` with a persistent `SessionService` (e.g., `DatabaseSessionService`).
  - Prefer a stable `user_id` and `session_id`; document whether memory is shared or per-user. Our bot uses a shared key `memory::shared`.

- Tools: function shape and docstrings
  - Expose tools as plain Python functions (or simple wrappers) with explicit parameters plus `ToolContext`.
  - Return structured dictionaries with clear fields like `status`, `message`, and result payloads. Avoid raising in normal flows; surface errors in the return shape.
  - Write rich docstrings. Include: purpose, args with types, return schema, side effects (what keys in `ToolContext.state` are read/written), and examples if non-trivial.
  - Keep tool logic deterministic and idempotent when possible; clearly note non-idempotent behavior.

- ToolContext state conventions
  - Namespace and normalize keys written to `ToolContext.state`. Prefer lowercase snake_case and avoid collisions; document the schema in tool docs.
  - Track discovered keys in a dedicated index (e.g., `facts._keys`) and avoid storing PII unless necessary and documented.
  - Validate inputs early and return actionable messages on invalid input.
  - **Critical - ADK State Change Tracking**: ADK only detects state changes through direct assignment to `ToolContext.state` keys. Nested object modifications are not automatically tracked or persisted to the database.

    **Problem Pattern (Won't Persist):**
    ```python
    # Get reference to nested object
    profile = tool_context.state["user_profile"]
    
    # Modify nested properties - ADK doesn't detect these changes
    profile["interests"]["music"] = "hobby"
    profile["personality_traits"].append("creative")
    profile["learned_facts"]["job"] = {"value": "engineer", "source": "conversation"}
    
    # ❌ Changes are lost - ADK didn't detect the modifications
    ```

    **Correct Pattern (Will Persist):**
    ```python
    # Get reference to nested object
    profile = tool_context.state["user_profile"]
    
    # Modify nested properties
    profile["interests"]["music"] = "hobby"
    profile["personality_traits"].append("creative")
    profile["learned_facts"]["job"] = {"value": "engineer", "source": "conversation"}
    
    # ✅ Trigger ADK's change detection by reassigning the modified object
    tool_context.state["user_profile"] = profile
    print("Profile updated in session state - will be persisted automatically")
    ```

    **Why This Happens:**
    - ADK watches for assignments to `tool_context.state` keys to detect changes
    - Nested modifications (like `obj["key"]["subkey"] = value`) don't trigger the watcher
    - Reassignment (`tool_context.state["key"] = obj`) signals ADK that the state changed
    - Without reassignment, changes remain in memory only and are lost when the session ends

- Prompting and instruction hygiene
  - Keep the agent instruction concise and explicit about when to call tools and when not to.
  - Encourage the model to ask for clarification when extraction is ambiguous; do not store questions or non-facts.

- API and wire format
  - When using ADK’s generated FastAPI helpers, default wire format is camelCase. If adding custom endpoints, keep naming consistent and document payload shapes.
  - Always provide a safe, non-empty response string to the UI even on failures.

- Testing and evaluation
  - Unit test tool functions (deterministic parts) with `pytest` focusing on edge cases and error messages.
  - Integration test the agent + runner path with mocked LLMs if needed.
  - Use ADK’s evaluation framework for end-to-end quality checks when introducing material prompt or tool changes.

- Operational practices
  - Load secrets (e.g., `GOOGLE_API_KEY`, `DB_URL`) from the environment; validate at startup.
  - Log meaningful events but never secrets or raw credentials. Prefer structured logs for session lifecycle and tool outcomes.
  - Handle exceptions at boundaries and translate them to user-facing messages; keep stack traces out of responses.

- Code style and imports
  - Use explicit imports from modules (avoid importing from `__init__.py`).
  - Prefer descriptive names for tools and fields (readability over brevity). Annotate function signatures and returned schemas where applicable.
  - Keep functions small; use early returns for error paths to avoid deep nesting.

Docstring template snippet for tools:

```python
def my_tool(arg1: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    One-line summary of what the tool does.

    Args:
        arg1 (str): Description and expected format.
        tool_context (ToolContext): ADK context; writes to tool_context.state['...'].

    Returns:
        Dict[str, Any]:
            - status: 'success' | 'error' | 'suggestion'
            - message: Human-readable outcome
            - data: Optional payload (document keys and types)

    Side Effects:
        - Writes/reads these state keys: 'facts._keys', 'facts.favorite_color', ...
    """
    ...
```
