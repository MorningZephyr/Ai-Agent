# AI Representative System

A simple, intelligent AI system that learns about users through conversation and can represent them to others.

## Features

- 🧠 **Automated Learning**: Learns about users naturally through conversation
- 💡 **Smart Inference**: Makes intelligent connections from stored information
- 💾 **Persistent Memory**: Remembers information across conversations using PostgreSQL
- 🎭 **User Representation**: Can represent users based on learned knowledge

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

### Learning & Inference
```
You: I love playing piano and guitar
AI: I've learned that you like playing piano and guitar.

You: What do you know about me?
AI: I know that you like playing piano and guitar. Based on this, 
    you seem to have an interest in musical instruments.
```

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

1. **Learning**: AI automatically extracts knowledge from conversations
2. **Storage**: Information stored in PostgreSQL via ADK sessions
3. **Retrieval**: Smart inference engine makes connections from stored data
4. **Representation**: AI can represent users based on learned profile

---

Built with Google's Agent Development Kit and Gemini 2.0 Flash 🚀