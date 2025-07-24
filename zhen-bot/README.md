# 🤖 Zhen Bot - Your Personal Learning AI Assistant

Zhen Bot is a personalized AI assistant built with Google's Agent Development Kit (ADK) that learns from your interactions and becomes increasingly tailored to your preferences, communication style, and needs.

## ✨ Features

- **🧠 Active Learning**: Automatically learns your preferences, interests, and personality traits
- **💾 Persistent Memory**: Remembers everything across conversations using SQLite database
- **🎯 Personalized Responses**: Adapts communication style based on learned preferences
- **📝 Conversation Memory**: Remembers important topics and context from past discussions
- **🔧 Context Awareness**: Tracks current projects, goals, and personal context
- **📊 Learning Summary**: View what the bot has learned about you

## 🏗️ Architecture

The bot uses a sophisticated learning system with several specialized tools:

### Learning Tools
- **`learn_about_user`**: Stores factual information about you in categorized knowledge base
- **`update_user_preference`**: Tracks specific preferences (communication style, tools, etc.)
- **`remember_conversation_topic`**: Remembers important discussion topics and key points
- **`update_personal_context`**: Tracks current situation, projects, mood, goals
- **`get_my_knowledge_summary`**: Provides overview of learned information

### State Management
- **Knowledge Base**: Categorized facts about you with timestamps
- **User Preferences**: Your preferred communication styles, tools, approaches
- **Personal Context**: Current projects, goals, mood, challenges
- **Conversation Memory**: Important topics and discussions (last 50)
- **Interaction History**: Track of all conversations with metadata

## 🚀 Getting Started

### Prerequisites

1. **Python 3.9+**
2. **Google API Key** - Get one from [Google AI Studio](https://aistudio.google.com/apikey)
3. **Virtual Environment** (recommended)

### Installation

1. **Set up virtual environment** (if not already done):
   ```bash
   # From the main project directory
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

 2. **Install dependencies**:
    ```bash
    # Install the ADK and required packages for Zhen Bot
    pip install -r requirements.txt
    ```

3. **Configure environment**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Google API key
   # GOOGLE_API_KEY=your_actual_api_key_here
   ```

### Running Zhen Bot

```bash
# Navigate to the zhen-bot directory
cd zhen-bot

# Run the bot
python main.py
```

## 💬 How to Use

### Starting a Conversation
When you first run Zhen Bot, it will create a new learning session. In subsequent runs, it will remember your previous conversations.

### Learning Process
Simply chat naturally! The bot will:
- **Automatically detect** preferences and interests you mention
- **Ask follow-up questions** to learn more about you
- **Store information** using its learning tools
- **Reference past conversations** to build context

### Special Commands
- **`summary`** - See what the bot has learned about you
- **`help`** or **`commands`** - Show available commands
- **`exit`**, **`quit`**, **`bye`** - End conversation and show learning summary

### What to Share
The bot learns best when you share:
- **Professional background** and expertise areas
- **Personal interests** and hobbies
- **Communication preferences** (formal vs. casual, detail level, etc.)
- **Current projects** and goals
- **Problem-solving approaches** you prefer
- **Tools and technologies** you use
- **Values and personality traits**

## 📈 Learning Examples

The bot will learn things like:

```
🧠 Knowledge Base:
   • Professional Background: "Software engineer with 5 years experience"
   • Interests: "Loves hiking and photography"
   • Current Projects: "Building a mobile app for fitness tracking"

⚙️ Preferences:
   • Communication Style: "Prefers concise, technical explanations"
   • Tools: "Uses VS Code and prefers Python for backend development"
   • Meeting Style: "Likes agenda-driven meetings with clear action items"

📝 Conversation Memory:
   • "AI Development Kit discussion": Key points about learning ADK patterns
   • "Mobile App Architecture": Discussed React Native vs Flutter pros/cons
```

## 🗄️ Data Storage

Zhen Bot uses SQLite database for persistent storage:
- **Database File**: `zhen_bot_memory.db` (created automatically)
- **Location**: Same directory as `main.py`
- **Data Included**: All learned information, preferences, and conversation history
- **Privacy**: Stored locally on your machine only

## 🔧 Customization

### Changing Database Location
Edit `.env` file:
```env
DB_URL=sqlite:///./custom_path/zhen_bot_memory.db
```

### Modifying Learning Behavior
Edit `agent.py` to:
- Add new learning tools
- Modify learning categories
- Adjust conversation memory limits
- Change personality traits

### Adding New Capabilities
The bot is built on ADK, so you can:
- Add new tools for specific tasks
- Integrate with external APIs
- Create sub-agents for specialized tasks
- Add multi-modal capabilities

## 🛡️ Privacy & Security

- **Local Storage**: All data stays on your machine
- **No External Sharing**: Your information is never sent to third parties
- **Consent-Based Learning**: Only learns what you willingly share
- **Data Control**: You can delete the database file to reset all learned data

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**:
   ```bash
   # Make sure you've activated the virtual environment
   source .venv/bin/activate  # Mac/Linux
   .venv\Scripts\activate     # Windows
   
       # Install dependencies
    pip install -r requirements.txt
   ```

2. **"API key not found" errors**:
   - Check that `.env` file exists in the `zhen-bot` directory
   - Verify your Google API key is correctly set in the `.env` file
   - Ensure no extra spaces around the API key

3. **Database permission errors**:
   - Make sure you have write permissions in the directory
   - Try running from a different directory
   - Check disk space availability

4. **Session/memory issues**:
   - Delete `zhen_bot_memory.db` to start fresh
   - Check database file isn't corrupted
   - Restart the bot application

### Getting Help

If you encounter issues:
1. Check the error messages for specific guidance
2. Verify your environment setup matches the requirements
3. Try creating a fresh environment and reinstalling dependencies
4. Check that your Google API key has proper permissions

## 🎯 Future Enhancements

Potential improvements:
- **Multi-modal Learning**: Process images, documents, voice
- **Integration Tools**: Connect with calendar, email, notes apps
- **Advanced Analytics**: Deeper insights into conversation patterns
- **Export/Import**: Backup and restore learned data
- **Team Sharing**: Share learned preferences with other AI assistants

## 📚 Based on ADK Examples

This bot incorporates patterns from several ADK examples:
- **Persistent Storage** (Example 6): Database session management
- **Stateful Agents** (Example 8): State tracking across conversations
- **Custom Tools**: Function-based learning tools
- **Session Management**: Proper ADK session handling

---

**Happy Learning! 🎉**

Zhen Bot is designed to become your most helpful AI companion by truly understanding you through our conversations. The more you interact, the better it becomes at assisting you in your unique style and context. 