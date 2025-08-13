
# Ai-Agent — Simple Memory Bot (Aug 2025)

## Overview

This repo hosts a simple AI assistant built with FastAPI + Google ADK (Gemini 2.0 Flash) and a Next.js UI. The bot uses the LLM to decide if a statement expresses a user fact, preference, or hobby, and stores facts in persistent memory. No authentication barriers—anyone can teach the bot new information.

## Architecture

- **Backend**: `backend/`
  - FastAPI app (`web_api.py`) exposes `/api/auth`, `/api/chat/{session_id}`, `/api/session/*`, `/api/health`.
  - Bot (`src/core/bot.py`) uses Google ADK Agent + Runner and a `DatabaseSessionService` for persistence.
  - Single tool (`src/tools/user_info_tool.py`) implements `learn_about_user(statement)` to store facts as key-value pairs, using model-driven extraction.
  - Tool manager (`src/tools/tool_manager.py`) exposes the learn tool to the bot.
  - Config (`src/core/config.py`) reads `GOOGLE_API_KEY` and `DB_URL`; model is `gemini-2.0-flash`.
  - Sessions: all users share a single memory session `memory::shared`.

- **Frontend**: `frontend/`
  - Next.js 15 app providing a chat UI where you enter a `user_id` and chat with the bot.

- **ADK Reference**: `adk-python/` — Google ADK documentation and samples.

## Current Behavior

- The bot has 1 tool: `learn_about_user(statement)` that stores any statement as a key-value fact if possible.
- Teaching examples: "My favorite color is blue", "I work at Google", "I love hiking"
- The tool uses the LLM to extract structured facts (e.g., "I like basketball" → key: "hobby", value: "basketball").
- If the statement is ambiguous, the bot suggests a key name and asks for user approval.
- Questions and non-factual statements are ignored and not stored.
- All users contribute to the same knowledge base stored in `memory::shared`.

## Recent Changes

- **Model-Driven Extraction**: Fact extraction is now guided by the LLM, not hardcoded patterns.
- **No Raw Statement Storage**: Only key-value facts are stored; ambiguous statements prompt for key approval.
- **Simplified Architecture**: Removed owner/guest complexity—anyone can teach the bot.
- **Single Tool**: Replaced 6 complex tools with 1 simple `learn_about_user(statement)` tool.
- **Shared Memory**: All users contribute to the same knowledge base stored in `memory::shared`.
- **Robust Responses**: Added fallbacks to ensure the API always returns meaningful strings.

## How to Run (Windows PowerShell)

Prerequisites: Python 3.10+, Node 18+, PostgreSQL running and accessible.

- **Backend** (from `backend/`):
```powershell
python -m uvicorn web_api:app --reload --port 8000
```

- **Frontend** (from `frontend/`):
```powershell
npm install
npm run dev
```

Open http://localhost:3000 and connect with any `user_id` (e.g., "user_001", "alice", "bob").

Try teaching the bot:
- "My favorite color is blue"
- "I work at Google"
- "I love hiking on weekends"

Then ask questions like "What's my favorite color?" or just chat naturally.

## Environment

Create a `.env` in `backend/` with at least:
```
GOOGLE_API_KEY=your_key
DB_URL=postgresql://user:password@localhost:5432/your_db
```

`src/core/config.py` will validate these at runtime.

## API Endpoints

- POST `/api/auth` → `{ session_id, user_id, is_owner, message }`
- POST `/api/chat/{session_id}` → `{ response, session_id }`
- GET `/api/session/{session_id}/info` → Session snapshot
- DELETE `/api/session/{session_id}` → End session
- GET `/api/health` → Health + active sessions

## Testing Notes

- Quick Demo: 
  - Say: "My favorite color is blue" → bot learns it
  - Ask: "What's my favorite color?" → bot answers "blue"
  - Say: "I work at Google" → bot learns job info
  - Ask: "Where do I work?" → bot recalls Google

- Unit tests available in `backend/tests/`:
  - `test_user_info_tool.py`: Tests the learn tool's heuristic extraction
  - `test_bot.py`: Tests bot initialization and simplified behavior

## Known Limitations / Next Steps

- Could add `list_facts()` and `search_facts(query)` tools for better memory retrieval.
- Heuristic extraction is basic - could be enhanced with more patterns.
- Consider adding fact categories or tagging for better organization.
- Add more comprehensive unit/integration tests and CI.
- The bot instruction could be tuned for even more natural conversations.

## Folder Map

- `backend/` — FastAPI + ADK bot with simple memory tool
- `frontend/` — Next.js chat UI
- `adk-python/` — Google ADK reference documentation

---

The system is now focused on simplicity: one tool that learns anything, persistent memory for all users, and natural conversation without artificial barriers. See `src/tools/user_info_tool.py` for the learn tool implementation.
