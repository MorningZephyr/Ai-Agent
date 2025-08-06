"""
Main entry point for the Multi-User AI Agent System.
"""

import asyncio
from src.core import UserAuthenticatedBot


async def main():
    """Main application entry point."""
    print("🚀 Multi-User AI Agent System")
    print("=" * 30)
    
    # For now, just run the demo
    # In the future, this could start a FastAPI server
    from scripts.demo import demo_multi_user_system
    await demo_multi_user_system()


if __name__ == '__main__':
    asyncio.run(main())
