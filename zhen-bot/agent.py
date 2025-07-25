from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from datetime import datetime
import json

CONFIRMATION_KEY = "pending_learning_action"


def _ask_for_confirmation(action_type, data, tool_context, prompt):
    # Store the pending action in state
    tool_context.state[CONFIRMATION_KEY] = {
        "action_type": action_type,
        "data": data,
        "prompt": prompt,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return {
        "action": "ask_confirmation",
        "message": prompt,
        "pending_action": tool_context.state[CONFIRMATION_KEY]
    }

def _check_confirmation(tool_context):
    # Check if the user has confirmed a pending action
    confirm = tool_context.input_state.get("confirm_learning", None)
    return confirm is True

def _clear_pending(tool_context):
    if CONFIRMATION_KEY in tool_context.state:
        del tool_context.state[CONFIRMATION_KEY]


def learn_about_user(information: str, category: str, tool_context: ToolContext) -> dict:
    """Learn and store new information about the user, with confirmation."""
    # If confirmation is not present, ask for it
    if not _check_confirmation(tool_context):
        prompt = f"Do you want me to remember this about you: '{information}' (category: {category})? Please reply with 'yes' to confirm."
        return _ask_for_confirmation("learn_about_user", {"information": information, "category": category}, tool_context, prompt)

    # If confirmed, perform the learning
    knowledge_base = tool_context.state.get("knowledge_base", {})
    if category not in knowledge_base:
        knowledge_base[category] = []
    new_entry = {
        "information": information,
        "learned_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "confidence": 1.0
    }
    knowledge_base[category].append(new_entry)
    tool_context.state["knowledge_base"] = knowledge_base
    _clear_pending(tool_context)
    return {
        "action": "learn_about_user",
        "category": category,
        "information": information,
        "message": f"I've learned that {information} (category: {category})"
    }


def update_user_preference(preference_type: str, preference_value: str, tool_context: ToolContext) -> dict:
    """Update or add a user preference, with confirmation."""
    if not _check_confirmation(tool_context):
        prompt = f"Do you want me to remember your preference: {preference_type} = {preference_value}? Please reply with 'yes' to confirm."
        return _ask_for_confirmation("update_user_preference", {"preference_type": preference_type, "preference_value": preference_value}, tool_context, prompt)

    preferences = tool_context.state.get("user_preferences", {})
    old_value = preferences.get(preference_type, "not set")
    preferences[preference_type] = {
        "value": preference_value,
        "updated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tool_context.state["user_preferences"] = preferences
    _clear_pending(tool_context)
    return {
        "action": "update_preference",
        "preference_type": preference_type,
        "old_value": old_value,
        "new_value": preference_value,
        "message": f"Updated your {preference_type} preference to: {preference_value}"
    }


def remember_conversation_topic(topic: str, key_points: str, tool_context: ToolContext) -> dict:
    """Remember important topics and key points from our conversations, with confirmation."""
    if not _check_confirmation(tool_context):
        prompt = f"Do you want me to remember our conversation about '{topic}'? Please reply with 'yes' to confirm."
        return _ask_for_confirmation("remember_conversation_topic", {"topic": topic, "key_points": key_points}, tool_context, prompt)

    conversation_memory = tool_context.state.get("conversation_memory", [])
    memory_entry = {
        "topic": topic,
        "key_points": key_points,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_context": len(conversation_memory) + 1
    }
    conversation_memory.append(memory_entry)
    if len(conversation_memory) > 50:
        conversation_memory = conversation_memory[-50:]
    tool_context.state["conversation_memory"] = conversation_memory
    _clear_pending(tool_context)
    return {
        "action": "remember_conversation",
        "topic": topic,
        "key_points": key_points,
        "message": f"I've remembered our conversation about {topic}"
    }


def update_personal_context(context_type: str, context_value: str, tool_context: ToolContext) -> dict:
    """Update personal context information about the user, with confirmation."""
    if not _check_confirmation(tool_context):
        prompt = f"Do you want me to remember your {context_type}: {context_value}? Please reply with 'yes' to confirm."
        return _ask_for_confirmation("update_personal_context", {"context_type": context_type, "context_value": context_value}, tool_context, prompt)

    personal_context = tool_context.state.get("personal_context", {})
    personal_context[context_type] = {
        "value": context_value,
        "updated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tool_context.state["personal_context"] = personal_context
    _clear_pending(tool_context)
    return {
        "action": "update_context",
        "context_type": context_type,
        "context_value": context_value,
        "message": f"Updated your {context_type}: {context_value}"
    }


def get_my_knowledge_summary(tool_context: ToolContext) -> dict:
    """Get a summary of what I know about the user."""
    knowledge_base = tool_context.state.get("knowledge_base", {})
    preferences = tool_context.state.get("user_preferences", {})
    personal_context = tool_context.state.get("personal_context", {})
    conversation_memory = tool_context.state.get("conversation_memory", [])
    summary = {
        "knowledge_categories": list(knowledge_base.keys()),
        "total_facts_learned": sum(len(facts) for facts in knowledge_base.values()),
        "preferences_set": list(preferences.keys()),
        "current_context": list(personal_context.keys()),
        "conversation_topics_remembered": len(conversation_memory),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return {
        "action": "knowledge_summary",
        "summary": summary,
        "message": "Here's a summary of what I know about you"
    }


# Create the Zhen Bot agent
root_agent = Agent(
    name="zhen_bot",
    model="gemini-2.0-flash",
    description="A personalized AI assistant that learns and adapts to represent Zhen through interactions",
    instruction="""
    You are Zhen Bot, a personalized AI assistant designed to learn about and represent Zhen through your interactions.
    Your primary goal is to become increasingly personalized and helpful by learning from every conversation.

    **Current Knowledge About Zhen:**
    
    **User Preferences:**
    {user_preferences}
    
    **Knowledge Base:**
    {knowledge_base}
    
    **Personal Context:**
    {personal_context}
    
    **Recent Conversation Memory:**
    {conversation_memory}

    **Core Capabilities:**

    1. **Active Learning**: Continuously learn from conversations by:
       - Picking up on preferences, interests, and personality traits
       - Remembering important personal information
       - Understanding communication style preferences
       - Learning about current projects, goals, and challenges

    2. **Adaptive Personality**: 
       - Mirror Zhen's communication style over time
       - Adapt your responses based on learned preferences
       - Become more familiar and personalized with each interaction

    3. **Contextual Memory**:
       - Remember previous conversations and their context
       - Build upon past discussions
       - Reference relevant past interactions when appropriate

    4. **Proactive Learning**:
       - Ask clarifying questions to learn more when appropriate
       - Suggest ways to be more helpful based on what you know
       - Use tools to store and organize learned information

    **Learning Guidelines:**

    1. **When to Use Learning Tools:**
       - Use `learn_about_user` for factual information about Zhen (interests, background, experiences)
       - Use `update_user_preference` for specific preferences (communication style, tools, approaches)
       - Use `remember_conversation_topic` for important discussion topics and their key points
       - Use `update_personal_context` for current situation, projects, mood, goals

    2. **What to Learn:**
       - Professional background and expertise
       - Interests and hobbies
       - Communication preferences
       - Current projects and goals
       - Problem-solving approaches
       - Personality traits and values
       - Favorite tools, technologies, or methods

    3. **How to Learn:**
       - Listen actively to what Zhen shares
       - Ask follow-up questions naturally in conversation
       - Notice patterns in communication style and preferences
       - Remember context from previous conversations

    **Interaction Style:**
    - Be genuinely curious about Zhen as a person
    - Ask thoughtful follow-up questions
    - Reference past conversations when relevant
    - Adapt your communication style to match preferences
    - Be proactive in offering help based on what you know
    - Show that you remember and care about Zhen's interests and goals

    **Important Notes:**
    - ALWAYS use the learning tools when you discover new information about Zhen
    - Be natural and conversational - don't make learning feel mechanical
    - Respect privacy - only learn what Zhen willingly shares
    - Use learned information to provide increasingly personalized assistance
    - Build genuine rapport through consistent memory and personalization

    Your ultimate goal is to become the most helpful, personalized AI assistant for Zhen by truly understanding their preferences, style, and needs through active learning and adaptation.
    """,
    tools=[
        learn_about_user,
        update_user_preference,
        remember_conversation_topic,
        update_personal_context,
        get_my_knowledge_summary
    ]
)
