# Ai-Agent — Project Status (Aug 2025)

## Overview

This repo hosts a multi-user AI assistant built with FastAPI + Google ADK (Gemini 2.0 Flash) and a Next.js UI. The assistant represents a single owner (e.g., "zhen") and persists facts about the owner in a shared session. Behavior changes based on who is speaking:

- Owner: can teach/update/delete facts (setter tools) and retrieve them (getter tools).
- Guests: can only retrieve/search facts (getter tools); no learning or changes.

## Architecture

- Backend: `backend/`
  - FastAPI app (`web_api.py`) exposes `/api/auth`, `/api/chat/{session_id}`, `/api/session/*`, `/api/health`.
  - Bot (`src/core/bot.py`) uses Google ADK Agent + Runner and a `DatabaseSessionService` for persistence.
  - Unified tools (`src/tools/user_info_tool.py`) implement setter/getter APIs.
  - Tool manager (`src/tools/tool_manager.py`) assigns the right tool set based on role (owner vs guest).
  - Config (`src/core/config.py`) reads `GOOGLE_API_KEY` and `DB_URL`; model is `gemini-2.0-flash`.
  - Sessions: all users share a single memory keyed by `{owner}_bot_shared_knowledge`.

- Frontend: `frontend/`
  - Next.js 15 app providing a chat UI where you enter `user_id` and `bot_owner_id` and chat with the bot.

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

Open http://localhost:3000 and connect with:
- `user_id = zhen`, `bot_owner_id = zhen` (Owner mode)
- `user_id = user_001`, `bot_owner_id = zhen` (Guest mode)

## Environment

Create a `.env` in `backend/` with at least:
```
GOOGLE_API_KEY=your_key
DB_URL=postgresql://user:password@localhost:5432/your_db
```

`src/core/config.py` will validate these at runtime.

## API Endpoints

- POST `/api/auth` → `{ session_id, user_id, bot_owner_id, is_owner }`
- POST `/api/chat/{session_id}` → `{ response, session_id, is_owner }`
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

- ADK response sometimes includes function calls without text; mitigated with fallbacks.
- Prompting could be tuned further to improve natural guest queries.
- Consider surfacing tool results even when the model returns function_call-only outputs by directly reading tool results from ADK events.
- Add more comprehensive unit/integration tests and CI.

## Folder Map

- `backend/` — FastAPI + ADK bot and tools
- `frontend/` — Next.js chat UI
- `zhen-bot/` — Legacy/archived bot files (kept for reference)

---

Maintainers: see `src/core/bot.py` for agent behavior and `src/tools/user_info_tool.py` for the unified tool. The system currently targets a single owner-bot with role-aware capabilities.
