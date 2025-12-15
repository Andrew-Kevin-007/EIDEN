"use client";

import React, { useState, useEffect } from "react";
import { VoicePoweredOrb } from "@/components/ui/voice-powered-orb";
import { Button } from "@/components/ui/button";
import { Mic, MicOff, Volume2, VolumeX } from "lucide-react";

export default function Home() {
  const [isListening, setIsListening] = useState(false);
  const [voiceDetected, setVoiceDetected] = useState(false);
  const [statusText, setStatusText] = useState("Click Start to activate JARVIS");
  const [recognizedText, setRecognizedText] = useState("");
  const [response, setResponse] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // Speech Recognition
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'en-US';

        recognitionInstance.onresult = (event: any) => {
          const transcript = Array.from(event.results)
            .map((result: any) => result[0])
            .map((result: any) => result.transcript)
            .join('');

          setRecognizedText(transcript);

          // Check for wake words
          const lowerTranscript = transcript.toLowerCase();
          if (lowerTranscript.includes('hey assistant') || lowerTranscript.includes('jarvis')) {
            handleCommand(transcript);
          }
        };

        recognitionInstance.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setStatusText(`Error: ${event.error}`);
        };

        recognitionInstance.onend = () => {
          if (isListening) {
            recognitionInstance.start();
          }
        };

        setRecognition(recognitionInstance);
      } else {
        setStatusText("Speech recognition not supported in this browser");
      }
    }
  }, []);

  const toggleListening = async () => {
    if (!recognition) {
      setStatusText("Speech recognition not available");
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
      setStatusText("JARVIS stopped");
    } else {
      try {
        recognition.start();
        setIsListening(true);
        setStatusText('Listening for "Hey Assistant" or "Jarvis"...');
      } catch (error) {
        console.error('Failed to start recognition:', error);
        setStatusText("Failed to start listening");
      }
    }
  };

  const handleCommand = async (text: string) => {
    setIsProcessing(true);
    setStatusText("Processing your command...");

    try {
      // Send command to Python backend
      const res = await fetch('http://localhost:8000/api/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: text }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      setResponse(data.response);
      setStatusText("Response received!");

      // Speak the response
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(data.response);
        utterance.rate = 1.1;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        utterance.onend = () => {
          setIsProcessing(false);
          setStatusText('Listening for "Hey Assistant" or "Jarvis"...');
        };

        window.speechSynthesis.speak(utterance);
      } else {
        setIsProcessing(false);
        setStatusText('Listening for "Hey Assistant" or "Jarvis"...');
      }

    } catch (error) {
      console.error('Error processing command:', error);
      setStatusText("Error: Backend not connected");
      setIsProcessing(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-purple-950/20 to-black flex items-center justify-center p-8">
      <div className="flex flex-col items-center space-y-8 max-w-4xl w-full">
        {/* Title */}
        <div className="text-center space-y-2">
          <h1 className="text-6xl font-bold text-white tracking-tight">
            JARVIS
          </h1>
          <p className="text-xl text-purple-300">
            AI-Powered Voice Assistant
          </p>
        </div>

        {/* Voice-Powered Orb */}
        <div className="w-[500px] h-[500px] relative">
          <VoicePoweredOrb
            enableVoiceControl={isListening}
            className="rounded-full overflow-hidden shadow-2xl shadow-purple-500/50"
            onVoiceDetected={setVoiceDetected}
            hue={isProcessing ? 280 : 0}
            voiceSensitivity={2.0}
            maxRotationSpeed={1.5}
            maxHoverIntensity={1.0}
          />
          
          {/* Voice indicator overlay */}
          {voiceDetected && isListening && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="bg-white/10 backdrop-blur-sm rounded-full p-4">
                <Volume2 className="w-12 h-12 text-white animate-pulse" />
              </div>
            </div>
          )}
        </div>

        {/* Status and Text Display */}
        <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 w-full max-w-2xl border border-white/10">
          <div className="space-y-4">
            {/* Status */}
            <div className="text-center">
              <p className={`text-sm font-medium ${
                isListening ? 'text-green-400' : 'text-purple-400'
              }`}>
                {statusText}
              </p>
            </div>

            {/* Recognized Text */}
            {recognizedText && (
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-xs text-purple-300 mb-1">You said:</p>
                <p className="text-white">{recognizedText}</p>
              </div>
            )}

            {/* Response */}
            {response && (
              <div className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                <p className="text-xs text-purple-300 mb-1">JARVIS:</p>
                <p className="text-white">{response}</p>
              </div>
            )}
          </div>
        </div>

        {/* Control Button */}
        <Button
          onClick={toggleListening}
          variant={isListening ? "destructive" : "default"}
          size="lg"
          className="px-12 py-6 text-lg"
          disabled={!recognition}
        >
          {isListening ? (
            <>
              <MicOff className="w-6 h-6 mr-3" />
              Stop Listening
            </>
          ) : (
            <>
              <Mic className="w-6 h-6 mr-3" />
              Start JARVIS
            </>
          )}
        </Button>

        {/* Instructions */}
        <div className="text-center max-w-md space-y-2">
          <p className="text-sm text-purple-300">
            Click "Start JARVIS" then say <span className="font-bold text-white">"Hey Assistant"</span> or <span className="font-bold text-white">"Jarvis"</span>
          </p>
          <p className="text-xs text-purple-400">
            The orb responds to your voice with beautiful animations
          </p>
        </div>
      </div>
    </main>
  );
}
