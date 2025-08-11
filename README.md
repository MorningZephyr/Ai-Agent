# Ai-Agent — Simple## Current Be## Recent Changes

- **Simplified Architecture**: Remo## Testing Notes

- Quick Demo: 
  - Say: "My favorite color is blue" → bot learns it
  - Ask: "What's my favorite color?" → bot answers "blue"
  - Say: "I work at Google" → bot learns job info
  - Ask: "Where do I work?" → bot recalls Google

- Unit tests available in `backend/tests/`:
  - `test_user_info_tool.py`: Tests the learn tool's heuristic extraction
  - `test_bot.py`: Tests bot initialization and simplified behaviorguest complexity - now anyone can teach the bot.
- **Single Tool**: Replaced 6 complex tools with 1 simple `learn_about_user(statement)` tool.
- **Heuristic Extraction**: Automatically extracts facts from natural language ("My X is Y" patterns).
- **Shared Memory**: All users contribute to the same knowledge base stored in `memory::shared`.
- **Robust Responses**: Added fallbacks to ensure the API always returns meaningful strings.

- The bot has 1 tool: `learn_about_user(statement)` that stores any statement and extracts key/value facts.
- Teaching examples: "My favorite color is blue", "I work at Google", "I love hiking"
- The tool automatically extracts structured facts when possible (e.g., "My X is Y" becomes key=X, value=Y).
- All statements are stored in `facts._raw` and extracted facts in `facts.{key}`.
- The bot's instructions encourage natural conversation while using the learn tool for new information.y Bot (Aug 2025)

## Overview

This repo hosts a simple AI assistant built with FastAPI + Google ADK (Gemini 2.0 Flash) and a Next.js UI. The bot learns anything you tell it and stores facts in persistent memory. No authentication barriers - anyone can teach the bot new information.

## Architecture

- Backend: `backend/`
  - FastAPI app (`web_api.py`) exposes `/api/auth`, `/api/chat/{session_id}`, `/api/session/*`, `/api/health`.
  - Bot (`src/core/bot.py`) uses Google ADK Agent + Runner and a `DatabaseSessionService` for persistence.
  - Single tool (`src/tools/user_info_tool.py`) implements `learn_about_user(statement)` to store any facts.
  - Tool manager (`src/tools/tool_manager.py`) exposes the learn tool to the bot.
  - Config (`src/core/config.py`) reads `GOOGLE_API_KEY` and `DB_URL`; model is `gemini-2.0-flash`.
  - Sessions: all users share a single memory session `memory::shared`.

- Frontend: `frontend/`
  - Next.js 15 app providing a chat UI where you enter a `user_id` and chat with the bot.

## Current Behavior

- Owner gets 6 tools: `set_info`, `update_info`, `delete_info`, `get_info`, `list_all_info`, `search_info`.
- Guests get 3 tools: `get_info`, `list_all_info`, `search_info`.
- The agent dynamically refreshes its tools per message using the current speaker.
- Tool usage is encouraged by the bot’s instructions (e.g., use `get_info('favorite_color')` when asked about favorite color).

## Recent Fixes

- Hardened responses to ensure the API always returns a string (prevents `None` from causing 500s)
  - `bot.chat()` now returns a friendly fallback when no text parts are produced.
  - `web_api.py` coerces non-string/empty bot responses to role-aware messages.
- Added a guard for guest setter-like messages (e.g., “it’s red”, “set …”):
  - Guests will receive a polite refusal: "I can't change Zhen's info for visitors. Please ask the owner to update it."

## How to Run (Windows PowerShell)

Prereqs: Python 3.10+, Node 18+, PostgreSQL running and accessible.

- Backend (from `backend/`):
```powershell
python -m uvicorn web_api:app --reload --port 8000
```

- Frontend (from `frontend/`):
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

- Quick E2E: 
  - Owner: "My favorite color is blue" → bot should learn it.
  - Guest: "What is Zhen's favorite color?" → bot answers "blue".
  - Guest: "it's red" → bot refuses and does not update.

- Python test scripts are available in `backend/`:
  - `test_unified_tools.py`: Owner vs Guest tool counts and flows.
  - `test_guest_access.py`: Guest can see owner’s stored info.

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
