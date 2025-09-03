"""
Simple AI Representative System
Architected intelligent conversational AI system using Google's Agent Development Kit 
with automated knowledge extraction, dynamically learning and modeling user interests 
for cross-user representation.
"""

import asyncio
from services import AIRepresentativeSystem


async def main():
    """Terminal interface for testing the AI Representative System."""
    print("🤖 AI Representative System")
    print("=" * 60)
    print("Intelligent conversational AI with automated knowledge extraction")
    print("Building persistent user profiles for cross-user representation")
    print("=" * 60)
    
    # Initialize the AI system
    ai_system = AIRepresentativeSystem()
    
    print("\n🔄 Initializing AI Representative System...")
    if not await ai_system.initialize():
        print("❌ Failed to initialize. Check your database connection and API key.")
        return
    
    print("✅ AI Representative System ready!")
    print("\n💡 I'll automatically learn about you as we chat!")
    print("🧠 Plus, I can answer questions with smart inference!")
    print("\n📝 Try sharing:")
    print("   - Your interests and hobbies")
    print("   - Your personality and preferences") 
    print("   - Your work and experiences")
    print("   - Anything about yourself!")
    print("\n🔍 Then try asking:")
    print("   - 'What's my favorite instrument?' (after mentioning you play piano)")
    print("   - 'What do I like to do?' (after sharing hobbies)")
    print("   - 'What's my job?' (after mentioning work)")
    print("\n🛑 Type 'quit' to exit, 'profile' to see what I've learned\n")
    
    user_id = input("👤 Enter your name/ID to log in: ").strip() or "default_user"
    print(f"✅ Hello {user_id}! You are now logged in.")
    
    # By default, you are talking to your own AI representative.
    target_user_id = user_id 
    print(f"🎤 You are now talking to your own AI. Type 'talk to <name>' to chat with someone else's AI.")
    print("-" * 60)
    
    # Chat loop with learning
    try:
        while True:
            try:
                prompt_user = f"{user_id} (to {target_user_id}'s AI)"
                user_input = input(f"\n{prompt_user}: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n👋 Goodbye {user_id}! Your profile has been saved for next time.")
                    break
                
                if user_input.lower().startswith('talk to '):
                    new_target = user_input[8:].strip()
                    if new_target:
                        target_user_id = new_target
                        print(f"🎤 You are now talking to {target_user_id}'s AI.")
                    else:
                        print("❓ Please specify a user to talk to, e.g., 'talk to Jane'.")
                    continue

                if user_input.lower() == 'profile':
                    profile = await ai_system.get_user_profile(user_id)
                    if profile:
                        print(f"\n📊 Your Current Profile:")
                        print(f"   Interests: {len(profile.interests)} identified")
                        print(f"   Personality Traits: {len(profile.personality_traits)} identified")
                        print(f"   Communication Style: {profile.communication_style}")
                        print(f"   Learned Facts: {len(profile.learned_facts)} stored")
                        print(f"   Last Updated: {profile.last_updated}")
                    else:
                        print("\n📊 No profile found yet. Keep chatting to build one!")
                    continue
                
                if not user_input:
                    print("💭 (Please type something)")
                    continue
                
                print("🤖 Processing and learning...")
                response = await ai_system.chat(user_input, user_id, target_user_id)
                print(f"🤖 AI ({target_user_id}'s Rep): {response}")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye {user_id}!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
                
    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye {user_id}!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
