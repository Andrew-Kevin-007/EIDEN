"""Performance optimizations for JARVIS."""

# Speech Recognition Settings
WAKE_WORD_DURATION = 2  # seconds (reduced from 3)
COMMAND_DURATION = 4    # seconds (reduced from 5)

# TTS Settings
TTS_RATE = 200  # words per minute (increased from 150)
TTS_VOLUME = 1.0

# LLM Settings
LLM_TEMPERATURE = 0.3      # Lower = faster, more deterministic
LLM_TIMEOUT = 10           # seconds for chat
LLM_INTENT_TIMEOUT = 5     # seconds for intent extraction
LLM_MAX_TOKENS = 100       # Limit response length

# Fast Command Patterns (skip LLM)
FAST_COMMANDS = {
    # Time queries
    'time': ['time', 'what time', "what's the time"],
    
    # Date queries
    'date': ['date', 'what day', 'today', 'what date'],
    
    # Applications
    'calculator': ['calculator', 'calc', 'open calc'],
    'explorer': ['file explorer', 'open explorer', 'explorer'],
    'notepad': ['notepad', 'open notepad'],
    'paint': ['paint', 'open paint'],
    
    # Folders
    'downloads': ['downloads', 'download folder', 'open downloads'],
    'documents': ['documents', 'document folder', 'my documents'],
    'pictures': ['pictures', 'picture folder', 'photos'],
    'desktop': ['desktop', 'open desktop'],
    
    # Media
    'play': ['play', 'resume'],
    'pause': ['pause', 'stop music'],
    'next': ['next', 'next song', 'skip'],
    'previous': ['previous', 'last song', 'back'],
    
    # Volume
    'volume up': ['volume up', 'louder', 'increase volume'],
    'volume down': ['volume down', 'quieter', 'decrease volume'],
    'mute': ['mute', 'silence'],
}

# Cache Settings
ENABLE_CACHE = True
CACHE_SIZE = 100  # Number of commands to cache

# Performance Monitoring
ENABLE_TIMING = False  # Set to True to see response times
