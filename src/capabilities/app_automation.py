"""
Application automation - type in Word, draft emails, control applications.
"""
import logging
import time
from typing import Optional, List
import subprocess
import os

try:
    import pyautogui
    import keyboard
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    logging.warning("pyautogui/keyboard not available - app automation disabled")


class AppAutomation:
    """Automate typing and interaction with applications."""
    
    def __init__(self):
        self.logger = logging.getLogger('jarvis.app_automation')
        self.supported_apps = {
            'word': ['WINWORD.EXE', 'Microsoft Word'],
            'notepad': ['notepad.exe', 'Notepad'],
            'notepad++': ['notepad++.exe', 'Notepad++'],
            'excel': ['EXCEL.EXE', 'Microsoft Excel'],
            'powerpoint': ['POWERPNT.EXE', 'Microsoft PowerPoint'],
            'outlook': ['OUTLOOK.EXE', 'Microsoft Outlook'],
            'chrome': ['chrome.exe', 'Google Chrome'],
            'firefox': ['firefox.exe', 'Mozilla Firefox'],
            'edge': ['msedge.exe', 'Microsoft Edge']
        }
        
        if AUTOMATION_AVAILABLE:
            pyautogui.FAILSAFE = True  # Move mouse to corner to stop
            pyautogui.PAUSE = 0.1  # Pause between actions
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if application is running."""
        app_name = app_name.lower()
        exe_names = self.supported_apps.get(app_name, [app_name + '.exe'])
        
        try:
            result = subprocess.run(
                ['tasklist'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for exe in exe_names:
                if exe.lower() in result.stdout.lower():
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if app running: {e}")
            return False
    
    def open_and_type(self, app_name: str, text: str) -> str:
        """Open application and type text."""
        if not AUTOMATION_AVAILABLE:
            return "Automation requires 'pyautogui' and 'keyboard' packages"
        
        try:
            # Check if app is running
            if not self.is_app_running(app_name):
                self.logger.info(f"Opening {app_name}...")
                # Try to open the app
                if app_name.lower() in self.supported_apps:
                    exe = self.supported_apps[app_name.lower()][0]
                    subprocess.Popen(exe, shell=True)
                    time.sleep(3)  # Wait for app to open
                else:
                    return f"Don't know how to open {app_name}"
            
            # Wait a moment for window to be ready
            time.sleep(1)
            
            # Type the text
            pyautogui.write(text, interval=0.05)
            
            self.logger.info(f"Typed text in {app_name}")
            return f"Typed in {app_name}"
            
        except Exception as e:
            self.logger.error(f"Error typing in app: {e}")
            return f"Failed to type in {app_name}: {e}"
    
    def draft_email_outlook(self, to: str, subject: str, body: str) -> str:
        """Draft email in Outlook."""
        if not AUTOMATION_AVAILABLE:
            return "Automation requires 'pyautogui' and 'keyboard' packages"
        
        try:
            # Open Outlook if not running
            if not self.is_app_running('outlook'):
                subprocess.Popen('OUTLOOK.EXE', shell=True)
                time.sleep(5)
            
            # Create new email (Ctrl+N in Outlook)
            time.sleep(1)
            keyboard.press_and_release('ctrl+n')
            time.sleep(2)
            
            # Fill in To field
            pyautogui.write(to, interval=0.05)
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Skip CC (press tab)
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Fill in subject
            pyautogui.write(subject, interval=0.05)
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Fill in body
            pyautogui.write(body, interval=0.05)
            
            self.logger.info("Drafted email in Outlook")
            return "Email drafted in Outlook"
            
        except Exception as e:
            self.logger.error(f"Error drafting email: {e}")
            return f"Failed to draft email: {e}"
    
    def type_in_active_window(self, text: str) -> str:
        """Type text in currently active window."""
        if not AUTOMATION_AVAILABLE:
            return "Automation requires 'pyautogui' package"
        
        try:
            time.sleep(1)  # Brief pause
            pyautogui.write(text, interval=0.05)
            
            self.logger.info("Typed in active window")
            return "Typed text in active window"
            
        except Exception as e:
            self.logger.error(f"Error typing: {e}")
            return f"Failed to type: {e}"
    
    def press_keys(self, keys: List[str]) -> str:
        """Press keyboard keys/shortcuts."""
        if not AUTOMATION_AVAILABLE:
            return "Automation requires 'keyboard' package"
        
        try:
            key_combination = '+'.join(keys)
            keyboard.press_and_release(key_combination)
            
            self.logger.info(f"Pressed keys: {key_combination}")
            return f"Pressed {key_combination}"
            
        except Exception as e:
            self.logger.error(f"Error pressing keys: {e}")
            return f"Failed to press keys: {e}"
    
    def copy_to_clipboard(self, text: str) -> str:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            
            self.logger.info("Copied to clipboard")
            return "Copied to clipboard"
            
        except ImportError:
            return "Clipboard requires 'pyperclip' package"
        except Exception as e:
            self.logger.error(f"Clipboard error: {e}")
            return f"Failed to copy: {e}"
    
    def paste_from_clipboard(self) -> str:
        """Get text from clipboard."""
        try:
            import pyperclip
            text = pyperclip.paste()
            
            self.logger.info("Retrieved from clipboard")
            return text
            
        except ImportError:
            return "Clipboard requires 'pyperclip' package"
        except Exception as e:
            self.logger.error(f"Clipboard error: {e}")
            return ""
    
    def take_screenshot(self, save_path: Optional[str] = None) -> str:
        """Take screenshot."""
        if not AUTOMATION_AVAILABLE:
            return "Screenshot requires 'pyautogui' package"
        
        try:
            if save_path is None:
                save_path = f"screenshot_{int(time.time())}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            
            self.logger.info(f"Screenshot saved to: {save_path}")
            return f"Screenshot saved to {save_path}"
            
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return f"Failed to take screenshot: {e}"
    
    def click_at_position(self, x: int, y: int) -> str:
        """Click at specific screen position."""
        if not AUTOMATION_AVAILABLE:
            return "Click requires 'pyautogui' package"
        
        try:
            pyautogui.click(x, y)
            
            self.logger.info(f"Clicked at ({x}, {y})")
            return f"Clicked at position ({x}, {y})"
            
        except Exception as e:
            self.logger.error(f"Click error: {e}")
            return f"Failed to click: {e}"
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> str:
        """Move mouse to position."""
        if not AUTOMATION_AVAILABLE:
            return "Mouse control requires 'pyautogui' package"
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            
            self.logger.info(f"Moved mouse to ({x}, {y})")
            return f"Moved mouse to ({x}, {y})"
            
        except Exception as e:
            self.logger.error(f"Mouse movement error: {e}")
            return f"Failed to move mouse: {e}"
    
    def get_mouse_position(self) -> tuple:
        """Get current mouse position."""
        if not AUTOMATION_AVAILABLE:
            return (0, 0)
        
        return pyautogui.position()
    
    def scroll(self, amount: int) -> str:
        """Scroll up (positive) or down (negative)."""
        if not AUTOMATION_AVAILABLE:
            return "Scroll requires 'pyautogui' package"
        
        try:
            pyautogui.scroll(amount)
            
            direction = "up" if amount > 0 else "down"
            self.logger.info(f"Scrolled {direction}")
            return f"Scrolled {direction}"
            
        except Exception as e:
            self.logger.error(f"Scroll error: {e}")
            return f"Failed to scroll: {e}"
    
    def write_document(self, app_name: str, content: str, save_as: Optional[str] = None) -> str:
        """Write document in specified application."""
        if not AUTOMATION_AVAILABLE:
            return "Document writing requires 'pyautogui' and 'keyboard' packages"
        
        try:
            # Open app and type
            result = self.open_and_type(app_name, content)
            
            # Save if path provided
            if save_as:
                time.sleep(1)
                keyboard.press_and_release('ctrl+s')
                time.sleep(1)
                pyautogui.write(save_as, interval=0.05)
                pyautogui.press('enter')
                
                return f"{result} and saved as {save_as}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Document writing error: {e}")
            return f"Failed to write document: {e}"
    
    def ask_user_for_app(self) -> str:
        """Interactive: Ask user which app to use."""
        print("\nAvailable applications:")
        for i, (name, info) in enumerate(self.supported_apps.items(), 1):
            status = "✓" if self.is_app_running(name) else " "
            print(f"[{status}] {i}. {info[1]} ({name})")
        
        print("\nWhich application? (name or number): ", end="")
        choice = input().strip().lower()
        
        # Try by number
        try:
            idx = int(choice) - 1
            apps = list(self.supported_apps.keys())
            if 0 <= idx < len(apps):
                return apps[idx]
        except:
            pass
        
        # Try by name
        if choice in self.supported_apps:
            return choice
        
        # Search partial match
        for app_name in self.supported_apps:
            if choice in app_name:
                return app_name
        
        return "notepad"  # Default
