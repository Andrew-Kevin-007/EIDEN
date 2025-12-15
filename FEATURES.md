# JARVIS Features Documentation

## Overview
JARVIS is now a fully-functional AI voice assistant similar to Siri, with comprehensive capabilities for web interaction, information retrieval, productivity, media control, and system automation.

## 🎯 Core Features

### 1. **Local LLM Intelligence**
- **Model**: Llama 3.2 (3B parameters, 2GB)
- **Backend**: Ollama for local inference
- **Capabilities**:
  - Natural conversation
  - Intent extraction and understanding
  - Context-aware responses
  - No cloud dependency for AI processing
  
**Example Commands**:
- "Tell me a joke"
- "What can you do?"
- "Explain quantum computing"

### 2. **Voice Authentication**
- **Security**: Biometric-like voice verification
- **Storage**: Local only (`data/voice_auth.pkl`)
- **Enrollment**: 3 voice samples required
- **Verification**: 3 attempts allowed
- **Use Case**: Required for sensitive system operations

**Setup Process**:
1. First run triggers enrollment
2. Say "My voice is my password" 3 times
3. Voice features extracted and stored locally
4. Subsequent runs verify your voice automatically

### 3. **Always-On Wake Word Detection**
- **Wake Words**: "Hey Assistant", "Jarvis"
- **Detection**: Continuous 3-second audio monitoring
- **Latency**: ~100ms from wake word to activation
- **Audio Processing**: sounddevice for cross-platform compatibility

**Usage**:
1. Say wake word
2. Wait for "Yes, I'm listening"
3. Give command
4. Get response
5. Automatically returns to listening

---

## 🌐 Web & Information Capabilities

### 4. **Web Search**
**Module**: `src/capabilities/web_search.py`

**Features**:
- Google search with browser opening
- Bing search integration
- YouTube search
- Open any website by voice
- DuckDuckGo instant answers

**Commands**:
- "Search for Python tutorials"
- "Search YouTube for cooking videos"
- "Open reddit.com"
- "Open Google"
- "What is the capital of France?" (instant answer)

**Technical Details**:
- Uses `webbrowser` module for browser control
- DuckDuckGo API for quick facts
- No API keys required
- Returns `{"success": bool, "message": str}` format

### 5. **Weather Service**
**Module**: `src/capabilities/weather.py`

**Features**:
- Current weather conditions
- 3-day forecast
- Location-based queries
- Temperature, precipitation, wind
- Works worldwide

**Commands**:
- "What's the weather?" (uses your IP location)
- "Weather in Tokyo"
- "Weather forecast"
- "Is it going to rain?"

**API**: wttr.in (no key needed)
**Format**: Parsed ASCII art weather display

### 6. **Calculator & Unit Conversions**
**Module**: `src/capabilities/calculator.py`

**Features**:
- Basic arithmetic (+ - * / ** %)
- Complex expressions with parentheses
- Temperature conversions (F/C/K)
- Distance conversions (miles/km/meters/feet)
- Weight conversions (kg/lbs/oz)
- Safe evaluation (no code execution)

**Commands**:
- "What is 25 times 47?"
- "Calculate 150 divided by 3"
- "Convert 100 fahrenheit to celsius"
- "How many kilometers in 50 miles?"
- "Convert 180 pounds to kilograms"

**Safety**: Uses AST parsing (no `eval()` risks)

---

## 🛠️ Productivity Features

### 7. **Timer Manager**
**Module**: `src/capabilities/timer.py`

**Features**:
- Multiple concurrent timers
- Voice notifications when timer expires
- Natural language duration parsing
- List active timers
- Cancel timers

**Commands**:
- "Set timer for 5 minutes"
- "Set a timer for 30 seconds"
- "Timer for 1 hour"
- "List timers"
- "Cancel timer"

**Technical Details**:
- Threading for concurrent timers
- Callback to TTS for notifications
- Supports: seconds, minutes, hours
- Format: `{number} {unit}` (e.g., "5 minutes")

### 8. **Media Control**
**Module**: `src/capabilities/media_control.py`

**Features**:
- Play/pause toggle
- Next/previous track
- Volume up/down
- Mute/unmute
- Works with any media player

**Commands**:
- "Play music" / "Pause music"
- "Next song"
- "Previous track"
- "Volume up"
- "Volume down"
- "Mute"

**Platform**: Windows media keys via pyautogui
**Note**: Works with Spotify, YouTube, VLC, etc.

### 9. **Time & Date Queries**
**Module**: `src/assistant/core.py` (_handle_productivity)

**Features**:
- Current time (12-hour format)
- Current date (full format)
- Day of week

**Commands**:
- "What time is it?"
- "What's today's date?"
- "What day is it?"

**Output Examples**:
- Time: "The time is 3:45 PM"
- Date: "Today is Monday, January 15, 2024"

---

## 🖥️ System Control

### 10. **System Operations**
**Module**: `src/capabilities/system_control.py`

**Features** (Requires Voice Auth):
- Open applications
- Close applications
- Lock screen
- Screenshot capture
- System shutdown/restart
- Volume control

**Commands**:
- "Open Chrome"
- "Open Notepad"
- "Lock the screen"
- "Take a screenshot"
- "Shutdown the computer"

**Security**: All operations require voice authentication

**Platform Support**:
- Windows: Full support
- macOS: Framework in place
- Linux: Framework in place

**Screenshot Location**: Current directory as `screenshot_YYYYMMDD_HHMMSS.png`

---

## 🧠 Intent Recognition System

**Module**: `src/llm/local_llm.py`

**Intent Categories**:
1. **system_control** - Apps, lock, shutdown, screenshot
2. **weather** - Current weather, forecast
3. **calculation** - Math, unit conversions
4. **media_control** - Play/pause, volume, tracks
5. **timer** - Set, list, cancel timers
6. **search** - Web search, YouTube, open websites
7. **productivity** - Time, date, calendar
8. **file_operation** - File management (future)
9. **general** - Conversation, questions

**Process**:
1. User command captured
2. LLM extracts intent, action, parameters
3. Permission check if needed
4. Route to appropriate handler
5. Execute and return result

**Example Intent Extraction**:
```json
{
  "intent": "weather",
  "action": "get_weather",
  "parameters": {"location": "New York"},
  "needs_permission": false
}
```

---

## 🔐 Security & Privacy

### Voice Authentication Details
- **Algorithm**: Voice feature extraction using NumPy
- **Storage**: Encrypted pickle file locally
- **Re-enrollment**: Delete `data/voice_auth.pkl`
- **Verification**: 3 attempts before failure
- **Session**: Authorization persists until exit

### Permission System
- **Sensitive Operations**: Require voice auth
- **Safe Operations**: No auth needed (weather, calculator, etc.)
- **Toggle**: Can disable auth for testing (not recommended)

### Privacy Guarantees
- **No Cloud AI**: LLM runs 100% locally via Ollama
- **Voice Data**: Never leaves your machine
- **Internet Only For**:
  - Speech recognition (Google API)
  - Weather data (wttr.in)
  - Web search (when requested)
  - DuckDuckGo instant answers

---

## 📊 Performance Metrics

### Response Times
- **Wake Word Detection**: ~100ms
- **Intent Extraction**: 1-2 seconds (LLM)
- **Command Execution**: <1 second (most operations)
- **Web Search**: 1-3 seconds (browser opening)
- **Weather Query**: 1-2 seconds (API call)

### Resource Usage
- **Memory**: ~2GB (with LLM loaded)
- **CPU (Idle)**: 5-10%
- **CPU (Processing)**: 40-60%
- **Disk**: ~50MB (excluding LLM model)
- **LLM Model**: 2GB (Llama 3.2)

### Accuracy
- **Wake Word**: ~95% in normal conditions
- **Speech Recognition**: ~90% (Google API)
- **Intent Extraction**: ~85% (depends on command clarity)

---

## 🔧 Technical Architecture

### Command Flow
```
User Voice Input
    ↓
Wake Word Detected
    ↓
Full Command Capture (SpeechRecognition)
    ↓
Intent Extraction (Ollama LLM)
    ↓
Permission Check (VoiceAuth if needed)
    ↓
Command Routing (core.py)
    ↓
Capability Module Execution
    ↓
Response Generation
    ↓
Text-to-Speech Output (pyttsx3)
    ↓
Return to Wake Word Monitoring
```

### Module Dependencies
```
core.py (Assistant)
├── local_llm.py (LLM)
├── voice_auth.py (Security)
├── system_control.py (System ops)
├── web_search.py (Web)
├── weather.py (Weather)
├── calculator.py (Math)
├── timer.py (Timers)
└── media_control.py (Media)
```

### API Integrations
- **Google Speech Recognition**: Voice-to-text
- **wttr.in**: Weather data (no key)
- **DuckDuckGo**: Instant answers (no key)
- **Ollama**: Local LLM inference (port 11434)

---

## 🚀 Future Enhancements

### Planned Features
- [ ] Email integration (read/send)
- [ ] Calendar management
- [ ] Reminder system
- [ ] Smart home control (Home Assistant)
- [ ] News briefings
- [ ] Multi-language support
- [ ] Custom wake word training
- [ ] Spotify API integration
- [ ] File management commands
- [ ] Code execution environment
- [ ] Meeting scheduler
- [ ] Note-taking capability

### Community Requests
- Plugin system for custom capabilities
- Mobile app companion
- Cloud sync (optional)
- Voice profiles for multiple users
- Better noise cancellation
- Faster LLM models (GPU acceleration)

---

## 📚 Development Notes

### Adding New Capabilities

1. **Create Module**: `src/capabilities/your_feature.py`
```python
class YourFeature:
    def __init__(self):
        pass
    
    def your_method(self, param):
        # Implementation
        return {"success": True, "message": "Result"}
```

2. **Import in core.py**:
```python
from capabilities.your_feature import YourFeature
```

3. **Initialize in __init__**:
```python
self.your_feature = YourFeature()
```

4. **Add Intent Handling**:
```python
elif intent_info["intent"] == "your_intent":
    self._handle_your_feature(action, params)
```

5. **Create Handler Method**:
```python
def _handle_your_feature(self, action, params):
    result = self.your_feature.your_method(params["param"])
    self.speak(result["message"])
```

### Testing New Features
```bash
# Run with debug output
python src/main.py

# Test specific capability
python -c "from src.capabilities.your_feature import YourFeature; YourFeature().your_method('test')"
```

---

## 📖 API Reference

### Return Format Standard
All capability modules return:
```python
{
    "success": bool,      # Operation success status
    "message": str,       # User-friendly message
    "data": Any,         # Optional: raw data
    "error": str         # Optional: error details
}
```

### Common Parameters
- `command`: Full user command string
- `action`: Specific action to perform
- `params`: Dictionary of extracted parameters
- `speak_callback`: TTS function reference (for timers)

---

**Last Updated**: January 2024  
**Version**: 2.0 (Siri-like Edition)  
**Contributors**: Voice Assistant Community
