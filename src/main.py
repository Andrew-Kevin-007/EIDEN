"""Main entry point for the voice-controlled personal assistant."""
import sys
import signal
import logging
from pathlib import Path
from assistant.core import Assistant
from utils.config_manager import get_config
from utils.logging_config import setup_production_logging, HealthMonitor

# Version
VERSION = "2.1.0"

def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT/SIGTERM."""
    print("\n\nReceived shutdown signal...")
    sys.exit(0)

def main():
    """Initialize and run the voice assistant with wake word detection."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    config = get_config()
    
    # Setup logging
    log_config = config.get('logging', {})
    if log_config.get('enabled', True):
        setup_production_logging(log_config)
    
    logger = logging.getLogger('jarvis.main')
    logger.info(f"JARVIS Voice Assistant v{VERSION}")
    
    # Initialize health monitor
    health_monitor = HealthMonitor()
    
    # Display startup banner
    print("=" * 50)
    print(f"JARVIS Voice Assistant v{VERSION}")
    print("Production Mode")
    print("=" * 50)
    
    try:
        # Initialize assistant
        logger.info("Initializing assistant...")
        assistant = Assistant(config=config, health_monitor=health_monitor)
        assistant.initialize()
        
        if not assistant.is_initialized:
            logger.error("Failed to initialize assistant")
            print("Failed to initialize assistant. Check logs/jarvis.log")
            sys.exit(1)
        
        logger.info("Assistant initialized successfully")
        print("\nStarting always-on mode...")
        print("The assistant will now continuously listen for wake words.")
        print("Logs: logs/jarvis.log | Health: logs/health.json")
        
        # Start continuous wake word detection
        assistant.listen_for_wake_word()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        print("\n\nShutting down gracefully...")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"\n✗ Fatal error: {e}")
        print("Check logs/errors.log for details")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            if 'assistant' in locals():
                assistant.running = False
                assistant.speak("Goodbye!")
            
            # Save health report
            if 'health_monitor' in locals():
                health_monitor.save_health_report()
                status = health_monitor.get_health_status()
                logger.info(f"Final health status: {status}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()