from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import CitizenProfile
from .conversation import process_message
from .speech import transcribe_audio


# ---------------------------------------------------------
# FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="SEVA AI - Member 2 AI Service",
    description=(
        "Free local AI conversation, "
        "Kannada/English understanding and "
        "citizen information extraction service."
    ),
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS - ALLOW REACT FRONTEND
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# CURRENT CITIZEN PROFILE
# ---------------------------------------------------------

current_profile = CitizenProfile()


# ---------------------------------------------------------
# REQUEST MODEL
# ---------------------------------------------------------

class MessageRequest(BaseModel):
    message: str


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "SEVA AI Member 2 AI service is running",
        "module": "AI Conversation + Voice + Information Extraction"
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ---------------------------------------------------------
# AI MESSAGE ENDPOINT
# ---------------------------------------------------------

@app.post("/api/ai/message")
def ai_message(request: MessageRequest):

    global current_profile

    result = process_message(
        request.message,
        current_profile
    )

    # Update shared in-memory profile
    current_profile = CitizenProfile(
        **result["profile"]
    )

    return result


# ---------------------------------------------------------
# AI VOICE ENDPOINT
# ---------------------------------------------------------

@app.post("/api/ai/voice")
async def ai_voice(
    file: UploadFile = File(...),
    language: str = "en-IN"
):

    global current_profile

    # Read uploaded audio
    audio_data = await file.read()

    # Convert speech to text
    text = transcribe_audio(
        audio_data,
        language
    )

    # If speech could not be understood
    if not text:

        return {
            "success": False,
            "message": "Could not understand the audio.",
            "transcribed_text": "",
            "profile": current_profile.model_dump()
        }

    # Send transcribed text through
    # the SAME conversation pipeline
    result = process_message(
        text,
        current_profile
    )

    # Update shared profile
    current_profile = CitizenProfile(
        **result["profile"]
    )

    return {
        "success": True,
        "transcribed_text": text,
        "reply": result["reply"],
        "profile": result["profile"],
        "missing_fields": result["missing_fields"],
        "next_question": result["next_question"],
        "language": result["language"]
    }


# ---------------------------------------------------------
# RESET CONVERSATION
# ---------------------------------------------------------

@app.post("/api/ai/reset")
def reset_conversation():

    global current_profile

    current_profile = CitizenProfile()

    return {
        "message": "Conversation reset successfully",
        "profile": current_profile.model_dump()
    }