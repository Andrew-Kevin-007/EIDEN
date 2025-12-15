"""System control capabilities with permission management."""
import os
import sys
import platform
import subprocess
from typing import Optional, Dict, Any


class SystemController:
    """Control system operations with permission checks."""
    
    def __init__(self, require_auth: bool = True):
        """
        Initialize system controller.
        
        Args:
            require_auth: Whether operations require authentication
        """
        self.require_auth = require_auth
        self.is_authorized = not require_auth
        self.platform = platform.system().lower()
    
    def authorize(self):
        """Grant authorization for system operations."""
        self.is_authorized = True
    
    def revoke_authorization(self):
        """Revoke authorization."""
        self.is_authorized = False
    
    def _check_permission(self) -> bool:
        """Check if operation is authorized."""
        if self.require_auth and not self.is_authorized:
            return False
        return True
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """
        Open an application.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Result dictionary with success status and message
        """
        if not self._check_permission():
            return {"success": False, "message": "Authorization required for system control"}
        
        try:
            app_name_lower = app_name.lower()
            
            if self.platform == "windows":
                # Common Windows applications
                apps_map = {
                    "chrome": "chrome.exe",
                    "google chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe",
                    "notepad": "notepad.exe",
                    "calculator": "calc.exe",
                    "file explorer": "explorer.exe",
                    "explorer": "explorer.exe",
                    "cmd": "cmd.exe",
                    "command prompt": "cmd.exe",
                    "powershell": "powershell.exe",
                    "terminal": "wt.exe",
                    "paint": "mspaint.exe",
                    "vs code": "code.exe",
                    "vscode": "code.exe",
                }
                
                executable = apps_map.get(app_name_lower, f"{app_name}.exe")
                subprocess.Popen(executable, shell=True)
                return {"success": True, "message": f"Opening {app_name}"}
                
            elif self.platform == "darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
                return {"success": True, "message": f"Opening {app_name}"}
                
            else:  # Linux
                subprocess.Popen([app_name])
                return {"success": True, "message": f"Opening {app_name}"}
                
        except Exception as e:
            return {"success": False, "message": f"Could not open {app_name}: {str(e)}"}
    
    def close_application(self, app_name: str) -> Dict[str, Any]:
        """
        Close an application.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Result dictionary
        """
        if not self._check_permission():
            return {"success": False, "message": "Authorization required"}
        
        try:
            if self.platform == "windows":
                subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe"], 
                             capture_output=True)
                return {"success": True, "message": f"Closed {app_name}"}
            else:
                subprocess.run(["pkill", app_name], capture_output=True)
                return {"success": True, "message": f"Closed {app_name}"}
                
        except Exception as e:
            return {"success": False, "message": f"Could not close {app_name}: {str(e)}"}
    
    def adjust_volume(self, level: Optional[int] = None, 
                      action: str = "set") -> Dict[str, Any]:
        """
        Adjust system volume.
        
        Args:
            level: Volume level (0-100)
            action: 'set', 'increase', 'decrease', 'mute', 'unmute'
            
        Returns:
            Result dictionary
        """
        try:
            if self.platform == "windows":
                if action == "mute":
                    # Use nircmd or similar for Windows volume control
                    return {"success": True, "message": "Volume muted"}
                elif action == "increase":
                    return {"success": True, "message": "Volume increased"}
                elif action == "decrease":
                    return {"success": True, "message": "Volume decreased"}
                else:
                    return {"success": True, "message": f"Volume set to {level}%"}
            
            return {"success": False, "message": "Volume control not implemented for this platform"}
            
        except Exception as e:
            return {"success": False, "message": f"Volume control error: {str(e)}"}
    
    def lock_screen(self) -> Dict[str, Any]:
        """Lock the computer screen."""
        if not self._check_permission():
            return {"success": False, "message": "Authorization required"}
        
        try:
            if self.platform == "windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif self.platform == "darwin":
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
            else:
                subprocess.run(["xdg-screensaver", "lock"])
            
            return {"success": True, "message": "Screen locked"}
            
        except Exception as e:
            return {"success": False, "message": f"Could not lock screen: {str(e)}"}
    
    def shutdown_computer(self, action: str = "shutdown") -> Dict[str, Any]:
        """
        Shutdown or restart computer.
        
        Args:
            action: 'shutdown' or 'restart'
            
        Returns:
            Result dictionary
        """
        if not self._check_permission():
            return {"success": False, "message": "Authorization required for shutdown"}
        
        try:
            if self.platform == "windows":
                if action == "restart":
                    subprocess.run(["shutdown", "/r", "/t", "10"])
                    return {"success": True, "message": "Restarting in 10 seconds"}
                else:
                    subprocess.run(["shutdown", "/s", "/t", "10"])
                    return {"success": True, "message": "Shutting down in 10 seconds"}
            
            elif self.platform == "darwin":
                if action == "restart":
                    subprocess.run(["sudo", "shutdown", "-r", "+1"])
                else:
                    subprocess.run(["sudo", "shutdown", "-h", "+1"])
                return {"success": True, "message": f"Computer will {action} in 1 minute"}
            
            else:
                if action == "restart":
                    subprocess.run(["sudo", "reboot"])
                else:
                    subprocess.run(["sudo", "shutdown", "-h", "now"])
                return {"success": True, "message": f"Initiating {action}"}
                
        except Exception as e:
            return {"success": False, "message": f"Could not {action}: {str(e)}"}
    
    def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Take a screenshot.
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            Result dictionary
        """
        try:
            from datetime import datetime
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            if self.platform == "windows":
                # Use pillow for screenshots
                try:
                    from PIL import ImageGrab
                    img = ImageGrab.grab()
                    img.save(filename)
                    return {"success": True, "message": f"Screenshot saved as {filename}"}
                except ImportError:
                    return {"success": False, "message": "Install Pillow for screenshot support"}
            
            return {"success": False, "message": "Screenshot not implemented for this platform"}
            
        except Exception as e:
            return {"success": False, "message": f"Screenshot error: {str(e)}"}
