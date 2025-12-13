# Voice-Controlled Personal Assistant

A Python-based voice assistant with **always-on wake word detection**. The assistant runs continuously in the background and activates when you say a wake word.

## Features

✅ **Always-On Wake Word Detection** - Just say "Hey Assistant" or "Jarvis" to activate  
✅ **Offline Text-to-Speech** - Uses pyttsx3 for voice responses  
✅ **Speech Recognition** - Converts your voice to text using Google Speech Recognition  
✅ **Modular Architecture** - Clean, maintainable code structure  
✅ **Safe File Operations** - Read-only access to whitelisted directories  
✅ **No PyAudio Required** - Uses sounddevice for easier Windows installation  

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd voice-assistant
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Always-On Mode (Recommended)

Run the assistant once and it will continuously listen for wake words:

```
python src/main.py
```

**Wake words:** "Hey Assistant", "Jarvis", "Okay Assistant", "Assistant"

**Example interaction:**
1. Say: "Hey Assistant"
2. Assistant responds: "Yes, I'm listening."
3. Say your command: "What time is it?"
4. Assistant responds with the time
5. Continues listening for the next wake word

### Available Commands

- **"Hello"** / **"Hi"** - Greeting
- **"What time is it?"** - Current time
- **"What's the date?"** - Current date
- **"Help"** - List available commands
- **"List files"** - File operations (requires configuration)
- **"Goodbye"** / **"Exit"** - Stop the assistant

## How It Works

1. **Continuous Monitoring**: The assistant continuously records short audio clips (3 seconds)
2. **Wake Word Detection**: Checks each clip for wake words using speech recognition
3. **Command Processing**: When a wake word is detected, it listens for your command
4. **Response**: Processes the command and speaks the response
5. **Loop**: Returns to monitoring for wake words

## Project Structure

```
voice-assistant
├── src
│   ├── main.py               # Entry point of the application
│   ├── assistant             # Contains core logic for the assistant
│   ├── speech                # Handles speech recognition and synthesis
│   ├── commands              # Defines command handlers
│   ├── file_operations       # Manages safe file operations
│   └── utils                 # Utility functions and configurations
├── tests                     # Contains unit tests for the application
├── config                    # Configuration settings
├── requirements.txt          # Project dependencies
├── .gitignore                # Files to ignore in version control
└── README.md                 # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd voice-assistant
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the voice assistant, execute the following command:
```
python src/main.py
```

Follow the prompts and interact with the assistant using your voice. 

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.