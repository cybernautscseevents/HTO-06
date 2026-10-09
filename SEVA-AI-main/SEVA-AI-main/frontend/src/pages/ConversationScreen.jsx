import { useState } from "react";
import {
  sendAIMessage,
  checkEligibility,
} from "../services/api";

function ConversationScreen({
  initialMessage,
  initialAIReply,
  onEligibilityComplete,
}) {
  const [messages, setMessages] = useState([
    {
      sender: "user",
      text: initialMessage,
    },
    {
      sender: "ai",
      text:
        initialAIReply ||
        "I can help you find government schemes that may support you. I just need a few details about your situation.",
    },
  ]);

  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage = input.trim();

    setMessages((current) => [
      ...current,
      {
        sender: "user",
        text: userMessage,
      },
    ]);

    setInput("");
    setIsProcessing(true);

    try {
      // Send the user's answer to the AI backend
      const data = await sendAIMessage(userMessage);

      // Show the AI's reply
      setMessages((current) => [
        ...current,
        {
          sender: "ai",
          text: data.reply,
        },
      ]);

      // If the AI has collected all required information,
      // check the citizen's eligibility.
      if (data.missing_fields.length === 0) {
        try {
          const eligibilityData = await checkEligibility(data.profile);

          onEligibilityComplete(eligibilityData);
        } catch (error) {
          console.error(error);

          setMessages((current) => [
            ...current,
            {
              sender: "ai",
              text:
                "I found your information, but I could not check scheme eligibility right now. Please try again.",
            },
          ]);
        }
      }
    } catch (error) {
      console.error(error);

      setMessages((current) => [
        ...current,
        {
          sender: "ai",
          text:
            "Sorry, I could not connect to the AI service. Please try again.",
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="conversation-screen">
      <header className="conversation-top">
        <div className="brand">
          <div className="brand-icon">S</div>
          <span>SEVA AI</span>
        </div>

        <div className="conversation-status">
          <span className="status-dot"></span>
          AI Assistant
        </div>
      </header>

      <main className="conversation-container">
        <div className="conversation-heading">
          <p className="conversation-step">STEP 2 OF 4</p>

          <h1>Let's understand your situation</h1>

          <p>
            I'll ask a few simple questions so I can find the most relevant
            government schemes for you.
          </p>
        </div>

        <div className="messages-container">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message-row ${message.sender}`}
            >
              {message.sender === "ai" && (
                <div className="ai-avatar">S</div>
              )}

              <div className="message-bubble">
                {message.text}
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="message-row ai">
              <div className="ai-avatar">S</div>

              <div className="message-bubble">
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div className="message-input-area">
          <input
            type="text"
            placeholder={
              isProcessing
                ? "SEVA AI is processing..."
                : "Type your answer..."
            }
            value={input}
            disabled={isProcessing}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                sendMessage();
              }
            }}
          />

          <button
            onClick={sendMessage}
            disabled={isProcessing}
          >
            →
          </button>
        </div>

        <p className="conversation-hint">
          You can type your answer here.
        </p>
      </main>
    </div>
  );
}

export default ConversationScreen;