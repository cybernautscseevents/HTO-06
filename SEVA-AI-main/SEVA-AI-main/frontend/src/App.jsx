import "./App.css";

import VoiceScreen from "./pages/VoiceScreen";
import ConversationScreen from "./pages/ConversationScreen";
import SchemeResults from "./pages/SchemeResults";

import { useState } from "react";

function App() {
  const [screen, setScreen] = useState("home");

  const [transcript, setTranscript] = useState("");
  const [voiceResult, setVoiceResult] = useState(null);

  const [eligibilityResults, setEligibilityResults] = useState(null);

  if (screen === "voice") {
    return (
      <VoiceScreen
        onComplete={(voiceResult) => {
          setTranscript(voiceResult.transcribed_text);
          setVoiceResult(voiceResult);
          setScreen("conversation");
        }}
      />
    );
  }

  if (screen === "conversation") {
    return (
      <ConversationScreen
        initialMessage={transcript}
        initialAIReply={voiceResult?.reply}
        onEligibilityComplete={(data) => {
          setEligibilityResults(data);
          setScreen("results");
        }}
      />
    );
  }

  if (screen === "results") {
    return (
      <SchemeResults
        eligibilityResults={eligibilityResults}
      />
    );
  }

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <span>SEVA AI</span>
        </div>

        <div className="nav-right">
          <span>English</span>
          <button className="help-button">Help</button>
        </div>
      </header>

      <main className="hero">
        <div className="hero-content">
          <div className="badge">
            <span className="badge-dot"></span>
            Government benefits made simple
          </div>

          <h1>
            Get the benefits
            <br />
            <span>you deserve.</span>
          </h1>

          <p className="hero-description">
            Tell us what you need in your own words. SEVA AI helps you
            discover government schemes, check your eligibility, and prepare
            the documents you need.
          </p>

          <button
            className="voice-button"
            onClick={() => setScreen("voice")}
          >
            <span className="mic-icon">🎙</span>
            <span>Tell us what you need</span>
          </button>

          <p className="voice-hint">
            You can speak in English or Kannada
          </p>

          {/* Temporary testing button */}
          <button
            className="voice-button"
            onClick={() => setScreen("results")}
          >
            View scheme results
          </button>
        </div>

        <div className="hero-visual">
          <div className="visual-card">
            <div className="visual-icon">✦</div>

            <h2>How can we help?</h2>

            <p>
              "I am a farmer and I need help with financial support."
            </p>

            <div className="example-label">
              SEVA AI can help you find:
            </div>

            <div className="scheme-preview">
              <div className="scheme-icon">₹</div>

              <div>
                <strong>Relevant schemes</strong>
                <span>Matched to your situation</span>
              </div>
            </div>

            <div className="scheme-preview">
              <div className="scheme-icon">✓</div>

              <div>
                <strong>Eligibility</strong>
                <span>Simple explanations</span>
              </div>
            </div>

            <div className="scheme-preview">
              <div className="scheme-icon">▣</div>

              <div>
                <strong>Documents</strong>
                <span>Personalized checklist</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      <section className="trust-section">
        <p>One simple conversation. Multiple benefits.</p>

        <div className="trust-items">
          <span>✓ Scheme discovery</span>
          <span>✓ Eligibility check</span>
          <span>✓ Document assistance</span>
          <span>✓ Application preparation</span>
        </div>
      </section>
    </div>
  );
}

export default App;