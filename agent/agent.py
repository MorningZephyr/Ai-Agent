from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Setting agent model
AGENT_MODEL = 'ollama/phi3:latest'

root_agent = Agent(
    name="pirate_agent",
    model= LiteLlm(model=AGENT_MODEL),
    description="Acts like a pirate",
    instruction="You are a pirate called Deez Nutz, you'll act as a pirate, including personality"
)
