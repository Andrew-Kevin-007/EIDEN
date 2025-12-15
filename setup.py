"""
JARVIS - Production Setup Script
Installs JARVIS as a system service and configures startup options.
"""
import os
import sys
import json
import winreg
from pathlib import Path
import subprocess
import shutil

JARVIS_NAME = "JARVIS Voice Assistant"
JARVIS_VERSION = "2.1.0"

class JARVISInstaller:
    def __init__(self):
        self.install_dir = Path(__file__).parent.absolute()
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        
    def create_directories(self):
        """Create necessary directories."""
        print("Creating directories...")
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        print("✓ Directories created")
    
    def create_default_config(self):
        """Create default configuration file."""
        print("Creating configuration...")
        config = {
            "version": JARVIS_VERSION,
            "assistant": {
                "name": "JARVIS",
                "wake_words": ["hey assistant", "jarvis"],
                "voice_rate": 200,
                "verbose": False
            },
            "llm": {
                "model": "llama3.2:3b",
                "host": "http://localhost:11434",
                "temperature": 0.3,
                "timeout": 10
            },
            "audio": {
                "sample_rate": 16000,
                "wake_word_duration": 2,
                "command_duration": 4
            },
            "features": {
                "voice_auth": True,
                "app_discovery": True,
                "email": False,
                "weather": True,
                "web_search": True
            },
            "startup": {
                "auto_start": False,
                "minimize_to_tray": True,
                "show_notifications": True
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
        
        config_file = self.config_dir / "settings.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✓ Configuration created at {config_file}")
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("\nInstalling dependencies...")
        requirements_file = self.install_dir / "requirements.txt"
        
        if not requirements_file.exists():
            print("✗ requirements.txt not found!")
            return False
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            print("✓ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False
    
    def add_to_startup(self):
        """Add JARVIS to Windows startup."""
        print("\nAdding to Windows startup...")
        
        try:
            # Create startup script
            startup_script = self.install_dir / "start_jarvis.bat"
            python_exe = sys.executable
            main_script = self.install_dir / "src" / "main.py"
            
            with open(startup_script, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{self.install_dir}"\n')
                f.write(f'start /min "" "{python_exe}" "{main_script}"\n')
            
            # Add to registry
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, JARVIS_NAME, 0, winreg.REG_SZ, str(startup_script))
            winreg.CloseKey(key)
            
            print(f"✓ Added to startup: {startup_script}")
            return True
        except Exception as e:
            print(f"✗ Failed to add to startup: {e}")
            return False
    
    def remove_from_startup(self):
        """Remove JARVIS from Windows startup."""
        print("\nRemoving from Windows startup...")
        
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, JARVIS_NAME)
            winreg.CloseKey(key)
            print("✓ Removed from startup")
            return True
        except FileNotFoundError:
            print("✓ Not in startup")
            return True
        except Exception as e:
            print(f"✗ Failed to remove from startup: {e}")
            return False
    
    def create_shortcuts(self):
        """Create desktop and start menu shortcuts."""
        print("\nCreating shortcuts...")
        
        try:
            # Desktop shortcut
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / f"{JARVIS_NAME}.lnk"
            
            # Use PowerShell to create shortcut
            ps_script = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{sys.executable}"
            $Shortcut.Arguments = '"{self.install_dir / "src" / "main.py"}"'
            $Shortcut.WorkingDirectory = "{self.install_dir}"
            $Shortcut.Description = "JARVIS Voice Assistant"
            $Shortcut.Save()
            """
            
            subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
            print(f"✓ Desktop shortcut created: {shortcut_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to create shortcuts: {e}")
            return False
    
    def check_ollama(self):
        """Check if Ollama is installed and running."""
        print("\nChecking Ollama installation...")
        
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✓ Ollama is running with {len(models)} models")
                
                # Check for required model
                has_model = any("llama3.2" in m.get("name", "") for m in models)
                if not has_model:
                    print("⚠ Warning: llama3.2:3b model not found")
                    print("  Run: ollama pull llama3.2:3b")
                return True
            else:
                print("✗ Ollama is not responding")
                return False
        except Exception as e:
            print(f"✗ Ollama is not installed or not running")
            print(f"  Install from: https://ollama.ai")
            return False
    
    def run_install(self):
        """Run full installation."""
        print("="*60)
        print(f"{JARVIS_NAME} - Installation")
        print(f"Version: {JARVIS_VERSION}")
        print("="*60)
        print()
        
        # Create directories
        self.create_directories()
        
        # Create config
        self.create_default_config()
        
        # Install dependencies
        if not self.install_dependencies():
            print("\n✗ Installation failed!")
            return False
        
        # Check Ollama
        self.check_ollama()
        
        # Ask about startup
        print("\n" + "="*60)
        response = input("Add JARVIS to Windows startup? (y/n): ").lower()
        if response == 'y':
            self.add_to_startup()
        
        # Ask about shortcuts
        response = input("Create desktop shortcut? (y/n): ").lower()
        if response == 'y':
            self.create_shortcuts()
        
        print("\n" + "="*60)
        print("✓ Installation complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull the model: ollama pull llama3.2:3b")
        print("3. Run JARVIS: python src/main.py")
        print("\nConfiguration file: config/settings.json")
        print("Logs directory: logs/")
        print("\n" + "="*60)
        
        return True
    
    def run_uninstall(self):
        """Run uninstallation."""
        print("="*60)
        print(f"{JARVIS_NAME} - Uninstallation")
        print("="*60)
        print()
        
        response = input("Are you sure you want to uninstall? (y/n): ").lower()
        if response != 'y':
            print("Uninstallation cancelled.")
            return
        
        # Remove from startup
        self.remove_from_startup()
        
        # Remove shortcuts
        try:
            desktop = Path.home() / "Desktop"
            shortcut = desktop / f"{JARVIS_NAME}.lnk"
            if shortcut.exists():
                shortcut.unlink()
                print(f"✓ Removed shortcut: {shortcut}")
        except Exception as e:
            print(f"✗ Failed to remove shortcut: {e}")
        
        print("\n✓ Uninstallation complete!")
        print("\nNote: Configuration and data files were preserved.")
        print("To completely remove, delete the installation directory.")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        print("JARVIS Installation Script")
        print("Usage:")
        print("  python setup.py install   - Install JARVIS")
        print("  python setup.py uninstall - Uninstall JARVIS")
        print("  python setup.py startup   - Add to Windows startup")
        print("  python setup.py nostartup - Remove from startup")
        return
    
    installer = JARVISInstaller()
    
    if command == "install":
        installer.run_install()
    elif command == "uninstall":
        installer.run_uninstall()
    elif command == "startup":
        installer.add_to_startup()
    elif command == "nostartup":
        installer.remove_from_startup()
    else:
        print(f"Unknown command: {command}")
        print("Use: install, uninstall, startup, or nostartup")

if __name__ == "__main__":
    main()
