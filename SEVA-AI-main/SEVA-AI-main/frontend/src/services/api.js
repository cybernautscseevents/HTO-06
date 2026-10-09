const API_BASE_URL = "http://127.0.0.1:8000";

export async function sendAIMessage(message) {
  const response = await fetch(`${API_BASE_URL}/api/ai/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to connect to SEVA AI");
  }

  return response.json();
}

export async function sendAIVoice(audioBlob, language = "en-IN") {
  const formData = new FormData();

  formData.append("file", audioBlob, "voice.webm");
  formData.append("language", language);

  const response = await fetch(`${API_BASE_URL}/api/ai/voice`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to connect to SEVA AI voice service");
  }

  return response.json();
}
export async function checkEligibility(profile) {
  const response = await fetch(`${API_BASE_URL}/api/eligibility`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    throw new Error("Failed to check eligibility");
  }

  return response.json();
}