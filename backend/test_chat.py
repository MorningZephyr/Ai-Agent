import requests
import json

# Test the chat endpoint
def test_chat_endpoint():
    url = "http://localhost:5000/chat"
    
    # Test message 1: Regular user asking about Zhen
    test_data_1 = {
        "message": "What's Zhen's favorite hobby?",
        "user_id": "visitor123", 
        "is_zhen": False
    }
    
    # Test message 2: Zhen teaching the bot
    test_data_2 = {
        "message": "I love playing guitar and coding",
        "user_id": "zhen",
        "is_zhen": True
    }
    
    # Test message 3: Different visitor
    test_data_3 = {
        "message": "Tell me about Zhen's background",
        "user_id": "student456",
        "is_zhen": False
    }
    
    # Test message 4: Zhen updating information
    test_data_4 = {
        "message": "My favorite food is sushi and I study computer science",
        "user_id": "zhen",
        "is_zhen": True
    }
    
    # Test message 5: Empty message
    test_data_5 = {
        "message": "",
        "user_id": "test_user",
        "is_zhen": False
    }
    
    # Test message 6: Very long message
    test_data_6 = {
        "message": "This is a very long message to test how the API handles large inputs. " * 10,
        "user_id": "long_message_user",
        "is_zhen": False
    }
    
    # Test message 7: Special characters
    test_data_7 = {
        "message": "Hello! How are you? I'm asking about Zhen's interests... 😊",
        "user_id": "special_char_user",
        "is_zhen": False
    }
    
    # Test message 8: Missing user_id (should use default)
    test_data_8 = {
        "message": "What can you tell me about Zhen?",
        "is_zhen": False
    }
    
    # Test message 9: Missing is_zhen (should use default)
    test_data_9 = {
        "message": "Another question about Zhen",
        "user_id": "default_user"
    }
    
    # Test message 10: All fields missing except message
    test_data_10 = {
        "message": "Minimal test message"
    }
    
    print("🧪 Testing Chat Endpoint")
    print("=" * 50)
    
    # Test 1
    print("\n📤 Test 1 - Visitor asking question:")
    json_string_1 = json.dumps(test_data_1, indent=2)
    print(f"Sending: {json_string_1}")
    
    try:
        response_1 = requests.post(url, json=test_data_1)
        print(f"\n📥 Response (Status: {response_1.status_code}):")
        response_json_1 = json.dumps(response_1.json(), indent=2)
        print(response_json_1)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2
    print("\n" + "=" * 50)
    print("\n📤 Test 2 - Zhen teaching the bot:")
    json_string_2 = json.dumps(test_data_2, indent=2)
    print(f"Sending: {json_string_2}")
    
    try:
        response_2 = requests.post(url, json=test_data_2)
        print(f"\n📥 Response (Status: {response_2.status_code}):")
        response_json_2 = json.dumps(response_2.json(), indent=2)
        print(response_json_2)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3
    print("\n" + "=" * 50)
    print("\n📤 Test 3 - Different visitor:")
    json_string_3 = json.dumps(test_data_3, indent=2)
    print(f"Sending: {json_string_3}")
    
    try:
        response_3 = requests.post(url, json=test_data_3)
        print(f"\n📥 Response (Status: {response_3.status_code}):")
        response_json_3 = json.dumps(response_3.json(), indent=2)
        print(response_json_3)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4
    print("\n" + "=" * 50)
    print("\n📤 Test 4 - Zhen updating information:")
    json_string_4 = json.dumps(test_data_4, indent=2)
    print(f"Sending: {json_string_4}")
    
    try:
        response_4 = requests.post(url, json=test_data_4)
        print(f"\n📥 Response (Status: {response_4.status_code}):")
        response_json_4 = json.dumps(response_4.json(), indent=2)
        print(response_json_4)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5
    print("\n" + "=" * 50)
    print("\n📤 Test 5 - Empty message:")
    json_string_5 = json.dumps(test_data_5, indent=2)
    print(f"Sending: {json_string_5}")
    
    try:
        response_5 = requests.post(url, json=test_data_5)
        print(f"\n📥 Response (Status: {response_5.status_code}):")
        response_json_5 = json.dumps(response_5.json(), indent=2)
        print(response_json_5)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6
    print("\n" + "=" * 50)
    print("\n📤 Test 6 - Very long message:")
    json_string_6 = json.dumps(test_data_6, indent=2)
    print(f"Sending: {json_string_6}")
    
    try:
        response_6 = requests.post(url, json=test_data_6)
        print(f"\n📥 Response (Status: {response_6.status_code}):")
        response_json_6 = json.dumps(response_6.json(), indent=2)
        print(response_json_6)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7
    print("\n" + "=" * 50)
    print("\n📤 Test 7 - Special characters:")
    json_string_7 = json.dumps(test_data_7, indent=2)
    print(f"Sending: {json_string_7}")
    
    try:
        response_7 = requests.post(url, json=test_data_7)
        print(f"\n📥 Response (Status: {response_7.status_code}):")
        response_json_7 = json.dumps(response_7.json(), indent=2)
        print(response_json_7)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8
    print("\n" + "=" * 50)
    print("\n📤 Test 8 - Missing user_id (should use default):")
    json_string_8 = json.dumps(test_data_8, indent=2)
    print(f"Sending: {json_string_8}")
    
    try:
        response_8 = requests.post(url, json=test_data_8)
        print(f"\n📥 Response (Status: {response_8.status_code}):")
        response_json_8 = json.dumps(response_8.json(), indent=2)
        print(response_json_8)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 9
    print("\n" + "=" * 50)
    print("\n📤 Test 9 - Missing is_zhen (should use default):")
    json_string_9 = json.dumps(test_data_9, indent=2)
    print(f"Sending: {json_string_9}")
    
    try:
        response_9 = requests.post(url, json=test_data_9)
        print(f"\n📥 Response (Status: {response_9.status_code}):")
        response_json_9 = json.dumps(response_9.json(), indent=2)
        print(response_json_9)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 10
    print("\n" + "=" * 50)
    print("\n📤 Test 10 - Minimal data (only message):")
    json_string_10 = json.dumps(test_data_10, indent=2)
    print(f"Sending: {json_string_10}")
    
    try:
        response_10 = requests.post(url, json=test_data_10)
        print(f"\n📥 Response (Status: {response_10.status_code}):")
        response_json_10 = json.dumps(response_10.json(), indent=2)
        print(response_json_10)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 11 - Error case (missing message)
    print("\n" + "=" * 50)
    print("\n📤 Test 11 - Error case (missing message):")
    test_data_11 = {"user_id": "test"}
    json_string_11 = json.dumps(test_data_11, indent=2)
    print(f"Sending: {json_string_11}")
    
    try:
        response_11 = requests.post(url, json=test_data_11)
        print(f"\n📥 Response (Status: {response_11.status_code}):")
        response_json_11 = json.dumps(response_11.json(), indent=2)
        print(response_json_11)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 12 - Error case (completely empty)
    print("\n" + "=" * 50)
    print("\n📤 Test 12 - Error case (completely empty):")
    test_data_12 = {}
    json_string_12 = json.dumps(test_data_12, indent=2)
    print(f"Sending: {json_string_12}")
    
    try:
        response_12 = requests.post(url, json=test_data_12)
        print(f"\n📥 Response (Status: {response_12.status_code}):")
        response_json_12 = json.dumps(response_12.json(), indent=2)
        print(response_json_12)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_endpoint() 