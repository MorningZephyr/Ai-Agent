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
        """Remember a free-text statement about the user.

        Args:
            statement: e.g., "My favorite color is blue", "I work at Google".

        Behavior:
            - Always appends the raw statement to facts._raw
            - Tries to extract a simple key/value when phrased like "my X is Y" or "I am a Y"
            - Stores extracted facts under normalized keys in ToolContext.state

        Returns:
            Dict with status, message, and any extracted key/value.
        """
        if not statement or not statement.strip():
            return {"status": "error", "message": "Please provide something to learn."}

        st = statement.strip()

        # 1) Save raw statement
        raw_key = "facts._raw"
        raw_list = tool_context.state.get(raw_key) or []
        raw_list.append(st)
        tool_context.state[raw_key] = raw_list

        # 2) Heuristic extraction
        extracted = []
        lower = st.lower()

        # Pattern: "my X is Y"
        if lower.startswith("my ") and " is " in lower:
            try:
                after_my = st[3:].strip()  # drop "My "
                parts = after_my.split(" is ", 1)
                if len(parts) == 2:
                    key_raw, value = parts[0].strip(), parts[1].strip()
                    key = self._normalize_key(key_raw)
                    tool_context.state[key] = value
                    extracted.append((key, value))
            except Exception:
                pass

        # Pattern: "I am a/an Y" or "I'm a/an Y"
        if not extracted:
            for prefix in ["i am ", "i'm "]:
                if lower.startswith(prefix):
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
            return {
                "status": "stored",
                "message": "Stored your statement.",
            }

    # ADK compatibility shim (not used directly by our wrappers)
    def execute(self, tool_context: ToolContext, **kwargs) -> Dict[str, Any]:
        statement = kwargs.get("statement", "")
        return self.learn_about_user(tool_context, statement)
