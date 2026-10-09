const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const AI_API_BASE_URL =
  import.meta.env.VITE_AI_API_BASE_URL || "http://127.0.0.1:8001";
// =========================================================
// AI TEXT MESSAGE
// =========================================================

export async function sendAIMessage(message, language = "english") {
  const response = await fetch(
    `${AI_API_BASE_URL}/api/ai/message`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        language,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to connect to SEVA AI"
    );
  }

  return response.json();
}

export async function getAILocations() {
  const response = await fetch(`${AI_API_BASE_URL}/api/ai/locations`);
  if (!response.ok) throw new Error("Failed to load state and district options");
  return response.json();
}

export async function submitAILocation(state, district, language = "english") {
  const response = await fetch(`${AI_API_BASE_URL}/api/ai/location`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state, district, language }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Please select a valid district for the chosen state.");
  return data;
}

// =========================================================
// AI VOICE
// =========================================================

export async function sendAIVoice(
  audioBlob,
  language = "en-IN"
) {
  const formData = new FormData();

  formData.append(
    "file",
    audioBlob,
    "voice.webm"
  );

  formData.append(
    "language",
    language
  );

  const response = await fetch(
    `${AI_API_BASE_URL}/api/ai/voice`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to connect to SEVA AI voice service"
    );
  }

  return response.json();
}

// =========================================================
// RESET AI CONVERSATION
// =========================================================

export async function resetAIConversation(){
  const response = await fetch(
    `${AI_API_BASE_URL}/api/ai/reset`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Reset failed (${response.status}): ${errorText}`
    );
  }

  return await response.json();
}
// =========================================================
// ELIGIBILITY
// =========================================================

export async function checkEligibility(profile) {
  const response = await fetch(
    `${API_BASE_URL}/api/eligibility`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(profile),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to check eligibility"
    );
  }

  return response.json();
}

// =========================================================
// LIVE GOVERNMENT SCHEME SEARCH
// =========================================================

export async function searchWebSchemes(profile, language = "english") {
  const response = await fetch(
    `${AI_API_BASE_URL}/api/schemes/web-search`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ profile, language }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to search government schemes"
    );
  }

  return response.json();
}

export async function uploadDocument(
  file,
  documentName,
  name,
  income
) {
  const formData = new FormData();

  formData.append(
    "file",
    file,
    file.name
  );

  formData.append(
    "document_name",
    documentName
  );

  formData.append(
    "name",
    name
  );

  formData.append(
    "income",
    String(income)
  );

  const response = await fetch(
    `${API_BASE_URL}/api/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to upload document"
    );
  }

  return response.json();
}
