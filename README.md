
# Zhen's AI Representative — Simple Personal Bot (Jan 2025)

## Overview

A simple AI representative bot for Zhen built with Google ADK (Gemini 2.0 Flash). The bot learns facts about Zhen when he tells it things about himself and can answer questions about what it knows.

## Architecture

- **Backend**: `backend/`
  - Simple bot (`src/core/bot.py`) - ZhenBot class that represents Zhen
  - One tool (`src/tools/learn_about_zhen.py`) - learns facts from statements  
  - Config (`src/core/config.py`) reads `GOOGLE_API_KEY` and `DB_URL`
  - Terminal interface (`testing.py`) for direct chat testing
  - Optional web API (`web_api.py`) for web interface

- **Frontend**: `frontend/` (optional)
  - Next.js chat UI (if you want a web interface)

- **ADK Reference**: `adk-python/` — Google ADK documentation and samples

## How It Works

- **Simple Learning**: Tell the bot facts about yourself and it will extract and store them
  - "My favorite color is blue" → stores favorite_color = blue
  - "I work at Google" → stores job = works at Google
  - "I love hiking" → stores hobby = hiking

- **Memory**: The bot remembers everything you tell it and can reference stored facts in conversations
- **No Permissions**: Simplified - just Zhen talking to his representative (no guest users)

## Recent Simplification

- **Simplified Architecture**: Removed complex multi-user system, now just for Zhen
- **Single Tool**: `learn_about_zhen()` tool that extracts and stores facts
- **No Permissions**: Removed owner/visitor complexity - just Zhen using his bot
- **Clean Structure**: Removed redundant files and complex session management

## How to Run

Prerequisites: Python 3.10+, PostgreSQL running and accessible.

### **Quick Start - Terminal Interface** (Recommended)
```powershell
cd backend
python testing.py
```

Then just chat with your AI representative:
- "My favorite color is blue"
- "I work at Google as a software engineer" 
- "I love hiking and play guitar"
- "What do you know about me?"

### **Web Interface** (Optional)
```powershell
cd backend
python -m uvicorn web_api:app --reload --port 8000
```

Then optionally run the frontend:
```powershell
cd frontend
npm install
npm run dev
```

## Environment

Create a `.env` in `backend/` with:
```
GOOGLE_API_KEY=your_google_api_key
DB_URL=postgresql://user:password@localhost:5432/your_db
```

`src/core/config.py` will validate these at runtime.

## Testing Examples

Try these in the terminal interface:

**Teaching Facts:**
- "My favorite color is blue"
- "I work at Google as a software engineer"
- "I love hiking and play guitar"
- "I studied computer science at Stanford"

**Asking Questions:**
- "What do you know about me?"
- "Tell me about my work"
- "What are my hobbies?"

The bot will use the `learn_about_zhen` tool to extract facts and store them with timestamps.

## File Structure

```
backend/
├── src/
│   ├── core/
│   │   ├── bot.py              # ZhenBot class
│   │   └── config.py           # Simple config
│   └── tools/
│       └── learn_about_zhen.py # Single learning tool
├── testing.py                  # Terminal interface (recommended)
├── web_api.py                  # Optional web API
└── requirements.txt
```

## Next Steps

- Add more sophisticated fact retrieval
- Improve natural language understanding
- Add fact editing/updating capabilities

---

**Simple, focused, and clean** - just Zhen and his AI representative! 🤖
