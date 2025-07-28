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
    
    # Test 3 - Error case (missing message)
    print("\n" + "=" * 50)
    print("\n📤 Test 3 - Error case (missing message):")
    test_data_3 = {"user_id": "test"}
    json_string_3 = json.dumps(test_data_3, indent=2)
    print(f"Sending: {json_string_3}")
    
    try:
        response_3 = requests.post(url, json=test_data_3)
        print(f"\n📥 Response (Status: {response_3.status_code}):")
        response_json_3 = json.dumps(response_3.json(), indent=2)
        print(response_json_3)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_endpoint() 