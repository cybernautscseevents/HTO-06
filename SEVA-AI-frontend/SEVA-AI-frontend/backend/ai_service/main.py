from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import CitizenProfile
from .conversation import get_missing_fields, get_next_question, process_message
from .locations import canonical_district, canonical_state, get_locations
from .speech import transcribe_audio
from ..benefits_api import router as benefits_router
from ..scheme_web_api import router as scheme_web_router


# ---------------------------------------------------------
# FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="SEVA AI - Member 2 AI Service",
    description=(
        "Free local AI conversation, "
        "multilingual understanding and "
        "citizen information extraction service."
    ),
    version="1.0.0"
)
app.include_router(benefits_router)
app.include_router(scheme_web_router)

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
    language: str = "english"


class LocationRequest(BaseModel):
    state: str
    district: str
    language: str = "english"


SUPPORTED_LANGUAGES = {"english", "kannada", "tamil", "telugu", "hindi", "malayalam"}
SPEECH_LANGUAGE_NAMES = {
    "en": "english", "kn": "kannada", "ta": "tamil",
    "te": "telugu", "hi": "hindi", "ml": "malayalam",
}


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
        current_profile,
        request.language,
    )

    # Update shared in-memory profile
    current_profile = CitizenProfile(
        **result["profile"]
    )

    return result


@app.get("/api/ai/locations")
def ai_locations():
    return {"locations": get_locations()}


@app.post("/api/ai/location")
def ai_location(request: LocationRequest):
    global current_profile

    state = canonical_state(request.state)
    district = canonical_district(state, request.district)
    if not state or not district:
        raise HTTPException(
            status_code=422,
            detail="Choose a district from the selected state or union territory.",
        )

    current_profile.state = state
    current_profile.district = district
    missing_fields = get_missing_fields(current_profile)
    language = request.language if request.language in SUPPORTED_LANGUAGES else "english"
    next_question = get_next_question(current_profile, language)
    reply = (
        ({
            "kannada": "ಸ್ಥಳವನ್ನು ಉಳಿಸಲಾಗಿದೆ. ", "tamil": "இடம் சேமிக்கப்பட்டது. ",
            "telugu": "ప్రాంతం సేవ్ చేయబడింది. ", "hindi": "स्थान सहेज लिया गया। ",
            "malayalam": "സ്ഥലം സംരക്ഷിച്ചു. ",
        }.get(language, "Location saved. ")) + next_question
        if next_question
        else (
            "ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸಂಗ್ರಹಿಸಲಾಗಿದೆ."
            if language == "kannada"
            else {
                "tamil": "உங்கள் தகவல்கள் வெற்றிகரமாகச் சேகரிக்கப்பட்டன.",
                "telugu": "మీ సమాచారం విజయవంతంగా సేకరించబడింది.",
                "hindi": "आपकी जानकारी सफलतापूर्वक एकत्र की गई है।",
                "malayalam": "നിങ്ങളുടെ വിവരങ്ങൾ വിജയകരമായി ശേഖരിച്ചു.",
            }.get(language, "Your information has been successfully collected.")
        )
    )
    return {
        "reply": reply,
        "profile": current_profile.model_dump(),
        "missing_fields": missing_fields,
        "next_question": next_question,
        "language": language,
    }


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
        current_profile,
        SPEECH_LANGUAGE_NAMES.get(language[:2].lower(), "english"),
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
