from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
# from question_answering_agent import question_answering_agent
from dotenv import load_dotenv
import asyncio
load_dotenv()

async def main():
    session_service_stateful = InMemorySessionService()

    intial_state = {
        "user_name" : "Red",
        "user_preference": """
            I like basketball.
            My favorite food is sushi.
            My favorite instrument is piano.
        """
    }
    question_answering_agent = Agent(
    name="question_answering_agent",
    model="gemini-2.0-flash",
    description="Question answering agent",
    instruction="""
        You are a helpful assistant that answers questions about the user's preferences.

        Here is some information about the user:
        Name: {user_name}
        Preferences: {user_preference}
        """
    )

    APP_NAME = "Zephyr Bot"
    USER_ID = "Zephyr123"
    SESSION_ID = "001"

    # --- Create a session ---
    stateful_session = await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=intial_state
    )
    print("New session created")

    # --- Runner ---
    runner = Runner(
        app_name=APP_NAME,
        agent=question_answering_agent,
        session_service=session_service_stateful
    )

    # --- Making a message object for query the agent ---
    new_message = types.Content(
        role="user", parts=[types.Part(text="What is Red's favorite food")]
    )

    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final response: {event.content.parts[0].text}")

    print("==== Session Event Exploration ====")
    session = await session_service_stateful.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("Final session state: ")
    for key, value in session.state.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())