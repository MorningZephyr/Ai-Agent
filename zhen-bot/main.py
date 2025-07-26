import asyncio
import warnings
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from agent import root_agent

load_dotenv()

# Suppress the ADK framework warning about non-text parts in responses
# This warning occurs when the agent uses tools and is expected behavior
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")

DB_URL = "sqlite:///./zhen_bot_memory.db"
session_service = DatabaseSessionService(db_url=DB_URL)

def initial_zhen_bot_state():
    return {
        "is_zhen": True  # Set to True when Zhen is using the bot, False for others
    }

async def call_agent_async(runner, user_id, session_id, query, session_service=None):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            # DEBUG: Show ALL events, not just final response (commented out for clean output)
            # print(f"\n📡 EVENT TYPE: {type(event).__name__}")
            # print(f"   Is final: {event.is_final_response()}")
            # 
            # # Check if this event has candidates (raw model response)
            # if hasattr(event, 'candidates'):
            #     print(f"   Has candidates: True")
            #     if event.candidates:
            #         for i, candidate in enumerate(event.candidates):
            #             print(f"   Candidate {i} content parts:")
            #             if hasattr(candidate, 'content') and candidate.content:
            #                 print(f"     {candidate.content.parts}")
            # else:
            #     print(f"   Has candidates: False")
            
            if event.is_final_response():
                if event.content and event.content.parts:
                    # DEBUG: Show the raw parts (commented out for clean output)
                    # print(f"\n🔍 FINAL event.content.parts:")
                    # print(event.content.parts)
                    
                    # DEBUG: Check session state (commented out for clean output) 
                    # print("🔧 DEBUG: About to check session state...")
                    # if session_service:
                    #     try:
                    #         print("🔧 DEBUG: session_service exists, calling get_session...")
                    #         current_session = await session_service.get_session(
                    #             app_name="Zhen Bot",
                    #             user_id=user_id, 
                    #             session_id=session_id
                    #         )
                    #         print(f"\n💾 CURRENT SESSION STATE:")
                    #         print(f"   {current_session.state}")
                    #     except Exception as e:
                    #         print(f"   ❌ Could not retrieve session state: {e}")
                    # else:
                    #     print("🔧 DEBUG: session_service is None!")
                    
                    # Handle responses that may contain both text and function calls
                    text_parts = []
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    
                    if text_parts:
                        response_text = ' '.join(text_parts)
                        print(f"Zhen-Bot: {response_text}")
                    else:
                        # If no text parts, the agent might have only made tool calls
                        print("Zhen-Bot: [Processing your request...]")
                        
    except Exception as e:
        print(f"Error: {e}")

async def main_async():
    APP_NAME = "Zhen Bot"
    USER_ID = "zhen"
    try:
        existing_sessions = await session_service.list_sessions(
            app_name=APP_NAME,
            user_id=USER_ID,
        )
        print(f"Existing sessions: {existing_sessions}")
        if existing_sessions and len(existing_sessions.sessions) > 0:
            print(f"Found existing session: {existing_sessions.sessions[0].id}")
            SESSION_ID = existing_sessions.sessions[0].id
        else:
            print("No existing session found, creating new session")
            initial_state = initial_zhen_bot_state()
            new_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                state=initial_state,
            )
            SESSION_ID = new_session.id
    except Exception as e:
        print(f"Session error: {e}")
        return
    
    # Get the current session state to check the mode
    try:
        current_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        is_zhen = current_session.state.get("is_zhen", False)
        
        if is_zhen:
            mode_message = "Learning mode enabled (you can teach me about Zhen)"
        else:
            mode_message = "Sharing mode enabled (I can answer questions about Zhen)"
            
    except Exception as e:
        print(f"Could not determine mode: {e}")
        mode_message = "Mode unknown"
    
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    print("Type your message (or 'exit' to quit):")
    print(f"Note: {mode_message}")
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print("Goodbye!")
                break
            if not user_input:
                continue
            await call_agent_async(runner, USER_ID, SESSION_ID, user_input, session_service)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 