"""Voice authentication system for secure access."""
import os
import pickle
import numpy as np
from typing import Optional
import sounddevice as sd
import speech_recognition as sr
from io import BytesIO
import wave


class VoiceAuthenticator:
    """Voice-based authentication system."""
    
    def __init__(self, auth_file: str = "data/voice_auth.pkl"):
        """
        Initialize voice authenticator.
        
        Args:
            auth_file: Path to store voice authentication data
        """
        self.auth_file = auth_file
        self.is_authenticated = False
        self.sample_rate = 16000
        self.channels = 1
        self.recognizer = sr.Recognizer()
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(auth_file) if os.path.dirname(auth_file) else "data", exist_ok=True)
        
        # Load existing authentication data
        self.auth_data = self._load_auth_data()
    
    def _load_auth_data(self) -> dict:
        """Load saved authentication data."""
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading auth data: {e}")
                return {}
        return {}
    
    def _save_auth_data(self):
        """Save authentication data."""
        try:
            with open(self.auth_file, 'wb') as f:
                pickle.dump(self.auth_data, f)
        except Exception as e:
            print(f"Error saving auth data: {e}")
    
    def _record_voice_sample(self, duration: int = 3) -> Optional[bytes]:
        """
        Record a voice sample for authentication.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as bytes
        """
        try:
            print(f"Recording for {duration} seconds...")
            recording = sd.rec(int(duration * self.sample_rate),
                             samplerate=self.sample_rate,
                             channels=self.channels,
                             dtype='int16')
            sd.wait()
            
            # Convert to WAV format
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(recording.tobytes())
            
            wav_buffer.seek(0)
            return wav_buffer.read()
            
        except Exception as e:
            print(f"Recording error: {e}")
            return None
    
    def _extract_voice_features(self, audio_data: bytes) -> Optional[np.ndarray]:
        """
        Extract voice features for comparison (simplified version).
        In production, use proper voice biometrics like speaker recognition models.
        
        Args:
            audio_data: Audio data
            
        Returns:
            Feature vector
        """
        try:
            # Convert audio to numpy array
            audio_buffer = BytesIO(audio_data)
            with wave.open(audio_buffer, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                audio_array = np.frombuffer(frames, dtype=np.int16)
            
            # Simple features: mean, std, energy
            features = np.array([
                np.mean(audio_array),
                np.std(audio_array),
                np.sum(audio_array ** 2) / len(audio_array),  # Energy
                np.max(audio_array),
                np.min(audio_array)
            ])
            
            return features
            
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None
    
    def enroll_user(self, passphrase: str = "My voice is my password") -> bool:
        """
        Enroll a new user with voice authentication.
        
        Args:
            passphrase: Phrase to speak during enrollment
            
        Returns:
            True if enrollment successful
        """
        print("\n=== Voice Authentication Enrollment ===")
        print(f"Please say: '{passphrase}'")
        print("You will need to say it 3 times for verification.\n")
        print("TIP: Speak clearly in a quiet environment for best results.\n")
        
        samples = []
        attempts = 0
        max_attempts = 5  # Allow some retries
        
        for i in range(3):
            success = False
            while not success and attempts < max_attempts:
                try:
                    input(f"Press Enter to record sample {i+1}/3...")
                    audio_data = self._record_voice_sample(duration=4)
                    
                    if not audio_data:
                        print("✗ Failed to record audio. Please try again.")
                        attempts += 1
                        continue
                    
                    # Verify they said something (optional passphrase check)
                    try:
                        with sr.AudioFile(BytesIO(audio_data)) as source:
                            audio = self.recognizer.record(source)
                            text = self.recognizer.recognize_google(audio).lower()  # type: ignore
                            
                            print(f"Recognized: '{text}'")
                            
                            # More lenient - just check if they said something substantial
                            if len(text.split()) >= 3:
                                features = self._extract_voice_features(audio_data)
                                if features is not None:
                                    samples.append(features)
                                    print(f"✓ Sample {i+1} recorded successfully\n")
                                    success = True
                                else:
                                    print("✗ Could not process voice sample. Please try again.")
                                    attempts += 1
                            else:
                                print(f"✗ Please speak the full passphrase clearly.")
                                attempts += 1
                                
                    except sr.UnknownValueError:
                        print(f"✗ Could not understand speech. Please speak more clearly.")
                        attempts += 1
                    except sr.RequestError as e:
                        print(f"✗ Speech recognition error: {e}")
                        print("Note: Internet connection required for enrollment.")
                        attempts += 1
                    except Exception as e:
                        print(f"✗ Error processing sample: {e}")
                        attempts += 1
                        
                except KeyboardInterrupt:
                    print("\n✗ Enrollment cancelled by user")
                    return False
                except Exception as e:
                    print(f"✗ Unexpected error: {e}")
                    attempts += 1
            
            if not success:
                print("\n✗ Enrollment failed after multiple attempts")
                return False
        
        if len(samples) == 3:
            # Store average features
            self.auth_data['voice_profile'] = np.mean(samples, axis=0)
            self.auth_data['passphrase'] = passphrase.lower()
            self._save_auth_data()
            print("\n✓ Voice authentication enrolled successfully!")
            return True
        else:
            print("\n✗ Enrollment failed")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate user via voice.
        
        Returns:
            True if authenticated
        """
        if not self.auth_data or 'voice_profile' not in self.auth_data:
            print("⚠ No voice profile found. Please enroll first.")
            return False
        
        print("\n=== Voice Authentication Required ===")
        print(f"Please say: '{self.auth_data.get('passphrase', 'My voice is my password')}'")
        print("(Or say any phrase with at least 3 words)")
        input("Press Enter to begin authentication...")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            audio_data = self._record_voice_sample(duration=4)
            
            if audio_data:
                try:
                    # Verify something was said
                    with sr.AudioFile(BytesIO(audio_data)) as source:
                        audio = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio).lower()  # type: ignore
                        
                        print(f"Recognized: '{text}'")
                        
                        # Just check if they said something substantial
                        if len(text.split()) < 3:
                            print(f"✗ Please speak more clearly (Attempt {attempt + 1}/{max_attempts})")
                            if attempt < max_attempts - 1:
                                continue
                            else:
                                return False
                    
                    # Verify voice features (simplified comparison)
                    features = self._extract_voice_features(audio_data)
                    if features is not None:
                        stored_profile = self.auth_data['voice_profile']
                        
                        # Calculate similarity (lower distance = more similar)
                        distance = np.linalg.norm(features - stored_profile)
                        threshold = np.linalg.norm(stored_profile) * 0.5  # 50% tolerance
                        
                        if distance < threshold:
                            print("✓ Voice authentication successful!")
                            self.is_authenticated = True
                            return True
                        else:
                            print(f"✗ Voice not recognized (Attempt {attempt + 1}/{max_attempts})")
                            if attempt < max_attempts - 1:
                                print("Please try again...")
                            else:
                                print("✗ Authentication failed after multiple attempts")
                                return False
                    else:
                        print(f"✗ Could not process voice sample (Attempt {attempt + 1}/{max_attempts})")
                        if attempt < max_attempts - 1:
                            continue
                                
                except sr.UnknownValueError:
                    print(f"✗ Could not understand speech (Attempt {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        print("Please speak more clearly...")
                        continue
                except sr.RequestError as e:
                    print(f"✗ Speech recognition error: {e}")
                    return False
                except Exception as e:
                    print(f"✗ Authentication error: {e}")
                    if attempt < max_attempts - 1:
                        continue
            else:
                print(f"✗ Failed to record audio (Attempt {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    continue
        
        return False
    
    def is_enrolled(self) -> bool:
        """Check if a voice profile exists."""
        return 'voice_profile' in self.auth_data
    
    def reset_authentication(self):
        """Reset authentication status."""
        self.is_authenticated = False
