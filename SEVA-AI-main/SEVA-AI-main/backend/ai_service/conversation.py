from .extractor import extract_profile
from .models import CitizenProfile


# ---------------------------------------------------------
# REQUIRED PROFILE FIELDS
# ---------------------------------------------------------

REQUIRED_FIELDS = [
    "name",
    "age",
    "income",
    "occupation",
    "state",
    "district",
    "category",
    "problem",
]


# ---------------------------------------------------------
# MISSING FIELD DETECTION
# ---------------------------------------------------------

def get_missing_fields(profile: CitizenProfile) -> list[str]:
    missing = []

    for field in REQUIRED_FIELDS:
        value = getattr(profile, field)

        if value is None:
            missing.append(field)

        elif isinstance(value, str) and value.strip() == "":
            missing.append(field)

    return missing


# ---------------------------------------------------------
# MERGE PROFILES
# ---------------------------------------------------------

def merge_profiles(
    current: CitizenProfile,
    new: CitizenProfile
) -> CitizenProfile:

    # Update only when the new message actually
    # contains information.

    if new.name:
        current.name = new.name

    if new.age is not None:
        current.age = new.age

    if new.income is not None:
        current.income = new.income

    if new.occupation:
        current.occupation = new.occupation

    if new.state:
        current.state = new.state

    if new.district:
        current.district = new.district

    if new.category:
        current.category = new.category

    if new.problem:
        current.problem = new.problem

    if new.additional_details:
        current.additional_details.update(
            new.additional_details
        )

    return current


# ---------------------------------------------------------
# FOLLOW-UP QUESTIONS
# ---------------------------------------------------------

QUESTIONS = {
    "name": {
        "english": "What is your name?",
        "kannada": "ನಿಮ್ಮ ಹೆಸರು ಏನು?"
    },

    "age": {
        "english": "What is your age?",
        "kannada": "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?"
    },

    "income": {
        "english": "What is your approximate annual income?",
        "kannada": "ನಿಮ್ಮ ಅಂದಾಜು ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು?"
    },

    "occupation": {
        "english": "What is your occupation?",
        "kannada": "ನಿಮ್ಮ ಉದ್ಯೋಗ ಏನು?"
    },

    "state": {
        "english": "Which state are you from?",
        "kannada": "ನೀವು ಯಾವ ರಾಜ್ಯದವರು?"
    },

    "district": {
        "english": "Which district are you from?",
        "kannada": "ನೀವು ಯಾವ ಜಿಲ್ಲೆಯವರು?"
    },

    "category": {
        "english": "What is your social category, such as SC, ST, OBC or General?",
        "kannada": "ನಿಮ್ಮ ವರ್ಗ ಯಾವುದು? ಉದಾಹರಣೆಗೆ SC, ST, OBC ಅಥವಾ General?"
    },

    "problem": {
        "english": "Please tell me what problem you need help with.",
        "kannada": "ನಿಮಗೆ ಯಾವ ಸಮಸ್ಯೆಗೆ ಸಹಾಯ ಬೇಕು ಎಂದು ತಿಳಿಸಿ."
    },
}


# ---------------------------------------------------------
# LANGUAGE DETECTION
# ---------------------------------------------------------

def detect_language(text: str) -> str:
    """
    Simple Kannada detection.

    If Kannada Unicode characters are present,
    we treat the message as Kannada.
    """

    for character in text:
        if "\u0C80" <= character <= "\u0CFF":
            return "kannada"

    return "english"


# ---------------------------------------------------------
# NEXT QUESTION
# ---------------------------------------------------------

def get_next_question(
    profile: CitizenProfile,
    language: str
) -> str | None:

    missing = get_missing_fields(profile)

    if not missing:
        return None

    field = missing[0]

    return QUESTIONS[field][language]


# ---------------------------------------------------------
# PROCESS MESSAGE
# ---------------------------------------------------------

def process_message(
    message: str,
    current_profile: CitizenProfile
) -> dict:

    language = detect_language(message)

    extracted_profile = extract_profile(message)

    updated_profile = merge_profiles(
        current_profile,
        extracted_profile
    )

    missing_fields = get_missing_fields(
        updated_profile
    )

    next_question = get_next_question(
        updated_profile,
        language
    )

    if next_question:
        if language == "kannada":
            reply = (
                "ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ. "
                + next_question
            )
        else:
            reply = (
                "I have understood the information. "
                + next_question
            )

    else:
        if language == "kannada":
            reply = (
                "ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸಂಗ್ರಹಿಸಲಾಗಿದೆ."
            )
        else:
            reply = (
                "Your information has been successfully collected."
            )

    return {
        "reply": reply,
        "profile": updated_profile.model_dump(),
        "missing_fields": missing_fields,
        "next_question": next_question,
        "language": language,
    }