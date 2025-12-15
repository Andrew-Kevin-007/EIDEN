"""
JARVIS Desktop GUI - Simple High-Performance Orb
Professional Siri-like interface without OpenGL dependency
Uses optimized Tkinter Canvas with advanced animations
"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
import time
import math
import colorsys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Check for optional dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  numpy not available. Installing: pip install numpy")

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = NUMPY_AVAILABLE  # sounddevice needs numpy
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  sounddevice not available. Voice reactivity will be simulated.")

try:
    from assistant.core import Assistant
    from utils.config_manager import get_config
    ASSISTANT_AVAILABLE = True
except ImportError as e:
    ASSISTANT_AVAILABLE = False
    print(f"⚠️  Assistant import failed: {e}")


class VoiceAnalyzer:
    """Real-time voice level analyzer"""
    
    def __init__(self):
        self.voice_level = 0.0
        self.running = False
        self.thread = None
        
    def start(self):
        """Start voice analysis"""
        if not AUDIO_AVAILABLE:
            # Simulate voice activity
            self.running = True
            self.thread = threading.Thread(target=self._simulate_loop, daemon=True)
            self.thread.start()
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._analyze_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop voice analysis"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _simulate_loop(self):
        """Simulate voice activity when sounddevice is not available"""
        import random
        while self.running:
            # Random fluctuation
            self.voice_level = random.random() * 0.3
            time.sleep(0.05)
    
    def _analyze_loop(self):
        """Continuous voice analysis loop"""
        if not NUMPY_AVAILABLE:
            self._simulate_loop()
            return
            
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            
            # Calculate RMS (Root Mean Square) for volume level
            rms = np.sqrt(np.mean(indata**2))
            # Normalize to 0-1 range with sensitivity adjustment
            self.voice_level = min(1.0, rms * 50.0)
        
        try:
            with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=1024):
                while self.running:
                    time.sleep(0.01)
        except Exception as e:
            print(f"Audio error: {e}")
            # Fall back to simulation
            self._simulate_loop()
    
    def get_level(self):
        """Get current voice level"""
        return self.voice_level


class AdvancedOrbCanvas:
    """High-performance Canvas-based orb with voice reactivity"""
    
    def __init__(self, parent, size=600):
        self.size = size
        self.center = size // 2
        self.canvas = tk.Canvas(
            parent,
            width=size,
            height=size,
            bg='#000000',
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack()
        
        # Animation state
        self.voice_level = 0.0
        self.time = 0.0
        self.particles = []
        self.layers = []
        
        # Create orb layers
        self.create_orb_layers()
        
        # Create particles
        self.create_particles(50)
        
        # Start animation
        self.animating = False
        
    def create_orb_layers(self):
        """Create multiple layers for depth effect"""
        # Create 40 layers from center to edge
        for i in range(40):
            ratio = (i + 1) / 40.0
            radius = int(self.center * 0.8 * ratio)
            
            # Color gradient - blue to purple
            hue = 0.6 + ratio * 0.1  # 0.6 (blue) to 0.7 (purple)
            saturation = 0.8
            lightness = 0.5 + (1.0 - ratio) * 0.3
            
            rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
            color = '#%02x%02x%02x' % (
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            
            # Create circle
            oval = self.canvas.create_oval(
                self.center - radius,
                self.center - radius,
                self.center + radius,
                self.center + radius,
                fill=color,
                outline=''
            )
            
            self.layers.append({
                'id': oval,
                'base_radius': radius,
                'angle_offset': i * 9,  # Different rotation speed per layer
                'hue': hue
            })
    
    def create_particles(self, count):
        """Create floating particles around the orb"""
        for i in range(count):
            angle = (i / count) * 2 * math.pi
            distance = self.center * 0.9
            
            x = self.center + math.cos(angle) * distance
            y = self.center + math.sin(angle) * distance
            
            size = 2 + (i % 3)
            
            particle = self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill='#FFFFFF',
                outline='',
                stipple='gray50'
            )
            
            self.particles.append({
                'id': particle,
                'angle': angle,
                'base_distance': distance,
                'size': size,
                'speed': 0.5 + (i % 5) * 0.1
            })
    
    def update(self, voice_level=0.0):
        """Update animation frame"""
        self.voice_level = voice_level
        self.time += 0.016  # 60 FPS
        
        # Update layers
        for i, layer in enumerate(self.layers):
            # Voice-reactive pulsing
            pulse = math.sin(self.time * 2.0 + i * 0.1) * 0.5 + 0.5
            voice_scale = 1.0 + voice_level * 0.2
            
            # Calculate new radius
            new_radius = int(layer['base_radius'] * (1.0 + pulse * 0.1) * voice_scale)
            
            # Rotation effect (subtle)
            angle = self.time * 0.3 + layer['angle_offset']
            offset_x = math.sin(angle) * voice_level * 10
            offset_y = math.cos(angle) * voice_level * 10
            
            # Update position
            self.canvas.coords(
                layer['id'],
                self.center - new_radius + offset_x,
                self.center - new_radius + offset_y,
                self.center + new_radius + offset_x,
                self.center + new_radius + offset_y
            )
            
            # Dynamic color based on voice
            hue = layer['hue'] + voice_level * 0.1
            saturation = 0.7 + voice_level * 0.3
            lightness = 0.5 + (1.0 - i / len(self.layers)) * 0.3
            
            rgb = colorsys.hls_to_rgb(hue % 1.0, lightness, saturation)
            color = '#%02x%02x%02x' % (
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            self.canvas.itemconfig(layer['id'], fill=color)
        
        # Update particles
        for particle in self.particles:
            angle = particle['angle'] + self.time * particle['speed']
            distance = particle['base_distance'] * (1.0 + voice_level * 0.3)
            
            x = self.center + math.cos(angle) * distance
            y = self.center + math.sin(angle) * distance
            
            size = particle['size'] * (1.0 + voice_level * 0.5)
            
            self.canvas.coords(
                particle['id'],
                x - size, y - size,
                x + size, y + size
            )
            
            # Fade based on voice
            opacity = int(128 + voice_level * 127)
            if opacity > 200:
                self.canvas.itemconfig(particle['id'], state='normal')
            else:
                self.canvas.itemconfig(particle['id'], state='hidden')
    
    def start_animation(self):
        """Start the animation loop"""
        self.animating = True
        self._animate()
    
    def stop_animation(self):
        """Stop the animation loop"""
        self.animating = False
    
    def _animate(self):
        """Animation loop"""
        if not self.animating:
            return
        
        self.update(self.voice_level)
        self.canvas.after(16, self._animate)  # ~60 FPS
    
    def set_voice_level(self, level):
        """Update voice level"""
        self.voice_level = level


class JarvisDesktopSimple:
    """Simplified desktop GUI with high-performance Canvas orb"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS - AI Voice Assistant")
        self.root.geometry("800x1100")
        self.root.configure(bg='#000000')
        
        # Initialize components
        self.assistant = None
        self.orb_canvas = None
        self.voice_analyzer = VoiceAnalyzer()
        self.is_listening = False
        
        # Setup UI
        self.setup_ui()
        
        # Initialize assistant in background
        threading.Thread(target=self.init_assistant, daemon=True).start()
        
        # Start orb animation
        self.orb_canvas.start_animation()
        self.update_voice_level()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="JARVIS",
            font=('Segoe UI', 48, 'bold'),
            fg='#FFFFFF',
            bg='#000000'
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(
            main_frame,
            text="AI-Powered Voice Assistant",
            font=('Segoe UI', 16),
            fg='#B794F4',
            bg='#000000'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Orb
        orb_frame = tk.Frame(main_frame, bg='#000000')
        orb_frame.pack(pady=10)
        
        self.orb_canvas = AdvancedOrbCanvas(orb_frame, size=600)
        
        # Status
        self.status_label = tk.Label(
            main_frame,
            text="Initializing...",
            font=('Segoe UI', 14),
            fg='#A0AEC0',
            bg='#000000',
            wraplength=700
        )
        self.status_label.pack(pady=10)
        
        # Text displays
        displays_frame = tk.Frame(main_frame, bg='#000000')
        displays_frame.pack(pady=10, fill=tk.X)
        
        # Command display
        cmd_frame = tk.Frame(displays_frame, bg='#1A202C', bd=2, relief=tk.FLAT)
        cmd_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            cmd_frame,
            text="Your Command:",
            font=('Segoe UI', 10, 'bold'),
            fg='#A0AEC0',
            bg='#1A202C'
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        self.text_display = tk.Text(
            cmd_frame,
            height=3,
            font=('Segoe UI', 11),
            bg='#1A202C',
            fg='#E2E8F0',
            bd=0,
            wrap=tk.WORD,
            padx=10,
            pady=5
        )
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_display.insert('1.0', 'Waiting for your command...')
        self.text_display.config(state=tk.DISABLED)
        
        # Response display
        resp_frame = tk.Frame(displays_frame, bg='#2D3748', bd=2, relief=tk.FLAT)
        resp_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            resp_frame,
            text="JARVIS Response:",
            font=('Segoe UI', 10, 'bold'),
            fg='#A0AEC0',
            bg='#2D3748'
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        self.response_display = tk.Text(
            resp_frame,
            height=3,
            font=('Segoe UI', 11),
            bg='#2D3748',
            fg='#E2E8F0',
            bd=0,
            wrap=tk.WORD,
            padx=10,
            pady=5
        )
        self.response_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.response_display.insert('1.0', 'JARVIS will respond here...')
        self.response_display.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#000000')
        button_frame.pack(pady=15)
        
        self.listen_button = tk.Button(
            button_frame,
            text="🎤 Start Listening",
            font=('Segoe UI', 14, 'bold'),
            bg='#6B46C1',
            fg='#FFFFFF',
            activebackground='#553C9A',
            activeforeground='#FFFFFF',
            bd=0,
            padx=40,
            pady=15,
            cursor='hand2',
            command=self.toggle_listening
        )
        self.listen_button.pack()
        
        # Quick commands
        quick_frame = tk.Frame(main_frame, bg='#000000')
        quick_frame.pack(pady=10)
        
        tk.Label(
            quick_frame,
            text="Quick Commands:",
            font=('Segoe UI', 10, 'bold'),
            fg='#A0AEC0',
            bg='#000000'
        ).pack(pady=(0, 5))
        
        commands_grid = tk.Frame(quick_frame, bg='#000000')
        commands_grid.pack()
        
        commands = [
            "What time is it?",
            "Tell me a joke",
            "What's the weather?",
            "Search Wikipedia",
            "Take a screenshot",
            "Open calculator"
        ]
        
        for idx, cmd in enumerate(commands):
            btn = tk.Button(
                commands_grid,
                text=cmd,
                font=('Segoe UI', 9),
                bg='#2D3748',
                fg='#E2E8F0',
                activebackground='#4A5568',
                activeforeground='#FFFFFF',
                bd=0,
                padx=12,
                pady=8,
                cursor='hand2',
                command=lambda c=cmd: self.execute_command(c)
            )
            row = idx // 3
            col = idx % 3
            btn.grid(row=row, column=col, padx=3, pady=3)
    
    def init_assistant(self):
        """Initialize assistant"""
        try:
            if not ASSISTANT_AVAILABLE:
                self.update_status("❌ Assistant module not available. Check imports.")
                return
                
            self.update_status("Loading JARVIS assistant...")
            config = get_config()
            self.assistant = Assistant(config=config)
            self.update_status("✅ JARVIS ready! Click 'Start Listening' to begin.")
        except Exception as e:
            error_msg = f"❌ Error initializing assistant: {e}"
            self.update_status(error_msg)
            print(error_msg)
            import traceback
            traceback.print_exc()
    
    def update_voice_level(self):
        """Update orb with voice level"""
        if self.is_listening:
            level = self.voice_analyzer.get_level()
            self.orb_canvas.set_voice_level(level)
        else:
            self.orb_canvas.set_voice_level(0.0)
        
        self.root.after(50, self.update_voice_level)
    
    def toggle_listening(self):
        """Toggle listening"""
        if not self.assistant:
            self.update_status("❌ Assistant not ready...")
            return
        
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.listen_button.config(
                text="⏹ Stop Listening",
                bg='#E53E3E',
                activebackground='#C53030'
            )
            self.update_status("🎤 Listening for your command...")
            self.voice_analyzer.start()
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.listen_button.config(
                text="🎤 Start Listening",
                bg='#6B46C1',
                activebackground='#553C9A'
            )
            self.update_status("✅ Stopped listening")
            self.voice_analyzer.stop()
    
    def listen_loop(self):
        """Listen for commands"""
        while self.is_listening and self.assistant:
            try:
                self.update_status("🎤 Listening...")
                command = self.assistant.listen()
                
                if command and self.is_listening:
                    self.execute_command(command)
                    
            except Exception as e:
                print(f"Listen error: {e}")
                time.sleep(0.5)
    
    def execute_command(self, command):
        """Execute command"""
        if not self.assistant:
            return
        
        self.update_status(f"⚙️ Processing: {command}")
        self.update_text_display(f"{command}")
        
        def process():
            try:
                response = self.assistant._get_response_for_command(command)
                self.update_response_display(f"{response}")
                self.assistant.speak(response)
                self.update_status("✅ Ready for next command")
            except Exception as e:
                self.update_response_display(f"Error: {e}")
                self.update_status("❌ Error processing")
        
        threading.Thread(target=process, daemon=True).start()
    
    def update_status(self, text):
        """Update status"""
        try:
            self.status_label.config(text=text)
        except:
            pass
    
    def update_text_display(self, text):
        """Update text display"""
        try:
            self.text_display.config(state=tk.NORMAL)
            self.text_display.delete('1.0', tk.END)
            self.text_display.insert('1.0', text)
            self.text_display.config(state=tk.DISABLED)
        except:
            pass
    
    def update_response_display(self, text):
        """Update response display"""
        try:
            self.response_display.config(state=tk.NORMAL)
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', text)
            self.response_display.config(state=tk.DISABLED)
        except:
            pass
    
    def run(self):
        """Run the app"""
        self.root.mainloop()
    
    def cleanup(self):
        """Cleanup"""
        self.orb_canvas.stop_animation()
        self.voice_analyzer.stop()


def main():
    """Main entry point"""
    print("=" * 50)
    print("   JARVIS Desktop - Simple High-Performance Orb")
    print("=" * 50)
    print()
    
    app = None
    try:
        app = JarvisDesktopSimple()
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if app:
            try:
                app.cleanup()
            except:
                pass


if __name__ == "__main__":
    main()
