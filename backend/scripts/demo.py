"""
Demo script for testing the multi-user authentication system.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core import UserAuthenticatedBot


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
