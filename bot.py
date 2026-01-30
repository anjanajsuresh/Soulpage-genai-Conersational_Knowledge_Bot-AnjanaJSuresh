"""
Conversational Knowledge Bot - General Purpose Wikipedia Search Bot
Memory, Wikipedia Search, and Conversational Flow

Handles ANY knowledge-based question from Wikipedia dynamically.
"""

import os
import sys
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import deque

# Wikipedia import
import wikipedia
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


class ConversationMemory:
    """Simple conversation memory for storing chat history."""
    
    def __init__(self, max_history: int = 10):
        self.history = deque(maxlen=max_history)
        self.last_user_query = None
    
    def save_context(self, user_input: str, bot_response: str):
        self.history.append({
            "user": user_input,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        self.last_user_query = user_input
    
    def load_memory(self) -> str:
        if not self.history:
            return ""
        lines = []
        for entry in self.history:
            lines.append(f"User: {entry['user']}")
            lines.append(f"Bot: {entry['bot']}")
        return "\n".join(lines)
    
    def get_last_user_input(self) -> str:
        return self.last_user_query or ""
    
    def clear(self):
        self.history.clear()
        self.last_user_query = None


class KnowledgeBot:
    """Main conversational bot with memory and general Wikipedia search."""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self._greet()
    
    def _greet(self):
        print(f"{Fore.CYAN}{Style.BRIGHT}=" * 60)
        print(f"CONVERSATIONAL KNOWLEDGE BOT")
        print(f"Memory: Active | Wikipedia: Enabled")
        print(f"{Fore.CYAN}{Style.BRIGHT}=" * 60)
        print(f"{Fore.GREEN} Ready! Ask me anything factual.{Style.RESET_ALL}\n")
    
    def process_query(self, query: str) -> str:
        query = query.strip()
        
        if not query:
            return "Please ask a question."
        
        # Handle special commands
        if query.lower() in ["hi", "hello", "hey"]:
            return self._handle_greeting()
        
        if query.lower() in ["help", "?"]:
            return self._get_help()
        
        if "thank" in query.lower():
            return self._handle_thanks()
        
        # Process the query 
        response = self._search_wikipedia(query)
        
        # Save to conversation memory
        self.memory.save_context(query, response)
        
        return response
    
    def _clean_query(self, query: str) -> str:
        """Clean query by removing question words and prefixes."""
        query = query.strip()
        
        prefixes = [
            "who is", "who was", "who are", "who does",
            "what is", "what was", "what are", "what does",
            "where is", "where was", "where are", "where does",
            "when is", "when was", "when are", "when does",
            "why is", "why was", "why are", "why does",
            "how is", "how was", "how are", "how does",
            "tell me about", "tell me more about", "describe",
            "explain", "information about", "details about",
            "give me information about", "i want to know about"
        ]
        
        query_lower = query.lower()
        for prefix in prefixes:
            if query_lower.startswith(prefix):
                query = query[len(prefix):].strip()
                query_lower = query.lower()
                break
        
        return query
    
    def _search_wikipedia(self, query: str) -> str:
        """General Wikipedia search that handles ANY knowledge question."""
        try:
            # Clean the query
            clean_query = self._clean_query(query)
            
            if not clean_query:
                return f"Please provide a specific topic to search for."
            
            search_results = []
            
            # Strategy 1: Try clean query
            try:
                search_results = wikipedia.search(clean_query, results=10)
            except:
                pass
            
            # Strategy 2: Try original query
            if not search_results:
                try:
                    search_results = wikipedia.search(query, results=10)
                except:
                    pass
            
            # Strategy 3: Try key terms
            if not search_results:
                words = query.split()
                if len(words) >= 2:
                    for i in range(min(3, len(words))):
                        key_terms = ' '.join(words[i:i+3])
                        try:
                            results = wikipedia.search(key_terms, results=10)
                            if results:
                                search_results = results
                                break
                        except:
                            continue
            
            if not search_results:
                return f"Could not find information about '{query}'.\n\n Try rephrasing your question or checking the spelling."
            
            # Try to get summary for the best match
            for result in search_results[:5]:
                try:
                    page = wikipedia.page(result, auto_suggest=True)
                    summary = wikipedia.summary(result, sentences=5, auto_suggest=True)
                    
                    title = page.title
                    url = page.url
                    
                    response = f"**{title}**\n\n{summary}\n\n"
                    response += f" [Read more]({url})"
                    
                    return response
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Try each option from disambiguation
                    for option in e.options[:5]:
                        try:
                            page = wikipedia.page(option)
                            summary = wikipedia.summary(option, sentences=5)
                            
                            title = page.title
                            url = page.url
                            
                            response = f"**{title}**\n\n{summary}\n\n"
                            response += f" [Read more]({url})\n\n"
                            response += f" Multiple matches found. Showing the most relevant result."
                            
                            return response
                            
                        except:
                            continue
                            
                except:
                    continue
            
            return f" Could not find information about '{query}'.\n\n Try being more specific in your question."
            
        except Exception as e:
            return f" Error: {str(e)}. Please try again."
    
    def _handle_greeting(self) -> str:
        return """ Hello! I'm your Conversational Knowledge Bot.

I can:
- Answer any factual question using Wikipedia
- Search for information about people, places, concepts, history, science, and more
- Remember our conversation for context

Try asking:
- "Who is the CEO of Google?"
- "What is quantum computing?"
- "Where is the Taj Mahal?"
- "When was World War II?"
- "Who painted the Mona Lisa?"
- "What is the capital of Australia?"

What would you like to know?"""
    
    def _handle_thanks(self) -> str:
        return " You're welcome! Feel free to ask more questions anytime."
    
    def _get_help(self) -> str:
        return """ **HELP - Conversational Knowledge Bot**

**What I can do:**
• Answer ANY factual question using Wikipedia
• Search for information about people, places, events, concepts
• Explain topics and provide detailed information
• Provide source links for verification

**Example Questions:**
• Who is the CEO of OpenAI?
• What is artificial intelligence?
• Where is the Amazon River located?
• When did World War II end?
• Who discovered penicillin?
• What is the population of Tokyo?
• Who wrote Romeo and Juliet?
• What is photosynthesis?
• Where is the Great Barrier Reef?
• Who is the President of France?

**Tips:**
• Be specific with names and topics
• Use full names for people
• Check spelling of proper nouns

Type 'quit' to exit anytime!"""
    
    def clear_memory(self):
        self.memory.clear()
        print(f"{Fore.YELLOW} Memory cleared!{Style.RESET_ALL}")
    
    def get_memory(self) -> str:
        return self.memory.load_memory()


# Alias for compatibility
WikiBot = KnowledgeBot
SimpleKnowledgeBot = KnowledgeBot


def main():
    bot = KnowledgeBot()
    print("Type 'help' for instructions, 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input(f"{Fore.BLUE}You: {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["quit", "exit"]:
                print(f"\n{Fore.CYAN} Goodbye!{Style.RESET_ALL}")
                break
            
            response = bot.process_query(user_input)
            
            print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Bot: {Style.RESET_ALL}{response}")
            print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN} Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED} Error: {str(e)}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    
    main()
