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


class Assistant:
    """Main assistant class that coordinates speech recognition, synthesis, and command handling."""
    
    def __init__(self):
        """Initialize the assistant with all required components."""
        self.recognizer = sr.Recognizer()
        self.sample_rate = 16000
        self.channels = 1
        self.tts = None
        self.is_initialized = False
        self.is_listening = False
        self.wake_word_detected = False
        self.running = True
        
    def initialize(self) -> None:
        """Initialize the text-to-speech engine and calibrate microphone."""
        try:
            # Import and initialize TTS
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 150)
            self.tts.setProperty('volume', 1.0)
            
            # Test microphone
            print("Testing microphone... Please wait.")
            print("Available audio devices:")
            print(sd.query_devices())
            
            print("\nInitialization complete!")
            self.speak("Voice Assistant is ready. How can I help you?")
            self.is_initialized = True
            
        except Exception as e:
            print(f"Initialization error: {e}")
            self.is_initialized = False
    
    def speak(self, text: str) -> None:
        """Convert text to speech and play it."""
        try:
            if self.tts:
                print(f"Assistant: {text}")
                self.tts.say(text)
                self.tts.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
    
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text using sounddevice."""
        try:
            print("\nListening...")
            
            # Record audio using sounddevice
            duration = 5  # seconds
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
                duration = 3
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
        """Process a voice command."""
        if not command:
            return
            
        # Handle exit commands
        if any(word in command for word in ["exit", "quit", "goodbye", "bye", "stop listening"]):
            self.speak("Goodbye!")
            self.running = False
            return
        
        # Handle greetings
        elif any(word in command for word in ["hello", "hi", "hey"]):
            self.speak("Hello! How can I assist you?")
        
        # Handle help requests
        elif "help" in command:
            self.speak("I can greet you, list files, and perform basic tasks. Say goodbye to exit.")
        
        # Handle file operations
        elif "list files" in command or "show files" in command:
            self.speak("File listing functionality is available but requires a configured directory.")
        
        # Handle time request
        elif "time" in command or "what time" in command:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {current_time}")
        
        # Handle date request
        elif "date" in command or "what day" in command:
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
        
        # Default response
        else:
            self.speak(f"You said: {command}. I'm still learning how to respond to that.")
    
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