# JARVIS - Personal AI Assistant

## Quick Start Guide

### What's New
Your voice assistant has been upgraded to **JARVIS** - a fully functional AI-powered personal assistant like Siri with:

✅ **Local LLM Brain** - Uses Llama 3.2 (3B) for intelligent conversations  
✅ **Voice Authentication** - Secure access to system controls  
✅ **System Control** - Open apps, lock screen, take screenshots, shutdown  
✅ **Web Search** - Google, Bing, YouTube, DuckDuckGo instant answers  
✅ **Weather Service** - Current weather and forecasts for any location  
✅ **Calculator** - Math operations and unit conversions  
✅ **Timer Manager** - Set, list, and cancel timers with voice notifications  
✅ **Media Control** - Play/pause, next/previous, volume control  
✅ **Intent Recognition** - Understands what you want without exact commands  
✅ **Cross-Platform Ready** - Works on Windows, macOS, Linux  
✅ **Always-On** - Responds to "Hey Assistant" or "Jarvis"  

### First Run

1. **Start JARVIS:**
   ```bash
   cd d:\Edien\voice-assistant
   python src/main.py
   ```

2. **Voice Authentication Setup** (First time only):
   - Say "My voice is my password" 3 times when prompted
   - This secures system-level operations

3. **Wake Word Activation:**
   - Say "Hey Assistant" or "Jarvis"
   - Wait for "Yes, I'm listening"
   - Give your command

### Example Commands

**General Conversation:**
- "What's the weather like?"
- "Tell me a joke"
- "What can you do?"
- "How are you?"

**Web Search:**
- "Search for Python tutorials"
- "Search YouTube for cooking videos"
- "Open Google"
- "Open reddit.com"
- "What is the capital of France?" (quick answer)

**Weather:**
- "What's the weather?"
- "Weather in New York"
- "Weather forecast"
- "Is it going to rain today?"

**Calculator & Conversions:**
- "What is 25 times 47?"
- "Calculate 150 divided by 3"
- "Convert 100 fahrenheit to celsius"
- "How many kilometers in 50 miles?"

**Timers:**
- "Set timer for 5 minutes"
- "Set a timer for 30 seconds"
- "List timers" or "Active timers"
- "Cancel timer" or "Stop timer"

**Media Control:**
- "Play music" or "Pause music"
- "Next song" or "Previous song"
- "Volume up" or "Volume down"
- "Mute"

**Productivity:**
- "What time is it?"
- "What's today's date?"
- "What day is it?"

**System Control** (Requires voice auth):
- "Open Chrome"
- "Open Notepad"
- "Lock the screen"
- "Take a screenshot"
- "Shutdown the computer"

**Exit:**
- "Goodbye" or "Exit"

### Features

#### 1. **Local LLM (Ollama)**
- Runs Llama 3.2 locally - no cloud needed
- Understands context and natural language
- Privacy-focused - all processing on your machine

#### 2. **Voice Authentication**
- Biometric-like security using your voice
- Required for sensitive system operations
- Stored locally in `data/voice_auth.pkl`

#### 3. **Web Integration**
- Search Google, Bing, YouTube
- Open any website by voice
- DuckDuckGo instant answers for quick facts
- No API keys required

#### 4. **Weather Service**
- Current weather for any location
- 3-day forecast
- Temperature, conditions, precipitation
- Uses wttr.in API (no key needed)

#### 5. **Calculator & Conversions**
- Basic math operations
- Temperature conversions (F/C/K)
- Distance conversions (miles/km/meters)
- Weight conversions (kg/lbs)
- More units coming soon

#### 6. **Timer Manager**
- Multiple concurrent timers
- Voice notifications when timer expires
- List and cancel active timers
- Natural language duration parsing

#### 7. **Media Control**
- Control any media player
- Play/pause toggle
- Track navigation
- Volume adjustment
- Simulates media keys on Windows

#### 8. **System Control**
- Open/close applications
- Lock screen
- Take screenshots
- Shutdown/restart
- Requires voice authentication

#### 9. **Permission System**
- Sensitive operations require voice authentication
- Authorization persists during session
- Automatically resets on restart

### Architecture

```
voice-assistant/
├── src/
│   ├── assistant/
│   │   └── core.py          # Main JARVIS logic
│   ├── llm/
│   │   └── local_llm.py     # Ollama integration
│   ├── auth/
│   │   └── voice_auth.py    # Voice authentication
│   ├── capabilities/
│   │   ├── system_control.py # System operations
│   │   ├── web_search.py     # Web search & browser
│   │   ├── weather.py        # Weather service
│   │   ├── calculator.py     # Math & conversions
│   │   ├── timer.py          # Timer manager
│   │   └── media_control.py  # Media player control
│   └── main.py              # Entry point
└── data/                     # Voice auth data (auto-created)
```

### Troubleshooting

**"Cannot connect to neural network"**
- Ensure Ollama is running: `ollama serve`
- Model installed: `ollama pull llama3.2:3b`

**Voice authentication fails:**
- Speak clearly in a quiet environment
- Ensure microphone is working
- Re-enroll: Delete `data/voice_auth.pkl` and restart

**System commands not working:**
- Complete voice authentication first
- Say the passphrase clearly
- Check if application name is correct

### Next Steps

Coming soon:
- [ ] Web search integration
- [ ] File management with voice
- [ ] Calendar and reminders
- [ ] Smart home control
- [ ] Mobile app (Android/iOS)
- [ ] Background service mode

### Requirements

- Python 3.8+
- Ollama with llama3.2:3b model
- Working microphone
- Internet for speech recognition API
- Windows/macOS/Linux

### Security Notes

- Voice authentication data stored locally
- System operations require authentication
- No data sent to cloud (except Google Speech API)
- LLM runs entirely on your machine

---

**Built with:** Python, Ollama, SpeechRecognition, pyttsx3, sounddevice
