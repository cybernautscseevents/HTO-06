import { useEffect, useRef, useState } from "react";
import {
  checkEligibility,
  getAILocations,
  sendAIMessage,
  sendAIVoice,
  submitAILocation,
} from "../services/api";
import TranslateTree from "../i18n";

function ConversationScreen({
  initialMessage,
  initialAIReply,
  initialProfile,
  initialMissingFields,
  language,
  onEligibilityComplete,
}) {
  const speechLocale = {
    english: "en-IN", kannada: "kn-IN", tamil: "ta-IN",
    telugu: "te-IN", hindi: "hi-IN", malayalam: "ml-IN",
  }[language] || "en-IN";
  const [messages, setMessages] = useState([
    ...(initialMessage ? [{ sender: "user", text: initialMessage }] : []),
    {
      sender: "ai",
      text: initialAIReply || "I can help you find government schemes that may support you. I just need a few details about your situation.",
    },
  ]);
  const [missingFields, setMissingFields] = useState(initialMissingFields || []);
  const [input, setInput] = useState("");
  const [locations, setLocations] = useState([]);
  const [selectedState, setSelectedState] = useState(initialProfile?.state || "");
  const [selectedDistrict, setSelectedDistrict] = useState(initialProfile?.district || "");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState("");
  const [speakingMessageIndex, setSpeakingMessageIndex] = useState(null);
  const eligibilityStartedRef = useRef(false);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const speakingMessageRef = useRef(null);

  useEffect(() => {
    getAILocations()
      .then((data) => setLocations(data.locations || []))
      .catch((loadError) => {
        console.error("Could not load state and district options:", loadError);
        setError("Could not load state and district options. Please try again.");
      });
    return () => streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  useEffect(() => () => {
    window.speechSynthesis?.cancel();
  }, []);

  const readMessageAloud = (text, index) => {
    const speech = window.speechSynthesis;
    if (!speech || typeof window.SpeechSynthesisUtterance !== "function") {
      setError("Read-aloud is not available in this browser.");
      return;
    }

    if (speakingMessageRef.current === index) {
      speech.cancel();
      speakingMessageRef.current = null;
      setSpeakingMessageIndex(null);
      return;
    }

    speech.cancel();
    const preferredLanguage = speechLocale;
    const voices = speech.getVoices();
    const preferredVoice =
      voices.find((voice) => voice.lang?.toLowerCase() === preferredLanguage.toLowerCase()) ||
      voices.find((voice) => voice.lang?.toLowerCase().startsWith(preferredLanguage.slice(0, 2))) ||
      voices.find((voice) => voice.lang?.toLowerCase().startsWith("en-")) ||
      voices[0];
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = preferredVoice?.lang || preferredLanguage;
    if (preferredVoice) utterance.voice = preferredVoice;
    utterance.volume = 1;
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onstart = () => {
      speakingMessageRef.current = index;
      setSpeakingMessageIndex(index);
      setError("");
    };
    utterance.onend = () => {
      if (speakingMessageRef.current === index) {
        speakingMessageRef.current = null;
        setSpeakingMessageIndex(null);
      }
    };
    utterance.onerror = (event) => {
      if (speakingMessageRef.current === index) {
        speakingMessageRef.current = null;
        setSpeakingMessageIndex(null);
        setError(
          `Could not play the voice (${event.error || "audio unavailable"}). Check your PC and browser sound output, then try again.`
        );
      }
    };
    speakingMessageRef.current = index;
    speech.speak(utterance);
  };

  useEffect(() => {
    if (!initialProfile || initialMissingFields?.length !== 0 || eligibilityStartedRef.current) return;
    eligibilityStartedRef.current = true;
    setIsProcessing(true);
    setMessages((current) => [...current, { sender: "ai", text: "I have collected all the information I need. Checking which government schemes may apply to you..." }]);
    checkEligibility(initialProfile)
      .then(onEligibilityComplete)
      .catch((checkError) => {
        console.error("Automatic eligibility check failed:", checkError);
        setMessages((current) => [...current, { sender: "ai", text: "I collected your information, but I could not check scheme eligibility right now. Please try again." }]);
        eligibilityStartedRef.current = false;
      })
      .finally(() => setIsProcessing(false));
  }, [initialProfile, initialMissingFields, onEligibilityComplete]);

  const appendResult = async (data) => {
    setMissingFields(data.missing_fields || []);
    setSelectedState(data.profile?.state || "");
    setSelectedDistrict(data.profile?.district || "");
    if (data.reply) setMessages((current) => [...current, { sender: "ai", text: data.reply }]);

    if (Array.isArray(data.missing_fields) && data.missing_fields.length === 0) {
      eligibilityStartedRef.current = true;
      try {
        const eligibilityData = await checkEligibility(data.profile);
        onEligibilityComplete(eligibilityData);
      } catch (checkError) {
        console.error(checkError);
        eligibilityStartedRef.current = false;
        setMessages((current) => [...current, { sender: "ai", text: "I found your information, but I could not check scheme eligibility right now. Please try again." }]);
      }
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isProcessing) return;
    const userMessage = input.trim();
    setMessages((current) => [...current, { sender: "user", text: userMessage }]);
    setInput("");
    setError("");
    setIsProcessing(true);
    try {
      await appendResult(await sendAIMessage(userMessage, language));
    } catch (sendError) {
      console.error(sendError);
      setMessages((current) => [...current, { sender: "ai", text: "Sorry, I could not connect to the AI service. Please try again." }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const startListening = async () => {
    try {
      setError("");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const recorder = new MediaRecorder(stream);
      recorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        setIsListening(false);
        setIsProcessing(true);
        stream.getTracks().forEach((track) => track.stop());
        const audio = new Blob(chunksRef.current, { type: recorder.mimeType });
        try {
          const data = await sendAIVoice(
            audio,
            speechLocale
          );
          if (!data.success || !data.transcribed_text) throw new Error("Speech was not recognized");
          setMessages((current) => [...current, { sender: "user", text: data.transcribed_text }]);
          await appendResult(data);
        } catch (voiceError) {
          console.error(voiceError);
          setError("Sorry, I could not understand that recording. Please try again or type your answer.");
        } finally {
          setIsProcessing(false);
        }
      };
      recorder.start();
      setIsListening(true);
    } catch (listenError) {
      console.error(listenError);
      setError("Microphone access was blocked. Please allow microphone permission and try again.");
    }
  };

  const saveLocation = async () => {
    if (!selectedState || !selectedDistrict || isProcessing) return;
    setError("");
    setIsProcessing(true);
    setMessages((current) => [...current, { sender: "user", text: `${selectedDistrict}, ${selectedState}` }]);
    try {
      await appendResult(await submitAILocation(selectedState, selectedDistrict, language));
    } catch (saveError) {
      console.error(saveError);
      setError(saveError.message || "Please select a valid district for the chosen state.");
    } finally {
      setIsProcessing(false);
    }
  };

  const districtOptions = locations.find((item) => item.state === selectedState)?.districts || [];
  const needsLocation = missingFields.includes("state") || missingFields.includes("district");

  return (
    <TranslateTree language={language}>
    <div className="conversation-screen">
      <header className="conversation-top">
        <div className="brand"><div className="brand-icon">S</div><div className="brand-text"><span>SEVA AI</span><small>Citizen Assistance</small></div></div>
        <div className="conversation-status"><span className="status-dot"></span>AI Assistant</div>
      </header>

      <main className="conversation-container">
        <div className="conversation-heading">
          <p className="conversation-step">STEP 2 OF 4</p>
          <h1>Let's understand your situation</h1>
          <p>I'll collect the information needed to identify relevant government schemes for you.</p>
        </div>

        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message-row ${message.sender}`}>
              {message.sender === "ai" && <div className="ai-avatar">S</div>}
              <div className="message-bubble">{message.text}</div>
              {message.sender === "ai" && (
                <button
                  className={`read-aloud-button ${speakingMessageIndex === index ? "speaking" : ""}`}
                  type="button"
                  onClick={() => readMessageAloud(message.text, index)}
                  aria-label={speakingMessageIndex === index ? "Stop reading message" : "Read message aloud"}
                  title={speakingMessageIndex === index ? "Stop reading" : "Read aloud"}
                >
                  {speakingMessageIndex === index ? "■" : "🔊"}
                </button>
              )}
            </div>
          ))}
          {isProcessing && <div className="message-row ai"><div className="ai-avatar">S</div><div className="message-bubble">Checking...</div></div>}
        </div>

        {!isProcessing && needsLocation && (
          <div className="location-picker">
            <label>
              State or Union Territory
              <select value={selectedState} onChange={(event) => { setSelectedState(event.target.value); setSelectedDistrict(""); }}>
                <option value="">Choose a state or union territory</option>
                {locations.map((item) => <option key={item.state} value={item.state}>{item.state}</option>)}
              </select>
            </label>
            <label>
              District
              <select value={selectedDistrict} disabled={!selectedState || !districtOptions.length} onChange={(event) => setSelectedDistrict(event.target.value)}>
                <option value="">{selectedState ? "Choose a district" : "Choose a state first"}</option>
                {districtOptions.map((district) => <option key={district} value={district}>{district}</option>)}
              </select>
            </label>
            <button className="location-submit" onClick={saveLocation} disabled={!selectedState || !selectedDistrict}>Save location</button>
          </div>
        )}

        {!isProcessing && (
          <div className="message-input-area">
            <input type="text" placeholder="Type your answer..." value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") sendMessage(); }} />
            <button type="button" onClick={sendMessage} disabled={!input.trim()} aria-label="Send message">→</button>
          </div>
        )}

        {!isProcessing && <button type="button" className={`conversation-mic ${isListening ? "listening" : ""}`} onClick={() => (isListening ? recorderRef.current?.stop() : startListening())}>
          {isListening ? "Stop speaking" : "🎙 Speak your answer"}
        </button>}
        {error && <p className="conversation-error">{error}</p>}
        <p className="conversation-hint">You can type or speak your answer. For location, choose a state and then one of its districts.</p>
      </main>
    </div>
    </TranslateTree>
  );
}

export default ConversationScreen;
