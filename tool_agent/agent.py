from google.adk.agents import Agent
from google.adk.tools import google_search
from datetime import datetime
## Tip:
##      - The return should be as specific as possible so ADK knows what the return 
##          stuff is. Default is {"Result": val}, so it's not very specific. 
##      - You can only use 1 built-in google functions. CANT USE built-in along with custom functions.
def get_current_time() -> dict:
    """Get the current time in the format YYYY-MM-DD HH:MM:SS"""

    return {
        "current_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash",
    description="A tool agent. ",
    instruction="You are an agent with the following tools:" 
                # "- google_search" 
                "- get_current_time",
    tools=[
        # google_search,
        get_current_time
    ]
)
