
# AI Representative — Enhanced Profile Bot (Jan 2025)

## Overview

This repo hosts an AI representative system built with FastAPI + Google ADK (Gemini 2.0 Flash) and a Next.js UI. The bot represents a single person in the digital world, using LLM-driven fact extraction to learn and recall information about them. Anyone can teach the bot facts about the represented person and ask questions to get informed responses.

## Architecture

- **Backend**: `backend/`
  - FastAPI app (`web_api.py`) exposes `/api/auth`, `/api/chat/{session_id}`, `/api/session/*`, `/api/health`.
  - Bot (`src/core/bot.py`) uses Google ADK Agent + Runner with a dedicated profile session for the represented person.
  - Enhanced tools (`src/tools/user_info_tool.py`) with LLM-driven fact extraction, validation, and retrieval capabilities.
  - Tool manager (`src/tools/tool_manager.py`) exposes three tools: `learn_about_user()`, `list_known_facts()`, `search_facts()`.
  - Config (`src/core/config.py`) reads `GOOGLE_API_KEY`, `DB_URL`, `REPRESENTED_USER_ID`, `REPRESENTED_NAME`.
  - Sessions: dedicated profile session `profile::{REPRESENTED_USER_ID}` for the person being represented.

- **Frontend**: `frontend/`
  - Next.js 15 app providing a chat UI where you enter a `user_id` and chat with the bot.

- **ADK Reference**: `adk-python/` — Google ADK documentation and samples.

## Current Behavior

- **Owner/Visitor Permissions**: Only the represented person (owner) can teach new facts. Others can ask questions about existing knowledge.
- **Enhanced Learning**: `learn_about_user(statement)` uses LLM-driven extraction for owners to store multiple facts from complex statements.
- **Smart Retrieval**: `list_known_facts()` and `search_facts(query)` available to everyone for comprehensive information access.
- **Robust Storage**: Facts include confidence levels, timestamps, audit trails, and collision-resistant key normalization.
- **Validation**: Content validation prevents storing inappropriate or invalid information.
- **Owner examples**: "I work at Google as a software engineer and love hiking" → extracts profession, employer, and hobby facts.
- **Visitor examples**: "What do you know about their work?" → searches and returns work-related facts.
- **Representative Mode**: Dedicated profile session `profile::{REPRESENTED_USER_ID}` with permission-based access control.

## Recent Changes

- **LLM-Driven Extraction**: Advanced fact extraction using Gemini 2.0 Flash with confidence scoring and multi-fact support.
- **Enhanced Tool Suite**: Three specialized tools for learning, listing, and searching facts about the represented person.
- **Representative Architecture**: Dedicated profile sessions for individual representation rather than shared memory.
- **Robust Validation**: Content filtering, key collision handling, and fact validation before storage.
- **Audit Trail**: Complete provenance tracking with timestamps and source statements.
- **Structured Storage**: Rich fact metadata including confidence, timestamps, and original context.

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

**As the Owner** (check "I am the person being represented"):
- "I work at Google as a software engineer and love hiking"
- "My favorite color is blue and I studied at Stanford"
- "I play guitar and enjoy cooking on weekends"

**As a Visitor** (uncheck the owner box):
- "What do you know about their work?"
- "Tell me about their hobbies"
- "List everything you know about this person"

## Environment

Create a `.env` in `backend/` with:
```
GOOGLE_API_KEY=your_google_api_key
DB_URL=postgresql://user:password@localhost:5432/your_db
REPRESENTED_USER_ID=your_username
REPRESENTED_NAME=Your Full Name
```

`src/core/config.py` will validate these at runtime. The `REPRESENTED_USER_ID` and `REPRESENTED_NAME` configure whose digital representative this bot will be.

## API Endpoints

- POST `/api/auth` → `{ session_id, user_id, is_owner, message }`
- POST `/api/chat/{session_id}` → `{ response, session_id }`
- GET `/api/session/{session_id}/info` → Session snapshot
- DELETE `/api/session/{session_id}` → End session
- GET `/api/health` → Health + active sessions

## Testing Notes

- **Owner Mode Testing** (with checkbox checked):
  - Say: "I work at Google as a software engineer and my favorite color is blue" → bot extracts multiple facts
  - Say: "I love hiking and play guitar" → stores hobbies with confidence scoring
  - Ask: "What do you know about me?" → bot lists your stored facts

- **Visitor Mode Testing** (checkbox unchecked):
  - Ask: "What do you know about their work?" → bot searches and responds with work-related facts
  - Say: "List everything you know about this person" → bot uses list_known_facts() tool
  - Try: "They like pizza" → bot politely refuses and explains only owner can teach facts

- **Permission System**:
  - `learn_about_user()`: Only available to owners (person being represented)
  - `list_known_facts()` & `search_facts()`: Available to everyone
  - Bot instruction enforces permission boundaries

- Unit tests available in `backend/tests/`:
  - `test_user_info_tool.py`: Tests enhanced extraction, validation, and retrieval
  - `test_bot.py`: Tests representative bot initialization and behavior

## Known Limitations / Next Steps

- **Semantic Search**: Current search uses keyword matching; could enhance with vector embeddings for semantic search.
- **Fact Relationships**: Could add support for fact relationships and dependencies (e.g., job history timeline).
- **Multi-modal Support**: Could extend to learn from images, documents, or other media about the person.
- **Confidence Tuning**: Fine-tune confidence thresholds and validation rules based on usage patterns.
- **Privacy Controls**: Add mechanisms to mark certain facts as private or sensitive.
- **Export/Import**: Add functionality to export/import profile data for backup or migration.

## Folder Map

- `backend/` — FastAPI + ADK bot with enhanced memory management and LLM-driven fact extraction
- `frontend/` — Next.js chat UI for interacting with the AI representative
- `adk-python/` — Google ADK reference documentation and samples

---

The system focuses on intelligent representation: LLM-driven fact extraction, structured memory with audit trails, and comprehensive retrieval capabilities. The AI representative can learn complex information about a person and respond knowledgeably to questions. See `src/tools/user_info_tool.py` for the enhanced tool implementation.
