# AI Representative System

A multi-user AI system where each user can train their own AI representative that others can interact with safely.

## Features

- 🧠 **Automated Learning**: Learns about users naturally through conversation
- 💡 **Smart Inference**: Makes intelligent connections from stored information
- 💾 **Persistent Memory**: Remembers information across conversations using PostgreSQL
- 🎭 **User Representation**: Can represent users based on learned knowledge
- 👥 **Multi-User Support**: Each user has their own AI representative
- 🔒 **Read-Only Protection**: Others can chat with your AI but cannot modify your data

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL database
- Google API key for Gemini

### Setup

1. **Install Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment**:
```bash
# Copy config template
copy config.example .env

# Edit .env with your credentials:
GOOGLE_API_KEY=your_google_api_key
DB_URL=postgresql://user:password@localhost:5432/ai_representative_db
```

3. **Run the System**:
```bash
# Terminal Interface (Recommended)
python main.py

# Or Web API (Optional)
python web_server.py
```

## Usage Examples

### Training Your Own AI
```
Zhen: I love playing piano and basketball
AI: I've learned that you like playing piano and basketball.

Zhen: What do you know about me?
AI: I know that you like playing piano and basketball. Based on this, 
    you seem to have interests in music and sports.
```

### Multi-User Interactions
```
# Bob logs in and talks to Zhen's AI
Bob: talk to Zhen
System: You are now talking to Zhen's AI.

Bob: What does Zhen like?
Zhen's AI: Zhen likes playing the piano and basketball.

Bob: He also likes guitar
Zhen's AI: Thank you for sharing, but I can only learn new 
          information from Zhen directly.
```

### Read-Only Protection
- ✅ **Users can access** other people's AI representatives
- ✅ **Users can ask questions** about what others like
- ❌ **Users cannot modify** other people's profiles
- ❌ **Users cannot add false information** about others

### Persistent Memory
Information is remembered across conversations using PostgreSQL and ADK's session framework.

## Technical Stack

- **AI**: Google ADK with Gemini 2.0 Flash
- **Database**: PostgreSQL
- **API** (Optional): FastAPI
- **Language**: Python 3.10+

## Architecture

Simple backend-only design focused on core functionality:

```
backend/
├── main.py          # Core AI system
├── web_server.py    # Optional web API
├── requirements.txt # Dependencies
└── config.example   # Config template
```

## How It Works

1. **User Login**: Each user gets their own AI representative
2. **Learning Mode**: When users talk to their own AI, it learns and updates their profile
3. **Read-Only Mode**: When users talk to someone else's AI, they can ask questions but cannot modify data
4. **Smart Protection**: The system automatically prevents unauthorized profile modifications
5. **Cross-User Discovery**: Users can explore and interact with other AI representatives safely

---

Built with Google's Agent Development Kit and Gemini 2.0 Flash 🚀