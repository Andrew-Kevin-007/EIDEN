"""Application discovery and learning system for Windows."""
import os
import json
import winreg
from pathlib import Path
from typing import List, Dict, Optional, Any
import platform


class AppDiscovery:
    """Discovers and caches installed applications on Windows."""
    
    def __init__(self, cache_file: str = "data/app_cache.json"):
        """Initialize app discovery system."""
        self.cache_file = cache_file
        self.app_cache = self._load_cache()
        
        # Common system utilities
        self.system_apps = {
            "file explorer": "explorer.exe",
            "explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "wordpad": "write.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "registry editor": "regedit.exe",
            "device manager": "devmgmt.msc",
            "disk management": "diskmgmt.msc",
            "services": "services.msc",
            "event viewer": "eventvwr.msc",
            "system information": "msinfo32.exe",
            "resource monitor": "resmon.exe",
            "snipping tool": "snippingtool.exe",
            "sticky notes": "ms-stickynotes:",
            "camera": "microsoft.windows.camera:",
            "mail": "outlookmailapp:",
            "calendar": "outlookcal:",
            "store": "ms-windows-store:",
            "photos": "ms-photos:",
            "maps": "bingmaps:",
            "weather": "bingweather:",
            "news": "bingnews:",
            "music": "mswindowsmusic:",
            "movies": "mswindowsvideo:",
        }
        
        # Auto-discover on first run
        if not self.app_cache or len(self.app_cache) < 10:
            self.discover_applications()
    
    def _load_cache(self) -> Dict[str, str]:
        """Load cached application paths."""
        try:
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading app cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save application paths to cache."""
        try:
            cache_path = Path(self.cache_file)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'w') as f:
                json.dump(self.app_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving app cache: {e}")
    
    def discover_applications(self) -> Dict[str, str]:
        """
        Discover installed applications on Windows.
        Returns dictionary of app_name -> executable_path.
        """
        if platform.system() != "Windows":
            return self.app_cache
        
        discovered = {}
        
        # Add system apps first
        discovered.update(self.system_apps)
        
        # Search Windows Registry for installed apps
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"),
        ]
        
        for hkey, path in registry_paths:
            try:
                reg_key = winreg.OpenKey(hkey, path)
                i = 0
                while True:
                    try:
                        app_key = winreg.EnumKey(reg_key, i)
                        app_path_key = winreg.OpenKey(reg_key, app_key)
                        exe_path, _ = winreg.QueryValueEx(app_path_key, "")
                        
                        # Extract app name from .exe
                        app_name = app_key.lower().replace(".exe", "")
                        discovered[app_name] = exe_path
                        
                        winreg.CloseKey(app_path_key)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(reg_key)
            except Exception as e:
                pass
        
        # Search common program directories
        program_dirs = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
        ]
        
        for prog_dir in program_dirs:
            if os.path.exists(prog_dir):
                try:
                    for root, dirs, files in os.walk(prog_dir):
                        # Only search 2 levels deep
                        depth = root[len(prog_dir):].count(os.sep)
                        if depth > 2:
                            continue
                        
                        for file in files:
                            if file.lower().endswith('.exe'):
                                app_name = file.lower().replace(".exe", "")
                                full_path = os.path.join(root, file)
                                
                                # Avoid duplicate entries, prefer App Paths
                                if app_name not in discovered:
                                    discovered[app_name] = full_path
                except Exception:
                    pass
        
        # Update cache
        self.app_cache.update(discovered)
        self._save_cache()
        
        return discovered
    
    def find_application(self, app_name: str) -> Optional[str]:
        """
        Find application path by name (fuzzy matching).
        
        Args:
            app_name: Name of the application to find
            
        Returns:
            Path to application executable or None
        """
        app_name = app_name.lower().strip()
        
        # Exact match
        if app_name in self.app_cache:
            return self.app_cache[app_name]
        
        # Partial match
        for name, path in self.app_cache.items():
            if app_name in name or name in app_name:
                return path
        
        # Try common variations
        variations = [
            app_name,
            app_name.replace(" ", ""),
            app_name.replace(" ", "_"),
            app_name + ".exe",
        ]
        
        for var in variations:
            if var in self.app_cache:
                return self.app_cache[var]
        
        return None
    
    def get_all_apps(self) -> List[str]:
        """Get list of all discovered application names."""
        return sorted(self.app_cache.keys())
    
    def refresh_cache(self) -> int:
        """Refresh application cache. Returns number of apps discovered."""
        self.app_cache = {}
        self.discover_applications()
        return len(self.app_cache)
    
    def open_file_explorer(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Open File Explorer at specific path or home directory.
        
        Args:
            path: Directory path to open (optional)
            
        Returns:
            Result dictionary
        """
        import subprocess
        
        try:
            if path and os.path.exists(path):
                subprocess.Popen(f'explorer "{path}"')
                return {
                    "success": True,
                    "message": f"Opened File Explorer at {path}"
                }
            else:
                subprocess.Popen('explorer')
                return {
                    "success": True,
                    "message": "Opened File Explorer"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open File Explorer: {str(e)}"
            }
    
    def open_system_location(self, location: str) -> Dict[str, Any]:
        """
        Open common system locations.
        
        Args:
            location: downloads, documents, pictures, desktop, music, videos
            
        Returns:
            Result dictionary
        """
        import subprocess
        
        location = location.lower()
        
        # Map locations to shell folders
        shell_folders = {
            "downloads": "Downloads",
            "documents": "Documents",
            "pictures": "Pictures",
            "desktop": "Desktop",
            "music": "Music",
            "videos": "Videos",
            "my documents": "Documents",
            "my pictures": "Pictures",
            "my music": "Music",
            "my videos": "Videos",
        }
        
        folder = shell_folders.get(location)
        if not folder:
            return {
                "success": False,
                "message": f"Unknown location: {location}"
            }
        
        try:
            user_folder = os.path.expanduser(f"~/{folder}")
            if os.path.exists(user_folder):
                subprocess.Popen(f'explorer "{user_folder}"')
                return {
                    "success": True,
                    "message": f"Opened {folder} folder"
                }
            else:
                return {
                    "success": False,
                    "message": f"{folder} folder not found"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open {folder}: {str(e)}"
            }
