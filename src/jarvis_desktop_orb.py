"""
JARVIS Desktop GUI with OpenGL Voice-Reactive Orb
Professional Siri-like interface using ModernGL
"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
import numpy as np
import time
from PIL import Image, ImageTk
import io

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import moderngl
    import moderngl_window as mglw
    MODERNGL_AVAILABLE = True
except ImportError:
    MODERNGL_AVAILABLE = False
    print("ModernGL not available. Install: pip install moderngl moderngl-window")

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("sounddevice not available. Install: pip install sounddevice")

from assistant.core import Assistant
from utils.config_manager import get_config


class OrbRenderer:
    """OpenGL-based orb renderer with voice reactivity"""
    
    # Vertex shader
    VERTEX_SHADER = """
    #version 330
    in vec2 in_position;
    out vec2 fragCoord;
    
    void main() {
        gl_Position = vec4(in_position, 0.0, 1.0);
        fragCoord = in_position;
    }
    """
    
    # Fragment shader - Siri-like animated orb
    FRAGMENT_SHADER = """
    #version 330
    uniform float iTime;
    uniform vec2 iResolution;
    uniform float voiceLevel;
    uniform float hue;
    
    out vec4 fragColor;
    in vec2 fragCoord;
    
    // Simplex noise function
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }
    
    float snoise(vec2 v) {
        const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
        vec2 i  = floor(v + dot(v, C.yy));
        vec2 x0 = v -   i + dot(i, C.xx);
        vec2 i1;
        i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz;
        x12.xy -= i1;
        i = mod289(i);
        vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
        vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
        m = m*m;
        m = m*m;
        vec3 x = 2.0 * fract(p * C.www) - 1.0;
        vec3 h = abs(x) - 0.5;
        vec3 ox = floor(x + 0.5);
        vec3 a0 = x - ox;
        m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
        vec3 g;
        g.x  = a0.x  * x0.x  + h.x  * x0.y;
        g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
    }
    
    // HSV to RGB conversion
    vec3 hsv2rgb(vec3 c) {
        vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
        vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
        return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }
    
    void main() {
        // Normalize coordinates
        vec2 uv = fragCoord;
        vec2 center = vec2(0.0, 0.0);
        
        // Distance from center
        float dist = length(uv - center);
        
        // Voice reactive parameters
        float intensity = 0.3 + voiceLevel * 0.7;
        float rotationSpeed = 0.3 + voiceLevel * 1.2;
        float pulseSpeed = 1.5 + voiceLevel * 2.0;
        
        // Animated rotation
        float angle = iTime * rotationSpeed;
        mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
        vec2 rotUV = rot * uv;
        
        // Multiple layers of noise for depth
        float noise1 = snoise(rotUV * 3.0 + iTime * 0.5);
        float noise2 = snoise(rotUV * 5.0 - iTime * 0.3);
        float noise3 = snoise(rotUV * 8.0 + iTime * 0.7);
        
        // Combine noise layers
        float combinedNoise = noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2;
        
        // Pulsing effect
        float pulse = sin(iTime * pulseSpeed) * 0.5 + 0.5;
        float orbRadius = 0.6 + pulse * 0.1 * intensity;
        
        // Orb shape with soft edges
        float orbDist = dist - orbRadius;
        float orb = smoothstep(0.1, -0.1, orbDist);
        
        // Add noise displacement to edges
        orb *= smoothstep(0.2, -0.2, orbDist + combinedNoise * 0.15 * intensity);
        
        // Color gradient based on angle and distance
        float colorAngle = atan(uv.y, uv.x);
        float colorDist = length(uv);
        
        // Dynamic hue shift
        float dynamicHue = hue + colorAngle * 0.1 + iTime * 0.05;
        float saturation = 0.7 + combinedNoise * 0.3;
        float brightness = 0.5 + intensity * 0.5;
        
        // Create gradient from center to edge
        brightness *= 1.0 - colorDist * 0.5;
        
        // Convert to RGB
        vec3 color = hsv2rgb(vec3(dynamicHue, saturation, brightness));
        
        // Add glow effect
        float glow = exp(-dist * 2.0) * intensity * 0.8;
        color += vec3(glow) * hsv2rgb(vec3(hue, 0.8, 1.0));
        
        // Add highlights
        float highlight = pow(1.0 - dist, 3.0) * intensity * 0.5;
        color += vec3(highlight);
        
        // Final alpha
        float alpha = orb + glow * 0.3;
        
        fragColor = vec4(color, alpha);
    }
    """
    
    def __init__(self, width=800, height=800):
        self.width = width
        self.height = height
        self.voice_level = 0.0
        self.hue = 0.55  # Blue-purple base
        self.time_value = 0.0
        
        if not MODERNGL_AVAILABLE:
            return
            
        # Create standalone context
        self.ctx = moderngl.create_standalone_context()
        
        # Create shader program
        self.prog = self.ctx.program(
            vertex_shader=self.VERTEX_SHADER,
            fragment_shader=self.FRAGMENT_SHADER
        )
        
        # Full screen quad
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')
        
        # Create framebuffer for off-screen rendering
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((width, height), 4)]
        )
        
    def render(self):
        """Render the orb and return PIL Image"""
        if not MODERNGL_AVAILABLE:
            return None
            
        self.time_value += 0.016  # ~60 FPS
        
        # Update uniforms
        self.prog['iTime'].value = self.time_value
        self.prog['iResolution'].value = (self.width, self.height)
        self.prog['voiceLevel'].value = self.voice_level
        self.prog['hue'].value = self.hue
        
        # Render to framebuffer
        self.fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        
        # Read pixels
        data = self.fbo.read(components=4)
        img = Image.frombytes('RGBA', (self.width, self.height), data)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        return img
    
    def set_voice_level(self, level):
        """Update voice level (0.0 to 1.0)"""
        self.voice_level = max(0.0, min(1.0, level))
    
    def set_hue(self, hue):
        """Set base hue (0.0 to 1.0)"""
        self.hue = hue


class VoiceAnalyzer:
    """Real-time voice level analyzer"""
    
    def __init__(self):
        self.voice_level = 0.0
        self.running = False
        self.thread = None
        
    def start(self):
        """Start voice analysis"""
        if not AUDIO_AVAILABLE:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._analyze_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop voice analysis"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _analyze_loop(self):
        """Continuous voice analysis loop"""
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
    
    def get_level(self):
        """Get current voice level"""
        return self.voice_level


class JarvisDesktopGUI:
    """Main desktop GUI with OpenGL orb"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS - AI Voice Assistant")
        self.root.geometry("900x1000")
        self.root.configure(bg='#000000')
        
        # Make window stay on top and frameless for modern look
        self.root.attributes('-topmost', False)
        
        # Initialize components
        self.assistant = None
        self.orb_renderer = None
        self.voice_analyzer = VoiceAnalyzer()
        self.is_listening = False
        self.orb_label = None
        self.animation_running = False
        
        # Setup UI
        self.setup_ui()
        
        # Initialize assistant in background
        threading.Thread(target=self.init_assistant, daemon=True).start()
        
        # Start orb animation
        if MODERNGL_AVAILABLE:
            self.orb_renderer = OrbRenderer(width=600, height=600)
            self.start_orb_animation()
        
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
        
        # Orb container
        orb_container = tk.Frame(main_frame, bg='#000000')
        orb_container.pack(pady=20)
        
        if MODERNGL_AVAILABLE:
            self.orb_label = tk.Label(orb_container, bg='#000000', bd=0)
            self.orb_label.pack()
        else:
            # Fallback: Simple animated circle
            no_gl_label = tk.Label(
                orb_container,
                text="⚫",
                font=('Segoe UI', 200),
                fg='#6B46C1',
                bg='#000000'
            )
            no_gl_label.pack()
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Initializing...",
            font=('Segoe UI', 14),
            fg='#A0AEC0',
            bg='#000000',
            wraplength=700
        )
        self.status_label.pack(pady=10)
        
        # Recognized text display
        text_frame = tk.Frame(main_frame, bg='#1A202C', bd=2, relief=tk.FLAT)
        text_frame.pack(pady=10, fill=tk.X)
        
        self.text_display = tk.Text(
            text_frame,
            height=4,
            font=('Segoe UI', 12),
            bg='#1A202C',
            fg='#E2E8F0',
            bd=0,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)
        self.text_display.insert('1.0', 'Your commands will appear here...')
        self.text_display.config(state=tk.DISABLED)
        
        # Response display
        response_frame = tk.Frame(main_frame, bg='#2D3748', bd=2, relief=tk.FLAT)
        response_frame.pack(pady=10, fill=tk.X)
        
        self.response_display = tk.Text(
            response_frame,
            height=4,
            font=('Segoe UI', 12),
            bg='#2D3748',
            fg='#E2E8F0',
            bd=0,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.response_display.pack(fill=tk.BOTH, expand=True)
        self.response_display.insert('1.0', 'JARVIS responses will appear here...')
        self.response_display.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#000000')
        button_frame.pack(pady=20)
        
        # Start/Stop button
        self.listen_button = tk.Button(
            button_frame,
            text="▶ Start Listening",
            font=('Segoe UI', 14, 'bold'),
            bg='#6B46C1',
            fg='#FFFFFF',
            activebackground='#553C9A',
            activeforeground='#FFFFFF',
            bd=0,
            padx=30,
            pady=15,
            cursor='hand2',
            command=self.toggle_listening
        )
        self.listen_button.pack(side=tk.LEFT, padx=10)
        
        # Quick command buttons
        quick_frame = tk.Frame(main_frame, bg='#000000')
        quick_frame.pack(pady=10)
        
        commands = [
            "What time is it?",
            "Tell me a joke",
            "What's the weather?",
        ]
        
        for cmd in commands:
            btn = tk.Button(
                quick_frame,
                text=cmd,
                font=('Segoe UI', 10),
                bg='#2D3748',
                fg='#E2E8F0',
                activebackground='#4A5568',
                activeforeground='#FFFFFF',
                bd=0,
                padx=15,
                pady=8,
                cursor='hand2',
                command=lambda c=cmd: self.execute_command(c)
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def init_assistant(self):
        """Initialize the assistant"""
        try:
            self.update_status("Loading JARVIS assistant...")
            config = get_config()
            self.assistant = Assistant(config=config, verbose=True)
            self.update_status("✅ JARVIS ready! Click 'Start Listening' to begin.")
        except Exception as e:
            self.update_status(f"❌ Error initializing assistant: {e}")
    
    def start_orb_animation(self):
        """Start the orb animation loop"""
        if not self.orb_renderer or self.animation_running:
            return
            
        self.animation_running = True
        self.animate_orb()
    
    def animate_orb(self):
        """Animate the orb"""
        if not self.animation_running or not self.orb_renderer:
            return
        
        try:
            # Update orb with voice level
            if self.is_listening:
                voice_level = self.voice_analyzer.get_level()
                self.orb_renderer.set_voice_level(voice_level)
                # Change hue based on activity
                self.orb_renderer.set_hue(0.55 + voice_level * 0.2)
            else:
                self.orb_renderer.set_voice_level(0.0)
                self.orb_renderer.set_hue(0.55)
            
            # Render frame
            img = self.orb_renderer.render()
            if img and self.orb_label:
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                self.orb_label.config(image=photo)
                self.orb_label.image = photo  # Keep reference
            
            # Schedule next frame (~60 FPS)
            self.root.after(16, self.animate_orb)
        except Exception as e:
            print(f"Animation error: {e}")
            self.root.after(16, self.animate_orb)
    
    def toggle_listening(self):
        """Toggle listening state"""
        if not self.assistant:
            self.update_status("❌ Assistant not ready yet...")
            return
        
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.listen_button.config(
                text="⏸ Stop Listening",
                bg='#E53E3E',
                activebackground='#C53030'
            )
            self.update_status("🎤 Listening... Speak your command!")
            self.voice_analyzer.start()
            # Start listening in background
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.listen_button.config(
                text="▶ Start Listening",
                bg='#6B46C1',
                activebackground='#553C9A'
            )
            self.update_status("✅ Stopped listening.")
            self.voice_analyzer.stop()
    
    def listen_loop(self):
        """Continuous listening loop"""
        while self.is_listening and self.assistant:
            try:
                self.update_status("🎤 Listening...")
                command = self.assistant.listen()
                
                if command and self.is_listening:
                    self.update_text_display(f"You: {command}")
                    self.execute_command(command)
                    
            except Exception as e:
                print(f"Listen error: {e}")
                time.sleep(0.5)
    
    def execute_command(self, command):
        """Execute a voice command"""
        if not self.assistant:
            return
        
        self.update_status(f"⚙️ Processing: {command}")
        self.update_text_display(f"You: {command}")
        
        def process():
            try:
                # Get response without speaking
                response = self.assistant._get_response_for_command(command)
                self.update_response_display(f"JARVIS: {response}")
                
                # Speak the response
                self.assistant.speak(response)
                self.update_status("✅ Ready for next command")
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.update_response_display(f"JARVIS: {error_msg}")
                self.update_status("❌ Error processing command")
        
        threading.Thread(target=process, daemon=True).start()
    
    def update_status(self, text):
        """Update status label"""
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
        """Start the GUI"""
        self.root.mainloop()
    
    def cleanup(self):
        """Cleanup resources"""
        self.animation_running = False
        self.voice_analyzer.stop()


def main():
    """Main entry point"""
    print("=" * 50)
    print("   JARVIS Desktop - OpenGL Voice-Reactive Orb")
    print("=" * 50)
    print()
    
    if not MODERNGL_AVAILABLE:
        print("⚠️  ModernGL not available - orb will use fallback rendering")
        print("   Install with: pip install moderngl moderngl-window")
        print()
    
    if not AUDIO_AVAILABLE:
        print("⚠️  sounddevice not available - voice reactivity disabled")
        print("   Install with: pip install sounddevice")
        print()
    
    try:
        app = JarvisDesktopGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if 'app' in locals():
            app.cleanup()


if __name__ == "__main__":
    main()
