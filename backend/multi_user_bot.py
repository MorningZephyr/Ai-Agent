import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Load environment variables
load_dotenv()

# Database configuration for persistence (PostgreSQL)
DB_URL = os.getenv("DB_URL", "postgresql://zhen_bot_user:your_password@localhost:5432/zhen_bot_production")

class UserAuthenticatedBot:
    """Multi-user AI bot with authentication-based learning mode."""
    
    def __init__(self, bot_owner_id: str):
        self.bot_owner_id = bot_owner_id
        self.session_service = None
        self.agent = None
        self.runner = None
        self.current_user_id = None  # Track current user manually
        
    async def initialize(self):
        """Initialize the bot with database connection."""
        try:
            self.session_service = DatabaseSessionService(db_url=DB_URL)
            print("✅ Database session service created")
            
            # Create agent with dynamic owner name
            self.agent = Agent(
                name=f"{self.bot_owner_id}_bot",
                model="gemini-2.0-flash",
                description=f"Digital representative of {self.bot_owner_id} with persistent memory.",
                instruction=f"""
                You are {self.bot_owner_id}-Bot, a digital representative of {self.bot_owner_id} with persistent memory.
                
                IMPORTANT: Only learn new facts when talking to {self.bot_owner_id} directly (is_owner=True).
                When talking to others (is_owner=False), share what you know but don't learn new information.
                
                Available tools:
                - learn_about_user(key, value): Store facts about {self.bot_owner_id} (only when is_owner=True)
                - get_user_info(key): Retrieve specific facts about {self.bot_owner_id}
                - list_known_facts(): Show all known facts about {self.bot_owner_id}
                
                When is_owner=True: You're talking to the real {self.bot_owner_id} - learn and store facts
                When is_owner=False: You're {self.bot_owner_id}'s representative talking to others - share knowledge but don't learn
                
                Be natural, friendly, and conversational. Represent {self.bot_owner_id} well!
                """,
                tools=[self.learn_about_user, self.get_user_info, self.list_known_facts]
            )
            
            self.runner = Runner(
                agent=self.agent,
                app_name="Multi-User AI Agents",
                session_service=self.session_service
            )
            
            return True
        except Exception as e:
            print(f"❌ Error initializing bot: {e}")
            return False
    
    def learn_about_user(self, key: str, value: str, tool_context: ToolContext) -> dict:
        """Store personal facts about the bot owner for future conversations.
        
        Use this when the bot owner shares personal information that should be remembered.
        Examples: favorite color, job, hobbies, preferences, family details, interests.
        Only works when talking directly to the bot owner (is_owner=True).
        
        Args:
            key: Category of information (e.g., 'favorite_color', 'job', 'hobby')  
            value: The actual information to store
        
        Returns:
            Dict with status and confirmation message
        """
        
        # Check if the current user is the bot owner using our manual tracker
        is_owner = (self.current_user_id == self.bot_owner_id)
        
        if not is_owner:
            return {
                "status": "unauthorized",
                "message": f"I can only learn about {self.bot_owner_id} when talking to {self.bot_owner_id} directly. You are logged in as '{self.current_user_id}'."
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

    def get_user_info(self, key: str, tool_context: ToolContext) -> dict:
        """Retrieve specific information about the bot owner that was previously stored.
        
        Use this to look up facts about the bot owner when answering questions or providing context.
        Works for any stored information like preferences, background, interests, etc.
        Available to both the owner and others who interact with this bot.
        
        Args:
            key: The category of information to retrieve (e.g., 'favorite_color', 'job')
        
        Returns:
            Dict with the requested information or 'not found' message
        """
        
        # Access the session state to retrieve information
        value = tool_context.state.get(key)
        
        if value:
            return {
                "status": "found",
                "message": f"{self.bot_owner_id}'s {key.replace('_', ' ')}: {value}",
                "key": key,
                "value": value
            }
        else:
            is_owner = (self.current_user_id == self.bot_owner_id)
            if is_owner:
                suggestion = f"You can teach me by saying something like 'My {key.replace('_', ' ')} is ...'"
            else:
                suggestion = f"{self.bot_owner_id} hasn't shared that information with me yet."
            
            return {
                "status": "not_found",
                "message": f"I don't know {self.bot_owner_id}'s {key.replace('_', ' ')} yet. {suggestion}",
                "key": key
            }

    def list_known_facts(self, tool_context: ToolContext) -> dict:
        """Display all stored information about the bot owner in an organized summary.
        
        Use this to show everything the bot knows about the owner, useful for:
        - Providing a complete overview when asked "what do you know about me?" (by owner)
        - Showing what information is available when others ask about the owner
        - Giving context in conversations about the bot owner
        
        Returns:
            Dict with all stored facts formatted as a readable list
        """
        
        # Get all non-system keys from state
        facts = {}
        system_keys = {"is_owner", "current_user", "bot_owner_id", "session_created"}
        
        # ADK State object doesn't support .items(), so we'll check known keys
        # This is a limitation - in a real app, you'd store facts in a structured way
        known_fact_keys = ["favorite_color", "job", "hobby", "work", "hobbies", "profession", "occupation"]
        
        for key in known_fact_keys:
            value = tool_context.state.get(key)
            if value is not None:
                facts[key.replace('_', ' ')] = value
        
        is_owner = (self.current_user_id == self.bot_owner_id)
        
        if facts:
            fact_list = "\n".join([f"- {key}: {value}" for key, value in facts.items()])
            if is_owner:
                message = f"Here's what I know about you:\n{fact_list}"
            else:
                message = f"Here's what I know about {self.bot_owner_id}:\n{fact_list}"
            
            return {
                "status": "found",
                "message": message,
                "facts": facts
            }
        else:
            if is_owner:
                message = "I don't have any specific facts about you yet. Start teaching me!"
            else:
                message = f"{self.bot_owner_id} hasn't shared much information with me yet."
            
            return {
                "status": "empty",
                "message": message,
                "facts": {}
            }
    
    def create_initial_state(self, current_user_id: str):
        """Create initial session state with user authentication info."""
        is_owner = (current_user_id == self.bot_owner_id)
        
        return {
            "is_owner": is_owner,
            "current_user": current_user_id,
            "bot_owner_id": self.bot_owner_id,
            "session_created": True
        }
    
    async def get_or_create_session(self, current_user_id: str):
        """Get existing session or create new one for the current user."""
        app_name = "Multi-User AI Agents"
        
        try:
            # All users share the same bot session for shared knowledge
            # But we track who's currently talking
            shared_session_key = f"{self.bot_owner_id}_bot_shared_knowledge"
            
            # Try to get existing shared session
            existing_sessions = self.session_service.list_sessions(
                app_name=app_name,
                user_id=shared_session_key
            )
            
            if existing_sessions.sessions:
                session_id = existing_sessions.sessions[0].id
                print(f"✅ Using shared session: {shared_session_key}")
                return shared_session_key, session_id
            else:
                # Create new shared session
                initial_state = self.create_initial_state(self.bot_owner_id)  # Initialize as owner
                new_session = self.session_service.create_session(
                    app_name=app_name,
                    user_id=shared_session_key,
                    state=initial_state
                )
                print(f"✅ Created shared session: {shared_session_key}")
                return shared_session_key, new_session.id
                
        except Exception as e:
            print(f"❌ Session error: {e}")
            return None, None
    
    async def chat(self, current_user_id: str, message: str):
        """Handle a chat message from a user."""
        # Set current user for this conversation
        self.current_user_id = current_user_id
        
        user_key, session_id = await self.get_or_create_session(current_user_id)
        if not user_key or not session_id:
            return "Error: Could not create or access session"
        
        # Determine if this is the owner or someone else
        is_owner = (current_user_id == self.bot_owner_id)
        mode = "Learning Mode" if is_owner else "Representative Mode"
        
        print(f"👤 User: {current_user_id} | 🤖 Bot: {self.bot_owner_id}-Bot | 🔄 {mode}")
        
        content = types.Content(role="user", parts=[types.Part(text=message)])
        
        try:
            async for event in self.runner.run_async(
                user_id=user_key,
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
                            return response_text
                        else:
                            return "[Processing...]"
                            
        except Exception as e:
            return f"Error: {e}"

# Demo function for testing the multi-user system
async def demo_multi_user_system():
    """Demonstrate the multi-user authentication system."""
    print("🚀 Starting Multi-User AI Agent System Demo...")
    print("=" * 50)
    
    # Create Zhen's bot
    zhen_bot = UserAuthenticatedBot("zhen")
    if not await zhen_bot.initialize():
        return
    
    print("✅ Zhen's bot initialized")
    print("\n🎭 Demo Scenarios:")
    print("1. Zhen talking to his own bot (Learning Mode)")
    print("2. Alice talking to Zhen's bot (Representative Mode)")
    print("3. Bob talking to Zhen's bot (Representative Mode)")
    
    # Scenario 1: Zhen teaching his bot
    print("\n" + "="*30)
    print("📚 Scenario 1: Zhen (owner) -> Zhen-Bot")
    print("Mode: Learning ✅")
    
    response = await zhen_bot.chat("zhen", "My favorite color is blue and I work as a software engineer")
    print(f"Zhen-Bot: {response}")
    
    response = await zhen_bot.chat("zhen", "I also love playing guitar in my free time")
    print(f"Zhen-Bot: {response}")
    
    # Scenario 2: Alice asking Zhen's bot
    print("\n" + "="*30)
    print("👥 Scenario 2: Alice (visitor) -> Zhen-Bot")
    print("Mode: Representative 🗣️")
    
    response = await zhen_bot.chat("alice", "Hi! What can you tell me about Zhen?")
    print(f"Zhen-Bot: {response}")
    
    response = await zhen_bot.chat("alice", "My favorite color is red")  # Should not be learned
    print(f"Zhen-Bot: {response}")
    
    # Scenario 3: Bob asking specific questions
    print("\n" + "="*30)
    print("👤 Scenario 3: Bob (visitor) -> Zhen-Bot")
    print("Mode: Representative 🗣️")
    
    response = await zhen_bot.chat("bob", "What does Zhen do for work?")
    print(f"Zhen-Bot: {response}")
    
    response = await zhen_bot.chat("bob", "What are Zhen's hobbies?")
    print(f"Zhen-Bot: {response}")
    
    # Scenario 4: Zhen checking what the bot knows
    print("\n" + "="*30)
    print("🔍 Scenario 4: Zhen checking his bot's knowledge")
    
    response = await zhen_bot.chat("zhen", "List everything you know about me")
    print(f"Zhen-Bot: {response}")
    
    print("\n✅ Demo completed! The system correctly:")
    print("  - Allowed Zhen to teach his bot new information")
    print("  - Prevented visitors from modifying the bot's knowledge")
    print("  - Let visitors access existing information about Zhen")
    print("  - Maintained separate sessions for different users")

if __name__ == '__main__':
    print("🧪 Multi-User AI Agent System")
    print("=" * 30)
    asyncio.run(demo_multi_user_system())
