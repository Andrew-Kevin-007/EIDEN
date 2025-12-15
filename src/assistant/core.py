"""Core assistant module that coordinates all components."""
from typing import Optional, Any
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from io import BytesIO
import wave
import struct
import threading
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.local_llm import LocalLLM
from auth.voice_auth import VoiceAuthenticator
from capabilities.system_control import SystemController
from capabilities.web_search import WebSearcher
from capabilities.weather import WeatherService
from capabilities.calculator import Calculator
from capabilities.timer import TimerManager
from capabilities.media_control import MediaController
from capabilities.app_discovery import AppDiscovery
from capabilities.email_manager import EmailManager
from capabilities.web_automation import WebAutomation
from capabilities.app_automation import AppAutomation


class Assistant:
    """Main assistant class that coordinates speech recognition, synthesis, and command handling."""
    
    def __init__(self, config=None, health_monitor=None):
        """Initialize the assistant with all required components."""
        import logging
        self.logger = logging.getLogger('jarvis.assistant')
        self.config = config
        self.health_monitor = health_monitor
        
        self.recognizer = sr.Recognizer()
        self.sample_rate = 16000 if not config else config.get('audio.sample_rate', 16000)
        self.channels = 1
        self.tts = None
        self.is_initialized = False
        self.is_listening = False
        self.wake_word_detected = False
        self.running = True
        
        # Initialize all capability modules
        model_name = "llama3.2:3b" if not config else config.get('llm.model', 'llama3.2:3b')
        self.llm = LocalLLM(model=model_name)
        self.authenticator = VoiceAuthenticator()
        
        require_auth = True if not config else config.get('security.require_auth_for_system', True)
        self.system_controller = SystemController(require_auth=require_auth)
        
        self.web_searcher = WebSearcher()
        self.weather_service = WeatherService()
        self.calculator = Calculator()
        self.timer_manager: Optional[TimerManager] = None  # Initialize after TTS is ready
        self.media_controller = MediaController()
        self.app_discovery = AppDiscovery()
        self.email_manager = EmailManager()
        self.web_automation = WebAutomation()
        self.app_automation = AppAutomation()
        
        # Voice-first mode: minimize console output
        self.verbose = False if not config else config.get('assistant.verbose', False)
        
        # Command cache for speed
        cache_enabled = True if not config else config.get('performance.enable_cache', True)
        cache_size = 100 if not config else config.get('performance.cache_size', 100)
        self.command_cache = {} if cache_enabled else None
        self.cache_hits = 0
        
        self.logger.info("Assistant components initialized")
        self.verbose = False
        
    def initialize(self) -> None:
        """Initialize the text-to-speech engine and calibrate microphone."""
        try:
            self.logger.info("Starting initialization...")
            
            # Import and initialize TTS
            import pyttsx3
            self.tts = pyttsx3.init()
            
            voice_rate = 200 if not self.config else self.config.get('assistant.voice_rate', 200)
            voice_volume = 1.0 if not self.config else self.config.get('assistant.voice_volume', 1.0)
            
            self.tts.setProperty('rate', voice_rate)
            self.tts.setProperty('volume', voice_volume)
            
            # Fast command patterns (skip LLM for common commands)
            self.fast_patterns = {
                'time': ['time', 'what time'],
                'date': ['date', 'what day', 'today'],
                'weather': ['weather'],
                'email': ['check email', 'check my email', 'any email'],
                'explorer': ['file explorer', 'open explorer'],
                'downloads': ['downloads', 'download folder'],
                'calculator': ['calculator', 'open calc'],
            }
            
            self.logger.info("TTS initialized successfully")
            
            # Test microphone
            print("Testing microphone... Please wait.")
            print("Available audio devices:")
            print(sd.query_devices())
            
            # Check if voice authentication is enrolled
            if not self.authenticator.is_enrolled():
                print("\n" + "="*50)
                print("FIRST TIME SETUP")
                print("="*50)
                self.speak("Welcome! Let's set up voice authentication for secure access.")
                if self.authenticator.enroll_user():
                    self.speak("Voice authentication setup complete.")
                else:
                    self.speak("Authentication setup failed. Please try again later.")
            
            # Initialize timer manager with speech callback
            self.timer_manager = TimerManager(speak_callback=self.speak)
            
            print("\nInitialization complete!")
            self.speak("JARVIS online. All systems operational.")
            self.is_initialized = True
            
        except Exception as e:
            print(f"Initialization error: {e}")
            self.is_initialized = False
    
    def speak(self, text: str) -> None:
        """Convert text to speech and play it."""
        try:
            if self.tts:
                if self.verbose:
                    print(f"Assistant: {text}")
                self.tts.say(text)
                self.tts.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
    
    def _get_response_for_command(self, command: str) -> str:
        """Get text response for a command without speaking (for API)."""
        from datetime import datetime
        import re
        
        command_lower = command.lower()
        
        # Time
        if 'time' in command_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The time is {current_time}"
        
        # Date
        if 'date' in command_lower:
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"Today is {current_date}"
        
        # Greetings
        if any(word in command_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you?"
        
        # Weather
        if 'weather' in command_lower:
            result = self.weather_service.get_weather()
            return result["message"]
        
        # Calculator
        if any(word in command_lower for word in ['calculate', 'what is', 'plus', 'minus', 'times', 'divided']):
            result = self.calculator.calculate(command)
            if result["success"]:
                return result["message"]
        
        # Use LLM for general conversation
        try:
            response = self.llm.chat(command)
            return response
        except:
            return "I'm processing your request. How else can I help you?"
    
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text using sounddevice."""
        try:
            if self.verbose:
                print("\nListening...")
            
            # Record audio using sounddevice
            duration = 4  # seconds - faster
            recording = sd.rec(int(duration * self.sample_rate), 
                             samplerate=self.sample_rate, 
                             channels=self.channels, 
                             dtype='int16')
            sd.wait()  # Wait until recording is finished
            
            print("Processing speech...")
            
            # Convert numpy array to WAV format in memory
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(recording.tobytes())
            
            wav_buffer.seek(0)
            
            # Convert to AudioData for speech recognition
            with sr.AudioFile(wav_buffer) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)  # type: ignore
            print(f"You said: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            print("Could not understand audio.")
            self.speak("Sorry, I didn't catch that.")
            return None
        except sr.RequestError as e:
            print(f"Recognition service error: {e}")
            self.speak("Speech recognition service is unavailable.")
            return None
        except Exception as e:
            print(f"Listening error: {e}")
            return None
    
    def listen_for_wake_word(self) -> None:
        """Continuously listen for wake word in background."""
        print("\n" + "="*50)
        print("Wake Word Detection Active")
        print("="*50)
        print("Say 'Hey Assistant' or 'Jarvis' to activate")
        print("The assistant will automatically listen for your command")
        print("Press Ctrl+C to stop")
        print("="*50 + "\n")
        
        # Simple wake word detection using continuous audio monitoring
        wake_words = ["hey assistant", "jarvis", "okay assistant", "assistant"]
        
        while self.running:
            try:
                # Record short audio chunks
                duration = 2  # Faster detection
                recording = sd.rec(int(duration * self.sample_rate), 
                                 samplerate=self.sample_rate, 
                                 channels=self.channels, 
                                 dtype='int16')
                sd.wait()
                
                # Convert to audio format for recognition
                wav_buffer = BytesIO()
                with wave.open(wav_buffer, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(recording.tobytes())
                
                wav_buffer.seek(0)
                
                # Try to recognize wake word
                with sr.AudioFile(wav_buffer) as source:
                    audio = self.recognizer.record(source)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()  # type: ignore
                    
                    # Check for wake word
                    if any(wake_word in text for wake_word in wake_words):
                        print(f"\n🎤 Wake word detected: '{text}'")
                        self.speak("Yes, I'm listening.")
                        
                        # Now listen for the actual command
                        command = self.listen()
                        if command:
                            self.process_command(command)
                        
                        print("\nWaiting for wake word...")
                        
                except sr.UnknownValueError:
                    # No speech detected, continue listening
                    pass
                except sr.RequestError as e:
                    print(f"Recognition service error: {e}")
                    time.sleep(5)  # Wait before retrying
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Wake word detection error: {e}")
                time.sleep(1)
    
    def process_command(self, command: str) -> None:
        """Process a voice command using LLM intelligence."""
        if not command:
            return
        
        if self.verbose:
            print(f"\n🧠 Processing: {command}")
        
        command_lower = command.lower()
        
        # Fast path: Check common patterns first (no LLM needed)
        if self._handle_fast_command(command_lower):
            return
        
        # Check cache for repeated commands
        if command_lower in self.command_cache:
            intent_data = self.command_cache[command_lower]
            self.cache_hits += 1
        else:
            # Extract intent using LLM
            intent_data = self.llm.extract_intent(command)
            # Cache the result (limit cache size)
            if len(self.command_cache) < 100:
                self.command_cache[command_lower] = intent_data
        
        intent = intent_data.get("intent", "general")
        action = intent_data.get("action", "chat")
        needs_permission = intent_data.get("needs_permission", False)
        parameters = intent_data.get("parameters", {})
        
        if self.verbose:
            print(f"Intent: {intent}, Action: {action}, Needs Auth: {needs_permission}")
        
        # Handle exit commands
        if any(word in command for word in ["exit", "quit", "goodbye", "bye", "stop listening", "shut down", "power off"]):
            self.speak("Goodbye sir.")
            self.running = False
            return
        
        # Check if authentication is needed
        if needs_permission and intent == "system_control":
            if not self.authenticator.is_authenticated:
                self.speak("Voice authentication required for system access.")
                if self.authenticator.authenticate():
                    self.system_controller.authorize()
                    self.speak("Access granted.")
                else:
                    self.speak("Access denied. Command cancelled.")
                    return
        
        # Route to appropriate capability
        if intent == "system_control":
            self._handle_system_control(action, parameters)
        elif intent == "file_operation":
            self._handle_file_operation(action, parameters, command)
        elif intent == "search":
            self._handle_search(action, parameters, command)
        elif intent == "productivity":
            self._handle_productivity(action, parameters, command)
        elif intent == "weather":
            self._handle_weather(action, parameters)
        elif intent == "calculation":
            self._handle_calculation(action, parameters, command)
        elif intent == "media_control":
            self._handle_media_control(action, parameters)
        elif intent == "timer":
            self._handle_timer(action, parameters, command)
        elif intent == "email":
            self._handle_email(action, parameters, command)
        elif intent == "web_browsing":
            self._handle_web_browsing(action, parameters, command)
        elif intent == "app_automation":
            self._handle_app_automation(action, parameters, command)
        else:
            # Use LLM for general conversation
            response = self.llm.chat(command)
            self.speak(response)
    
    def _handle_fast_command(self, command: str) -> bool:
        """Handle common commands instantly without LLM. Returns True if handled."""
        from datetime import datetime
        
        # Time
        if 'time' in command and not 'timer' in command:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"{current_time}")
            return True
        
        # Date
        if 'date' in command or ('what' in command and 'day' in command):
            current_date = datetime.now().strftime("%A, %B %d")
            self.speak(current_date)
            return True
        
        # Calculator
        if 'calculator' in command or 'open calc' in command:
            self.speak("Opening Calculator")
            import subprocess
            subprocess.Popen('calc.exe')
            return True
        
        # File Explorer
        if 'file explorer' in command or 'open explorer' in command:
            if 'download' in command:
                self.app_discovery.open_system_location('downloads')
            elif 'document' in command:
                self.app_discovery.open_system_location('documents')
            elif 'picture' in command:
                self.app_discovery.open_system_location('pictures')
            else:
                self.app_discovery.open_file_explorer()
            self.speak("Done")
            return True
        
        # Downloads folder
        if 'download' in command and 'folder' in command:
            self.app_discovery.open_system_location('downloads')
            self.speak("Downloads")
            return True
        
        # Weather (quick check)
        if command.startswith('weather') or command.startswith('what') and 'weather' in command:
            result = self.weather_service.get_weather()
            self.speak(result["message"])
            return True
        
        return False
    
    def _handle_system_control(self, action: str, params: dict):
        """Handle system control actions."""
        if action == "open_app":
            app_name = params.get("app", "")
            
            # Try smart app discovery first
            app_path = self.app_discovery.find_application(app_name)
            if app_path:
                result = self.system_controller.open_application(app_path)
            else:
                # Fallback to default behavior
                result = self.system_controller.open_application(app_name)
            self.speak(result["message"])
            
        elif action == "close_app":
            app_name = params.get("app", "")
            result = self.system_controller.close_application(app_name)
            self.speak(result["message"])
            
        elif action == "lock_screen":
            result = self.system_controller.lock_screen()
            self.speak(result["message"])
            
        elif action == "shutdown" or action == "restart":
            result = self.system_controller.shutdown_computer(action)
            self.speak(result["message"])
            
        elif action == "screenshot":
            result = self.system_controller.take_screenshot()
            self.speak(result["message"])
        
        else:
            # Use LLM to handle unclear system commands
            response = self.llm.chat(f"Help with system control: {params}")
            self.speak(response)
    
    def _handle_file_operation(self, action: str, params: dict, command: str):
        """Handle file operations including File Explorer."""
        command_lower = command.lower()
        
        # Open File Explorer
        if "file explorer" in command_lower or "explorer" in command_lower:
            # Check if specific location mentioned
            if "downloads" in command_lower:
                result = self.app_discovery.open_system_location("downloads")
            elif "documents" in command_lower:
                result = self.app_discovery.open_system_location("documents")
            elif "pictures" in command_lower or "photos" in command_lower:
                result = self.app_discovery.open_system_location("pictures")
            elif "desktop" in command_lower:
                result = self.app_discovery.open_system_location("desktop")
            elif "music" in command_lower:
                result = self.app_discovery.open_system_location("music")
            elif "videos" in command_lower:
                result = self.app_discovery.open_system_location("videos")
            else:
                result = self.app_discovery.open_file_explorer()
            
            self.speak(result["message"])
        
        # Open specific folders
        elif any(loc in command_lower for loc in ["downloads", "documents", "pictures", "desktop", "music", "videos"]):
            for location in ["downloads", "documents", "pictures", "desktop", "music", "videos"]:
                if location in command_lower:
                    result = self.app_discovery.open_system_location(location)
                    self.speak(result["message"])
                    return
        
        else:
            self.speak("File operation not yet supported. Try opening File Explorer or folders like Downloads.")
    
    def _handle_search(self, action: str, params: dict, command: str):
        """Handle search operations."""
        query = params.get("query", command)
        
        if "youtube" in command.lower():
            result = self.web_searcher.search_youtube(query)
            self.speak(result["message"])
        elif "website" in command.lower() or "open" in command.lower():
            url = params.get("url", query)
            result = self.web_searcher.open_website(url)
            self.speak(result["message"])
        else:
            # Try to get quick answer first
            quick_answer = self.web_searcher.get_quick_answer(query)
            if quick_answer and len(quick_answer) < 200:
                self.speak(quick_answer)
            else:
                result = self.web_searcher.search(query)
                self.speak(result["message"])
    
    def _handle_weather(self, action: str, params: dict):
        """Handle weather requests."""
        location = params.get("location", None)
        
        if action == "forecast":
            result = self.weather_service.get_forecast(location)
        else:
            result = self.weather_service.get_weather(location)
        
        self.speak(result["message"])
    
    def _handle_calculation(self, action: str, params: dict, command: str):
        """Handle calculations and conversions."""
        if "convert" in command.lower():
            # Use LLM to help with conversion
            response = self.llm.chat(f"Parse this conversion and give just the result: {command}")
            self.speak(response)
        else:
            result = self.calculator.calculate(command)
            if result["success"]:
                self.speak(result["message"])
            else:
                # Fallback to LLM
                response = self.llm.chat(command)
                self.speak(response)
    
    def _handle_media_control(self, action: str, params: dict):
        """Handle media player control."""
        if action == "play_pause" or action == "play" or action == "pause":
            result = self.media_controller.play_pause()
        elif action == "next" or action == "next_track":
            result = self.media_controller.next_track()
        elif action == "previous" or action == "previous_track":
            result = self.media_controller.previous_track()
        elif action == "volume_up":
            result = self.media_controller.volume_up()
        elif action == "volume_down":
            result = self.media_controller.volume_down()
        elif action == "mute":
            result = self.media_controller.mute()
        else:
            result = {"success": False, "message": "Unknown media command"}
        
        self.speak(result["message"])
    
    def _handle_timer(self, action: str, params: dict, command: str):
        """Handle timer operations."""
        if not self.timer_manager:
            self.speak("Timer service not initialized.")
            return
            
        if "set timer" in command.lower() or "timer for" in command.lower():
            duration = self.timer_manager.parse_duration(command)
            if duration:
                result = self.timer_manager.set_timer(duration)
                self.speak(result["message"])
            else:
                self.speak("I couldn't understand the duration. Please specify time like '5 minutes' or '30 seconds'.")
        
        elif "list timer" in command.lower() or "active timer" in command.lower():
            result = self.timer_manager.list_timers()
            self.speak(result["message"])
        
        elif "cancel timer" in command.lower() or "stop timer" in command.lower():
            result = self.timer_manager.cancel_timer()
            self.speak(result["message"])
        
        else:
            # Try to parse as a simple timer command
            duration = self.timer_manager.parse_duration(command)
            if duration:
                result = self.timer_manager.set_timer(duration)
                self.speak(result["message"])
            else:
                self.speak("Timer command not recognized.")
    
    def _handle_productivity(self, action: str, params: dict, command: str):
        """Handle productivity tasks."""
        # Time and date queries
        if "time" in command.lower():
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {current_time}")
        
        elif "date" in command.lower() or "day" in command.lower():
            from datetime import datetime
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {current_date}")
        
        else:
            self.speak("Productivity feature coming soon.")
    
    def _handle_email(self, action: str, params: dict, command: str):
        """Handle email operations."""
        command_lower = command.lower()
        
        # Check email
        if "check" in command_lower or "any email" in command_lower or "new email" in command_lower:
            result = self.email_manager.check_email(limit=5)
            self.speak(result["message"])
            
            # Read first email details if available
            if result.get("success") and result.get("emails"):
                self.speak("Would you like me to read any of them?")
        
        # Unread count
        elif "unread" in command_lower or "how many" in command_lower:
            result = self.email_manager.get_unread_count()
            self.speak(result["message"])
        
        # Read email
        elif "read" in command_lower:
            # Try to extract email index
            index = 0
            if "first" in command_lower or "latest" in command_lower:
                index = 0
            elif "second" in command_lower:
                index = 1
            elif "third" in command_lower:
                index = 2
            
            result = self.email_manager.read_email(index)
            self.speak(result["message"])
        
        # Send email (requires more context)
        elif "send" in command_lower:
            if not self.email_manager.is_configured:
                self.speak("Email not configured. Please set up your email account first.")
            else:
                self.speak("Email sending requires recipient, subject, and message. This feature needs interactive setup.")
        
        # Configure email
        elif "configure" in command_lower or "setup" in command_lower:
            self.speak("To configure email, you'll need to edit the configuration file manually for security. Check the documentation.")
        
        else:
            self.speak("Email command not recognized. Try 'check email', 'read email', or 'unread emails'.")
    
    def _handle_web_browsing(self, action: str, params: dict, command: str):
        """Handle web browsing actions."""
        command_lower = command.lower()
        
        # Search web
        if "search" in command_lower or "google" in command_lower or "look up" in command_lower:
            # Extract search query
            query = params.get("query", "")
            if not query:
                # Try to extract from command
                for phrase in ["search for", "google", "look up", "find"]:
                    if phrase in command_lower:
                        query = command_lower.split(phrase, 1)[1].strip()
                        break
            
            if query:
                # Determine search engine
                engine = "google"
                if "youtube" in command_lower:
                    engine = "youtube"
                elif "bing" in command_lower:
                    engine = "bing"
                
                result = self.web_automation.search_web(query, engine)
                self.speak(f"Searching {engine} for {query}")
            else:
                self.speak("What would you like me to search for?")
        
        # Open website
        elif "open" in command_lower and ("website" in command_lower or "site" in command_lower or ".com" in command_lower):
            url = params.get("url", "")
            if not url:
                # Try to extract URL from command
                words = command_lower.split()
                for word in words:
                    if "." in word and len(word) > 3:
                        url = word
                        break
            
            if url:
                result = self.web_automation.open_website(url)
                self.speak(f"Opening {url}")
            else:
                self.speak("Which website would you like me to open?")
        
        # Fetch webpage content
        elif "fetch" in command_lower or "get content" in command_lower or "read page" in command_lower:
            url = params.get("url", "")
            if url:
                self.speak(f"Fetching content from {url}")
                content = self.web_automation.fetch_webpage_content(url)
                if content:
                    # Summarize using LLM
                    summary = self.llm.chat(f"Summarize this content briefly: {content[:2000]}")
                    self.speak(summary)
                else:
                    self.speak("Failed to fetch webpage content")
            else:
                self.speak("Please specify a URL to fetch")
        
        # Get news
        elif "news" in command_lower or "headlines" in command_lower:
            topic = params.get("topic", "world")
            self.speak(f"Fetching {topic} news headlines")
            headlines = self.web_automation.get_news_headlines(topic)
            
            if headlines:
                self.speak(f"Here are the top {len(headlines)} headlines")
                for i, headline in enumerate(headlines[:3], 1):
                    self.speak(f"{i}. {headline}")
            else:
                self.speak("Could not fetch news headlines")
        
        else:
            self.speak("Web browsing command not recognized")
    
    def _handle_app_automation(self, action: str, params: dict, command: str):
        """Handle application automation actions."""
        command_lower = command.lower()
        
        # Type in application
        if "type" in command_lower or "write" in command_lower:
            # Determine target app
            app_name = None
            for app in ["word", "notepad", "notepad++", "excel"]:
                if app in command_lower or app.replace("++", " plus plus") in command_lower:
                    app_name = app
                    break
            
            # If no app specified, ask user
            if not app_name:
                self.speak("Which application would you like me to write in? Word, Notepad, or Excel?")
                app_response = self.listen()
                if app_response:
                    for app in ["word", "notepad", "excel"]:
                        if app in app_response.lower():
                            app_name = app
                            break
            
            if not app_name:
                app_name = "notepad"  # Default
            
            # Get text to type
            text = params.get("text", "")
            if not text:
                # Extract from command
                for phrase in ["type", "write", "in"]:
                    if phrase in command_lower:
                        parts = command_lower.split(phrase)
                        if len(parts) > 1:
                            text = parts[-1].strip()
                            break
            
            if not text:
                self.speak("What would you like me to write?")
                text_response = self.listen()
                if text_response:
                    text = text_response
            
            if text:
                self.speak(f"Writing in {app_name}")
                result = self.app_automation.open_and_type(app_name, text)
                self.speak("Done")
            else:
                self.speak("I didn't get the text to write")
        
        # Draft email in Outlook
        elif "draft email" in command_lower or "compose email" in command_lower:
            self.speak("Who is the email to?")
            to = self.listen()
            
            if to:
                self.speak("What is the subject?")
                subject = self.listen()
                
                self.speak("What would you like to say?")
                body = self.listen()
                
                if subject and body:
                    self.speak("Drafting email in Outlook")
                    result = self.app_automation.draft_email_outlook(to, subject, body)
                    self.speak("Email drafted. Please review and send when ready")
                else:
                    self.speak("Email draft cancelled")
            else:
                self.speak("Email draft cancelled")
        
        # Take screenshot
        elif "screenshot" in command_lower or "screen capture" in command_lower:
            self.speak("Taking screenshot")
            result = self.app_automation.take_screenshot()
            self.speak("Screenshot saved")
        
        # Copy to clipboard
        elif "copy" in command_lower and "clipboard" in command_lower:
            text = params.get("text", "")
            if text:
                result = self.app_automation.copy_to_clipboard(text)
                self.speak("Copied to clipboard")
            else:
                self.speak("What would you like me to copy?")
        
        # Paste from clipboard
        elif "paste" in command_lower:
            text = self.app_automation.paste_from_clipboard()
            if text:
                self.speak(f"Clipboard contains: {text[:100]}")
            else:
                self.speak("Clipboard is empty")
        
        # Press keyboard shortcut
        elif "press" in command_lower:
            # Extract keys
            keys = []
            if "ctrl" in command_lower or "control" in command_lower:
                keys.append("ctrl")
            if "alt" in command_lower:
                keys.append("alt")
            if "shift" in command_lower:
                keys.append("shift")
            
            # Common shortcuts
            if "c" in command_lower and "ctrl" in keys:
                keys.append("c")
            elif "v" in command_lower and "ctrl" in keys:
                keys.append("v")
            elif "s" in command_lower and "ctrl" in keys:
                keys.append("s")
            
            if len(keys) > 1:
                result = self.app_automation.press_keys(keys)
                self.speak(f"Pressed {' plus '.join(keys)}")
            else:
                self.speak("Which keyboard shortcut would you like me to press?")
        
        else:
            self.speak("Application automation command not recognized")
    
    def process_commands(self) -> None:
        """Listen for and process voice commands."""
        if not self.is_initialized:
            print("Assistant not initialized!")
            return
        
        command = self.listen()
        
        if command:
            # Handle exit commands
            if any(word in command for word in ["exit", "quit", "goodbye", "bye"]):
                self.speak("Goodbye!")
                exit(0)
            
            # Handle greetings
            elif any(word in command for word in ["hello", "hi", "hey"]):
                self.speak("Hello! How can I assist you?")
            
            # Handle help requests
            elif "help" in command:
                self.speak("I can greet you, list files, and perform basic tasks. Say goodbye to exit.")
            
            # Handle file operations
            elif "list files" in command or "show files" in command:
                self.speak("File listing functionality is available but requires a configured directory.")
            
            # Default response
            else:
                self.speak(f"You said: {command}. I'm still learning how to respond to that.")
        
        return