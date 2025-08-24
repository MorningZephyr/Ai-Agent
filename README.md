# AI Representative System

**Intelligent Conversational AI with Automated Knowledge Extraction and User Representation**

## Project Overview

Architected intelligent conversational AI system using Google's Agent Development Kit with automated knowledge extraction, dynamically learning and modeling user interests for cross-user representation. Implemented persistent conversation memory using PostgreSQL and ADK's session framework, enabling the AI to remember user information across multiple conversation sessions.

## Key Features

### 🧠 Automated Knowledge Extraction & Smart Inference
- **Dynamic Learning**: Automatically extracts interests, personality traits, and factual information from conversations
- **Intelligent Parsing**: Uses Gemini 2.0 Flash to understand and categorize user information
- **Smart Inference**: Makes reasonable conclusions from stored data (e.g., "plays piano" → piano is likely favorite instrument)
- **Real-time Profile Building**: Continuously updates user profiles as conversations progress

### 💾 Persistent Conversation Memory
- **PostgreSQL Integration**: Stores user profiles and conversation history in PostgreSQL database
- **ADK Session Framework**: Leverages Google ADK's session management for seamless memory persistence
- **Cross-Session Continuity**: Remembers users across multiple conversations and sessions

### 🎭 Cross-User Representation
- **AI Representation**: Can represent users to others based on learned personality and communication style
- **Contextual Responses**: Responds as the user would, incorporating their interests and traits
- **Dynamic Modeling**: Adapts representation based on accumulated knowledge about users

## Architecture

**Simple Backend-Only Design** - No unnecessary class wraps or complex abstractions

```
backend/
├── main.py              # Core AI system with terminal interface
├── web_server.py        # Optional FastAPI web interface  
├── requirements.txt     # Minimal dependencies
├── config.example       # Configuration template
└── db/                  # Database setup scripts
```

### Core Components

1. **AIRepresentativeSystem** - Main system class handling:
   - Automated knowledge extraction from conversations
   - Persistent user profile management via PostgreSQL
   - Cross-user representation capabilities
   - ADK agent integration with Gemini 2.0 Flash

2. **Knowledge Extraction Pipeline**:
   - Real-time conversation analysis
   - Structured information extraction (interests, traits, facts)
   - Dynamic profile updates with timestamps
   - Intelligent categorization of user information

3. **Persistent Memory Layer**:
   - PostgreSQL database for long-term storage
   - ADK DatabaseSessionService integration
   - Cross-session state management
   - User profile versioning and updates

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL database
- Google API key for Gemini

### Setup

1. **Install Dependencies**:
```powershell
cd backend
pip install -r requirements.txt
```

2. **Configure Environment**:
```powershell
# Copy configuration template
copy config.example .env

# Edit .env with your credentials:
# GOOGLE_API_KEY=your_google_api_key
# DB_URL=postgresql://user:password@localhost:5432/ai_representative_db
```

3. **Run Terminal Interface** (Recommended):
```powershell
python main.py
```

4. **Or Run Web API** (Optional):
```powershell
python web_server.py
```

## Usage Examples

### Learning About Users
The AI automatically extracts knowledge from natural conversation:

```
User: "I love hiking and photography. I work as a software engineer at Google."

AI: "I've updated my understanding of you based on what you shared."
    # Automatically extracts:
    # - Interests: {"hiking": "outdoor activity", "photography": "creative hobby"}
    # - Facts: {"job": "software engineer", "company": "Google"}
```

### Smart Inference from Stored Data
The AI can answer questions by making intelligent inferences:

```
User: "I love playing piano"
[Later] Someone asks: "What's their favorite instrument?"
AI: "Piano is likely their favorite instrument (This is an inference based on: 
     User mentioned loving to play piano) Supporting information: plays piano"
```

### Persistent Memory
Information persists across sessions:

```
Session 1: "I'm really into rock climbing"
Session 2: "What do you know about my hobbies?"
AI: "I know you're into rock climbing and hiking based on our previous conversations."
```

### Cross-User Representation
AI can represent users to others:

```
Context: "What would John say about the new project proposal?"
AI: "Based on John's engineering background and preference for thorough planning, 
     he would likely want to see detailed technical specifications and a clear 
     timeline before giving approval."
```

## Technical Implementation

### Knowledge Extraction Process
1. **Input Analysis**: Every user message is analyzed for extractable information
2. **Structured Extraction**: Uses Gemini 2.0 Flash to parse information into structured format
3. **Profile Integration**: Updates persistent user profile with new information
4. **Memory Storage**: Saves to PostgreSQL via ADK session framework

### Database Schema
- **User Profiles**: Interests, personality traits, communication style
- **Learned Facts**: Timestamped factual information with source tracking
- **Session History**: Conversation continuity across sessions
- **Cross-References**: Relationships between users for representation

### AI Agent Configuration
```python
Agent(
    name="ai_representative",
    model="gemini-2.0-flash",
    tools=[extract_and_learn, represent_user],
    instruction="Intelligent AI that learns about users and represents them"
)
```

## Web API Endpoints

### Core Endpoints
- `POST /api/chat` - Chat with automated learning
- `POST /api/ask` - Ask questions about users with smart inference
- `GET /api/profile/{user_id}` - Get learned user profile
- `POST /api/represent` - Request user representation
- `GET /api/health` - System health and features

### Example API Usage
```bash
# Chat with learning
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I love playing piano", "user_id": "john"}'

# Ask question with smart inference
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is their favorite instrument?", "target_user_id": "john"}'

# Get user profile
curl "http://localhost:8000/api/profile/john"
```

## Resume-Ready Description

*"Architected intelligent conversational AI system using Google's Agent Development Kit with automated knowledge extraction, dynamically learning and modeling user interests for cross-user representation. Implemented persistent conversation memory using PostgreSQL and ADK's session framework, enabling the AI to remember user information across multiple conversation sessions."*

## Technology Stack

- **AI Framework**: Google Agent Development Kit (ADK)
- **AI Model**: Gemini 2.0 Flash
- **Database**: PostgreSQL
- **Memory Management**: ADK Session Framework
- **Web Framework**: FastAPI (optional)
- **Language**: Python 3.10+

## Key Innovations

1. **Automated Knowledge Extraction**: No manual data entry - learns from natural conversation
2. **Smart Inference Engine**: Makes intelligent conclusions from stored data with confidence scoring
3. **Dynamic User Modeling**: Continuously builds and refines user profiles over time
4. **Cross-User Representation**: AI can authentically represent users to others
5. **Persistent Memory**: True conversation continuity across sessions using PostgreSQL
6. **Simple Architecture**: Clean, maintainable code without unnecessary complexity

### 🎯 Smart Inference Examples:
- **Input**: "I love playing guitar and piano"
- **Question**: "What's their favorite instrument?" 
- **AI Response**: "Based on their mention of loving both guitar and piano, they likely enjoy both instruments equally, though I'd need more specific preference information to determine a single favorite."

- **Input**: "I work as a data scientist and love solving puzzles"
- **Question**: "Do they enjoy analytical work?"
- **AI Response**: "Yes, very likely - they work as a data scientist (analytical profession) and enjoy puzzles (analytical hobby), indicating a strong preference for analytical thinking."

---

**Simple, focused, and intelligent** - An AI system that truly learns and remembers! 🤖✨