from google.adk.agents import Agent

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="An agent that greets users.",
    instruction="You are a friendly assistant that greets users."
                "Ask for the user's name and then greet them by name",
)
