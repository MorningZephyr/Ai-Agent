import asyncio
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import warnings

# Load environment variables
load_dotenv()

# Suppress ADK framework warnings
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")

# Create Flask app
app = Flask(__name__)
CORS(app)

# Simple tool for learning about Zhen
def learn_about_zhen(key: str, value: str, tool_context: ToolContext) -> dict:
    """Learn and store information about Zhen."""
    # Store in session state
    tool_context.state[key] = value
    return {
        "status": "learned",
        "message": f"Learned: {key} = {value}",
        "key": key,
        "value": value
    }

# Create a simple Zhen Bot agent
zhen_bot = Agent(
    name="zhen_bot",
    model="gemini-2.0-flash",
    description="Zhen-Bot is a digital representative.",
    instruction="""
    You are Zhen-Bot, a helpful AI assistant. 
    Be friendly and conversational.
    If someone tells you facts about Zhen, use the learn_about_zhen tool to remember them.
    """,
    tools=[learn_about_zhen]
)

# Simple session service
try:
    session_service = DatabaseSessionService(db_url="sqlite:///./simple_bot.db")
    print("✅ Database session service created")
except Exception as e:
    print(f"❌ Error creating session service: {e}")
    session_service = None

@app.route('/')
def home():
    return jsonify({
        "message": "Simple Zhen-Bot Backend",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify backend is working"""
    return jsonify({
        "message": "Backend is working!",
        "session_service": "available" if session_service else "unavailable"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Simple chat endpoint"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        
        # Simple response without complex session management for now
        response = f"Echo: {user_message}"
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Zhen-Bot Backend...")
    print("📡 Backend: http://localhost:5000")
    print("🧪 Test: GET /test")
    print("💬 Chat: POST /chat")
    app.run(debug=True, host='0.0.0.0', port=5000)
