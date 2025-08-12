"""
Terminal interface for testing the memory bot directly.
Run this for quick testing without the web API.
"""

import asyncio
import sys
import os

# Add backend src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.bot import MemoryBot
from src.core.config import config


async def main():
    """Main terminal interface loop."""
    print("🤖 Memory Bot Terminal Interface")
    print("=" * 50)
    
    # Validate config first
    try:
        config.validate()
        print("✅ Configuration valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Make sure you have a valid .env file with GOOGLE_API_KEY and DB_URL")
        return
    
    # Initialize bot
    bot = MemoryBot()
    print("\n🔄 Initializing bot...")
    
    if not await bot.initialize():
        print("❌ Failed to initialize bot. Check your database connection and API key.")
        return
    
    print("✅ Bot initialized successfully!")
    print("\n💡 You can now chat with the bot. It will learn anything you tell it.")
    print("📝 Examples:")
    print("   - 'My favorite color is blue'")
    print("   - 'I work at Google'") 
    print("   - 'I love hiking'")
    print("\n🛑 Type 'quit', 'exit', or press Ctrl+C to stop.\n")

    USER_ID = "DEMO_USER"  # Change this to any user name you want

    print(f"✅ Chatting as: {USER_ID}")
    print("-" * 50)
    
    # Chat loop
    try:
        while True:
            try:
                # Get user input
                user_input = input(f"\n{USER_ID}: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    print("💭 (Please type something)")
                    continue
                
                # Send to bot
                print("🤖 Thinking...")
                response = await bot.chat(USER_ID, user_input)
                print(f"🤖 Bot: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")