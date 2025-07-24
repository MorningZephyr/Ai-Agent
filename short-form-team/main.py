from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .script_agent.agent import script_agent
import asyncio
import dotenv

dotenv.load_dotenv()

script_agent = Agent(
    name="script_agent",
    description="An agent that can write scripts based on user what user describes.",
    instruction="""
        You are a script writing agent. Your task is to write scripts based on the user's description.
        Make it interesting and engaging. The script should be well-structured and easy to follow.
        Make sure it's not too long, because it's meant for a short-form video. 

        IMPORTANT:
        - You should have a strong opening hook to grab the viewer's attention.
        - If the user greets you, respond with a friendly greeting, you don't need to write a script in this case.
        - Otherwise, your response output should just be the script, without any additional text or explanation, UNLESS the user specifically asks for an explanation or additional context, in which case you can provide a brief summary or context.
        - The script should be concise, ideally under 300 words, to fit the short-form video format.
        - If user asks anything that is not related to script writing, politely inform them that you are only capable of writing scripts.
        """
)

async def main():

    pass
   



if __name__ == "__main__":    
    asyncio.run(main())