import { useRef, useState } from "react";
import { sendAIVoice } from "../services/api";

function VoiceScreen({ onComplete }) {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [voiceResult, setVoiceResult] = useState(null);
  const [error, setError] = useState("");

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  const startListening = async () => {
    try {
      setError("");
      setTranscript("");
      setVoiceResult(null);

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setIsListening(false);
        setIsProcessing(true);

        stream.getTracks().forEach((track) => track.stop());

        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType,
        });

        try {
          const data = await sendAIVoice(audioBlob, "en-IN");

          setTranscript(data.transcribed_text);
          setVoiceResult(data);
        } catch (error) {
          console.error(error);
          setError(
            "Sorry, I could not process your voice. Please try again."
          );
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start();
      setIsListening(true);
    } catch (error) {
      console.error(error);
      setError(
        "Microphone access was blocked. Please allow microphone permission and try again."
      );
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="voice-screen">
      <div className="voice-top">
        <div className="brand">
          <div className="brand-icon">S</div>
          <span>SEVA AI</span>
        </div>

        <span className="voice-language">English / ಕನ್ನಡ</span>
      </div>

      <div className="voice-screen-content">
        <div
          className={`voice-screen-icon ${
            isListening ? "listening" : ""
          }`}
        >
          🎙
        </div>

        <p className="voice-step">STEP 1 OF 4</p>

        <h1>
          {isProcessing
            ? "Understanding you..."
            : isListening
            ? "I'm listening..."
            : "Tell us what you need"}
        </h1>

        <p className="voice-description">
          {isProcessing
            ? "SEVA AI is processing what you said."
            : isListening
            ? "Speak naturally. Tell us about your situation and what kind of help you need."
            : "Speak naturally about your situation. Tell us what kind of help you are looking for."}
        </p>

        {error && <div className="transcript-box">{error}</div>}

        {transcript && voiceResult && (
          <>
            <div className="transcript-box">
              <span>You said</span>
              <p>"{transcript}"</p>
            </div>

            <div className="transcript-box">
              <span>SEVA AI</span>
              <p>{voiceResult.reply}</p>
            </div>

            <button
              className="start-listening-button"
              onClick={() => onComplete(voiceResult)}
            >
              <span>→</span>
              Continue
            </button>
          </>
        )}

        {!transcript && !isListening && !isProcessing && (
          <div className="voice-example">
            <span>For example</span>
            <p>
              "I am a farmer and I need financial support for my crops."
            </p>
          </div>
        )}

        {!transcript && !isProcessing && (
          <button
            className={`start-listening-button ${
              isListening ? "listening-button" : ""
            }`}
            onClick={isListening ? stopListening : startListening}
          >
            <span>{isListening ? "⏹" : "🎙"}</span>
            {isListening ? "Stop speaking" : "Start speaking"}
          </button>
        )}

        <p className="voice-screen-hint">
          You can speak in English or Kannada
        </p>
      </div>
    </div>
  );
}

export default VoiceScreen;