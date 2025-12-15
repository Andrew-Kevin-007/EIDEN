# JARVIS Web GUI

A professional web-based interface for JARVIS voice assistant with an Apple Siri-like animated orb powered by WebGL shaders.

## Features

- **WebGL Voice-Powered Orb**: Real-time animated orb that reacts to your voice using WebGL shaders
- **Voice Recognition**: Advanced voice command processing
- **Real-Time Communication**: WebSocket connection for instant responses
- **Modern UI**: Built with Next.js, React, TypeScript, and Tailwind CSS
- **Voice Reactivity**: Orb animation responds dynamically to voice input intensity
- **Chat History**: View all your conversations with JARVIS
- **Command Suggestions**: Quick-access buttons for common commands
- **Dark/Light Mode**: Automatic theme switching based on system preferences

## Architecture

### Frontend (Next.js + React)
- **Framework**: Next.js 16 with Turbopack
- **Language**: TypeScript
- **Styling**: Tailwind CSS with shadcn/ui components
- **WebGL**: OGL library for shader-based rendering
- **Voice Analysis**: Web Audio API for real-time voice detection

### Backend (FastAPI + Python)
- **API Framework**: FastAPI with WebSocket support
- **Voice Assistant**: Python-based JARVIS assistant
- **Speech Recognition**: sounddevice + vosk/whisper
- **Text-to-Speech**: pyttsx3
- **LLM Integration**: Ollama for natural language understanding

## Installation

### Prerequisites
- Python 3.14+ (virtual environment recommended)
- Node.js 18+ and npm/pnpm
- Microphone access
- Modern web browser (Chrome, Firefox, Edge recommended)

### Backend Setup

1. Navigate to the voice-assistant directory:
```bash
cd d:\Edien\voice-assistant
```

2. Install Python dependencies (in virtual environment):
```bash
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn[standard]
- websockets
- sounddevice
- numpy
- scipy
- pyttsx3
- vosk/whisper
- ollama

### Frontend Setup

1. Navigate to the web-gui directory:
```bash
cd web-gui
```

2. Install npm dependencies:
```bash
npm install
```

Key dependencies:
- next@latest
- react@18
- typescript
- tailwindcss
- ogl (WebGL library)
- @radix-ui components

## Running the Application

### Option 1: Using the Launcher Script (Recommended)

Simply double-click or run:
```bash
start_web_gui.bat
```

This will:
1. Start the FastAPI backend server (port 8000)
2. Start the Next.js frontend (port 3000)
3. Automatically open your browser to http://localhost:3000

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```bash
cd d:\Edien\voice-assistant
D:/Edien/voice-assistant/.venv/Scripts/python.exe api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd d:\Edien\voice-assistant\web-gui
npm run dev
```

Then open your browser to: http://localhost:3000

## Usage

### Basic Commands

1. **Click "Start Listening"** - Activates the microphone
2. **Speak your command** - The orb will react to your voice
3. **View response** - JARVIS will respond both visually and audibly

### Supported Commands

#### General
- "Hello JARVIS"
- "What time is it?"
- "What's the date?"

#### Web Automation
- "Search Google for Python tutorials"
- "Open YouTube"
- "Get news headlines"
- "Fetch content from [URL]"

#### App Automation
- "Type in Notepad: Hello World"
- "Draft an email to example@email.com"
- "Take a screenshot"
- "Copy this text to clipboard"

#### System Control
- "Open File Explorer"
- "Shut down computer"
- "Set volume to 50%"

#### Productivity
- "Set timer for 5 minutes"
- "Check the weather"
- "Calculate 25 * 47"

### Using the Web Interface

1. **Voice-Powered Orb**: The animated orb in the center responds to your voice:
   - **Idle**: Gentle pulsing animation
   - **Listening**: Dynamic rotation based on voice intensity
   - **Responding**: Smooth transitions

2. **Chat History**: View all your commands and JARVIS responses in the left panel

3. **Command Suggestions**: Click any suggested command button for quick access

4. **Recent Commands**: Your last 5 commands are shown for easy re-execution

## WebGL Orb Component

The voice-powered orb is a custom WebGL component featuring:

- **Fragment Shader**: 200+ lines of GLSL code for gradient rendering
- **Simplex Noise**: Procedural noise for organic movement
- **YIQ Color Space**: Smooth color transitions
- **Voice Analysis**: Real-time RMS calculation from microphone input
- **Dynamic Effects**: Rotation speed and intensity based on voice level

### Customization

You can customize the orb in [app/page.tsx](app/page.tsx):

```tsx
<VoicePoweredOrb
  hue={180}                      // Color (0-360)
  enableVoiceControl={true}      // Voice reactivity
  voiceSensitivity={1.5}         // Sensitivity multiplier
  maxRotationSpeed={1.2}         // Max rotation speed
  maxHoverIntensity={0.8}        // Max hover effect
  onVoiceDetected={(level) => {  // Voice level callback
    console.log('Voice level:', level);
  }}
/>
```

## API Endpoints

### REST API

- `POST /api/command` - Process voice command
  ```json
  {
    "command": "What's the weather?"
  }
  ```

- `POST /api/speak` - Text-to-speech
  ```json
  {
    "text": "Hello, how can I help?"
  }
  ```

- `POST /api/start` - Start assistant
- `POST /api/stop` - Stop assistant
- `GET /api/status` - Get assistant status

### WebSocket

Connect to `ws://localhost:8000/ws` for real-time updates:

**Sent Events:**
- `command`: User voice command
- `start_listening`: Begin voice recognition
- `stop_listening`: End voice recognition

**Received Events:**
- `status_update`: Assistant status changes
- `transcript_update`: Voice recognition results
- `response_update`: Assistant responses

## Project Structure

```
web-gui/
├── app/
│   ├── globals.css          # Global styles and CSS variables
│   ├── layout.tsx            # Root layout with fonts and metadata
│   └── page.tsx              # Main application component
├── components/
│   └── ui/
│       ├── button.tsx        # shadcn Button component
│       └── voice-powered-orb.tsx  # WebGL orb component
├── lib/
│   └── utils.ts              # Utility functions
├── public/                   # Static assets
├── next.config.js            # Next.js configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
├── postcss.config.js         # PostCSS configuration
└── package.json              # npm dependencies

voice-assistant/
├── api_server.py             # FastAPI backend
├── src/
│   ├── assistant/            # Core assistant logic
│   ├── capabilities/         # Web and app automation
│   ├── speech/               # Voice recognition and TTS
│   ├── llm/                  # LLM integration
│   └── utils/                # Configuration and logging
└── start_web_gui.bat         # Launcher script
```

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'X'"**
- Ensure you're using the virtual environment
- Run: `pip install -r requirements.txt`

**"Microphone not detected"**
- Check microphone permissions
- Verify audio device in Windows Settings
- See available devices in backend startup logs

**"LLM not responding"**
- Ensure Ollama is running
- Check Ollama model is downloaded: `ollama pull llama2`

### Frontend Issues

**"Module not found: tailwindcss-animate"**
- Run: `npm install` again
- Clear npm cache: `npm cache clean --force`

**"Port 3000 already in use"**
- Kill the process on port 3000
- Or change port in package.json: `"dev": "next dev -p 3001"`

**WebGL orb not rendering**
- Check browser console for errors
- Ensure WebGL is supported: Visit https://get.webgl.org/
- Try disabling browser extensions

**WebSocket connection failed**
- Verify backend is running on port 8000
- Check CORS settings in api_server.py
- Look for firewall blocking localhost connections

### Voice Issues

**Microphone permission denied**
- Browser will prompt for microphone access
- Check browser settings: chrome://settings/content/microphone
- Ensure HTTPS or localhost (required for getUserMedia)

**Voice not being detected**
- Increase `voiceSensitivity` prop
- Check browser console for audio context errors
- Verify microphone working in Windows Sound Settings

## Performance Tips

1. **WebGL Performance**: The orb runs at 60 FPS. If you experience lag:
   - Close other browser tabs
   - Disable browser hardware acceleration and re-enable
   - Reduce `maxRotationSpeed` and `maxHoverIntensity`

2. **WebSocket Connection**: Keep the backend running continuously for best performance

3. **Voice Recognition**: For faster responses:
   - Use a good quality microphone
   - Speak clearly and at moderate volume
   - Minimize background noise

## Development

### Adding New Commands

1. Add capability in `src/capabilities/`
2. Update `src/commands/handlers.py`
3. Add intent recognition in `src/llm/local_llm.py`
4. Update command suggestions in `web-gui/app/page.tsx`

### Customizing the UI

- **Colors**: Edit CSS variables in `app/globals.css`
- **Orb**: Modify shaders in `components/ui/voice-powered-orb.tsx`
- **Layout**: Update grid structure in `app/page.tsx`
- **Theme**: Configure Tailwind in `tailwind.config.ts`

### Building for Production

```bash
# Frontend
cd web-gui
npm run build
npm start  # Production server

# Backend
# Use gunicorn or uvicorn with multiple workers
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## Security Notes

- The application runs on localhost by default
- For production deployment:
  - Enable HTTPS
  - Configure proper CORS origins
  - Add authentication
  - Use environment variables for secrets
  - Implement rate limiting

## Credits

- **Voice Assistant Core**: Custom Python implementation
- **WebGL Orb**: Inspired by Apple's Siri interface
- **UI Components**: shadcn/ui (Radix UI + Tailwind CSS)
- **WebGL Library**: OGL by Nathan Gordon
- **Framework**: Next.js by Vercel

## License

See LICENSE file for details.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console for error messages
3. Check backend terminal for Python errors
4. Ensure all dependencies are installed correctly

---

**Enjoy your new JARVIS Web GUI! 🎙️✨**
