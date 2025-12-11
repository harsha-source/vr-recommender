import sys
import os
import json

# Add src to path
sys.path.append(os.getcwd())

try:
    from src.agent import ConversationAgent
    
    print("🔄 Initializing Conversation Agent...")
    agent = ConversationAgent()
    
    # Test 1: Simple Greeting
    print("\n🧪 Test 1: Greeting")
    res = agent.process_message("sess_1", "user_1", "Hello")
    print(f"   Response: {res['response']}")
    
    # Test 2: Search Query (Data Viz)
    print("\n🧪 Test 2: Search 'data visualization'")
    res = agent.process_message("sess_1", "user_1", "Show me apps for data visualization")
    print(f"   Tool Used: {res.get('tool_used')}")
    print(f"   Apps Found: {len(res.get('apps', []))}")
    if res.get('apps'):
        print(f"   First App: {res['apps'][0]['name']}")
        
    # Test 3: Complex Query (from screenshot)
    print("\n🧪 Test 3: Complex Query 'machine learning for public policy'")
    res = agent.process_message("sess_1", "user_1", "I want to learn machine learning for public policy")
    print(f"   Tool Used: {res.get('tool_used')}")
    print(f"   Apps Found: {len(res.get('apps', []))}")
    if res.get('apps'):
        print(f"   First App: {res['apps'][0]['name']}")
    else:
        print("   ❌ No apps found for complex query.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
