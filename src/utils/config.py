# Configuration settings for the voice-controlled personal assistant

# Directory paths
BASE_DIR = "path/to/base/directory"
DOWNLOADS_DIR = f"{BASE_DIR}/Downloads"

# Microphone settings
MICROPHONE_INDEX = 0  # Default microphone index
SAMPLE_RATE = 44100   # Sample rate for audio input
CHUNK_SIZE = 1024     # Buffer size for audio input

# Text-to-Speech settings
TTS_VOICE = "com.apple.speech.synthesis.voice.Alex"  # Example for macOS
TTS_RATE = 150  # Speech rate
TTS_VOLUME = 1.0  # Volume level (0.0 to 1.0)

# File operation settings
WHITELISTED_DIRS = [DOWNLOADS_DIR]  # Directories allowed for file operations
MAX_FILE_SIZE_MB = 5  # Maximum file size for operations in MB