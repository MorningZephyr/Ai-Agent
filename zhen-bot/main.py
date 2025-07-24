import asyncio
import uuid

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from agent import root_agent

load_dotenv()

# ===== PERSISTENT STORAGE SETUP =====
# Using SQLite database for persistent storage
DB_URL = "sqlite:///./zhen_bot_memory.db"
session_service = DatabaseSessionService(db_url=DB_URL)

# ===== INITIAL STATE SETUP =====
def initialize_zhen_bot_state():
    """Initialize the session state with default values for Zhen Bot."""
    return {
        "user_name": "Zhen",
        "knowledge_base": {},
        "user_preferences": {},
        "personal_context": {},
        "conversation_memory": [],
        "interaction_count": 0,
        "first_interaction_date": None
    }

async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    
    print(f"\n🤖 Processing: {query}")
    print("-" * 50)
    
    final_response_text = None
    
    try:
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                    print(f"🎯 Zhen Bot: {final_response_text}")
                    
    except Exception as e:
        print(f"❌ Error during agent run: {e}")
        
    return final_response_text

def display_session_summary(session_service, app_name, user_id, session_id):
    """Display a summary of what the bot has learned."""
    try:
        session = session_service.get_session(
            app_name=app_name, 
            user_id=user_id, 
            session_id=session_id
        )
        
        state = session.state
        knowledge_base = state.get("knowledge_base", {})
        preferences = state.get("user_preferences", {})
        conversation_memory = state.get("conversation_memory", [])
        interaction_count = state.get("interaction_count", 0)
        
        print("\n" + "="*60)
        print("📊 ZHEN BOT LEARNING SUMMARY")
        print("="*60)
        print(f"💬 Total Interactions: {interaction_count}")
        print(f"🧠 Knowledge Categories: {len(knowledge_base)}")
        print(f"⚙️  Preferences Learned: {len(preferences)}")
        print(f"📝 Conversations Remembered: {len(conversation_memory)}")
        
        if knowledge_base:
            print(f"\n🔍 Knowledge Categories:")
            for category, facts in knowledge_base.items():
                print(f"   • {category}: {len(facts)} facts")
                
        if preferences:
            print(f"\n⭐ Preferences Set:")
            for pref_type, pref_data in preferences.items():
                value = pref_data.get('value', 'Unknown') if isinstance(pref_data, dict) else pref_data
                print(f"   • {pref_type}: {value}")
                
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error displaying summary: {e}")

async def main_async():
    # Setup constants
    APP_NAME = "Zhen Bot"
    USER_ID = "zhen"
    
    print("🚀 Starting Zhen Bot - Your Personal Learning AI Assistant")
    print("="*60)
    
    # ===== SESSION MANAGEMENT =====
    # Check for existing sessions for this user
    try:
        existing_sessions = session_service.list_sessions(
            app_name=APP_NAME,
            user_id=USER_ID,
        )
        
        # If there's an existing session, use it, otherwise create a new one
        if existing_sessions and len(existing_sessions.sessions) > 0:
            # Use the most recent session
            SESSION_ID = existing_sessions.sessions[0].id
            print(f"📚 Continuing existing session: {SESSION_ID}")
            print("🧠 I remember our previous conversations!")
        else:
            # Create a new session with initial state
            initial_state = initialize_zhen_bot_state()
            new_session = session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                state=initial_state,
            )
            SESSION_ID = new_session.id
            print(f"✨ Created new session: {SESSION_ID}")
            print("👋 Nice to meet you! I'm here to learn about you and become your personalized assistant.")
            
    except Exception as e:
        print(f"❌ Error with session management: {e}")
        # Fallback to new session
        SESSION_ID = str(uuid.uuid4())
        initial_state = initialize_zhen_bot_state()
        session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
            state=initial_state,
        )
        print(f"🔄 Created fallback session: {SESSION_ID}")

    # ===== AGENT RUNNER SETUP =====
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ===== INTERACTIVE CONVERSATION LOOP =====
    print("\n💡 Tips:")
    print("   • Share your interests, preferences, and current projects")
    print("   • I'll remember everything and become more personalized over time")
    print("   • Type 'summary' to see what I've learned about you")
    print("   • Type 'exit' or 'quit' to end our conversation")
    print("\n" + "-"*60)

    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()

            # Check for special commands
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print("\n👋 Thanks for chatting! I'll remember everything for next time.")
                display_session_summary(session_service, APP_NAME, USER_ID, SESSION_ID)
                break
                
            elif user_input.lower() == "summary":
                display_session_summary(session_service, APP_NAME, USER_ID, SESSION_ID)
                continue
                
            elif user_input.lower() in ["help", "commands"]:
                print("\n🔧 Available Commands:")
                print("   • 'summary' - See what I've learned about you")
                print("   • 'exit', 'quit', 'bye' - End the conversation")
                print("   • 'help', 'commands' - Show this help message")
                print("   • Just chat normally and I'll learn from our conversation!")
                continue
                
            elif not user_input:
                print("   (Please type something to continue our conversation)")
                continue

            # Update interaction count
            try:
                session = session_service.get_session(
                    app_name=APP_NAME, 
                    user_id=USER_ID, 
                    session_id=SESSION_ID
                )
                current_count = session.state.get("interaction_count", 0)
                updated_state = session.state.copy()
                updated_state["interaction_count"] = current_count + 1
                
                # Set first interaction date if not set
                if not updated_state.get("first_interaction_date"):
                    from datetime import datetime
                    updated_state["first_interaction_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    state=updated_state,
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not update interaction count: {e}")

            # Process the user query through the agent
            await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

        except KeyboardInterrupt:
            print("\n\n👋 Conversation interrupted. I'll remember everything for next time!")
            display_session_summary(session_service, APP_NAME, USER_ID, SESSION_ID)
            break
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            print("💪 But don't worry, I'll keep trying to help you!")

def main():
    """Main entry point for the Zhen Bot."""
    try:
        asyncio.run(main_async())
    except Exception as e:
        print(f"❌ Failed to start Zhen Bot: {e}")
        print("🔧 Please check your setup and try again.")

if __name__ == "__main__":
    main() 