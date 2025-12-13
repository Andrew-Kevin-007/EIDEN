class TextToSpeech:
    def __init__(self, voice_id=None, rate=150, volume=1.0):
        import pyttsx3
        self.engine = pyttsx3.init()
        self.set_voice(voice_id)
        self.set_rate(rate)
        self.set_volume(volume)

    def set_voice(self, voice_id):
        if voice_id:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if voice.id == voice_id:
                    self.engine.setProperty('voice', voice.id)
                    break

    def set_rate(self, rate):
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume):
        self.engine.setProperty('volume', volume)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def speak_confirmation(self, command):
        confirmation_text = f"You said: {command}"
        self.speak(confirmation_text)