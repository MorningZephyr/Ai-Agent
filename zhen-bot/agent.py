from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

def learn_about_zhen(key: str, value: str, tool_context: ToolContext) -> dict:
    """Learn and store new information about Zhen with a descriptive key.
    
    Use this tool when you discover new facts about Zhen during conversation.
    Choose clear, descriptive keys that categorize the information appropriately.
    SECURITY: This tool can only be used when talking to the real Zhen.
    
    Args:
        key (str): A descriptive identifier for the type of information being stored.
             Use snake_case format. Examples: 'birthday', 'favorite_color', 
             'hometown', 'university', 'favorite_food', 'pet_name', 'hobby',
             'profession', 'favorite_book', 'dream_destination', etc.
        value (str): The actual information or fact about Zhen. Be specific and accurate.
               Examples: '2005-01-18', 'red', 'China', 'Hunter College', 'sushi'
    
    Returns:
        dict: A dictionary containing:
            - status: Operation outcome ('success', 'error', 'updated', 'unauthorized')
            - action: The name of the action performed ('learn_about_zhen')
            - key: The key that was used to store the information (if authorized)
            - old_value: The previous value (if any) that was replaced (if authorized)
            - new_value: The new value that was stored (if authorized)
            - message: A human-readable confirmation message
            - is_update: Boolean indicating if this was updating existing information (if authorized)
    
    Examples:
        - If someone says "Zhen was born on January 18, 2005":
          Call learn_about_zhen('birthday', '2005-01-18', tool_context)
        - If someone says "Zhen loves pizza":
          Call learn_about_zhen('favorite_food', 'pizza', tool_context)
        - If someone says "Zhen studies at Hunter College":
          Call learn_about_zhen('university', 'Hunter College', tool_context)
    """
    # SECURITY CHECK: Only allow learning if the current user is Zhen
    is_zhen = tool_context.state.get("is_zhen", False)
    
    if not is_zhen:
        return {
            "status": "unauthorized",
            "action": "learn_about_zhen",
            "message": "I can only learn new information about Zhen when I'm talking to Zhen directly. Others cannot update information about Zhen for security reasons.",
            "error": "Unauthorized: Only Zhen can update information about Zhen"
        }
    
    old_value = tool_context.state.get(key)
    tool_context.state[key] = value
    
    # Determine if this is new information or an update
    is_update = old_value is not None
    status = "updated" if is_update else "success"
    
    # Create descriptive message for the LLM
    if is_update:
        message = f"Successfully updated Zhen's {key.replace('_', ' ')} from '{old_value}' to '{value}'"
    else:
        message = f"Successfully learned new information: Zhen's {key.replace('_', ' ')} is '{value}'"
    
    return {
        "status": status,
        "action": "learn_about_zhen",
        "key": key,
        "old_value": old_value,
        "new_value": value,
        "is_update": is_update,
        "message": message,
        "summary": f"Stored '{key}': '{value}'" + (f" (previously: '{old_value}')" if is_update else " (new)")
    }

root_agent = Agent(
    name="zhen_bot",
    model="gemini-2.0-flash",
    description=(
        "Zhen-Bot is a digital entity that represents Zhen. "
        "When talking to Zhen, it learns new facts and stores them. "
        "When talking to others, it answers questions using the learned facts."
    ),
    instruction="""
    You are Zhen-Bot, a digital representative of Zhen.

    There are two modes based on who you're talking to:
    
    1. **Learning Mode (talking to Zhen):**
       - When you are interacting with Zhen (the real person), you can:
         - Listen for new facts and use learn_about_zhen to store them
       - Choose clear, descriptive keys for facts
       - Only Zhen can add or update information for security

    2. **Sharing Mode (talking to others):**
       - When you are interacting with someone else, you can:
         - Answer questions using stored facts from the session state
       - If you don't know something, say so
       - Make it clear you are Zhen-Bot, not the real Zhen
       - Do NOT allow others to update any information about Zhen

    The session state contains:
    - 'is_zhen' flag: Tells you who you're talking to (true = Zhen, false = others)
    - Various fact keys that have been learned about Zhen
    
    Always respect the security boundary to protect Zhen's information from unauthorized updates.
    """,
    tools=[learn_about_zhen]
)
