"""
Configuration management for JARVIS production deployment.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

class Config:
    """Production configuration manager."""
    
    def __init__(self, config_file="config/settings.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.get_default_config()
        else:
            # Create default config
            config = self.get_default_config()
            self.save_config(config)
            return config
    
    def save_config(self, config=None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "version": "2.1.0",
            "assistant": {
                "name": "JARVIS",
                "wake_words": ["hey assistant", "jarvis"],
                "voice_rate": 200,
                "voice_volume": 1.0,
                "verbose": False
            },
            "llm": {
                "model": "llama3.2:3b",
                "host": "http://localhost:11434",
                "temperature": 0.3,
                "timeout": 10,
                "intent_timeout": 5,
                "max_tokens": 100
            },
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "wake_word_duration": 2,
                "command_duration": 4
            },
            "features": {
                "voice_auth": True,
                "app_discovery": True,
                "email": False,
                "weather": True,
                "web_search": True,
                "calculator": True,
                "timer": True,
                "media_control": True
            },
            "startup": {
                "auto_start": False,
                "minimize_to_tray": False,
                "show_notifications": True
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "performance": {
                "enable_cache": True,
                "cache_size": 100,
                "enable_fast_commands": True,
                "enable_timing": False
            },
            "security": {
                "require_auth_for_system": True,
                "session_timeout_minutes": 60
            }
        }
    
    def get(self, key: str, default=None):
        """Get configuration value by key (supports nested keys with '.')."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports nested keys with '.')."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def reload(self):
        """Reload configuration from file."""
        self.config = self.load_config()
    
    def reset_to_default(self):
        """Reset configuration to defaults."""
        self.config = self.get_default_config()
        self.save_config()

# Global config instance
_config_instance = None

def get_config(config_file="config/settings.json") -> Config:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_file)
    return _config_instance
