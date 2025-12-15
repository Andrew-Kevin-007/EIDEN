"""Local LLM integration using Ollama."""
import requests
import json
from typing import Optional, List, Dict, Any


class LocalLLM:
    """Interface to local Ollama LLM for intelligent conversations."""
    
    def __init__(self, model: str = "llama3.2:3b", host: str = "http://localhost:11434"):
        """
        Initialize the local LLM.
        
        Args:
            model: Name of the Ollama model to use
            host: Ollama server URL
        """
        self.model = model
        self.host = host
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = """You are JARVIS, a highly intelligent personal AI assistant. 
You are helpful, concise, and proactive. You can control the computer, manage files, 
search the web, and assist with various tasks. Keep responses brief and actionable.
When the user asks you to perform an action, respond with clear intent."""
        
    def chat(self, user_message: str, include_history: bool = True) -> str:
        """
        Send a message to the LLM and get a response.
        
        Args:
            user_message: The user's message
            include_history: Whether to include conversation history
            
        Returns:
            The LLM's response
        """
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Prepare messages for the API
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if include_history:
                messages.extend(self.conversation_history[-10:])  # Last 10 messages
            else:
                messages.append({"role": "user", "content": user_message})
            
            # Call Ollama API
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower = faster, more deterministic
                        "top_p": 0.9,
                        "num_predict": 100,  # Limit response length
                    }
                },
                timeout=10  # Faster timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get("message", {}).get("content", "")
                
                # Add assistant response to history
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message.strip()
            else:
                return "I'm having trouble thinking right now. Please try again."
                
        except requests.exceptions.ConnectionError:
            return "I cannot connect to my neural network. Please ensure Ollama is running."
        except requests.exceptions.Timeout:
            return "My response is taking too long. Let me try that again."
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I encountered an error processing that request."
    
    def extract_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Extract intent and entities from user message.
        
        Args:
            user_message: The user's message
            
        Returns:
            Dictionary with intent, action, and parameters
        """
        prompt = f"""Analyze this command and extract the intent: "{user_message}"

Return ONLY a JSON object with:
- "intent": category (system_control, file_operation, search, productivity, weather, calculation, media_control, timer, email, general)
- "action": specific action
- "parameters": any relevant parameters
- "needs_permission": true/false for sensitive operations

Intent categories:
- system_control: open/close apps, lock screen, shutdown, screenshot
- file_operation: open file explorer, folders (downloads, documents, pictures, desktop, music, videos)
- weather: current weather, forecast, temperature queries
- calculation: math operations, unit conversions, currency
- media_control: play, pause, next, previous, volume
- timer: set timer, list timers, cancel timer
- email: check email, read email, send email, unread count
- search: web search, YouTube, open websites
- web_browsing: search web, open website, fetch content, get news
- app_automation: type in Word/Notepad, draft email, screenshot, clipboard
- productivity: time, date, calendar, reminders
- general: conversation, questions, general queries

Examples:
{{"intent": "file_operation", "action": "open_explorer", "parameters": {{"location": "downloads"}}, "needs_permission": false}}
{{"intent": "email", "action": "check_email", "parameters": {{}}, "needs_permission": false}}
{{"intent": "system_control", "action": "open_app", "parameters": {{"app": "file explorer"}}, "needs_permission": false}}
{{"intent": "weather", "action": "get_weather", "parameters": {{"location": "New York"}}, "needs_permission": false}}
{{"intent": "calculation", "action": "calculate", "parameters": {{"expression": "25 * 47"}}, "needs_permission": false}}
{{"intent": "timer", "action": "set_timer", "parameters": {{"duration": "5 minutes"}}, "needs_permission": false}}
{{"intent": "media_control", "action": "play_pause", "parameters": {{}}, "needs_permission": false}}
{{"intent": "search", "action": "search_web", "parameters": {{"query": "Python tutorials"}}, "needs_permission": false}}
{{"intent": "web_browsing", "action": "search_web", "parameters": {{"query": "AI news", "engine": "google"}}, "needs_permission": false}}
{{"intent": "app_automation", "action": "type_text", "parameters": {{"app": "word", "text": "Meeting notes"}}, "needs_permission": false}}"""
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,  # Very low for speed
                        "num_predict": 50,  # Short response
                    }
                },
                timeout=5  # Fast timeout for intent
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "{}")
                return json.loads(response_text)
            else:
                return {"intent": "general", "action": "chat", "parameters": {}, "needs_permission": False}
                
        except Exception as e:
            print(f"Intent extraction error: {e}")
            return {"intent": "general", "action": "chat", "parameters": {}, "needs_permission": False}
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt."""
        self.system_prompt = prompt
