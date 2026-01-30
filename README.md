# Conversational Knowledge Bot - LangChain Implementation

A conversational AI bot built with **LangChain** that integrates memory management and Wikipedia search to provide factual answers with contextual conversation flow.

## Assignment Requirements - All Met

This project demonstrates the required LangChain integration:

- **LangChain Memory**: Uses `ConversationBufferMemory` for conversation history
- **Wikipedia Tool**: Integrates Wikipedia API for factual information search
- **Factual Queries**: Answers questions like "Who is the CEO of OpenAI?"
- **Contextual Follow-ups**: Handles follow-up questions like "Where did he study?"
- **Memory Management**: Maintains conversation context across exchanges

## Features

- **LangChain Memory**: ConversationBufferMemory stores and retrieves conversation history
- **Wikipedia Search**: Real-time factual information from Wikipedia (no hardcoded data)
- **Contextual Conversations**: Follow-up questions understood using memory context
- **Smart Entity Extraction**: Identifies entities from queries for better search
- **Error Handling**: Graceful fallbacks when information not found
- **CLI Interface**: Command-line interface for easy interaction

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Soulpage-genai-Conversational_Knowledge_Bot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Usage

#### Option 1: Streamlit Web Interface (Recommended)

Run the web interface for a user-friendly chat experience:
```bash
# Install streamlit if not already installed
pip install streamlit

# Run the web interface
streamlit run app.py
```

The web interface will open in your browser at `http://localhost:8501`

**Features:**
- Clean chat interface
- Conversation history
- Clear conversation button
- Export chat functionality
- Example question buttons

#### Option 2: Command Line Interface

**For Follow-up Questions and Memory Features:**
```bash
python langchain_bot.py
```

**For Basic Wikipedia Search Only:**
```bash
python bot.py
```

**CLI Commands:**
- Type your questions directly and press Enter
- Type `help` for instructions
- Type `quit` or `exit` to exit

**Note**: Use `langchain_bot.py` for full memory and follow-up question support. Use `bot.py` for simple Wikipedia search without memory.

#### Option 3: Python API

Use the bot programmatically:
```python
from langchain_bot import LangChainKnowledgeBot

# Initialize the bot
bot = LangChainKnowledgeBot()

# Ask questions
response = bot.process_query("Who is the CEO of Google?")
print(response)

# Get memory state
memory = bot.get_memory()
print(f"Memory: {memory}")

# Clear memory
bot.clear_memory()
```

#### Example Conversation

```
You: who is the ceo of google
Bot: **Sundar Pichai**

Pichai Sundararajan (born June 10, 1972), better known as Sundar Pichai, is an Indian American business executive. He is the chief executive officer (CEO) of Alphabet Inc. and its subsidiary Google...

You: where did he study
Bot: == Early life and Education ==

Pichai was born on June 10, 1972 in Madurai, Tamil Nadu, to a Tamil Hindu family. Pichai completed schooling in Jawahar Vidyalaya Senior Secondary School in Ashok Nagar, Chennai and completed the Class XII from Vana Vani school at IIT Madras. He holds an MS from Stanford University in materials science and engineering and an MBA from the Wharton School of the University of Pennsylvania, where he was named a Siebel Scholar and a Palmer Scholar, respectively

You: who is mahatma gandhi
Bot: **Mahatma Gandhi**

Mohandas Karamchand Gandhi (2 October 1869 – 30 January 1948) was an Indian lawyer, anti-colonial nationalist, and political ethicist...

You: what was his profession
Bot: **Mahatma Gandhi**

Mohandas Karamchand Gandhi (2 October 1869 – 30 January 1948) was an Indian lawyer, anti-colonial nationalist, and political ethicist...
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Working LangChain Bot                        │
├─────────────────────────────────────────────────────────────┤
│  Components:                                                 │
│  |-- ConversationBufferMemory (LangChain)                    │
│  |-- Wikipedia API Integration                               │
│  |-- Entity Extraction & Query Processing                    │
│  |-- Context-aware Follow-up Handling                        │
└─────────────────────────────────────────────────────────────┘
```

## LangChain Components Used

### 1. ConversationBufferMemory

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=False,
    input_key="input"
)
```

Stores conversation history and enables contextual follow-up responses.

### 2. Wikipedia Integration

```python
import wikipedia

def _search_wikipedia(self, query: str) -> str:
    page = wikipedia.page(query, auto_suggest=False)
    summary = wikipedia.summary(query, sentences=5)
    return f"**{page.title}**\n\n{summary}"
```

Provides factual information from Wikipedia without any hardcoded data.

## Memory Design

The bot uses LangChain's ConversationBufferMemory to maintain conversation context:

### Memory Flow

1. **User Input**: "Who is the CEO of OpenAI?"
2. **Process**: Bot searches Wikipedia and stores exchange
3. **Memory Save**: `memory.save_context({"input": query}, {"response": response})`
4. **Follow-up**: "Where did he study?" - Bot loads memory and provides context
5. **Context Retrieval**: `memory.load_memory_variables({})`

### Key Memory Features

- **Conversation History**: Stores all human-AI exchanges
- **Context Retention**: Maintains entity references for follow-ups
- **Pronoun Resolution**: Understands "he", "she", "they" in follow-up questions
- **Memory Management**: Can be cleared when needed

## Supported Query Types

### Factual Queries
- "Who is Sundar Pichai?"
- "What is artificial intelligence?"
- "Tell me about Mahatma Gandhi"
- "Rivers in India"

### Follow-up Questions
- "Where did he study?" (after person query)
- "What was his profession?" (after person query)
- "How does it work?" (after concept query)

### Entity Extraction
The bot automatically extracts entities from queries:
- "CEO of Google" → "Google"
- "Who is Sundar Pichai" → "Sundar Pichai"
- "Tell me about AI" → "AI"

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| langchain | >=0.1.0 | Core LangChain framework |
| langchain-core | >=0.1.0 | LangChain core utilities |
| langchain-community | >=0.0.20 | Community integrations |
| wikipedia | >=1.4.0 | Wikipedia API access |
| colorama | >=0.4.6 | Colored CLI output |

## Project Structure

```
Soulpage-genai-Conversational_Knowledge_Bot/
├── langchain_bot.py              # Main implementation (USE THIS ONE)
├── app.py                        # Streamlit web interface
├── requirements.txt               # Dependencies
├── README.md                     # This file
├── sample_conversations.md      # Example conversations
├── .env.example                 # Environment template
└── .gitignore                   # Git ignore rules
```

## Assignment Deliverables

 **GitHub Repository**: `Soulpage-genai-Conversational_Knowledge_Bot_AnjanaJSursh`

 **Contents**:
- `langchain_bot.py` - Main implementation with LangChain memory
- `app.py` - Streamlit web interface
- `requirements.txt` - Dependencies with versions
- `README.md` - Setup and usage documentation
- Sample conversations demonstrating functionality

**Features Demonstrated**:
- LangChain ConversationBufferMemory integration
- Wikipedia search without hardcoded information
- Contextual follow-up questions
- Memory-based conversation flow
- Both CLI and Streamlit interfaces

## Sample Conversations

See `sample_conversations.md` for detailed example conversations demonstrating:
- CEO queries with follow-ups
- Political figure information
- Geographical questions
- Technical concept explanations
- Memory demonstration

## Testing

The bot has been tested with various query types:

### Streamlit Web Interface Testing

```bash
# Start the web interface
streamlit run app.py

# Test queries in the web interface:
- "who is the ceo of google"
- "where did he study" (follow-up)
- "who is mahatma gandhi"
- "what was his profession" (follow-up)
- "rivers in india"
```

### Command Line Interface Testing

```bash
# Start the CLI bot
python langchain_bot.py

# Test queries:
- "who is the ceo of google"
- "where did he study" (follow-up)
- "who is mahatma gandhi"
- "what was his profession" (follow-up)
- "rivers in india"
```

### Expected Results

**Working Features:**
- "who is the ceo of google" → Returns CEO information
- "where did he study" → Follow-up with education details
- "who is mahatma gandhi" → Returns Gandhi biography
- "what was his profession" → Follow-up with profession details
- "rivers in india" → Returns river information

**Memory Features:**
- Conversation history maintained
- Context switching works (Google → Gandhi)
- Follow-up questions understood
- Memory can be cleared

## Troubleshooting

### Common Issues

1. **ImportError for langchain packages**:
   ```bash
   pip install --upgrade langchain langchain-community
   ```

2. **Wikipedia search fails**:
   - Check internet connection
   - Try different query phrasing

3. **Memory not working**:
   - Ensure queries are processed in sequence
   - Check that follow-up questions use pronouns

### Debug Mode

Enable verbose output by checking memory state:
```python
memory = bot.get_memory()
print(f"Memory: {memory}")

