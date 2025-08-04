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

# Database configuration
DB_URL = "sqlite:///./zhen_bot_test.db"

def learn_about_zhen(key: str, value: str, tool_context: ToolContext) -> dict:
    """Learn and store information about Zhen."""
    is_zhen = tool_context.state.get("is_zhen", False)
    
    if not is_zhen:
        return {
            "status": "unauthorized",
            "message": "I can only learn about Zhen when talking to Zhen directly."
        }
    
    old_value = tool_context.state.get(key)
    tool_context.state[key] = value
    
    is_update = old_value is not None
    message = f"{'Updated' if is_update else 'Learned'}: {key.replace('_', ' ')} = '{value}'"
    if is_update:
        message += f" (was: '{old_value}')"
    
    return {
        "status": "learned" if not is_update else "updated",
        "message": message
    }

def get_zhen_info(key: str, tool_context: ToolContext) -> dict:
    """Get information about Zhen."""
    value = tool_context.state.get(key)
    
    if value:
        return {
            "status": "found",
            "message": f"Zhen's {key.replace('_', ' ')}: {value}"
        }
    else:
        return {
            "status": "not_found",
            "message": f"I don't know Zhen's {key.replace('_', ' ')} yet."
        }

# Create the Zhen Bot agent
zhen_bot = Agent(
    name="zhen_bot",
    model="gemini-2.0-flash",
    description="Zhen-Bot is a digital representative of Zhen.",
    instruction="""
    You are Zhen-Bot, a digital representative of Zhen.
    
    When is_zhen=True in the session state:
    - You're talking to the real Zhen
    - Learn facts about him using learn_about_zhen(key, value)
    - Be conversational and ask follow-up questions
    
    When is_zhen=False:
    - You're talking to someone else about Zhen
    - Share what you know using get_zhen_info(key)
    - Be helpful but maintain privacy
    
    Be natural, friendly, and conversational.
    """,
    tools=[learn_about_zhen, get_zhen_info]
)

def initial_state(is_zhen: bool = True):
    """Create initial session state."""
    return {
        "is_zhen": is_zhen,
        "session_created": True
    }

async def chat_with_bot(runner, user_id, session_id, message, session_service=None):
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
    """Main test function."""
    print("🚀 Starting Zhen-Bot Test Environment...")
    
    # Initialize session service
    try:
        session_service = DatabaseSessionService(db_url=DB_URL)
        print("✅ Database session service created")
    except Exception as e:
        print(f"❌ Error creating session service: {e}")
        return
    
    APP_NAME = "Zhen Bot Test"
    USER_ID = "test_user"
    
    # Create or get session
    try:
        # Try to get existing sessions
        existing_sessions = session_service.list_sessions(
            app_name=APP_NAME,
            user_id=USER_ID
        )
        
        if hasattr(existing_sessions, 'sessions') and existing_sessions.sessions:
            session_id = existing_sessions.sessions[0].id
            print(f"✅ Using existing session: {session_id}")
        else:
            # Create new session
            initial_session_state = initial_state(is_zhen=True)  # Start in learning mode
            new_session = session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                state=initial_session_state
            )
            session_id = new_session.id
            print(f"✅ Created new session: {session_id}")
            
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
    print("\n💬 Starting test conversation...")
    print("📝 Note: Bot is in learning mode (is_zhen=True)")
    print("Type 'exit' to quit, 'mode' to toggle learning/sharing mode\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() == 'mode':
                # Toggle mode
                try:
                    session = session_service.get_session(APP_NAME, USER_ID, session_id)
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
            await chat_with_bot(runner, USER_ID, session_id, user_input, session_service)
            
        except KeyboardInterrupt:
            print("\n� Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("🧪 Zhen-Bot Backend Test")
    print("=" * 40)
    asyncio.run(main())
