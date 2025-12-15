# JARVIS - AI-Powered Voice Assistant

A fully-functional Python-based voice assistant similar to Siri, powered by local AI. Features always-on wake word detection, local LLM brain, voice authentication, web search, weather, calculator, timers, media control, system automation, **Apple Siri-style GUI**, **web browsing**, and **application automation**.

## 🌟 Features

### 🎨 **NEW: Apple Siri-Style GUI** ✨
💎 **Fully Animated Orb** - Exact Apple Siri gradient orb with 60 FPS animations  
🌊 **Waveform Visualization** - Beautiful flowing waves when listening  
✨ **Particle Effects** - Dynamic particle system (60 particles)  
🎭 **4 Animation States** - Idle, Listening, Thinking, Speaking  
🖼️ **Frameless Design** - Sleek borderless window like macOS  
🎨 **Apple Colors** - Authentic iOS Siri color palette  
🎯 **60 FPS Rendering** - Buttery smooth animations  
📱 **Draggable Window** - Click and drag anywhere to move  

### 🌐 **NEW: Web Automation**
🌍 **Web Search** - Search Google, Bing, YouTube, DuckDuckGo  
🌍 **Open Websites** - Voice-controlled browser navigation  
🌍 **Fetch Content** - Extract and summarize webpage content  
🌍 **Get News** - Latest headlines from Google News  

### ⌨️ **NEW: Application Automation**
📝 **Type in Apps** - Auto-write in Word, Notepad, Excel  
📧 **Draft Emails** - Compose emails in Outlook  
📸 **Screenshots** - Voice-controlled screen capture  
📋 **Clipboard** - Copy/paste operations  
⌨️ **Keyboard Shortcuts** - Press Ctrl+S, Alt+Tab, etc.  

### Core Intelligence
✅ **Local LLM Brain** - Llama 3.2 (3B) via Ollama for natural conversations  
✅ **Intent Recognition** - Understands what you want without exact commands  
✅ **Always-On Wake Word** - Responds to "Hey Assistant" or "Jarvis"  
✅ **Voice Authentication** - Secure biometric-like access for system controls  

### Web & Information
✅ **Web Search** - Google, Bing, YouTube with DuckDuckGo instant answers  
✅ **Weather Service** - Current weather and forecasts worldwide  
✅ **Calculator** - Math operations, unit conversions, temperature  
✅ **Quick Answers** - Instant facts from DuckDuckGo  

### Productivity
✅ **Timer Manager** - Multiple concurrent timers with voice notifications  
✅ **Media Control** - Play/pause, next/previous, volume control  
✅ **Time & Date** - Current time and date queries  
✅ **System Control** - Open apps, lock screen, screenshots, shutdown  
✅ **Email Integration** - Check, read, send emails (SMTP/IMAP)  
✅ **App Discovery** - Auto-learns 199+ installed applications  

### Privacy & Security
✅ **100% Local Processing** - No cloud dependencies for core features  
✅ **Voice Authentication** - Secure system access  
✅ **Permission System** - Authorization for sensitive operations  
✅ **Offline TTS** - pyttsx3 for voice responses  

## 🚀 Quick Start

### Option 1: Apple Siri GUI (Recommended) ⭐
1. **Double-click** `start_siri_gui.bat`
2. Click **"Start Listening"** button  
3. Say **"Hey Assistant"** or **"Jarvis"**
4. Watch the beautiful animated orb respond!
5. Give your command!

### Option 2: Original GUI
1. **Double-click** `start_gui.bat`
2. Click **"Start Assistant"** button
3. Say **"Hey Assistant"** or **"Jarvis"**
4. Give your command!

### Option 3: Console Mode
1. **Double-click** `start.bat`
2. Say **"Hey Assistant"** or **"Jarvis"**
3. Give your command!

## 📦 Full Installation

### Prerequisites
- Python 3.10 or higher
- Ollama (for local LLM)
- Microphone and speakers

### 1. Clone the Repository
```bash
git clone https://github.com/Andrew-Kevin-007/EIDEN
cd voice-assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install and Setup Ollama
```bash
# Install Ollama from https://ollama.ai
# Then pull the Llama 3.2 model (2GB)
ollama pull llama3.2:3b
```

### 4. Run JARVIS
```bash
python src/main.py
```

## 📖 Usage

### First Time Setup

On first run, you'll set up voice authentication:
1. Say "My voice is my password" 3 times when prompted
2. This secures system-level operations

### Wake Word Activation

1. Say **"Hey Assistant"** or **"Jarvis"**
2. Wait for "Yes, I'm listening"
3. Give your command
4. Continue using - always listening in background

### Available Commands

#### 💬 General Conversation
- "What's the weather like?"
- "Tell me a joke"
- "What can you do?"
- "How are you?"

#### 🌐 Web Browsing (NEW)
- "Search Google for Python tutorials"
- "YouTube search meditation music"
- "Open website github.com"
- "Fetch content from wikipedia.org"
- "Get world news"
- "News about technology"

#### ⌨️ Application Automation (NEW)
- "Write in Word meeting notes"
- "Type in Notepad hello world"
- "Draft email"
- "Take screenshot"
- "Copy to clipboard"
- "Press ctrl+s"

#### 🔍 Web Search
- "Search for Python tutorials"
- "Search YouTube for cooking videos"
- "Open Google" / "Open reddit.com"
- "What is the capital of France?"

#### 📧 Email
- "Check my email"
- "How many unread emails"
- "Read latest email"
- "Read my emails"

#### 📁 File Operations
- "Open downloads folder"
- "Open documents"
- "Open file explorer"
- "Show my pictures"

#### 🌤️ Weather
- "What's the weather?"
- "Weather in New York"
- "Weather forecast"
- "Is it going to rain?"

#### 🧮 Calculator & Conversions
- "What is 25 times 47?"
- "Calculate 150 divided by 3"
- "Convert 100 fahrenheit to celsius"
- "How many kilometers in 50 miles?"

#### ⏱️ Timers
- "Set timer for 5 minutes"
- "Set a timer for 30 seconds"
- "List timers" / "Active timers"
- "Cancel timer" / "Stop timer"

#### 🎵 Media Control
- "Play music" / "Pause music"
- "Next song" / "Previous song"
- "Volume up" / "Volume down"
- "Mute"

#### 📅 Productivity
- "What time is it?"
- "What's today's date?"
- "What day is it?"

#### 🖥️ System Control (Requires Voice Auth)
- "Open Chrome" / "Open Notepad"
- "Lock the screen"
- "Take a screenshot"
- "Shutdown the computer"

#### 👋 Exit
- "Goodbye" / "Exit"

## 🏗️ Architecture

### Component Overview

```
voice-assistant/
├── src/
│   ├── main.py                    # Entry point with always-on loop
│   ├── assistant/
│   │   └── core.py                # Main orchestration & command routing
│   ├── llm/
│   │   └── local_llm.py           # Ollama integration & intent extraction
│   ├── auth/
│   │   └── voice_auth.py          # Voice biometric authentication
│   ├── capabilities/
│   │   ├── system_control.py      # System operations (apps, lock, shutdown)
│   │   ├── web_search.py          # Web search & browser control
│   │   ├── weather.py             # Weather API integration
│   │   ├── calculator.py          # Math & unit conversions
│   │   ├── timer.py               # Timer management with threading
│   │   └── media_control.py       # Media player control
│   ├── speech/
│   │   ├── recognition.py         # Speech-to-text
│   │   └── synthesis.py           # Text-to-speech
│   └── utils/
│       └── config.py              # Configuration management
├── data/                          # Voice auth data (auto-created)
├── config/
│   └── settings.json              # Application settings
├── requirements.txt               # Python dependencies
└── README.md
```

### How It Works

1. **Always-On Monitoring**: Continuously records 3-second audio clips
2. **Wake Word Detection**: Checks each clip for "Hey Assistant" or "Jarvis"
3. **Command Listening**: Captures full command after wake word
4. **Intent Extraction**: LLM analyzes command and extracts intent
5. **Permission Check**: Voice auth for sensitive operations
6. **Command Execution**: Routes to appropriate capability module
7. **Response**: Speaks result and returns to monitoring

### Key Technologies

- **SpeechRecognition**: Voice-to-text via Google Speech API
- **pyttsx3**: Offline text-to-speech engine
- **Ollama**: Local LLM inference (Llama 3.2)
- **sounddevice**: Cross-platform audio recording
- **NumPy**: Voice feature extraction for authentication
- **requests**: HTTP API calls (weather, web search)
- **pyautogui**: Media key simulation

## ⚙️ Configuration

### Voice Authentication
- Stored in `data/voice_auth.pkl`
- Delete file to re-enroll
- Requires 3 voice samples for enrollment

### LLM Settings
- Model: `llama3.2:3b` (2GB)
- Change in `src/assistant/core.py` line 42
- Available models: `ollama list`

### Wake Words
- Current: "Hey Assistant", "Jarvis"
- Modify in `src/assistant/core.py` method `listen_for_wake_word()`

### System Control Permissions
- Toggle in `src/assistant/core.py` line 44
- `require_auth=True` (default) or `False` for testing

## 🔧 Troubleshooting

### "Cannot connect to neural network"
```bash
# Ensure Ollama is running
ollama serve

# Check if model is installed
ollama list

# Pull model if needed
ollama pull llama3.2:3b
```

### Voice authentication fails
- Speak clearly during enrollment
- Use same microphone for enrollment and verification
- Re-enroll by deleting `data/voice_auth.pkl`

### Wake word not detected
- Check microphone input level
- Speak clearly: "Hey Assistant" or "Jarvis"
- Wait 1 second after assistant starts before speaking

### Media control not working
- Ensure pyautogui is installed: `pip install pyautogui`
- Start a media player (Spotify, YouTube, etc.)
- Test with "play music" or "pause"

### Weather not loading
- Check internet connection
- API uses wttr.in (no key needed)
- Try: "weather in London"

## 🚀 Advanced Usage

### Running in Background
```bash
# Windows
pythonw src/main.py

# Linux/Mac
nohup python src/main.py &
```

### Custom Capabilities
Add new modules to `src/capabilities/`:
1. Create module file (e.g., `email.py`)
2. Import in `src/assistant/core.py`
3. Add intent handling in `process_command()`

### Multiple Users
Each user needs their own voice enrollment:
```python
# Delete data/voice_auth.pkl
# Run assistant and enroll new user
python src/main.py
```

## 📊 Performance

- **Cold Start**: ~5 seconds (TTS + LLM initialization)
- **Wake Word Detection**: ~100ms latency
- **Command Processing**: 1-3 seconds (depends on LLM)
- **Memory Usage**: ~2GB (LLM model loaded)
- **CPU Usage**: 5-10% idle, 40-60% during command

## 🛣️ Roadmap

- [ ] Email integration (read, send)
- [ ] Calendar and reminders
- [ ] Smart home control (Home Assistant)
- [ ] Multi-language support
- [ ] Mobile app companion
- [ ] Conversation context memory
- [ ] Custom wake word training
- [ ] Plugin system for community extensions

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- New capability modules
- Better intent recognition
- Multi-platform testing
- Documentation improvements
- Bug fixes

Please open an issue or pull request on GitHub.

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **SpeechRecognition** - Voice input processing
- **pyttsx3** - Text-to-speech synthesis
- Inspired by JARVIS from Iron Man and Siri

## 📬 Support

- **Issues**: [GitHub Issues](https://github.com/Andrew-Kevin-007/EIDEN/issues)
- **Documentation**: See [QUICKSTART.md](QUICKSTART.md)
- **Repository**: https://github.com/Andrew-Kevin-007/EIDEN

---

**Made with ❤️ for voice assistant enthusiasts**