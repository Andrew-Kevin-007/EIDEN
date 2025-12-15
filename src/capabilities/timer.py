"""Timer and reminder capabilities."""
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import winsound  # For Windows beep


class TimerManager:
    """Manage timers and alarms."""
    
    def __init__(self, speak_callback=None):
        """
        Initialize timer manager.
        
        Args:
            speak_callback: Function to call for voice notifications
        """
        self.speak_callback = speak_callback
        self.timers: List[Dict[str, Any]] = []
        self.timer_id_counter = 0
    
    def _beep(self):
        """Play a beep sound."""
        try:
            # Windows beep
            for _ in range(3):
                winsound.Beep(1000, 500)  # 1000 Hz for 500ms
                time.sleep(0.2)
        except:
            # Fallback - just print
            print("\a" * 3)
    
    def _timer_thread(self, timer_id: int, duration: int, label: str):
        """Thread function for timer countdown."""
        time.sleep(duration)
        
        # Find and remove the timer
        self.timers = [t for t in self.timers if t['id'] != timer_id]
        
        # Alert
        self._beep()
        message = f"Timer finished: {label}" if label else "Timer finished!"
        print(f"\n🔔 {message}")
        
        if self.speak_callback:
            self.speak_callback(message)
    
    def set_timer(self, duration: int, label: Optional[str] = None) -> Dict[str, Any]:
        """
        Set a timer.
        
        Args:
            duration: Duration in seconds
            label: Optional label for the timer
            
        Returns:
            Result dictionary
        """
        try:
            self.timer_id_counter += 1
            timer_id = self.timer_id_counter
            
            timer_data = {
                'id': timer_id,
                'duration': duration,
                'label': label or f"Timer {timer_id}",
                'start_time': datetime.now(),
                'end_time': datetime.now() + timedelta(seconds=duration)
            }
            
            self.timers.append(timer_data)
            
            # Start timer thread
            thread = threading.Thread(
                target=self._timer_thread,
                args=(timer_id, duration, timer_data['label']),
                daemon=True
            )
            thread.start()
            
            minutes = duration // 60
            seconds = duration % 60
            
            time_str = ""
            if minutes > 0:
                time_str += f"{minutes} minute{'s' if minutes != 1 else ''}"
            if seconds > 0:
                if time_str:
                    time_str += f" and {seconds} second{'s' if seconds != 1 else ''}"
                else:
                    time_str += f"{seconds} second{'s' if seconds != 1 else ''}"
            
            return {
                "success": True,
                "message": f"Timer set for {time_str}",
                "timer_id": timer_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to set timer: {str(e)}"
            }
    
    def list_timers(self) -> Dict[str, Any]:
        """List active timers."""
        if not self.timers:
            return {
                "success": True,
                "message": "No active timers"
            }
        
        now = datetime.now()
        timer_list = []
        
        for timer in self.timers:
            remaining = (timer['end_time'] - now).total_seconds()
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                timer_list.append(
                    f"{timer['label']}: {minutes}m {seconds}s remaining"
                )
        
        message = "Active timers:\n" + "\n".join(timer_list)
        
        return {
            "success": True,
            "message": message,
            "timers": self.timers
        }
    
    def cancel_timer(self, timer_id: Optional[int] = None) -> Dict[str, Any]:
        """Cancel a timer."""
        if not self.timers:
            return {
                "success": False,
                "message": "No active timers to cancel"
            }
        
        if timer_id is None:
            # Cancel most recent
            timer = self.timers.pop()
            return {
                "success": True,
                "message": f"Cancelled timer: {timer['label']}"
            }
        else:
            # Cancel specific timer
            self.timers = [t for t in self.timers if t['id'] != timer_id]
            return {
                "success": True,
                "message": f"Cancelled timer {timer_id}"
            }
    
    def parse_duration(self, text: str) -> Optional[int]:
        """
        Parse duration from text.
        
        Args:
            text: Text containing duration (e.g., "5 minutes", "30 seconds")
            
        Returns:
            Duration in seconds or None
        """
        try:
            import re
            
            # Look for patterns like "5 minutes", "30 seconds", "1 hour"
            minutes_match = re.search(r'(\d+)\s*(?:minute|min|m)', text, re.IGNORECASE)
            seconds_match = re.search(r'(\d+)\s*(?:second|sec|s)', text, re.IGNORECASE)
            hours_match = re.search(r'(\d+)\s*(?:hour|hr|h)', text, re.IGNORECASE)
            
            total_seconds = 0
            
            if hours_match:
                total_seconds += int(hours_match.group(1)) * 3600
            if minutes_match:
                total_seconds += int(minutes_match.group(1)) * 60
            if seconds_match:
                total_seconds += int(seconds_match.group(1))
            
            return total_seconds if total_seconds > 0 else None
            
        except Exception as e:
            print(f"Duration parsing error: {e}")
            return None
