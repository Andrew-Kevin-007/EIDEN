import unittest
from src.speech.recognition import SpeechRecognizer
from src.speech.synthesis import TextToSpeech

class TestSpeechFunctions(unittest.TestCase):

    def setUp(self):
        self.recognizer = SpeechRecognizer()
        self.synthesizer = TextToSpeech()

    def test_speech_recognition(self):
        # Assuming we have a method to simulate microphone input for testing
        test_audio_input = "path/to/test/audio.wav"
        recognized_text = self.recognizer.recognize_from_audio(test_audio_input)
        self.assertIsInstance(recognized_text, str)
        self.assertNotEqual(recognized_text, "")

    def test_text_to_speech(self):
        test_text = "Hello, this is a test."
        self.synthesizer.speak(test_text)
        # Assuming we have a way to verify that speech was produced
        self.assertTrue(self.synthesizer.is_speaking)

if __name__ == '__main__':
    unittest.main()