"""
Test the refactored setter/getter pattern.
"""

import asyncio
from google.adk.tools.tool_context import ToolContext
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.agents import Agent

from src.tools.tool_wrappers import get_owner_tools, get_guest_tools
from src.core.config import config


async def test_setter_getter_pattern():
    """Test the new unified tool pattern."""
    
    print("🔧 Testing Setter/Getter Pattern Refactor")
    print("=" * 50)
    
    # Setup
    bot_owner_id = "alice"
    guest_user_id = "bob"
    
    try:
        # Test 1: Owner tools (should have setters + getters)
        print("\n1️⃣ Testing Owner Tools (setters + getters)")
        owner_tools = get_owner_tools(bot_owner_id, bot_owner_id)
        print(f"   Owner gets {len(owner_tools)} tools:")
        for i, tool in enumerate(owner_tools):
            print(f"   • Tool {i+1}: {tool.__name__} - {tool.__doc__}")
        
        # Test 2: Guest tools (should have getters only)
        print("\n2️⃣ Testing Guest Tools (getters only)")
        guest_tools = get_guest_tools(bot_owner_id, guest_user_id)
        print(f"   Guest gets {len(guest_tools)} tools:")
        for i, tool in enumerate(guest_tools):
            print(f"   • Tool {i+1}: {tool.__name__} - {tool.__doc__}")
        
        # Test 3: Verify tool differentiation
        print("\n3️⃣ Testing Tool Access Patterns")
        
        owner_tool_names = {tool.__name__ for tool in owner_tools}
        guest_tool_names = {tool.__name__ for tool in guest_tools}
        
        setter_tools = owner_tool_names - guest_tool_names
        getter_tools = owner_tool_names & guest_tool_names
        
        print(f"   Setter tools (owner only): {setter_tools}")
        print(f"   Getter tools (shared): {getter_tools}")
        
        # Verify expected pattern
        expected_setters = {"set_info", "update_info", "delete_info"}
        expected_getters = {"get_info", "list_all_info", "search_info"}
        
        if setter_tools == expected_setters:
            print("   ✅ Setter tools correctly restricted to owner")
        else:
            print(f"   ❌ Setter tools mismatch. Expected: {expected_setters}, Got: {setter_tools}")
            
        if getter_tools == expected_getters:
            print("   ✅ Getter tools correctly shared with guests")
        else:
            print(f"   ❌ Getter tools mismatch. Expected: {expected_getters}, Got: {getter_tools}")
        
        # Test 4: Verify tool counts
        print("\n4️⃣ Testing Tool Counts")
        if len(owner_tools) == 6:  # 3 setters + 3 getters
            print("   ✅ Owner has correct number of tools (6 total)")
        else:
            print(f"   ❌ Owner should have 6 tools, got {len(owner_tools)}")
            
        if len(guest_tools) == 3:  # 3 getters only
            print("   ✅ Guest has correct number of tools (3 getters)")
        else:
            print(f"   ❌ Guest should have 3 tools, got {len(guest_tools)}")
        
        print("\n🎉 Setter/Getter Pattern Refactor Test Complete!")
        print("\nBenefits of the new pattern:")
        print("• Single unified tool class instead of separate files")
        print("• Clear setter/getter method separation")
        print("• More intuitive and maintainable architecture")
        print("• Automatic permission enforcement at method level")
        print("• Easy to extend with new getter/setter methods")
        print("• Tools are simple functions, easy to test and debug")
        
    except Exception as e:
        print(f"❌ Error testing refactored pattern: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(test_setter_getter_pattern())
