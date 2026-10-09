import "./App.css";
import { useEffect, useState } from "react";
import TranslateTree from "./i18n";

import AuthScreen from "./pages/AuthScreen";
import VoiceScreen from "./pages/VoiceScreen";
import ConversationScreen from "./pages/ConversationScreen";
import SchemeResults from "./pages/SchemeResults";
import DocumentScreen from "./pages/DocumentScreen";
import ApplicationDraft from "./pages/ApplicationDraft";

import { resetAIConversation } from "./services/api";

const LANGUAGE_LABELS = {
  english: "Language",
  kannada: "ಭಾಷೆ",
  tamil: "மொழி",
  telugu: "భాష",
  hindi: "भाषा",
  malayalam: "ഭാഷ",
};

function App() {
  const [language, setLanguage] = useState(() =>
    ["english", "kannada", "tamil", "telugu", "hindi", "malayalam"].includes(localStorage.getItem("sevaLanguage"))
      ? localStorage.getItem("sevaLanguage")
      : "english"
  );

  useEffect(() => {
    document.documentElement.lang = {
      english: "en", kannada: "kn", tamil: "ta", telugu: "te", hindi: "hi", malayalam: "ml",
    }[language] || "en";
  }, [language]);
  const [isAuthenticated, setIsAuthenticated] = useState(
    localStorage.getItem("sevaAuthenticated") === "true"
  );

  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("sevaUser");

    return storedUser
      ? JSON.parse(storedUser)
      : null;
  });

  const [screen, setScreen] = useState("home");

  const [transcript, setTranscript] = useState("");

  const [voiceResult, setVoiceResult] = useState(null);

  const [eligibilityResults, setEligibilityResults] =
    useState(null);

  const [selectedScheme, setSelectedScheme] =
    useState(null);

  const [applicationDraft, setApplicationDraft] =
    useState(null);

  const handleAuthenticated = (authenticatedUser) => {
    setUser(authenticatedUser);
    setIsAuthenticated(true);
    setScreen("home");
  };

  const handleLogout = () => {
    localStorage.removeItem("sevaAuthenticated");

    setIsAuthenticated(false);
    setUser(null);

    setScreen("home");

    setTranscript("");
    setVoiceResult(null);
    setEligibilityResults(null);
    setSelectedScheme(null);
    setApplicationDraft(null);
  };

  const startNewJourney = async () => {
    try {
      await resetAIConversation();

      setTranscript("");
      setVoiceResult(null);
      setEligibilityResults(null);
      setSelectedScheme(null);
      setApplicationDraft(null);

      setScreen("voice");
    } catch (error) {
      console.error(error);

      alert(
        "Could not start a new SEVA AI conversation."
      );
    }
  };

  const updateLanguage = (event) => {
    const nextLanguage = event.target.value;
    setLanguage(nextLanguage);
    localStorage.setItem("sevaLanguage", nextLanguage);
  };

  const languageControl = (
    <label className="language-control">
      <span>{LANGUAGE_LABELS[language] || "Language"}</span>
      <select value={language} onChange={updateLanguage} aria-label="Language">
        <option value="english">English</option>
        <option value="kannada">ಕನ್ನಡ</option>
        <option value="tamil">தமிழ்</option>
        <option value="telugu">తెలుగు</option>
        <option value="hindi">हिन्दी</option>
        <option value="malayalam">മലയാളം</option>
      </select>
    </label>
  );

  if (!isAuthenticated) {
    return (
      <>
        {languageControl}
        <AuthScreen language={language} onAuthenticated={handleAuthenticated} />
      </>
    );
  }

  if (screen === "voice") {
    return (
      <>
      {languageControl}
      <VoiceScreen
        language={language}
        onComplete={(result) => {
          setTranscript(
            result.transcribed_text
          );

          setVoiceResult(result);

          setScreen("conversation");
        }}
      />
      </>
    );
  }

  if (screen === "conversation") {
    return (
      <>
      {languageControl}
      <ConversationScreen
        language={language}
        initialMessage={transcript}
        initialAIReply={voiceResult?.reply}
        initialProfile={voiceResult?.profile}
        initialMissingFields={
          voiceResult?.missing_fields || []
        }
        onEligibilityComplete={(data) => {
          setEligibilityResults(data);
          setScreen("results");
        }}
      />
      </>
    );
  }

  if (screen === "results") {
    return (
      <>
      {languageControl}
      <SchemeResults
        language={language}
        eligibilityResults={eligibilityResults}
        onContinueDocuments={(scheme) => {
          setSelectedScheme(scheme);
          setScreen("documents");
        }}
      />
      </>
    );
  }

  if (screen === "documents") {
    return (
      <>
      {languageControl}
      <DocumentScreen
        language={language}
        profile={eligibilityResults?.citizen}
        selectedScheme={selectedScheme}
        onBack={() => {
          setScreen("results");
        }}
        onComplete={(data) => {
          setApplicationDraft(data);
          setScreen("application");
        }}
      />
      </>
    );
  }

  if (screen === "application") {
    return (
      <>
      {languageControl}
      <ApplicationDraft
        language={language}
        selectedScheme={selectedScheme}
        profile={eligibilityResults?.citizen}
        providedInformation={
          applicationDraft?.providedInformation || {}
        }
        verificationResults={
          applicationDraft?.verificationResults || {}
        }
        onBack={() => {
          setScreen("documents");
        }}
      />
      </>
    );
  }

  return (
    <TranslateTree language={language}>
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">S</div>

          <div className="brand-text">
            <span>SEVA AI</span>
            <small>Citizen Assistance</small>
          </div>
        </div>

        <div className="nav-right">
          <div className="nav-user">
            <div className="nav-user-avatar">
              {(user?.name || "U")
                .charAt(0)
                .toUpperCase()}
            </div>

            <div className="nav-user-details">
              <strong>
                {user?.name || "User"}
              </strong>

              <span>Citizen</span>
            </div>
          </div>

          {languageControl}

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="hero">
        <div className="hero-content">
          <div className="badge">
            <span className="badge-dot"></span>
            Government benefits made simpler
          </div>

          <h1>
            Get the support
            <br />
            <span>you may be entitled to.</span>
          </h1>

          <p className="hero-description">
            Tell SEVA AI about your situation in your
            own words. We help you discover relevant
            government schemes, understand eligibility,
            and prepare what you need next.
          </p>

          <button
            className="voice-button primary"
            onClick={startNewJourney}
          >
            <span className="mic-icon">🎙</span>

            <span>
              Tell us what you need
            </span>

            <span className="button-arrow">
              →
            </span>
          </button>

          <p className="voice-hint">
            Voice-first assistance in your selected language
          </p>

          <div className="hero-trust-row">
            <div>
              <strong>01</strong>
              <span>
                Describe your situation
              </span>
            </div>

            <div>
              <strong>02</strong>
              <span>
                Check relevant schemes
              </span>
            </div>

            <div>
              <strong>03</strong>
              <span>
                Prepare your documents
              </span>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="visual-shell">
            <div className="visual-topline">
              <span className="visual-live-dot"></span>
              SEVA AI ASSISTANT
            </div>

            <div className="visual-main-card">
              <div className="visual-icon">
                ✦
              </div>

              <div>
                <span className="visual-label">
                  YOUR SITUATION
                </span>

                <h2>
                  "I need help with financial
                  support for my crops."
                </h2>
              </div>
            </div>

            <div className="visual-results">
              <span className="visual-label">
                WHAT WE CAN HELP WITH
              </span>

              <div className="visual-result">
                <div className="visual-result-icon">
                  ₹
                </div>

                <div>
                  <strong>
                    Scheme discovery
                  </strong>

                  <span>
                    Relevant government support
                  </span>
                </div>
              </div>

              <div className="visual-result">
                <div className="visual-result-icon">
                  ✓
                </div>

                <div>
                  <strong>
                    Eligibility understanding
                  </strong>

                  <span>
                    Simple explanations
                  </span>
                </div>
              </div>

              <div className="visual-result">
                <div className="visual-result-icon">
                  ▣
                </div>

                <div>
                  <strong>
                    Document assistance
                  </strong>

                  <span>
                    Know what you need next
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <section className="trust-section">
        <div>
          <span className="trust-eyebrow">
            ONE SIMPLE JOURNEY
          </span>

          <p>
            From your situation to your next step.
          </p>
        </div>

        <div className="trust-items">
          <span>Scheme discovery</span>
          <span>Eligibility</span>
          <span>Documents</span>
          <span>Application preparation</span>
        </div>
      </section>
    </div>
    </TranslateTree>
  );
}

export default App;
