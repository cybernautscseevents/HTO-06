
import re
from typing import Any

from .models import CitizenProfile


# =========================================================
# STATE KEYWORDS
# =========================================================

STATE_KEYWORDS = {
    "Karnataka": [
        "karnataka",
        "ಕರ್ನಾಟಕ",
    ],

    "Maharashtra": [
        "maharashtra",
        "maharastra",
        "महाराष्ट्र",
        "ಮಹಾರಾಷ್ಟ್ರ",
    ],

    "Kerala": [
        "kerala",
        "കേരളം",
        "കേരളാ",
        "കേറള",
        "ಕೇರಳ",
    ],
}


# =========================================================
# DISTRICT KEYWORDS
# ALL DISTRICTS OF KARNATAKA, MAHARASHTRA AND KERALA
# =========================================================

DISTRICT_KEYWORDS = {

    # -----------------------------------------------------
    # KARNATAKA
    # -----------------------------------------------------

    "Bagalkot": [
        "bagalkot",
        "bagalkote",
        "ಬಾಗಲಕೋಟೆ",
    ],

    "Ballari": [
        "ballari",
        "bellary",
        "ಬಳ್ಳಾರಿ",
    ],

    "Belagavi": [
        "belagavi",
        "belgaum",
        "ಬೆಳಗಾವಿ",
    ],

    "Bengaluru Rural": [
        "bengaluru rural",
        "bangalore rural",
        "ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ",
    ],

    "Bengaluru Urban": [
        "bengaluru urban",
        "bangalore urban",
        "bengaluru",
        "bangalore",
        "ಬೆಂಗಳೂರು",
    ],

    "Bidar": [
        "bidar",
        "ಬೀದರ್",
    ],

    "Chamarajanagar": [
        "chamarajanagar",
        "chamarajanagara",
        "ಚಾಮರಾಜನಗರ",
    ],

    "Chikkaballapur": [
        "chikkaballapur",
        "chikballapur",
        "ಚಿಕ್ಕಬಳ್ಳಾಪುರ",
    ],

    "Chikkamagaluru": [
        "chikkamagaluru",
        "chikmagalur",
        "ಚಿಕ್ಕಮಗಳೂರು",
    ],

    "Chitradurga": [
        "chitradurga",
        "ಚಿತ್ರದುರ್ಗ",
    ],

    "Dakshina Kannada": [
        "dakshina kannada",
        "south kanara",
        "dk",
        "ದಕ್ಷಿಣ ಕನ್ನಡ",
    ],

    "Davanagere": [
        "davanagere",
        "davangere",
        "ದಾವಣಗೆರೆ",
    ],

    "Dharwad": [
        "dharwad",
        "ಧಾರವಾಡ",
    ],

    "Gadag": [
        "gadag",
        "ಗದಗ",
    ],

    "Hassan": [
        "hassan",
        "ಹಾಸನ",
    ],

    "Haveri": [
        "haveri",
        "ಹಾವೇರಿ",
    ],

    "Kalaburagi": [
        "kalaburagi",
        "gulbarga",
        "ಕಲಬುರಗಿ",
        "ಗುಲಬರ್ಗಾ",
    ],

    "Kodagu": [
        "kodagu",
        "coorg",
        "ಕೊಡಗು",
    ],

    "Kolar": [
        "kolar",
        "ಕೋಲಾರ",
    ],

    "Koppal": [
        "koppal",
        "ಕೊಪ್ಪಳ",
    ],

    "Mandya": [
        "mandya",
        "ಮಂಡ್ಯ",
    ],

    "Mysuru": [
        "mysuru",
        "mysore",
        "ಮೈಸೂರು",
    ],

    "Raichur": [
        "raichur",
        "ರಾಯಚೂರು",
    ],

    "Ramanagara": [
        "ramanagara",
        "ramnagara",
        "ರಾಮನಗರ",
    ],

    "Shivamogga": [
        "shivamogga",
        "shimoga",
        "ಶಿವಮೊಗ್ಗ",
    ],

    "Tumakuru": [
        "tumakuru",
        "tumkur",
        "ತುಮಕೂರು",
    ],

    "Udupi": [
        "udupi",
        "ಉಡುಪಿ",
    ],

    "Uttara Kannada": [
        "uttara kannada",
        "north kanara",
        "ಉತ್ತರ ಕನ್ನಡ",
    ],

    "Vijayapura": [
        "vijayapura",
        "bijapur",
        "ವಿಜಯಪುರ",
    ],

    "Vijayanagara": [
        "vijayanagara",
        "vijayanagaram",
        "ವಿಜಯನಗರ",
    ],

    "Yadgir": [
        "yadgir",
        "yadagiri",
        "ಯಾದಗಿರಿ",
    ],


    # -----------------------------------------------------
    # MAHARASHTRA
    # -----------------------------------------------------

    "Ahmednagar": [
        "ahmednagar",
        "ahilyanagar",
        "अहमदनगर",
        "अहिल्यानगर",
    ],

    "Akola": [
        "akola",
        "अकोला",
    ],

    "Amravati": [
        "amravati",
        "अमरावती",
    ],

    "Aurangabad": [
        "aurangabad",
        "chhatrapati sambhajinagar",
        "छत्रपती संभाजीनगर",
        "औरंगाबाद",
    ],

    "Beed": [
        "beed",
        "बीड",
    ],

    "Bhandara": [
        "bhandara",
        "भंडारा",
    ],

    "Buldhana": [
        "buldhana",
        "बुलढाणा",
    ],

    "Chandrapur": [
        "chandrapur",
        "चंद्रपूर",
    ],

    "Dhule": [
        "dhule",
        "धुळे",
    ],

    "Gadchiroli": [
        "gadchiroli",
        "गडचिरोली",
    ],

    "Gondia": [
        "gondia",
        "गोंदिया",
    ],

    "Hingoli": [
        "hingoli",
        "हिंगोली",
    ],

    "Jalgaon": [
        "jalgaon",
        "जळगाव",
    ],

    "Jalna": [
        "jalna",
        "जालना",
    ],

    "Kolhapur": [
        "kolhapur",
        "कोल्हापूर",
    ],

    "Latur": [
        "latur",
        "लातूर",
    ],

    "Mumbai City": [
        "mumbai city",
        "मुंबई शहर",
    ],

    "Mumbai Suburban": [
        "mumbai suburban",
        "मुंबई उपनगर",
    ],

    "Nagpur": [
        "nagpur",
        "नागपूर",
    ],

    "Nanded": [
        "nanded",
        "नांदेड",
    ],

    "Nandurbar": [
        "nandurbar",
        "नंदुरबार",
    ],

    "Nashik": [
        "nashik",
        "nasik",
        "नाशिक",
    ],

    "Dharashiv": [
        "dharashiv",
        "osmanabad",
        "धाराशिव",
        "उस्मानाबाद",
    ],

    "Palghar": [
        "palghar",
        "पालघर",
    ],

    "Parbhani": [
        "parbhani",
        "परभणी",
    ],

    "Pune": [
        "pune",
        "poona",
        "पुणे",
    ],

    "Raigad": [
        "raigad",
        "रायगड",
    ],

    "Ratnagiri": [
        "ratnagiri",
        "रत्नागिरी",
    ],

    "Sangli": [
        "sangli",
        "सांगली",
    ],

    "Satara": [
        "satara",
        "सातारा",
    ],

    "Sindhudurg": [
        "sindhudurg",
        "सिंधुदुर्ग",
    ],

    "Solapur": [
        "solapur",
        "sholapur",
        "सोलापूर",
    ],

    "Thane": [
        "thane",
        "ठाणे",
    ],

    "Wardha": [
        "wardha",
        "वर्धा",
    ],

    "Washim": [
        "washim",
        "वाशिम",
    ],

    "Yavatmal": [
        "yavatmal",
        "यवतमाळ",
    ],


    # -----------------------------------------------------
    # KERALA
    # -----------------------------------------------------

    "Alappuzha": [
        "alappuzha",
        "alleppey",
        "ആലപ്പുഴ",
    ],

    "Ernakulam": [
        "ernakulam",
        "kochi",
        "cochin",
        "എറണാകുളം",
    ],

    "Idukki": [
        "idukki",
        "ഇടുക്കി",
    ],

    "Kannur": [
        "kannur",
        "cannanore",
        "കണ്ണൂർ",
    ],

    "Kasaragod": [
        "kasaragod",
        "kasargod",
        "കാസർഗോഡ്",
    ],

    "Kollam": [
        "kollam",
        "quilon",
        "കൊല്ലം",
    ],

    "Kottayam": [
        "kottayam",
        "കോട്ടയം",
    ],

    "Kozhikode": [
        "kozhikode",
        "calicut",
        "കോഴിക്കോട്",
    ],

    "Malappuram": [
        "malappuram",
        "മലപ്പുറം",
    ],

    "Palakkad": [
        "palakkad",
        "palghat",
        "പാലക്കാട്",
    ],

    "Pathanamthitta": [
        "pathanamthitta",
        "പത്തനംതിട്ട",
    ],

    "Thiruvananthapuram": [
        "thiruvananthapuram",
        "trivandrum",
        "തിരുവനന്തപുരം",
    ],

    "Thrissur": [
        "thrissur",
        "trichur",
        "തൃശ്ശൂർ",
    ],

    "Wayanad": [
        "wayanad",
        "വയനാട്",
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
        "अनुसूचित जाति",
    ],

    "ST": [
        "scheduled tribe",
        "scheduled tribes",
        "st category",
        "st",
        "ಪರಿಶಿಷ್ಟ ಪಂಗಡ",
        "अनुसूचित जनजाति",
    ],

    "OBC": [
        "other backward class",
        "other backward classes",
        "obc category",
        "obc",
        "ಹಿಂದುಳಿದ ವರ್ಗ",
        "इतर मागासवर्गीय",
    ],

    "GENERAL": [
        "general category",
        "general",
        "ಸಾಮಾನ್ಯ ವರ್ಗ",
        "सामान्य",
    ],
}


# =========================================================
# KEYWORD MATCHING
# =========================================================

def contains_keyword(text: str, keyword: str) -> bool:
    """
    Safely check whether a keyword exists in the text.
    """

    keyword = keyword.strip()

    if keyword.isascii() and len(keyword) <= 3:
        pattern = (
            r"(?<![A-Za-z])"
            + re.escape(keyword)
            + r"(?![A-Za-z])"
        )

        return re.search(
            pattern,
            text,
            re.IGNORECASE
        ) is not None

    return keyword.lower() in text.lower()


def find_keyword_match(
    text: str,
    keyword_map: dict
) -> str | None:

    for result, keywords in keyword_map.items():

        for keyword in keywords:

            if contains_keyword(text, keyword):
                return result

    return None


# =========================================================
# AGE EXTRACTION
# RANGE: 0 - 99
# =========================================================

def extract_age(text: str) -> int | None:
    """
    Extract age from natural language.

    Valid:
        0
        19
        43
        99
        I am 25
        I'm 25 years old
        age is 25
        age: 25
        I am 25 years old
        ನನಗೆ 25 ವರ್ಷ

    Invalid:
        -1
        100
        120
    """

    patterns = [

        r"\b(?:i\s+am|i'm|im|age\s+is|aged)\s+(\d{1,3})\b",

        r"\b(\d{1,3})\s*(?:years?\s+old|years?)\b",

        r"\bage\s*[:\-]?\s*(\d{1,3})\b",

        r"ವಯಸ್ಸು\s*[:\-]?\s*(\d{1,3})",

        r"ನನಗೆ\s*(\d{1,3})\s*(?:ವರ್ಷ|ವರ್ಷಗಳು)",

        r"^\s*(\d{1,3})\s*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            age = int(match.group(1))

            if 0 <= age <= 99:
                return age

    return None


# =========================================================
# INCOME EXTRACTION
# RANGE: 0 - 500000
# =========================================================

def extract_income(text: str):
    """
    Accept any annual income from 0 to 5,00,000.
    Currency symbols/prefixes are optional.
    """

    text_lower = text.lower().strip()

    # Remove common currency words/symbols
    cleaned = re.sub(
        r"(?:₹|rs\.?|inr|rupees)",
        "",
        text_lower
    ).strip()

    # Remove commas
    cleaned = cleaned.replace(",", "")

    # Find a number, including decimal numbers
    match = re.search(r"\b\d+(?:\.\d+)?\b", cleaned)

    if not match:
        return None

    try:
        income = float(match.group())
    except ValueError:
        return None

    # Accept ANY number from 0 to 5 lakh
    if 0 <= income <= 500000:
        return int(income)

    return None


# =========================================================
# NAME EXTRACTION
# =========================================================

def extract_name(text: str) -> str:
    """
    Extract a person's name.

    IMPORTANT:
    There is NO predefined list of names.

    Therefore names such as:

        Arif
        Rahul
        Nirek
        Nirek Jain
        Abdul Rahman
        Muhammad Arif
        John Smith
        A Kumar

    can all be accepted.

    It also supports:

        My name is Arif
        My name is Abdul Rahman
        Name: Nirek Jain
        I am Arif
        I'm Rahul
        Call me Arif

    A short standalone response is treated as a name.
    This is especially important when the AI has just asked:
        "What is your name?"
    """

    cleaned = text.strip()

    if not cleaned:
        return ""

    # -----------------------------------------------------
    # EXPLICIT NAME STATEMENTS
    # -----------------------------------------------------

    explicit_patterns = [

        r"^\s*my\s+name\s+is\s+(.+?)\s*[.!?,]?\s*$",

        r"^\s*my\s+name's\s+(.+?)\s*[.!?,]?\s*$",

        r"^\s*name\s*(?:is|:)\s*(.+?)\s*[.!?,]?\s*$",

        r"^\s*call\s+me\s+(.+?)\s*[.!?,]?\s*$",

        # I am Arif
        # Do NOT match "I am a farmer" here because of the
        # explicit article check.
        r"^\s*i\s+am\s+([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ.'-]*(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ.'-]*){0,3})\s*[.!?,]?\s*$",

        r"^\s*i'm\s+([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ.'-]*(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ.'-]*){0,3})\s*[.!?,]?\s*$",

        # Kannada
        r"^\s*ನನ್ನ\s+ಹೆಸರು\s+([^\.\n,!?]+)\s*$",

        r"^\s*ಹೆಸರು\s*[:\-]\s*([^\.\n,!?]+)\s*$",
    ]

    for pattern in explicit_patterns:

        match = re.match(
            pattern,
            cleaned,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            # "I am a farmer" must NOT become "a farmer"
            if name.lower().startswith(
                ("a ", "an ")
            ):
                continue

            if name:
                return name

    # -----------------------------------------------------
    # STANDALONE NAME
    # -----------------------------------------------------
    #
    # This is the important part for your situation.
    #
    # User:
    #     Arif
    #
    # becomes:
    #     name = "Arif"
    #
    # There is NO name database.
    # -----------------------------------------------------

    # Remove only trailing punctuation
    standalone = re.sub(
        r"[.!?,]+$",
        "",
        cleaned
    ).strip()

    # A standalone name can contain up to 5 words.
    if 1 <= len(standalone.split()) <= 5:

        # Accept alphabetic names, spaces, apostrophes,
        # hyphens and accented Latin characters.
        if re.fullmatch(
            r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ.'\-]*(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ.'\-]*){0,4}",
            standalone
        ):

            # Do not treat obvious conversational answers
            # as names.
            blocked = {
                "yes",
                "no",
                "okay",
                "ok",
                "yeah",
                "yep",
                "nope",
                "sure",
                "thanks",
                "thank you",
                "hello",
                "hi",
            }

            if standalone.lower() not in blocked:
                return standalone

    return ""


# =========================================================
# FREE-FORM OCCUPATION EXTRACTION
# =========================================================

def extract_occupation(text: str) -> str | None:
    """
    Extract ANY occupation instead of using a fixed list.

    Examples:

        I am a farmer
        I am a software engineer
        I work as a driver
        I am a nurse
        I am a shopkeeper
        I run a grocery shop
        I am unemployed
        My occupation is teacher
    """

    patterns = [

        # I am a farmer
        # I am a software engineer
        r"\b(?:i\s+am|i'm|im)\s+(?:an?\s+)"
        r"([A-Za-z][A-Za-z\s\-]{1,60}?)"
        r"(?=\s+(?:and|from|in|with|aged|age|my|i)\b|[.,!?]|$)",

        # I work as a software engineer
        r"\b(?:i\s+)?work\s+as\s+(?:an?\s+)"
        r"([A-Za-z][A-Za-z\s\-]{1,60}?)"
        r"(?=\s+(?:and|from|in|with|my|i)\b|[.,!?]|$)",

        # My occupation is teacher
        r"\boccupation\s*(?:is|:)\s*"
        r"([A-Za-z][A-Za-z\s\-]{1,60}?)"
        r"(?=[.,!?]|$)",

        # I am employed as a teacher
        r"\bemployed\s+as\s+(?:an?\s+)"
        r"([A-Za-z][A-Za-z\s\-]{1,60}?)"
        r"(?=[.,!?]|$)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            occupation = match.group(1).strip()

            occupation = re.sub(
                r"\s+(?:and\s+i\s+am|and\s+i|and)\s*$",
                "",
                occupation,
                flags=re.IGNORECASE
            ).strip()

            if occupation:

                if not re.fullmatch(
                    r"\d+(?:\s+years?)?",
                    occupation,
                    re.IGNORECASE
                ):
                    return occupation

    return None


# =========================================================
# FREE-FORM PROBLEM EXTRACTION
# =========================================================

def extract_problem(text: str) -> str | None:
    """
    Extract a free-form problem.

    There is NO fixed problem category restriction.
    """

    cleaned = text.strip()

    if not cleaned:
        return None

    patterns = [

        r"\b(?:my\s+)?(?:problem|issue|difficulty|need|requirement)"
        r"\s*(?:is|:)?\s*(.+)$",

        r"\bi\s+(?:need|require|want|am\s+looking\s+for)"
        r"\s+(.+)$",

        r"\bi\s+(?:lost|have|had|faced|face|suffered|suffer)"
        r"\s+(.+)$",

        r"\b(?:my|our)\s+(.+?)"
        r"\s+(?:was|were|is|are|has|have)\s+"
        r"(?:damaged|destroyed|affected|lost).*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            cleaned,
            re.IGNORECASE
        )

        if match:

            problem = match.group(1).strip()

            if problem:
                return problem

    problem_indicators = [
        "damaged",
        "damage",
        "destroyed",
        "destroy",
        "lost",
        "loss",
        "problem",
        "issue",
        "difficulty",
        "emergency",
        "support",
        "assistance",
        "help",
        "affected",
        "suffering",
        "need",
        "ನಷ್ಟ",
        "ಹಾನಿ",
        "ಸಮಸ್ಯೆ",
        "ಸಹಾಯ",
        "ಅಗತ್ಯ",
    ]

    lowered = cleaned.lower()

    if any(
        indicator.lower() in lowered
        for indicator in problem_indicators
    ):
        return cleaned

    return None


# =========================================================
# ADDITIONAL DETAILS
# =========================================================

def extract_additional_details(
    text: str
) -> dict[str, Any]:

    details: dict[str, Any] = {}

    cause_keywords = {

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

    cause = find_keyword_match(
        text,
        cause_keywords
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
    Convert a citizen message into the shared
    CitizenProfile structure.

    Requirements:

    - Age: 0-99
    - Income: 0-500000
    - Occupation: free-form
    - State: Karnataka / Maharashtra / Kerala
    - District: all districts in those states
    - Problem: free-form
    - Name: any reasonable name
    - Shared profile JSON remains unchanged
    """

    occupation = extract_occupation(text)

    problem = extract_problem(text)

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