import sys
import os
import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the parent directory to the path so we can import from zhen-bot
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import your existing zhen-bot components
# Note: We'll implement the full agent integration after testing the basic endpoint
# from zhen_bot.agent import root_agent
# from zhen_bot.main import call_agent_async, session_service, initial_zhen_bot_state
# from google.adk.runners import Runner
# from google.genai import types

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/')
def home():
    return jsonify({
        "message": "Zhen-Bot API is running!",
        "status": "healthy",
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "zhen-bot-api"
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the request data
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        user_id = data.get('user_id', 'web_user')
        is_zhen = data.get('is_zhen', False)  # For learning vs sharing mode
        
        # For now, we'll create a simple test response
        # We'll implement the full agent integration in the next step
        response_text = f"Echo: {user_message} (from user: {user_id}, is_zhen: {is_zhen})"
        
        return jsonify({
            'response': response_text,
            'user_id': user_id,
            'is_zhen': is_zhen
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Zhen-Bot API server...")
    print("📡 Server will be available at: http://localhost:5000")
    print("💬 Chat endpoint: POST /chat")
    app.run(debug=True, host='0.0.0.0', port=5000)
