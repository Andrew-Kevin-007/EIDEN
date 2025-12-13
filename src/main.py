"""Main entry point for the voice-controlled personal assistant."""
import sys
from assistant.core import Assistant


def main():
    """Initialize and run the voice assistant with wake word detection."""
    print("=" * 50)
    print("Voice-Controlled Personal Assistant")
    print("With Always-On Wake Word Detection")
    print("=" * 50)
    
    assistant = Assistant()
    assistant.initialize()
    
    if not assistant.is_initialized:
        print("Failed to initialize assistant. Exiting...")
        sys.exit(1)
    
    print("\nStarting always-on mode...")
    print("The assistant will now continuously listen for wake words.")
    
    try:
        # Start continuous wake word detection
        assistant.listen_for_wake_word()
        
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        assistant.running = False
        assistant.speak("Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()