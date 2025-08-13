"""
Enhanced memory tool with LLM-driven fact extraction and retrieval capabilities.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from google.adk.tools.tool_context import ToolContext
from google.genai import Client, types as genai_types


class UserInfoTool:
    """Enhanced memory tool with LLM-driven fact extraction and retrieval.

    Public methods exposed to the LLM:
    - learn_about_user(statement: str): Store facts using LLM-driven extraction
    - list_known_facts(): Retrieve all stored facts
    - search_facts(query: str): Search facts by query

    Storage model in ToolContext.state:
    - profile.facts: dict[str, dict] - each fact with value, timestamp, source
    - profile.audit: list[dict] - audit trail of changes
    - profile.keys: list[str] - normalized keys index
    """

    def __init__(self):
        self.client = Client()

    @staticmethod
    def _normalize_key(text: str) -> str:
        """Normalize a key for consistent storage and collision handling."""
        normalized = text.strip().lower()
        normalized = re.sub(r"['\"]", "", normalized)  # Remove quotes
        normalized = re.sub(r"[^\w\s]", " ", normalized)  # Replace punctuation with spaces
        normalized = re.sub(r"\s+", "_", normalized)  # Replace spaces with underscores
        normalized = re.sub(r"_+", "_", normalized)  # Collapse multiple underscores
        return normalized.strip("_")

    def _handle_key_collision(self, key: str, existing_facts: dict) -> str:
        """Handle key collisions by suggesting numbered variants."""
        if key not in existing_facts:
            return key
        
        # Try numbered variants
        for i in range(2, 10):
            variant = f"{key}_{i}"
            if variant not in existing_facts:
                return variant
        
        # Fallback to timestamp-based key
        timestamp = datetime.now().strftime("%m%d_%H%M")
        return f"{key}_{timestamp}"

    async def _extract_facts_with_llm(self, statement: str) -> Dict[str, Any]:
        """Use LLM to extract structured facts from a statement."""
        extraction_prompt = f"""
Analyze this statement about a person and extract factual information that can be stored as key-value pairs.

Statement: "{statement}"

Extract facts in this JSON format:
{{
  "facts": [
    {{"key": "descriptive_key_name", "value": "fact_value", "confidence": "high|medium|low"}}
  ],
  "is_factual": true|false,
  "reasoning": "brief explanation"
}}

Guidelines:
- Only extract stable, verifiable facts (not opinions, questions, or temporary states)
- Use clear, descriptive key names (e.g., "favorite_color", "profession", "hometown")
- Confidence: "high" for clear facts, "medium" for likely facts, "low" for uncertain
- Set is_factual=false for questions, greetings, or non-factual content
- Multiple facts from one statement are allowed

Examples:
- "My favorite color is blue" → {{"key": "favorite_color", "value": "blue", "confidence": "high"}}
- "I work at Google as a software engineer" → Two facts: profession and employer
- "I think I might like hiking" → {{"key": "hobby", "value": "hiking", "confidence": "low"}}
"""

        try:
            content = genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=extraction_prompt)]
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[content],
                config=genai_types.GenerateContentConfig(
                    system_instruction="You are a fact extraction assistant. Return only valid JSON."
                )
            )
            
            if response.candidates and response.candidates[0].content.parts:
                response_text = response.candidates[0].content.parts[0].text
                # Clean the response to extract JSON
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"facts": [], "is_factual": False, "reasoning": "No valid response from LLM"}
            
        except Exception as e:
            return {"facts": [], "is_factual": False, "reasoning": f"LLM extraction error: {str(e)}"}

    async def learn_about_user(self, tool_context: ToolContext, statement: str) -> Dict[str, Any]:
        """
        Use LLM-driven extraction to learn facts about the represented person.

        Args:
            tool_context: ADK context for state management
            statement: User statement about the person (e.g., "His favorite color is blue")

        Returns:
            Dict with status, message, and extracted facts
        """
        if not statement or not statement.strip():
            return {"status": "error", "message": "Please provide something to learn."}

        statement = statement.strip()
        
        # Initialize storage structure if needed
        if "profile" not in tool_context.state:
            tool_context.state["profile"] = {"facts": {}, "audit": [], "keys": []}
        
        profile = tool_context.state["profile"]
        existing_facts = profile["facts"]
        
        # Extract facts using LLM
        extraction_result = await self._extract_facts_with_llm(statement)
        
        if not extraction_result.get("is_factual", False):
            return {
                "status": "not_factual",
                "message": f"Statement doesn't contain extractable facts. {extraction_result.get('reasoning', '')}",
                "original_statement": statement
            }
        
        extracted_facts = extraction_result.get("facts", [])
        if not extracted_facts:
            return {
                "status": "no_facts",
                "message": "No facts could be extracted from this statement.",
                "original_statement": statement
            }
        
        # Process and store each extracted fact
        stored_facts = {}
        audit_entries = []
        timestamp = datetime.now().isoformat()
        
        for fact in extracted_facts:
            raw_key = fact.get("key", "")
            value = fact.get("value", "")
            confidence = fact.get("confidence", "medium")
            
            if not raw_key or not value:
                continue
                
            # Normalize and handle collisions
            normalized_key = self._normalize_key(raw_key)
            final_key = self._handle_key_collision(normalized_key, existing_facts)
            
            # Validate the fact
            if not self._validate_fact(final_key, value):
                continue
            
            # Store the fact
            existing_facts[final_key] = {
                "value": value,
                "confidence": confidence,
                "timestamp": timestamp,
                "source_statement": statement,
                "original_key": raw_key
            }
            
            stored_facts[final_key] = value
            
            # Track key and audit
            if final_key not in profile["keys"]:
                profile["keys"].append(final_key)
            
            audit_entries.append({
                "action": "learned",
                "key": final_key,
                "value": value,
                "timestamp": timestamp,
                "source": statement
            })
        
        # Update audit trail
        profile["audit"].extend(audit_entries)
        
        if stored_facts:
            fact_summary = ", ".join([f"{k}='{v}'" for k, v in stored_facts.items()])
            return {
                "status": "learned",
                "message": f"Successfully learned: {fact_summary}",
                "extracted": stored_facts,
                "reasoning": extraction_result.get("reasoning", "")
            }
        else:
            return {
                "status": "validation_failed",
                "message": "Facts were extracted but failed validation.",
                "original_statement": statement
            }

    def _validate_fact(self, key: str, value: str) -> bool:
        """Validate that a fact is reasonable before storing."""
        # Basic validation rules
        if len(key) > 50 or len(value) > 200:
            return False
        
        # Avoid storing obviously invalid or harmful content
        invalid_patterns = [
            r'\b(password|secret|private|confidential)\b',
            r'\b(kill|murder|hate|death)\b',
            r'^\s*$'  # empty/whitespace only
        ]
        
        text_to_check = f"{key} {value}".lower()
        for pattern in invalid_patterns:
            if re.search(pattern, text_to_check):
                return False
        
        return True

    def list_known_facts(self, tool_context: ToolContext) -> Dict[str, Any]:
        """
        List all known facts about the represented person.

        Args:
            tool_context: ADK context for state access

        Returns:
            Dict with status, message, and facts summary
        """
        if "profile" not in tool_context.state:
            return {
                "status": "empty",
                "message": "No facts have been learned yet.",
                "facts": {}
            }
        
        profile = tool_context.state["profile"]
        facts = profile.get("facts", {})
        
        if not facts:
            return {
                "status": "empty",
                "message": "No facts stored in the profile.",
                "facts": {}
            }
        
        # Prepare readable summary
        fact_summary = {}
        for key, fact_data in facts.items():
            if isinstance(fact_data, dict):
                fact_summary[key] = {
                    "value": fact_data.get("value", ""),
                    "confidence": fact_data.get("confidence", "unknown"),
                    "learned": fact_data.get("timestamp", "unknown")
                }
            else:
                # Handle legacy format
                fact_summary[key] = {"value": str(fact_data), "confidence": "unknown", "learned": "legacy"}
        
        return {
            "status": "success",
            "message": f"Found {len(fact_summary)} facts about the person.",
            "facts": fact_summary,
            "fact_count": len(fact_summary)
        }

    async def search_facts(self, tool_context: ToolContext, query: str) -> Dict[str, Any]:
        """
        Search facts by query using semantic matching.

        Args:
            tool_context: ADK context for state access
            query: Search query (e.g., "work", "hobbies", "personal details")

        Returns:
            Dict with status, message, and matching facts
        """
        if not query or not query.strip():
            return {"status": "error", "message": "Please provide a search query."}
        
        if "profile" not in tool_context.state:
            return {
                "status": "empty",
                "message": "No facts available to search.",
                "matches": {}
            }
        
        profile = tool_context.state["profile"]
        facts = profile.get("facts", {})
        
        if not facts:
            return {
                "status": "empty", 
                "message": "No facts stored to search through.",
                "matches": {}
            }
        
        query = query.strip().lower()
        matches = {}
        
        # Simple keyword-based search (could be enhanced with LLM semantic matching)
        for key, fact_data in facts.items():
            if isinstance(fact_data, dict):
                value = fact_data.get("value", "")
                source = fact_data.get("source_statement", "")
            else:
                value = str(fact_data)
                source = ""
            
            # Check if query matches key, value, or source
            searchable_text = f"{key} {value} {source}".lower()
            if query in searchable_text or any(word in searchable_text for word in query.split()):
                matches[key] = {
                    "value": value,
                    "confidence": fact_data.get("confidence", "unknown") if isinstance(fact_data, dict) else "unknown",
                    "source": source
                }
        
        if matches:
            return {
                "status": "found",
                "message": f"Found {len(matches)} facts matching '{query}'.",
                "matches": matches,
                "query": query
            }
        else:
            return {
                "status": "not_found",
                "message": f"No facts found matching '{query}'.",
                "matches": {},
                "query": query
            }

    # ADK compatibility shim
    async def execute(self, tool_context: ToolContext, **kwargs) -> Dict[str, Any]:
        """Execute method for ADK compatibility."""
        method = kwargs.get("method", "learn_about_user")
        
        if method == "learn_about_user":
            statement = kwargs.get("statement", "")
            return await self.learn_about_user(tool_context, statement)
        elif method == "list_known_facts":
            return self.list_known_facts(tool_context)
        elif method == "search_facts":
            query = kwargs.get("query", "")
            return await self.search_facts(tool_context, query)
        else:
            return {"status": "error", "message": f"Unknown method: {method}"}
