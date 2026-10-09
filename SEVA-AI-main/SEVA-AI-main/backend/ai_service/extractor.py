import re
from typing import Any

from .models import CitizenProfile


# =========================================================
# OCCUPATION KEYWORDS
# =========================================================

OCCUPATION_KEYWORDS = {
    "farmer": [
        "farmer",
        "farming",
        "agriculture",
        "agriculturist",
        "ರೈತ",
        "ಕೃಷಿಕ",
        "ಕೃಷಿ",
    ],

    "student": [
        "student",
        "college student",
        "school student",
        "ವಿದ್ಯಾರ್ಥಿ",
        "ವಿದ್ಯಾರ್ಥಿನಿ",
    ],

    "daily_wage_worker": [
        "daily wage",
        "daily wage worker",
        "labourer",
        "laborer",
        "ಕೂಲಿ",
        "ದಿನಗೂಲಿ",
        "ಕಾರ್ಮಿಕ",
    ],

    "business": [
        "business",
        "businessman",
        "businesswoman",
        "ವ್ಯಾಪಾರ",
        "ವ್ಯಾಪಾರಿ",
    ],

    "employee": [
        "employee",
        "job",
        "working",
        "private employee",
        "government employee",
        "ಉದ್ಯೋಗ",
        "ಕೆಲಸ",
    ],
}


# =========================================================
# PROBLEM KEYWORDS
# =========================================================

PROBLEM_KEYWORDS = {
    "crop_damage": [
    # English
    "crop damaged",
    "crop damage",
    "crops damaged",
    "crops were damaged",
    "crop was damaged",
    "crop loss",
    "crop losses",
    "crop failed",
    "crops failed",
    "crops were destroyed",
    "crop destroyed",

    # Kannada
    "ಬೆಳೆ ಹಾಳಾಗಿದೆ",
    "ಬೆಳೆಯು ಹಾಳಾಗಿದೆ",
    "ಬೆಳೆ ಹಾನಿಯಾಗಿದೆ",
    "ಬೆಳೆಯ ಹಾನಿಯಾಗಿದೆ",
    "ಬೆಳೆ ನಾಶವಾಗಿದೆ",
    "ಬೆಳೆಯು ನಾಶವಾಗಿದೆ",
    "ಬೆಳೆ ನಷ್ಟ",
    "ಬೆಳೆಯ ನಷ್ಟ",
    "ಬೆಳೆ ಹಾಳು",
    "ಬೆಳೆ ಹಾನಿ",
    "ಬೆಳೆ ನಾಶ",
],
    "unemployment": [
        "unemployed",
        "unemployment",
        "no job",
        "jobless",
        "lost my job",
        "ನಿರುದ್ಯೋಗ",
        "ಕೆಲಸ ಇಲ್ಲ",
        "ಉದ್ಯೋಗ ಇಲ್ಲ",
    ],

    "housing": [
        "house problem",
        "housing problem",
        "housing",
        "house damaged",
        "home damaged",
        "house is damaged",
        "need a house",
        "ಮನೆ ಸಮಸ್ಯೆ",
        "ಮನೆ ಹಾನಿ",
        "ಮನೆ ಬೇಕು",
    ],

    "education": [
        "education problem",
        "education",
        "school",
        "college fees",
        "college fee",
        "fees problem",
        "education fees",
        "ಶಿಕ್ಷಣ",
        "ಶಾಲೆ",
        "ಕಾಲೇಜು",
        "ಶುಲ್ಕ",
    ],

    "health": [
        "health problem",
        "medical problem",
        "health issue",
        "medical treatment",
        "hospital",
        "treatment",
        "ಆರೋಗ್ಯ",
        "ಆಸ್ಪತ್ರೆ",
        "ಚಿಕಿತ್ಸೆ",
    ],

    "financial": [
        "financial problem",
        "money problem",
        "financial help",
        "need money",
        "financial assistance",
        "ಹಣದ ಸಮಸ್ಯೆ",
        "ಆರ್ಥಿಕ ಸಮಸ್ಯೆ",
        "ಆರ್ಥಿಕ ಸಹಾಯ",
    ],
}


# =========================================================
# CAUSE KEYWORDS
# =========================================================

CAUSE_KEYWORDS = {
    "heavy_rain": [
        "heavy rain",
        "heavy rainfall",
        "heavy rains",
        "because of rain",
        "due to rain",
        "ಮಳೆ",
        "ಭಾರಿ ಮಳೆ",
    ],

    "flood": [
        "flood",
        "flooding",
        "flood water",
        "ಪ್ರವಾಹ",
        "ನೆರೆ",
    ],

    "drought": [
        "drought",
        "no rain",
        "lack of rain",
        "dry conditions",
        "ಬರ",
        "ಮಳೆ ಇಲ್ಲ",
    ],
}


# =========================================================
# CATEGORY KEYWORDS
# =========================================================

CATEGORY_KEYWORDS = {
    "SC": [
        "scheduled caste",
        "scheduled castes",
        "sc category",
        "sc",
        "ಪರಿಶಿಷ್ಟ ಜಾತಿ",
    ],

    "ST": [
        "scheduled tribe",
        "scheduled tribes",
        "st category",
        "st",
        "ಪರಿಶಿಷ್ಟ ಪಂಗಡ",
    ],

    "OBC": [
        "other backward class",
        "other backward classes",
        "obc category",
        "obc",
        "ಹಿಂದುಳಿದ ವರ್ಗ",
    ],

    "GENERAL": [
        "general category",
        "general",
        "ಸಾಮಾನ್ಯ ವರ್ಗ",
    ],
}


# =========================================================
# STATE KEYWORDS
# =========================================================

STATE_KEYWORDS = {
    "Karnataka": [
        "karnataka",
        "ಕರ್ನಾಟಕ",
    ],

    "Kerala": [
        "kerala",
        "ಕೇರಳ",
    ],

    "Tamil Nadu": [
        "tamil nadu",
        "ತಮಿಳುನಾಡು",
    ],

    "Andhra Pradesh": [
        "andhra pradesh",
        "ಆಂಧ್ರ ಪ್ರದೇಶ",
    ],

    "Telangana": [
        "telangana",
        "ತೆಲಂಗಾಣ",
    ],

    "Maharashtra": [
        "maharashtra",
        "ಮಹಾರಾಷ್ಟ್ರ",
    ],

    "Goa": [
        "goa",
        "ಗೋವಾ",
    ],
}


# =========================================================
# DISTRICT KEYWORDS
# =========================================================

DISTRICT_KEYWORDS = {
    "Mysuru": [
        "mysuru",
        "mysore",
        "ಮೈಸೂರು",
    ],

    "Mangaluru": [
        "mangaluru",
        "mangalore",
        "ಮಂಗಳೂರು",
    ],

    "Bengaluru": [
        "bengaluru",
        "bangalore",
        "ಬೆಂಗಳೂರು",
    ],

    "Mandya": [
        "mandya",
        "ಮಂಡ್ಯ",
    ],

    "Hassan": [
        "hassan",
        "ಹಾಸನ",
    ],

    "Kodagu": [
        "kodagu",
        "coorg",
        "ಕೊಡಗು",
    ],

    "Tumakuru": [
        "tumakuru",
        "tumkur",
        "ತುಮಕೂರು",
    ],

    "Shivamogga": [
        "shivamogga",
        "shimoga",
        "ಶಿವಮೊಗ್ಗ",
    ],

    "Udupi": [
        "udupi",
        "ಉಡುಪಿ",
    ],

    "Dakshina Kannada": [
        "dakshina kannada",
        "ದಕ್ಷಿಣ ಕನ್ನಡ",
    ],
}


# =========================================================
# KEYWORD MATCHING
# =========================================================
def contains_keyword(text: str, keyword: str) -> bool:
    """
    Safely check whether a keyword exists in the text.

    Short English keywords such as:
        SC
        ST
        OBC

    must match as complete words, not as parts of
    other words such as:
        district
        school
        student
    """

    keyword = keyword.strip()

    # For very short English keywords such as SC, ST, OBC,
    # require a complete-word match.
    if keyword.isascii() and len(keyword) <= 3:

        pattern = r"(?<![A-Za-z])" + re.escape(keyword) + r"(?![A-Za-z])"

        return re.search(
            pattern,
            text,
            re.IGNORECASE
        ) is not None

    # Normal matching for longer English/Kannada phrases.
    return keyword.lower() in text.lower()


def find_keyword_match(
    text: str,
    keyword_map: dict
) -> str | None:
    """
    Search the input text against a keyword dictionary.

    Returns the corresponding standardized value.
    Returns None when nothing is found.
    """

    for result, keywords in keyword_map.items():

        for keyword in keywords:

            if contains_keyword(text, keyword):
                return result

    return None


# =========================================================
# AGE EXTRACTION
# =========================================================

def extract_age(text: str) -> int | None:
    """
    Extract age from English or Kannada text.
    """

    patterns = [
        r"\b(?:i am|i'm|age is|aged)\s+(\d{1,3})\b",
        r"\b(\d{1,3})\s*(?:years old|year old)\b",
        r"\bage\s*[:\-]?\s*(\d{1,3})\b",
        r"\bವಯಸ್ಸು\s*[:\-]?\s*(\d{1,3})\b",
        r"\bನನಗೆ\s*(\d{1,3})\s*(?:ವರ್ಷ|ವರ್ಷಗಳು)\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            age = int(match.group(1))

            if 1 <= age <= 120:
                return age

    return None


# =========================================================
# INCOME EXTRACTION
# =========================================================

def extract_income(text: str) -> float | None:
    """
    Extract income from English or Kannada text.

    Examples:
        income is 180000
        annual income 180000
        ₹180000
        Rs 180000
        ಆದಾಯ 180000
    """

    patterns = [
        r"(?:annual\s+income|income|salary|earning|earn)\s*(?:is|of|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",

        r"(?:₹|rs\.?|inr)\s*([\d,]+)",

        r"ಆದಾಯ\s*(?:[:\-]?\s*)?([\d,]+)",

        r"ಸಂಬಳ\s*(?:[:\-]?\s*)?([\d,]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).replace(",", "")

            try:
                return float(value)
            except ValueError:
                pass

    return None


# =========================================================
# NAME EXTRACTION
# =========================================================

def extract_name(text: str) -> str:
    """
    Extract a person's name.

    Examples:

        My name is Arif.
        My name is Arif and I am 21 years old.
        Name: Arif
        ನನ್ನ ಹೆಸರು ಆರಿಫ್
    """

    patterns = [

        # My name is Arif and I am 21
        r"\bmy name is\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,3})(?=\s+and\b|[.,!?]|$)",

        # Name: Arif
        r"\bname\s*(?:is|:)\s*([A-Za-z]+(?:\s+[A-Za-z]+){0,3})(?=[.,!?]|$)",

        # Kannada
        r"\bನನ್ನ ಹೆಸರು\s+([^\.\n,]+)",

        # Kannada: ಹೆಸರು: Arif
        r"\bಹೆಸರು\s*[:\-]\s*([^\.\n,]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            if name:
                return name

    return ""


# =========================================================
# ADDITIONAL DETAILS
# =========================================================

def extract_additional_details(
    text: str
) -> dict[str, Any]:
    """
    Extract additional information without
    changing the shared citizen profile structure.
    """

    details: dict[str, Any] = {}

    cause = find_keyword_match(
        text,
        CAUSE_KEYWORDS
    )

    if cause:
        details["cause"] = cause

    return details


# =========================================================
# MAIN PROFILE EXTRACTION
# =========================================================

def extract_profile(
    text: str
) -> CitizenProfile:
    """
    Convert a citizen's message into the
    shared CitizenProfile structure.

    IMPORTANT:
    - Does not invent information.
    - Missing values remain empty/null.
    - Supports English and basic Kannada keywords.
    """

    occupation = find_keyword_match(
        text,
        OCCUPATION_KEYWORDS
    )

    problem = find_keyword_match(
        text,
        PROBLEM_KEYWORDS
    )

    category = find_keyword_match(
        text,
        CATEGORY_KEYWORDS
    )

    state = find_keyword_match(
        text,
        STATE_KEYWORDS
    )

    district = find_keyword_match(
        text,
        DISTRICT_KEYWORDS
    )

    age = extract_age(text)

    income = extract_income(text)

    name = extract_name(text)

    additional_details = extract_additional_details(
        text
    )

    return CitizenProfile(
        name=name,
        age=age,
        income=income,
        occupation=occupation or "",
        state=state or "",
        district=district or "",
        category=category or "",
        problem=problem or "",
        additional_details=additional_details,
    )