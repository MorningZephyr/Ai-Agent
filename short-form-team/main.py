from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from .script_agent.agent import script_agent
import asyncio
import dotenv

dotenv.load_dotenv()

 # --- Create Database if not already exist ---
db_url = "sqlite:///script.db"
session_service =  DatabaseSessionService(db_url=db_url)



async def main():
    pass
   



if __name__ == "__main__":    
    asyncio.run(main())