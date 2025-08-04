import asyncio
import warnings
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Load environment variables
load_dotenv()

# Suppress ADK framework warnings
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")

# Database configuration for persistence
DB_URL = "sqlite:///./zhen_bot_memory.db"

def learn_about_zhen(key: str, value: str, tool_context: ToolContext) -> dict:
    """Learn and store information about Zhen with session persistence."""
    
    # Check if we're in learning mode
    is_zhen = tool_context.state.get("is_zhen", False)
    
    if not is_zhen:
        return {
            "status": "unauthorized",
            "message": "I can only learn about Zhen when talking to Zhen directly. Switch to learning mode first."
        }
    
    # Get the old value if it exists
    old_value = tool_context.state.get(key)
    
    # Store the new information in session state (this persists with DatabaseSessionService!)
    tool_context.state[key] = value
    
    # Create response message
    is_update = old_value is not None
    if is_update:
        message = f"Updated: {key.replace('_', ' ')} = '{value}' (was: '{old_value}')"
        status = "updated"
    else:
        message = f"Learned: {key.replace('_', ' ')} = '{value}'"
        status = "learned"
    
    return {
        "status": status,
        "message": message,
        "key": key,
        "value": value,
        "previous_value": old_value
    }

def get_zhen_info(key: str, tool_context: ToolContext) -> dict:
    """Get information about Zhen from persistent session state."""
    
    # Access the session state to retrieve information
    value = tool_context.state.get(key)
    
    if value:
        return {
            "status": "found",
            "message": f"Zhen's {key.replace('_', ' ')}: {value}",
            "key": key,
            "value": value
        }
    else:
        return {
            "status": "not_found",
            "message": f"I don't know Zhen's {key.replace('_', ' ')} yet. You can teach me by saying something like 'My {key.replace('_', ' ')} is ...'",
            "key": key
        }

def list_known_facts(tool_context: ToolContext) -> dict:
    """List all known facts about Zhen from session state."""
    
    # Get all non-system keys from state
    facts = {}
    system_keys = {"is_zhen", "name", "session_created"}
    
    for key, value in tool_context.state.items():
        if key not in system_keys:
            facts[key.replace('_', ' ')] = value
    
    if facts:
        fact_list = "\n".join([f"- {key}: {value}" for key, value in facts.items()])
        return {
            "status": "found",
            "message": f"Here's what I know about Zhen:\n{fact_list}",
            "facts": facts
        }
    else:
        return {
            "status": "empty",
            "message": "I don't have any specific facts about Zhen yet. Start teaching me!",
            "facts": {}
        }

# Create the Zhen Bot agent with enhanced tools
zhen_bot = Agent(
    name="zhen_bot",
    model="gemini-2.0-flash",
    description="Zhen-Bot is a digital representative of Zhen with persistent memory.",
    instruction="""
    You are Zhen-Bot, a digital representative of Zhen with persistent memory.
    
    IMPORTANT: When someone tells you facts about Zhen, use learn_about_zhen to store them.
    
    Available tools:
    - learn_about_zhen(key, value): Store facts about Zhen (only when is_zhen=True)
    - get_zhen_info(key): Retrieve specific facts about Zhen
    - list_known_facts(): Show all known facts about Zhen
    
    When is_zhen=True: You're talking to the real Zhen - learn and store facts
    When is_zhen=False: You're sharing what you know about Zhen with others
    
    Be natural, friendly, and conversational. When learning, ask follow-up questions!
    """,
    tools=[learn_about_zhen, get_zhen_info, list_known_facts]
)

def initial_state(is_zhen: bool = True):
    """Create initial session state."""
    return {
        "is_zhen": is_zhen,
        "name": "Zhen", 
        "session_created": True
    }

async def chat_with_bot(runner, user_id, session_id, message):
    """Send a message to the bot and get response."""
    content = types.Content(role="user", parts=[types.Part(text=message)])
    
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    text_parts = []
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    
                    if text_parts:
                        response_text = ' '.join(text_parts)
                        print(f"Zhen-Bot: {response_text}")
                        return response_text
                    else:
                        print("Zhen-Bot: [Processing...]")
                        return "[Processing...]"
                        
    except Exception as e:
        error_msg = f"Error: {e}"
        print(error_msg)
        return error_msg

async def main():
    """Main test function with persistent database session."""
    print("🚀 Starting Zhen-Bot Test Environment with Persistent Memory...")
    
    # Initialize database session service for persistence
    try:
        session_service = DatabaseSessionService(db_url=DB_URL)
        print("✅ Database session service created - data will persist!")
        print(f"📄 Database: {DB_URL}")
    except Exception as e:
        print(f"❌ Error creating session service: {e}")
        return
    
    APP_NAME = "Zhen Bot"
    USER_ID = "zhen"
    
    # Create or get session (DatabaseSessionService - some methods might not be truly async in this version)
    try:
        # Try to get existing sessions  
        existing_sessions = session_service.list_sessions(
            app_name=APP_NAME,
            user_id=USER_ID
        )
        
        if existing_sessions.sessions:
            session_id = existing_sessions.sessions[0].id
            print(f"✅ Using existing session: {session_id}")
            
            # Show what we already know
            session = session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID, 
                session_id=session_id
            )
            if session and session.state:
                facts_count = len([k for k in session.state.keys() if k not in {"is_zhen", "name", "session_created"}])
                print(f"📚 Found {facts_count} stored facts about Zhen")
        else:
            # Create new session
            initial_session_state = initial_state(is_zhen=True)
            new_session = session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                state=initial_session_state
            )
            session_id = new_session.id
            print(f"✅ Created new session: {session_id}")
            print("📚 Starting with fresh memory")
            
    except Exception as e:
        print(f"❌ Session error: {e}")
        return
    
    # Create runner
    try:
        runner = Runner(
            agent=zhen_bot,
            app_name=APP_NAME,
            session_service=session_service
        )
        print("✅ Runner created successfully")
    except Exception as e:
        print(f"❌ Error creating runner: {e}")
        return
    
    # Test conversation
    print("\n💬 Starting persistent conversation...")
    print("📝 Type your message and press Enter")
    print("💡 Try: 'My favorite color is blue' or 'list what you know about me'")
    print("🔄 Type 'mode' to toggle between learning/sharing mode")
    print("🚪 Type 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye! Your data is saved and will be here next time.")
                break
                
            if user_input.lower() == 'mode':
                # Toggle mode
                try:
                    session = session_service.get_session(
                        app_name=APP_NAME,
                        user_id=USER_ID,
                        session_id=session_id
                    )
                    current_mode = session.state.get("is_zhen", True)
                    new_mode = not current_mode
                    session.state["is_zhen"] = new_mode
                    session_service.update_session(session)
                    
                    mode_name = "Learning (Zhen)" if new_mode else "Sharing (Others)"
                    print(f"🔄 Switched to {mode_name} mode")
                    continue
                except Exception as e:
                    print(f"❌ Error switching mode: {e}")
                    continue
            
            if not user_input:
                continue
                
            # Send message to bot
            await chat_with_bot(runner, USER_ID, session_id, user_input)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Your data is saved and will be here next time.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("🧪 Zhen-Bot ADK Testing")
    print("=" * 30)
    asyncio.run(main())
