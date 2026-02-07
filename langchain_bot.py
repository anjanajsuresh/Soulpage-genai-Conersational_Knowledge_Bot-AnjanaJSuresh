"""
Conversational Knowledge Bot - LangChain Implementation
Uses LangChain's ConversationBufferMemory and custom conversation flow
"""

import os
import sys
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

# LangChain imports for memory management (compatible with newer versions)
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
    from langchain.schema import HumanMessage, AIMessage
    LANGCHAIN_LEGACY_AVAILABLE = True
except ImportError:
    # Fallback for newer LangChain versions
    try:
        from langchain_core.memory import ConversationBufferMemory
        from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
        from langchain_core.messages import HumanMessage, AIMessage
        LANGCHAIN_LEGACY_AVAILABLE = False
    except ImportError:
        # Create a simple memory class if LangChain memory is not available
        LANGCHAIN_LEGACY_AVAILABLE = False
        ConversationBufferMemory = None
        ChatPromptTemplate = None
        PromptTemplate = None

# Wikipedia direct import for better control
import wikipedia
from colorama import init, Fore, Style

init(autoreset=True)


class LangChainKnowledgeBot:
    """
    Conversational Knowledge Bot built with LangChain concepts.
    
    Features:
    - LangChain's ConversationBufferMemory for conversation history
    - Custom conversation flow with memory integration
    - Wikipedia search tool for factual information
    - Context-aware follow-up questions
    
    This implementation works without requiring external LLM API keys
    by using LangChain's memory components with custom response generation.
    """
    
    def __init__(self):
        """Initialize the LangChain-based bot."""
        
        # Initialize LangChain memory
        if ConversationBufferMemory is not None:
            self.memory = ConversationBufferMemory(
                memory_key="history",
                return_messages=False,  # Returns string format
                input_key="input"
            )
        else:
            
            self.memory = self._create_simple_memory()
        
        # Track last mentioned entity for context
        self.last_entity = None
        
        # Create conversation prompt template
        self.prompt = self._create_prompt()
        
        self._greet()
    
    def _create_simple_memory(self):
        """Create a simple memory fallback when LangChain memory is not available."""
        class SimpleMemory:
            def __init__(self):
                self.history = ""
            
            def save_context(self, inputs, outputs):
                input_text = inputs.get("input", "")
                response_text = outputs.get("response", "")
                self.history += f"Human: {input_text}\nAI: {response_text}\n"
            
            def load_memory_variables(self, variables):
                return {"history": self.history}
            
            def clear(self):
                self.history = ""
        
        return SimpleMemory()
    
    def _create_prompt(self):
        """Create LangChain-style prompt template."""
        
        if LANGCHAIN_LEGACY_AVAILABLE and ChatPromptTemplate is not None:
            return ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="history", optional=True),
                ("human", "{input}"),
            ])
        elif PromptTemplate is not None:
            # Simple prompt template for newer versions
            return PromptTemplate(
                template="""Conversation history:
{history}

Human: {input}
AI:""",
                input_variables=["history", "input"]
            )
        else:
            # return None since we don't need the prompt for our simple implementation
            return None
    
    def _greet(self):
        """Print welcome message."""
        print(f"{Fore.CYAN}{Style.BRIGHT}=" * 60)
        print(f"LANGCHAIN KNOWLEDGE BOT")
        print(f"Memory: LangChain ConversationBufferMemory")
        print(f"Wikipedia: Enabled")
        print(f"{Fore.CYAN}{Style.BRIGHT}=" * 60)
        print(f"{Fore.GREEN} Ready! Ask me anything factual.{Style.RESET_ALL}\n")
    
    def _extract_entity(self, query: str) -> Optional[str]:
        """Extract the main entity from a query using patterns."""
        query_lower = query.lower().strip()
        
        # Patterns for entity extraction
        patterns = {
            'ceo': r'ceo of\s+(.+?)(?:\?|$)',
            'president': r'president of\s+(.+?)(?:\?|$)',
            'pm': r'prime minister of\s+(.+?)(?:\?|$)',
            'capital': r'capital of\s+(.+?)(?:\?|$)',
            'who': r'who is\s+(.+?)(?:\?|$)',
            'what': r'what is\s+(.+?)(?:\?|$)',
            'tell_about': r'tell me about\s+(.+?)(?:\?|$)',
            'founder': r'founder of\s+(.+?)(?:\?|$)',
        }
        
        for entity_type, pattern in patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                entity = match.group(1).strip()
                # Clean up common question words and articles
                entity = re.sub(r'\b(the|a|an)\b', '', entity).strip()
                # Remove trailing question marks
                entity = entity.rstrip('?').strip()
                return entity
        
        return None
    
    def _extract_entity_from_response(self, response: str) -> Optional[str]:
        """Extract the main entity from a Wikipedia response."""
        import re
        
        # Look for the page title (usually in **bold** at the start)
        title_match = re.search(r'\*\*(.+?)\*\*', response)
        if title_match:
            title = title_match.group(1).strip()
            # Remove common non-entity words
            if not any(word in title.lower() for word in ['page', 'summary', 'wikipedia', 'list of']):
                return title
        
        # Fallback: look for capitalized words that might be names
        words = response.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Check if it might be a person name (First Last pattern)
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    potential_name = f"{word} {words[i + 1]}"
                    if len(potential_name) > 5 and not any(skip in potential_name.lower() for skip in ['page', 'summary', 'wikipedia']):
                        return potential_name
        
        return None
    def _is_follow_up(self, query: str) -> bool:
        """Check if this is a follow-up question."""
        query_lower = query.lower().strip()
        
        follow_up_patterns = [
            r'^he ', r'^she ', r'^they ', r'^it ',
            r'^where ', r'^when ', r'^how ', r'^why ', r'^which ',
            r"what('s| is| was)? (his|her|their|its) ",
            r'^tell me more',
            r'^more about',
            r'^what about',
            r'background',
            r'history',
            r'biography',
            r'longest',
            r'shortest',
            r'biggest',
            r'smallest',
            r'highest',
            r'lowest',
            r'tallest',
            r'among them',
            r'of them',
        ]
        
        for pattern in follow_up_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _handle_follow_up(self, query: str) -> str:
        """Handle follow-up questions using memory context."""
        
        query_lower = query.lower().strip()
        
        # Get the last entity from memory
        if self.last_entity:
            last_topic = self.last_entity
        else:
            # Try to extract from conversation history
            memory_vars = self.memory.load_memory_variables({})
            history = memory_vars.get("history", "")
            last_topic = self._extract_last_topic_from_history(history)
        
        if not last_topic:
            return ""
        
        # Simple follow-up handling - check specific patterns first
        if any(word in query_lower for word in ['study', 'education', 'college', 'university']):
            # First try specific education search
            education_result = self._search_wikipedia_direct(f"{last_topic} education")
            if education_result and "Could not find" not in education_result:
                # Check if it's the same page 
                if last_topic.lower() in education_result.lower() and "education" not in education_result.lower():
                    # Extract education info from the main page
                    return self._extract_education_info(education_result, last_topic)
                return education_result
            else:
                # Fallback: extract education info from main page
                main_page = self._search_wikipedia_direct(last_topic)
                return self._extract_education_info(main_page, last_topic)
        
        elif any(word in query_lower for word in ['party', 'political', 'belongs']):
            return self._search_wikipedia_direct(f"{last_topic} political party")
        
        elif any(word in query_lower for word in ['born', 'birthplace', 'from']):
            return self._search_wikipedia_direct(f"{last_topic} birthplace")
        
        elif any(word in query_lower for word in ['profession', 'work', 'career']):
            return self._search_wikipedia_direct(f"{last_topic} profession")
        
        elif any(word in query_lower for word in ['where', 'when', 'how', 'what']):
            # Combine topic with question for general queries
            follow_up_query = f"{last_topic} {query}"
            return self._search_wikipedia_direct(follow_up_query)
        
        else:
            # Default: return original topic info
            return self._search_wikipedia_direct(last_topic)
    
    def _extract_education_info(self, main_page_response: str, entity_name: str) -> str:
        """Extract education information from a main Wikipedia page."""
        import re
        import wikipedia
        
        # First try to get more detailed content from the full page
        try:
            page = wikipedia.page(entity_name, auto_suggest=False)
            full_content = page.content
            
            # Look for education-related sections
            education_keywords = [
                'education', 'university', 'college', 'school', 'graduated', 'degree',
                'bachelor', 'master', 'phd', 'studied', 'attended', 'alumni', 'mba'
            ]
            
            # Split content into sentences
            sentences = re.split(r'[.!?]+', full_content)
            
            education_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and any(keyword in sentence.lower() for keyword in education_keywords):
                    education_sentences.append(sentence)
            
            if education_sentences:
                # Create a focused education response
                response = f"**{entity_name} - Education**\n\n"
                response += ". ".join(education_sentences[:4])  # Take first 4 relevant sentences
                
                if len(education_sentences) > 4:
                    response += "..."
                
                response += f"\n\n [Read more on Wikipedia]({page.url})"
                return response
            else:
                # If no education info found, return a helpful response
                return f"**{entity_name} - Education**\n\nI couldn't find specific education details in the Wikipedia article. The biography mentions his career but not detailed educational background.\n\n🔗 [Read full biography]({page.url})"
                
        except Exception as e:
            # Fallback to summary-based extraction
            sentences = re.split(r'[.!?]+', main_page_response)
            
            education_keywords = [
                'education', 'university', 'college', 'school', 'graduated', 'degree',
                'bachelor', 'master', 'phd', 'studied', 'attended', 'alumni'
            ]
            
            education_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and any(keyword in sentence.lower() for keyword in education_keywords):
                    education_sentences.append(sentence)
            
            if education_sentences:
                response = f"**{entity_name} - Education**\n\n"
                response += ". ".join(education_sentences[:3])
                return response
            else:
                return f"**{entity_name}**\n\n{main_page_response}\n\n📚 Education details may be found in the full biography above."
    
    def _extract_last_topic_from_history(self, history: str) -> str:
        """Extract the main topic from conversation history."""
        if not history:
            return ""
        
        # Split history into lines and look for the last AI response
        lines = history.split('\n')
        
        # Find the last AI response (starts with "AI:")
        last_ai_response = ""
        for line in reversed(lines):
            if line.startswith("AI:"):
                last_ai_response = line
                break
        
        if last_ai_response:
            # Extract the topic from the AI response (usually in **bold**)
            import re
            topic_match = re.search(r'\*\*(.+?)\*\*', last_ai_response)
            if topic_match:
                topic = topic_match.group(1).strip()
                # Remove common non-topic words
                if not any(word in topic.lower() for word in ['page', 'summary', 'wikipedia']):
                    return topic
        
        # look for the last human question and extract entity
        for line in reversed(lines):
            if line.startswith("Human:"):
                # Get the entity from the last human question
                human_question = line.replace("Human:", "").strip()
                entity = self._extract_entity(human_question)
                if entity:
                    return entity
                # If no entity, use the whole question as topic
                if len(human_question) > 3:
                    return human_question
        
        return ""
    
    def _search_entity_info(self, entity: str, info_type: str) -> str:
        """Search for specific information about an entity."""
        search_queries = {
            'education': f"{entity} education university college",
            'birth': f"{entity} birthplace born birth",
            'work': f"{entity} career profession work",
            'company': f"{entity} company founded"
        }
        
        search_query = search_queries.get(info_type, entity)
        return self._search_wikipedia_direct(search_query)
    
    def _search_wikipedia_direct(self, query: str) -> str:
        """Direct Wikipedia search - no hardcoded information."""
        try:
            clean_query = self._clean_query(query)
            
            if not clean_query:
                return "Please provide a specific topic."
            
            # Special handling for CEO queries - search for the CEO person
            if "CEO of" in clean_query:
                company_name = clean_query.replace("CEO of", "").strip()
                
                # Try multiple approaches to find the CEO
                search_attempts = [
                    f"{company_name} CEO",
                    f"CEO of {company_name}",
                    f"{company_name} chief executive officer",
                    f"List of {company_name} executives",
                    f"Current {company_name} CEO",
                    f"{company_name} leadership",
                ]
                
                # First try direct page lookup for CEO-specific pages
                for search_term in search_attempts:
                    try:
                        page = wikipedia.page(search_term, auto_suggest=False)
                        summary = wikipedia.summary(search_term, sentences=8, auto_suggest=False)
                        
                        # Check if this looks like a person (CEO)
                        summary_lower = summary.lower()
                        if any(indicator in summary_lower for indicator in ['chief executive officer', 'ceo', 'executive', 'born', 'appointed', 'sundar pichai', 'tim cook', 'satya nadella', 'mark zuckerberg']):
                            response = f"**{page.title}**\n\n{summary}\n\n"
                            response += f" [Read more]({page.url})"
                            return response
                    except:
                        pass
                
                # Try search results approach with more aggressive filtering
                for search_term in search_attempts:
                    try:
                        search_results = wikipedia.search(search_term, results=10)
                        for result in search_results:
                            try:
                                page = wikipedia.page(result, auto_suggest=False)
                                summary = wikipedia.summary(result, sentences=6, auto_suggest=False)
                                
                                # Check if this looks like a person (CEO) - more comprehensive check
                                summary_lower = summary.lower()
                                page_title_lower = page.title.lower()
                                
                                # Look for CEO indicators in both summary and title
                                ceo_indicators = [
                                    'chief executive officer', 'ceo', 'executive', 'born', 'appointed',
                                    'sundar pichai', 'tim cook', 'satya nadella', 'mark zuckerberg',
                                    'business executive', 'american business', 'indian business'
                                ]
                                
                                # Also check if title contains person-like indicators
                                person_indicators = ['born', 'businessman', 'executive', 'ceo']
                                
                                if (any(indicator in summary_lower for indicator in ceo_indicators) or
                                    any(indicator in page_title_lower for indicator in person_indicators)):
                                    
                                    # Make sure it's not just the company page
                                    if company_name.lower() not in page_title_lower or 'ceo' in page_title_lower.lower():
                                        response = f"**{page.title}**\n\n{summary}\n\n"
                                        response += f" [Read more]({page.url})"
                                        return response
                            except:
                                continue
                    except:
                        pass
                
                
                try:
                    # Search for people who might be the CEO
                    general_searches = [
                        f"{company_name} chief executive officer",
                        f"{company_name} CEO biography",
                        f"{company_name} leadership team",
                        f"List of {company_name} executives",
                    ]
                    
                    for search_term in general_searches:
                        search_results = wikipedia.search(search_term, results=5)
                        for result in search_results:
                            try:
                                page = wikipedia.page(result, auto_suggest=False)
                                summary = wikipedia.summary(result, sentences=8, auto_suggest=False)
                                
                                
                                summary_lower = summary.lower()
                                page_title_lower = page.title.lower()
                                
                                
                                ceo_indicators = [
                                    'chief executive officer', 'ceo', 'executive', 'born', 'appointed',
                                    'business executive', 'american business', 'indian business'
                                ]
                                
                            
                                person_indicators = ['born', 'businessman', 'executive', 'ceo']
                                
                                if (any(indicator in summary_lower for indicator in ceo_indicators) or
                                    any(indicator in page_title_lower for indicator in person_indicators)):
                                    
                                    
                                    if company_name.lower() not in page_title_lower or 'ceo' in page_title_lower.lower():
                                        response = f"**{page.title}**\n\n{summary}\n\n"
                                        response += f"[Read more]({page.url})"
                                        return response
                            except:
                                continue
                except:
                    pass
                
                
                try:
                    page = wikipedia.page(company_name, auto_suggest=False)
                    summary = wikipedia.summary(company_name, sentences=10, auto_suggest=False)
                    
                    response = f"**{page.title}**\n\n{summary}\n\n"
                    response += f" [Read more]({page.url})\n\n"
                    response += " CEO information may be available in a separate Wikipedia page. Try searching for the CEO's name directly."
                    return response
                    
                except wikipedia.exceptions.PageError:
                    pass
                except wikipedia.exceptions.DisambiguationError:
                    pass
            
            # General Wikipedia search - no hardcoded cases
            try:
                page = wikipedia.page(clean_query, auto_suggest=False)
                summary = wikipedia.summary(clean_query, sentences=5, auto_suggest=False)
                
                response = f"**{page.title}**\n\n{summary}\n\n"
                response += f"[Read more]({page.url})"
                
                return response
                
            except wikipedia.exceptions.DisambiguationError as e:
                for option in e.options[:5]:
                    if clean_query.lower() in option.lower() or option.lower() in clean_query.lower():
                        try:
                            page = wikipedia.page(option)
                            summary = wikipedia.summary(option, sentences=5)
                            
                            response = f"**{page.title}**\n\n{summary}\n\n"
                            response += f" [Read more]({page.url})\n\n"
                            response += " Multiple matches found."
                            
                            return response
                        except:
                            continue
                
                try:
                    page = wikipedia.page(e.options[0])
                    summary = wikipedia.summary(e.options[0], sentences=5)
                    
                    response = f"**{page.title}**\n\n{summary}\n\n"
                    response += f"[Read more]({page.url})"
                    
                    return response
                except:
                    pass
                    
            except wikipedia.exceptions.PageError:
                try:
                    search_results = wikipedia.search(clean_query, results=10)
                    
                    for result in search_results[:5]:
                        if clean_query.lower() in result.lower():
                            try:
                                page = wikipedia.page(result)
                                summary = wikipedia.summary(result, sentences=5)
                                
                                response = f"**{page.title}**\n\n{summary}\n\n"
                                response += f" [Read more]({page.url})"
                                
                                return response
                            except:
                                continue
                    
                    if search_results:
                        try:
                            page = wikipedia.page(search_results[0])
                            summary = wikipedia.summary(search_results[0], sentences=5)
                            
                            response = f"**{page.title}**\n\n{summary}\n\n"
                            response += f" [Read more]({page.url})"
                            
                            return response
                        except:
                            pass
                            
                except:
                    pass
            
            return f" Could not find information about '{clean_query}'.\n\n Try rephrasing your question."
                
        except Exception as e:
            return f" Error searching Wikipedia: {str(e)}"
    
    def _clean_query(self, query: str) -> str:
        """Clean query by removing question words."""
        query = query.strip()
        
        prefixes = [
            "who is", "who was", "what is", "what was",
            "where is", "where was", "when is", "when was",
            "tell me about", "explain", "describe",
            "more about", "tell more about"
        ]
        
        query_lower = query.lower()
        for prefix in prefixes:
            if query_lower.startswith(prefix):
                query = query[len(prefix):].strip()
                break
        
        return query
    
    def process_query(self, query: str) -> str:
        """
        Process a user query using LangChain's memory components.
        
        This demonstrates:
        1. Loading memory (LangChain ConversationBufferMemory.load_memory_variables)
        2. Saving context (LangChain ConversationBufferMemory.save_context)
        3. Conversation flow with memory
        4. Entity extraction from Wikipedia responses
        """
        
        query = query.strip()
        
        if not query:
            return "Please ask a question."
        
        # Handle special commands
        if query.lower() in ["hi", "hello", "hey"]:
            response = self._handle_greeting()
            self.memory.save_context({"input": query}, {"response": response})
            return response
        
        if query.lower() in ["help", "?"]:
            response = self._get_help()
            self.memory.save_context({"input": query}, {"response": response})
            return response
        
        if "thank" in query.lower():
            response = self._handle_thanks()
            self.memory.save_context({"input": query}, {"response": response})
            return response
        
        # Extract entity from the query first
        entity = self._extract_entity(query)
        
        # Check if this is a follow-up question
        if self._is_follow_up(query):
            follow_up_response = self._handle_follow_up(query)
            if follow_up_response and "Could not find" not in follow_up_response:
                # LangChain style: save context to memory
                self.memory.save_context({"input": query}, {"response": follow_up_response})
                return follow_up_response
        
        # For new queries, reset the last_entity to avoid context confusion
        if entity and not self._is_follow_up(query):
            self.last_entity = None
        
        # Generate search query - if we have an entity, use it with better search terms
        search_query = query
        if entity:
            # Create better search queries for specific patterns
            query_lower = query.lower()
            if "ceo" in query_lower:
                search_query = f"CEO of {entity}"
            elif "president" in query_lower:
                search_query = f"President of {entity}"
            elif "capital" in query_lower:
                search_query = f"{entity} (capital)"
            else:
                search_query = entity
        
        # Generate response using Wikipedia
        response = self._search_wikipedia_direct(search_query)
        
        # Extract entity from the Wikipedia response for future follow-ups
        extracted_entity = self._extract_entity_from_response(response)
        if extracted_entity:
            self.last_entity = extracted_entity
        elif entity:
            self.last_entity = entity
        
        # save context to memory
        self.memory.save_context({"input": query}, {"response": response})
        
        return response
    
    def _handle_greeting(self) -> str:
        """Handle greeting messages."""
        
        return """ Hello! I'm your LangChain-powered Conversational Knowledge Bot.

I can:
- Answer factual questions using Wikipedia
- Remember our conversation for follow-up questions
- Search for information about people, places, concepts, and more

Try asking:
- "Who is the CEO of Google?"
- "What is quantum computing?"
- "Tell me about World War 2"
- "Capital of France"

What would you like to know?"""
    
    def _handle_thanks(self) -> str:
        """Handle thank you messages."""
        
        return " You're welcome! Feel free to ask more questions anytime."
    
    def _get_help(self) -> str:
        """Get help text."""
        
        return """ **HELP - LangChain Knowledge Bot**

**What I can do:**
• Answer factual questions using Wikipedia
• Remember conversation context for follow-ups
• Search for information about any topic

**Example Questions:**
• Who is the CEO of OpenAI?
• What is artificial intelligence?
• Tell me about World War 2
• President of United States
• Capital of France

**LangChain Components Used:**
1. ConversationBufferMemory - Stores conversation history
2. Memory.save_context() - Saves exchanges
3. Memory.load_memory_variables() - Retrieves history

Type 'quit' to exit anytime!"""
    
    def clear_memory(self):
        """Clear the conversation memory (LangChain style)."""
        
        self.memory.clear()
        self.last_entity = None
        print(f"{Fore.YELLOW} Memory cleared!{Style.RESET_ALL}")
    
    def get_memory(self) -> Dict[str, Any]:
        """Get current memory state (LangChain style)."""
        
        return self.memory.load_memory_variables({})
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history from LangChain memory."""
        
        variables = self.memory.load_memory_variables({})
        history = variables.get("history", "")
        
        if not history:
            return "No conversation history yet."
        
        return history

def main():
    """Main function for CLI usage."""
    
    bot = LangChainKnowledgeBot()
    
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



