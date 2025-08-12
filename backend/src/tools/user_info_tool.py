"""
Simple memory tool: a single function to learn anything the user tells it.
"""

from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext


class UserInfoTool:
    """A minimal tool that remembers facts from free-text statements.

    One public method is exposed to the LLM:
    - learn_about_user(statement: str): Store the statement and heuristically extract key/value.

    Storage model in ToolContext.state:
    - facts._raw: list[str] of original statements
    - facts._keys: list[str] of normalized keys we discovered
    - facts.{key}: value for that key (when we can extract)
    """

    def __init__(self):
        pass

    @staticmethod
    def _normalize_key(text: str) -> str:
        return text.strip().lower().replace("'s ", " ").replace(" ", "_").replace("-", "_")

    def learn_about_user(self, tool_context: ToolContext, statement: str) -> Dict[str, Any]:
        """
        Use the LLM to decide if a statement expresses a user fact, preference, or hobby, and extract key-value pairs.

        Args:
            statement: Any user statement (e.g., "I like basketball", "My favorite color is blue").

        Behavior:
            - Uses the LLM to classify the statement and extract a key-value pair if possible
            - Stores extracted facts under normalized keys in ToolContext.state
            - If no key-value can be extracted, suggests a key name and asks for user approval

        Returns:
            Dict with:
                - status: 'learned' if fact stored, 'suggestion' if key name suggested, 'error' if invalid input
                - message: description of what was stored or suggested
                - extracted: dict of key-value pairs (if any)
                - suggested_key: key name suggestion (if applicable)
                - original_statement: the original input (if applicable)
        """
        if not statement or not statement.strip():
            return {"status": "error", "message": "Please provide something to learn."}

        st = statement.strip()

        # Use the LLM to classify and extract key-value
        # For demonstration, we'll simulate the LLM with a simple prompt and response
        # In production, you would call the LLM API here
        # Example prompt:
        # "Given the statement: 'I like basketball', does this express a user fact, preference, or hobby? If so, extract a key and value."

        # Simulated LLM logic (replace with actual LLM call)
        import re
        extracted = []
        # Simulate: If the statement contains 'like', treat as hobby/preference
        if re.search(r'\blike\b', st.lower()):
            key = self._normalize_key("hobby")
            value = re.sub(r'.*like ', '', st, flags=re.IGNORECASE).strip('.').strip()
            tool_context.state[key] = value
            extracted.append((key, value))
        # Simulate: If the statement matches 'my X is Y'
        elif st.lower().startswith("my ") and " is " in st.lower():
            after_my = st[3:].strip()
            parts = after_my.split(" is ", 1)
            if len(parts) == 2:
                key_raw, value = parts[0].strip(), parts[1].strip()
                key = self._normalize_key(key_raw)
                tool_context.state[key] = value
                extracted.append((key, value))
        # Simulate: If the statement matches 'I am a/an Y' or 'I'm a/an Y'
        elif any(st.lower().startswith(prefix) for prefix in ["i am ", "i'm "]):
            for prefix in ["i am ", "i'm "]:
                if st.lower().startswith(prefix):
                    value = st[len(prefix):].strip()
                    key = self._normalize_key("role")
                    tool_context.state[key] = value
                    extracted.append((key, value))
                    break

        # Track keys
        keys_key = "facts._keys"
        known_keys = tool_context.state.get(keys_key) or []
        for key, _ in extracted:
            if key not in known_keys:
                known_keys.append(key)
        tool_context.state[keys_key] = known_keys

        if extracted:
            pairs = ", ".join([f"{k}='{v}'" for k, v in extracted])
            return {
                "status": "learned",
                "message": f"Learned: {pairs}",
                "extracted": {k: v for k, v in extracted},
            }
        else:
            # If the LLM can't extract, suggest a key name
            suggestion = "fact"  # fallback
            words = st.split()
            if len(words) > 2:
                suggestion = self._normalize_key(words[1])
            return {
                "status": "suggestion",
                "message": f"No key-value extracted. Suggest key name: '{suggestion}'. Please approve or provide a better key.",
                "suggested_key": suggestion,
                "original_statement": st,
            }

    # ADK compatibility shim (not used directly by our wrappers)
    def execute(self, tool_context: ToolContext, **kwargs) -> Dict[str, Any]:
        statement = kwargs.get("statement", "")
        return self.learn_about_user(tool_context, statement)
