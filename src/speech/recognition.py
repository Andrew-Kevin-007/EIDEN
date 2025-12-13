class SpeechRecognizer:
    def __init__(self, recognizer, microphone):
        self.recognizer = recognizer
        self.microphone = microphone

    def calibrate(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def listen(self):
        with self.microphone as source:
            audio = self.recognizer.listen(source)
        return audio

    def recognize(self, audio):
        try:
            return self.recognizer.recognize_google(audio)
        except Exception as e:
            return str(e)