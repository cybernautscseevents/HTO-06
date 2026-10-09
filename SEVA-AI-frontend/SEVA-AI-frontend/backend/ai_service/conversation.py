import re

from .models import CitizenProfile
from .llm_extractor import extract_all_profile_info
from .locations import canonical_district, canonical_state


# ---------------------------------------------------------
# REQUIRED PROFILE FIELDS
# ---------------------------------------------------------

REQUIRED_FIELDS = [
    "name",
    "gender",
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

def get_missing_fields(
    profile: CitizenProfile
) -> list[str]:

    missing = []

    for field in REQUIRED_FIELDS:
        value = getattr(profile, field)

        if value is None:
            missing.append(field)

        elif isinstance(value, str) and value.strip() == "":
            missing.append(field)

    return missing


# ---------------------------------------------------------
# VALIDATE EXTRACTED VALUES
# ---------------------------------------------------------

def validate_extracted_value(
    field: str,
    value
):

    if value is None:
        return None

    if field == "age":

        try:
            age = int(value)

            if 0 <= age <= 99:
                return age

            return None

        except (TypeError, ValueError):
            return None

    if field == "income":

        try:
            income = float(value)

            if 0 <= income <= 500000:
                return income

            return None

        except (TypeError, ValueError):
            return None

    if field == "gender":
        normalized = str(value).strip().casefold()
        accepted = {
            "girl": "Girl", "female": "Girl", "woman": "Girl",
            "ಹುಡುಗಿ": "Girl", "ಮಹಿಳೆ": "Girl", "ಹೆಣ್ಣು": "Girl",
            "boy": "Boy", "male": "Boy", "man": "Boy",
            "ಹುಡುಗ": "Boy", "ಪುರುಷ": "Boy", "ಗಂಡು": "Boy",
            "prefer not to say": "Prefer not to say",
            "ಹೇಳಲು ಇಷ್ಟವಿಲ್ಲ": "Prefer not to say",
        }
        return accepted.get(normalized)

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return None

    return value


# ---------------------------------------------------------
# MERGE PROFILES
# ---------------------------------------------------------

def merge_profiles(
    current: CitizenProfile,
    extracted: dict
) -> CitizenProfile:

    fields = [
        "name",
        "gender",
        "age",
        "income",
        "occupation",
        "state",
        "district",
        "category",
        "problem",
    ]

    for field in fields:

        value = extracted.get(field)

        if value is None:
            continue

        value = validate_extracted_value(
            field,
            value
        )

        if value is None:
            continue

        setattr(
            current,
            field,
            value
        )

    # Location values extracted from voice or text must belong
    # to the selected Indian state/union territory.
    normalized_state = canonical_state(current.state)
    current.state = normalized_state or ""
    normalized_district = canonical_district(current.state, current.district)
    current.district = normalized_district or ""

    additional_details = extracted.get(
        "additional_details",
        {}
    )

    if additional_details:
        current.additional_details.update(
            additional_details
        )

    return current


# ---------------------------------------------------------
# FOLLOW-UP QUESTIONS
# ---------------------------------------------------------

QUESTIONS = {
    "name": {
        "english": "What is your name?",
        "kannada": "ನಿಮ್ಮ ಹೆಸರು ಏನು?",
        "tamil": "உங்கள் பெயர் என்ன?",
        "telugu": "మీ పేరు ఏమిటి?",
        "hindi": "आपका नाम क्या है?",
        "malayalam": "നിങ്ങളുടെ പേര് എന്താണ്?",
    },

    "gender": {
        "english": "Are you a girl or a boy? You can also say prefer not to say.",
        "kannada": "ನೀವು ಹುಡುಗಿಯೇ ಅಥವಾ ಹುಡುಗನೇ? ಹೇಳಲು ಇಷ್ಟವಿಲ್ಲ ಎಂದೂ ಹೇಳಬಹುದು.",
        "tamil": "நீங்கள் பெண்ணா அல்லது ஆணா? சொல்ல விருப்பமில்லை என்றும் கூறலாம்.",
        "telugu": "మీరు అమ్మాయా లేదా అబ్బాయా? చెప్పడానికి ఇష్టం లేదని కూడా చెప్పవచ్చు.",
        "hindi": "क्या आप लड़की हैं या लड़के? आप बताना नहीं चाहते, यह भी कह सकते हैं।",
        "malayalam": "നിങ്ങൾ പെൺകുട്ടിയാണോ ആൺകുട്ടിയാണോ? പറയാൻ താൽപര്യമില്ലെന്നും പറയാം.",
    },

    "age": {
        "english": "What is your age?",
        "kannada": "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?",
        "tamil": "உங்கள் வயது என்ன?",
        "telugu": "మీ వయస్సు ఎంత?",
        "hindi": "आपकी उम्र कितनी है?",
        "malayalam": "നിങ്ങളുടെ പ്രായം എത്രയാണ്?",
    },

    "income": {
        "english": "What is your approximate annual income?",
        "kannada": "ನಿಮ್ಮ ಅಂದಾಜು ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು?",
        "tamil": "உங்கள் தோராயமான ஆண்டு வருமானம் எவ்வளவு?",
        "telugu": "మీ అంచనా వార్షిక ఆదాయం ఎంత?",
        "hindi": "आपकी अनुमानित वार्षिक आय कितनी है?",
        "malayalam": "നിങ്ങളുടെ ഏകദേശ വാർഷിക വരുമാനം എത്രയാണ്?",
    },

    "occupation": {
        "english": "What is your occupation?",
        "kannada": "ನಿಮ್ಮ ಉದ್ಯೋಗ ಏನು?",
        "tamil": "உங்கள் தொழில் என்ன?",
        "telugu": "మీ వృత్తి ఏమిటి?",
        "hindi": "आपका व्यवसाय क्या है?",
        "malayalam": "നിങ്ങളുടെ തൊഴിൽ എന്താണ്?",
    },

    "state": {
        "english": "Which state are you from?",
        "kannada": "ನೀವು ಯಾವ ರಾಜ್ಯದವರು?",
        "tamil": "நீங்கள் எந்த மாநிலத்தைச் சேர்ந்தவர்?",
        "telugu": "మీరు ఏ రాష్ట్రానికి చెందినవారు?",
        "hindi": "आप किस राज्य से हैं?",
        "malayalam": "നിങ്ങൾ ഏത് സംസ്ഥാനത്തുനിന്നാണ്?",
    },

    "district": {
        "english": "Which district are you from?",
        "kannada": "ನೀವು ಯಾವ ಜಿಲ್ಲೆಯವರು?",
        "tamil": "நீங்கள் எந்த மாவட்டத்தைச் சேர்ந்தவர்?",
        "telugu": "మీరు ఏ జిల్లాకు చెందినవారు?",
        "hindi": "आप किस ज़िले से हैं?",
        "malayalam": "നിങ്ങൾ ഏത് ജില്ലയിൽ നിന്നാണ്?",
    },

    "category": {
        "english": (
            "What is your social category, such as "
            "SC, ST, OBC or General?"
        ),
        "kannada": (
            "ನಿಮ್ಮ ಸಾಮಾಜಿಕ ವರ್ಗ ಯಾವುದು, ಉದಾಹರಣೆಗೆ "
            "SC, ST, OBC ಅಥವಾ General?"
        ),
        "tamil": "உங்கள் சமூகப் பிரிவு என்ன? உதாரணமாக SC, ST, OBC அல்லது General?",
        "telugu": "మీ సామాజిక వర్గం ఏమిటి? ఉదాహరణకు SC, ST, OBC లేదా General?",
        "hindi": "आपकी सामाजिक श्रेणी क्या है, जैसे SC, ST, OBC या General?",
        "malayalam": "നിങ്ങളുടെ സാമൂഹിക വിഭാഗം ഏതാണ്? ഉദാഹരണത്തിന് SC, ST, OBC അല്ലെങ്കിൽ General?",
    },

    "problem": {
        "english": (
            "Please tell me what problem you need help with."
        ),
        "kannada": (
            "ನಿಮಗೆ ಯಾವ ಸಮಸ್ಯೆಗೆ ಸಹಾಯ ಬೇಕು ಎಂದು ತಿಳಿಸಿ."
        ),
        "tamil": "உங்களுக்கு எந்தப் பிரச்சினைக்கு உதவி தேவை என்பதைச் சொல்லுங்கள்.",
        "telugu": "మీకు ఏ సమస్యకు సహాయం కావాలో చెప్పండి.",
        "hindi": "बताइए, आपको किस समस्या में सहायता चाहिए।",
        "malayalam": "ഏത് പ്രശ്നത്തിനാണ് സഹായം വേണ്ടതെന്ന് പറയൂ.",
    },
}


FOLLOW_UP_QUESTIONS_KANNADA = {
    "children_status": "ನಿಮ್ಮ ಮಕ್ಕಳಿಗೆ ಶಿಕ್ಷಣ ಅಥವಾ ಕುಟುಂಬದ ಬೆಂಬಲ ಬೇಕಾಗಬಹುದೇ? ಇದ್ದರೆ ಎಷ್ಟು ಹೆಣ್ಣು ಮಕ್ಕಳು ಮತ್ತು ಗಂಡು ಮಕ್ಕಳು? ಇಲ್ಲ ಅಥವಾ ಬಿಡಿ ಎಂದು ಹೇಳಬಹುದು.",
    "children_details": "ನಿಮ್ಮ ಮಕ್ಕಳ ವಯಸ್ಸು ಮತ್ತು ಲಿಂಗವೇನು? ಅವರು ಶಾಲೆ ಅಥವಾ ಕಾಲೇಜಿನಲ್ಲಿ ಓದುತ್ತಿದ್ದಾರೆಯೇ? ಕೆಲವು ವಿವರಗಳನ್ನು ಬಿಡಬಹುದು.",
    "ration_card": "ನಿಮ್ಮ ಕುಟುಂಬಕ್ಕೆ ರೇಷನ್ ಕಾರ್ಡ್ ಅಥವಾ BPL/ಅಂತ್ಯೋದಯ ಕಾರ್ಡ್ ಇದೆಯೇ? ಇದ್ದರೆ ಯಾವ ವಿಧ? ಬಿಡಿ ಎಂದೂ ಹೇಳಬಹುದು.",
    "disability_status": "ನಿಮಗೆ ಅಥವಾ ಅವಲಂಬಿತರಿಗೆ ಅಂಗವೈಕಲ್ಯವಿದೆಯೇ? ಅಂಗವೈಕಲ್ಯ ಪ್ರಮಾಣಪತ್ರ ಇದೆಯೇ? ಇಲ್ಲ ಅಥವಾ ಬಿಡಿ ಎಂದು ಹೇಳಬಹುದು.",
    "farmer_details": "ನೀವು ಕೃಷಿ ಭೂಮಿಯನ್ನು ಹೊಂದಿದ್ದೀರಾ, ಗುತ್ತಿಗೆಗೆ ಪಡೆದಿದ್ದೀರಾ ಅಥವಾ ಬೆಳೆಸುತ್ತಿದ್ದೀರಾ? ಬೇಕಿದ್ದರೆ ಅಂದಾಜು ವಿಸ್ತೀರ್ಣ, ಬೆಳೆಗಳು ಮತ್ತು ರೈತರಾಗಿ ನೋಂದಣಿಯ ಬಗ್ಗೆ ತಿಳಿಸಿ. ಬಿಡಬಹುದು.",
    "education_details": "ನೀವು ಯಾವ ತರಗತಿ, ಕೋರ್ಸ್ ಅಥವಾ ಶಿಕ್ಷಣ ಹಂತದಲ್ಲಿ ಓದುತ್ತಿದ್ದೀರಿ? ಸಂಸ್ಥೆ ಸರ್ಕಾರಿ ಅಥವಾ ಖಾಸಗಿಯೇ? ಬಿಡಬಹುದು.",
    "marital_status": "ನೀವು ವಿವಾಹಿತರಾ, ಅವಿವಾಹಿತರಾ, ವಿಧವೆಯಾ ಅಥವಾ ಪ್ರತ್ಯೇಕವಾಗಿ ವಾಸಿಸುತ್ತಿದ್ದೀರಾ? ಈ ಪ್ರಶ್ನೆಯನ್ನು ಬಿಡಬಹುದು.",
    "senior_support": "ನೀವು ಈಗ ಪಿಂಚಣಿ ಅಥವಾ ಹಿರಿಯ ನಾಗರಿಕರ ಸಹಾಯಧನ ಪಡೆಯುತ್ತಿದ್ದೀರಾ? ಇಲ್ಲ ಅಥವಾ ಬಿಡಿ ಎಂದು ಹೇಳಬಹುದು.",
}

FOLLOW_UP_QUESTIONS = {
    "tamil": {
        "children_status": "கல்வி அல்லது குடும்ப உதவி தேவைப்படக்கூடிய குழந்தைகள் உள்ளனரா? இருந்தால், எத்தனை மகள்கள் மற்றும் மகன்கள்? இல்லை அல்லது தவிர்க்கலாம்.",
        "children_details": "உங்கள் குழந்தைகளின் வயது மற்றும் பாலினம் என்ன? அவர்கள் பள்ளி அல்லது கல்லூரியில் படிக்கிறார்களா? விவரங்களைத் தவிர்க்கலாம்.",
        "ration_card": "உங்கள் குடும்பத்திடம் ரேஷன் அட்டை அல்லது BPL/அந்தியோதயா அட்டை உள்ளதா? இருந்தால், எந்த வகை? தவிர்க்கலாம்.",
        "disability_status": "உங்களுக்கோ அல்லது உங்களைச் சார்ந்தவருக்கோ மாற்றுத்திறன் உள்ளதா? மாற்றுத்திறன் சான்றிதழ் உள்ளதா? இல்லை அல்லது தவிர்க்கலாம்.",
        "farmer_details": "உங்களுக்குச் சொந்தமாக, குத்தகைக்கு அல்லது பயிரிடும் விவசாய நிலம் உள்ளதா? விருப்பமிருந்தால் பரப்பளவு, பயிர்கள் மற்றும் விவசாயி பதிவைப் பகிரலாம். தவிர்க்கலாம்.",
        "education_details": "நீங்கள் எந்த வகுப்பு, படிப்பு அல்லது கல்வி நிலையில் இருக்கிறீர்கள்? கல்வி நிறுவனம் அரசு அல்லது தனியாரா? தவிர்க்கலாம்.",
        "marital_status": "நீங்கள் திருமணமானவரா, திருமணமாகாதவரா, விதவையா அல்லது பிரிந்தவரா? இந்தக் கேள்வியைத் தவிர்க்கலாம்.",
        "senior_support": "நீங்கள் தற்போது ஓய்வூதியம் அல்லது மூத்த குடிமக்கள் உதவி பெறுகிறீர்களா? இல்லை அல்லது தவிர்க்கலாம்.",
    },
    "telugu": {
        "children_status": "విద్య లేదా కుటుంబ సహాయం అవసరమయ్యే పిల్లలు ఉన్నారా? ఉంటే, ఎంతమంది కుమార్తెలు, కుమారులు? లేరు అని చెప్పవచ్చు లేదా వదిలేయవచ్చు.",
        "children_details": "మీ పిల్లల వయస్సులు, లింగాలు ఏమిటి? వారు పాఠశాల లేదా కళాశాలలో చదువుతున్నారా? వివరాలను వదిలేయవచ్చు.",
        "ration_card": "మీ కుటుంబానికి రేషన్ కార్డు లేదా BPL/అంత్యోదయ కార్డు ఉందా? ఉంటే, ఏ రకం? వదిలేయవచ్చు.",
        "disability_status": "మీకు లేదా మీపై ఆధారపడిన వారికి వైకల్యం ఉందా? వైకల్య ధృవీకరణ పత్రం ఉందా? లేదు అని చెప్పవచ్చు లేదా వదిలేయవచ్చు.",
        "farmer_details": "మీకు వ్యవసాయ భూమి ఉందా, కౌలుకు తీసుకున్నారా లేదా సాగు చేస్తున్నారా? కావాలంటే విస్తీర్ణం, పంటలు, రైతుగా నమోదు వివరాలు చెప్పండి. వదిలేయవచ్చు.",
        "education_details": "మీరు ఏ తరగతి, కోర్సు లేదా విద్యా స్థాయిలో చదువుతున్నారు? విద్యాసంస్థ ప్రభుత్వమా లేదా ప్రైవేటా? వదిలేయవచ్చు.",
        "marital_status": "మీరు వివాహితులా, అవివాహితులా, విధవరాలా/విధురుడా లేదా విడిగా ఉంటున్నారా? ఈ ప్రశ్నను వదిలేయవచ్చు.",
        "senior_support": "మీరు ప్రస్తుతం పింఛను లేదా వృద్ధుల సహాయం పొందుతున్నారా? లేదు అని చెప్పవచ్చు లేదా వదిలేయవచ్చు.",
    },
    "hindi": {
        "children_status": "क्या आपके बच्चे हैं जिन्हें शिक्षा या परिवार संबंधी सहायता की ज़रूरत हो सकती है? यदि हाँ, तो कितनी बेटियाँ और बेटे? नहीं कह सकते हैं या छोड़ सकते हैं।",
        "children_details": "आपके बच्चों की उम्र और लिंग क्या है? क्या वे स्कूल या कॉलेज में पढ़ते हैं? कोई भी जानकारी छोड़ सकते हैं।",
        "ration_card": "क्या आपके परिवार के पास राशन कार्ड या BPL/अंत्योदय कार्ड है? यदि हाँ, तो किस प्रकार का? छोड़ सकते हैं।",
        "disability_status": "क्या आपको या आप पर निर्भर किसी व्यक्ति को दिव्यांगता है? क्या दिव्यांगता प्रमाणपत्र है? नहीं कह सकते हैं या छोड़ सकते हैं।",
        "farmer_details": "क्या आपके पास खेती की ज़मीन है, आप उसे पट्टे पर लेते हैं या खेती करते हैं? चाहें तो क्षेत्रफल, फसलें और किसान पंजीकरण बताएँ। छोड़ सकते हैं।",
        "education_details": "आप किस कक्षा, पाठ्यक्रम या शिक्षा स्तर में पढ़ रहे हैं? संस्थान सरकारी है या निजी? छोड़ सकते हैं।",
        "marital_status": "क्या आप विवाहित, अविवाहित, विधवा/विधुर या अलग रह रहे हैं? इस प्रश्न को छोड़ सकते हैं।",
        "senior_support": "क्या आपको अभी पेंशन या वरिष्ठ नागरिक सहायता मिलती है? नहीं कह सकते हैं या छोड़ सकते हैं।",
    },
    "malayalam": {
        "children_status": "വിദ്യാഭ്യാസത്തിനോ കുടുംബസഹായത്തിനോ പിന്തുണ വേണ്ട കുട്ടികളുണ്ടോ? ഉണ്ടെങ്കിൽ എത്ര പെൺമക്കളും ആൺമക്കളും? ഇല്ലെന്നോ ഒഴിവാക്കാമെന്നോ പറയാം.",
        "children_details": "നിങ്ങളുടെ കുട്ടികളുടെ പ്രായവും ലിംഗവും എന്താണ്? അവർ സ്കൂളിലോ കോളേജിലോ പഠിക്കുന്നുണ്ടോ? വിവരങ്ങൾ ഒഴിവാക്കാം.",
        "ration_card": "നിങ്ങളുടെ കുടുംബത്തിന് റേഷൻ കാർഡോ BPL/അന്ത്യോദയ കാർഡോ ഉണ്ടോ? ഉണ്ടെങ്കിൽ ഏത് തരം? ഒഴിവാക്കാം.",
        "disability_status": "നിങ്ങൾക്കോ ആശ്രിതർക്കോ ഭിന്നശേഷിയുണ്ടോ? ഭിന്നശേഷി സർട്ടിഫിക്കറ്റ് ഉണ്ടോ? ഇല്ലെന്നോ ഒഴിവാക്കാമെന്നോ പറയാം.",
        "farmer_details": "നിങ്ങൾക്ക് കൃഷിഭൂമിയുണ്ടോ, പാട്ടത്തിനെടുത്തിട്ടുണ്ടോ, കൃഷി ചെയ്യുന്നുണ്ടോ? വേണമെങ്കിൽ വിസ്തീർണം, വിളകൾ, കർഷക രജിസ്ട്രേഷൻ എന്നിവ പറയാം. ഒഴിവാക്കാം.",
        "education_details": "നിങ്ങൾ ഏത് ക്ലാസിലോ കോഴ്സിലോ വിദ്യാഭ്യാസ തലത്തിലോ പഠിക്കുന്നു? സ്ഥാപനം സർക്കാർ അല്ലെങ്കിൽ സ്വകാര്യ സ്ഥാപനമാണോ? ഒഴിവാക്കാം.",
        "marital_status": "നിങ്ങൾ വിവാഹിതനോ അവിവാഹിതനോ വിധവയോ വേർപിരിഞ്ഞ് കഴിയുന്നയാളോ? ഈ ചോദ്യം ഒഴിവാക്കാം.",
        "senior_support": "നിങ്ങൾക്ക് ഇപ്പോൾ പെൻഷനോ മുതിർന്ന പൗരന്മാർക്കുള്ള സഹായമോ ലഭിക്കുന്നുണ്ടോ? ഇല്ലെന്നോ ഒഴിവാക്കാമെന്നോ പറയാം.",
    },
}


def get_next_follow_up(profile: CitizenProfile) -> dict | None:
    """Return the next unanswered scheme-discovery question."""
    details = profile.additional_details or {}

    def answered(key: str) -> bool:
        return bool(str(details.get(key, "")).strip())

    if not answered("children_status"):
        return {
            "key": "children_status",
            "question": (
                "Do you have children who may need education or family support? "
                "If yes, how many daughters and sons? You can say no or skip."
            ),
        }

    children_status = str(details.get("children_status", "")).casefold()
    has_children = any(word in children_status for word in (
        "yes", "daughter", "son", "child", "children", "மகள்", "மகன்", "குழந்தை", "குழந்தைகள்",
        "కుమార్తె", "కుమారుడు", "పిల్ల", "పిల్లలు", "बेटी", "बेटा", "बच्चा", "बच्चे",
        "മകൾ", "മകൻ", "കുട്ടി", "കുട്ടികൾ", "ಮಕ್ಕಳು", "ಮಗಳು", "ಮಗ",
    ))
    no_children = any(word in children_status for word in (
        "no", "none", "prefer not", "skip", "இல்லை", "வேண்டாம்", "వద్దు", "లేరు", "లేదు",
        "नहीं", "कोई नहीं", "ഇല്ല", "വേണ്ട", "ഒഴിവാക്കാം", "ಇಲ್ಲ", "ಬೇಡ", "ಬಿಡಿ",
    ))
    if has_children and not no_children and not answered("children_details"):
        return {
            "key": "children_details",
            "question": (
                "What are your children's ages and genders, and are they in school or college? "
                "You can skip any detail."
            ),
        }

    for key, question in (
        (
            "ration_card",
            "Does your household have a ration card or BPL/Antyodaya card? If yes, what type? You can skip.",
        ),
        (
            "disability_status",
            "Do you or a dependent have a disability, and is there a disability certificate? You can say no or skip.",
        ),
    ):
        if not answered(key):
            return {"key": key, "question": question}

    occupation = profile.occupation.casefold()
    problem = profile.problem.casefold()
    is_farmer = any(term in occupation or term in problem for term in ("farm", "agricultur", "crop", "cultivat", "ರೈತ", "ಕೃಷಿ", "ಬೆಳೆ"))
    if is_farmer and not answered("farmer_details"):
        return {
            "key": "farmer_details",
            "question": (
                "Do you own, lease, or cultivate farmland? If relevant, share the approximate area, "
                "main crops, and whether you are registered as a farmer. You can skip."
            ),
        }

    is_student = any(term in occupation or term in problem for term in ("student", "school", "college", "education", "scholarship", "ವಿದ್ಯಾರ್ಥಿ", "ಶಾಲೆ", "ಕಾಲೇಜು", "ಶಿಕ್ಷಣ"))
    if is_student and not answered("education_details"):
        return {
            "key": "education_details",
            "question": (
                "What class, course, or level of study are you enrolled in, and is the institution "
                "government or private? You can skip."
            ),
        }

    if profile.gender == "Girl" and profile.age is not None and profile.age >= 18 and not answered("marital_status"):
        return {
            "key": "marital_status",
            "question": "Are you married, unmarried, widowed, or separated? You can skip this question.",
        }

    if profile.age is not None and profile.age >= 60 and not answered("senior_support"):
        return {
            "key": "senior_support",
            "question": "Do you currently receive a pension or senior-citizen support? You can say no or skip.",
        }

    return None


def capture_expected_follow_up(extracted: dict, message: str, expected_field: str | None) -> None:
    if not expected_field or not expected_field.startswith("follow_up:"):
        return

    key = expected_field.split(":", 1)[1]
    details = extracted.setdefault("additional_details", {})
    text = message.strip()
    normalized = text.casefold()

    if key == "children_status":
        no_children = normalized.strip() in {
            "no", "none", "nope", "not applicable", "இல்லை", "வேண்டாம்", "లేరు", "లేదు", "नहीं", "कोई नहीं", "ഇല്ല", "വേണ്ട", "ಇಲ್ಲ", "ಬೇಡ", "ಯಾರೂ ಇಲ್ಲ"
        } or any(
            phrase in normalized for phrase in (
                "ಮಕ್ಕಳು ಇಲ್ಲ", "ಮಕ್ಕಳಿಲ್ಲ", "ಮಗಳು ಇಲ್ಲ", "ಮಗ ಇಲ್ಲ", "குழந்தைகள் இல்லை", "குழந்தை இல்லை",
                "పిల్లలు లేరు", "పిల్లలు లేవు", "बच्चे नहीं", "बच्चा नहीं", "കുട്ടികളില്ല", "കുട്ടികൾ ഇല്ല",
            )
        ) or re.search(
            r"\b(no|don't|do not|without)\s+(have\s+)?(any\s+)?(children|child|daughter|son|kids)\b",
            normalized,
        )
        if no_children:
            details[key] = "no"
            return
        if "skip" in normalized or "prefer not" in normalized or any(word in normalized for word in (
            "ಹೇಳಲು ಇಷ್ಟವಿಲ್ಲ", "ಬಿಡಿ", "ಬಿಟ್ಟುಬಿಡಿ", "தவிர்க்க", "விருப்பமில்லை", "వదిలేయ", "చెప్పడానికి ఇష్టం లేదు", "छोड़", "नहीं बताना", "ഒഴിവാക്ക", "താൽപര്യമില്ല"
        )):
            details[key] = "prefer not to say"
            return
        details[key] = "yes" if any(word in normalized for word in (
            "yes", "daughter", "son", "child", "children", "kids", "હા", "ஆம்", "ஆமாம்", "ఉన్నారు", "అవును", "हाँ", "ഉണ്ട്", "അതെ", "ಹೌದು", "ಮಕ್ಕಳು", "மகள்", "குழந்தை", "పిల్ల", "బిడ్డ", "बच्चे", "മകൾ", "കുട്ടി"
        )) else text
        if re.search(r"\b\d{1,2}\b|\b(one|two|three|four|five|six|seven|eight|nine|ten)\b|school|college|studying|class|aged?\s+\d", normalized):
            details["children_details"] = text
        return

    details[key] = "prefer not to say" if "skip" in normalized or "prefer not" in normalized or "ಬಿಡಿ" in normalized else text


# ---------------------------------------------------------
# LANGUAGE DETECTION
# ---------------------------------------------------------

def detect_language(text: str) -> str:

    for character in text:

        codepoint = ord(character)
        if 0x0C80 <= codepoint <= 0x0CFF:
            return "kannada"
        if 0x0B80 <= codepoint <= 0x0BFF:
            return "tamil"
        if 0x0C00 <= codepoint <= 0x0C7F:
            return "telugu"
        if 0x0900 <= codepoint <= 0x097F:
            return "hindi"
        if 0x0D00 <= codepoint <= 0x0D7F:
            return "malayalam"

    return "english"


# ---------------------------------------------------------
# NEXT QUESTION
# ---------------------------------------------------------

def get_next_question(
    profile: CitizenProfile,
    language: str
) -> str | None:

    missing = get_missing_fields(
        profile
    )

    if not missing:
        return None

    field = missing[0]

    return QUESTIONS[field][language]


# ---------------------------------------------------------
# PROCESS MESSAGE
# ---------------------------------------------------------

def process_message(
    message: str,
    current_profile: CitizenProfile,
    preferred_language: str | None = None,
) -> dict:

    supported_languages = {"english", "kannada", "tamil", "telugu", "hindi", "malayalam"}
    language = preferred_language if preferred_language in supported_languages else detect_language(message)

    # Determine what is currently missing.
    missing_before = get_missing_fields(
        current_profile
    )

    current_follow_up = (
        get_next_follow_up(current_profile)
        if not missing_before
        else None
    )
    if missing_before:
        expected_field = missing_before[0]
    elif current_follow_up:
        expected_field = f"follow_up:{current_follow_up['key']}"
    else:
        expected_field = None

    # ---------------------------------------------------------
    # GEMINI EXTRACTS EVERYTHING
    # ---------------------------------------------------------

    extracted_data = extract_all_profile_info(
        message=message,
        current_profile=current_profile.model_dump(),
        expected_field=expected_field,
    )

    capture_expected_follow_up(
        extracted_data,
        message,
        expected_field,
    )

    # ---------------------------------------------------------
    # MERGE INFORMATION
    # ---------------------------------------------------------

    updated_profile = merge_profiles(
        current=current_profile,
        extracted=extracted_data,
    )

    # ---------------------------------------------------------
    # FIND WHAT IS STILL MISSING
    # ---------------------------------------------------------

    missing_fields = get_missing_fields(
        updated_profile
    )

    next_question = get_next_question(
        updated_profile,
        language
    )

    follow_up = (
        get_next_follow_up(updated_profile)
        if not missing_fields
        else None
    )

    if not next_question and follow_up:
        follow_up_question = follow_up["question"]
        if language == "kannada":
            follow_up_question = FOLLOW_UP_QUESTIONS_KANNADA.get(follow_up["key"], follow_up_question)
        elif language in FOLLOW_UP_QUESTIONS:
            follow_up_question = FOLLOW_UP_QUESTIONS[language].get(follow_up["key"], follow_up_question)
        intro = {
            "kannada": "ನಿಮ್ಮ ಕುಟುಂಬಕ್ಕೆ ಹೊಂದುವ ಇನ್ನಷ್ಟು ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಲು ಕೆಲವು ಐಚ್ಛಿಕ ಪ್ರಶ್ನೆಗಳಿವೆ. ಯಾವುದೇ ಪ್ರಶ್ನೆಯನ್ನು ಬಿಡಬಹುದು. ",
            "tamil": "உங்கள் குடும்பத்திற்குப் பொருத்தமான திட்டங்களைக் கண்டறிய சில விருப்பக் கேள்விகள் உள்ளன. எதையும் தவிர்க்கலாம். ",
            "telugu": "మీ కుటుంబానికి సరిపోయే పథకాలను కనుగొనడానికి కొన్ని ఐచ్ఛిక ప్రశ్నలు ఉన్నాయి. దేనినైనా వదిలేయవచ్చు. ",
            "hindi": "आपके परिवार के लिए उपयुक्त योजनाएँ खोजने हेतु कुछ वैकल्पिक प्रश्न हैं। आप कोई भी प्रश्न छोड़ सकते हैं। ",
            "malayalam": "നിങ്ങളുടെ കുടുംബത്തിന് അനുയോജ്യമായ പദ്ധതികൾ കണ്ടെത്താൻ ചില ഐച്ഛിക ചോദ്യങ്ങളുണ്ട്. ഏതും ഒഴിവാക്കാം. ",
        }.get(language, "To find more schemes that may fit your household, I have a few optional questions. You can skip any question. ")
        next_question = (
            intro
            + follow_up_question
        )
        missing_fields.append("follow_up")

    # ---------------------------------------------------------
    # GENERATE RESPONSE
    # ---------------------------------------------------------

    if next_question:

        acknowledgement = {
            "kannada": "ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ. ",
            "tamil": "உங்கள் தகவலைப் புரிந்துகொண்டேன். ",
            "telugu": "మీ సమాచారాన్ని అర్థం చేసుకున్నాను. ",
            "hindi": "मैंने आपकी जानकारी समझ ली है। ",
            "malayalam": "നിങ്ങളുടെ വിവരം മനസ്സിലാക്കി. ",
        }.get(language, "I have understood the information. ")
        reply = acknowledgement + next_question

    else:

        reply = {
            "kannada": "ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸಂಗ್ರಹಿಸಲಾಗಿದೆ.",
            "tamil": "உங்கள் தகவல்கள் வெற்றிகரமாகச் சேகரிக்கப்பட்டன.",
            "telugu": "మీ సమాచారం విజయవంతంగా సేకరించబడింది.",
            "hindi": "आपकी जानकारी सफलतापूर्वक एकत्र की गई है।",
            "malayalam": "നിങ്ങളുടെ വിവരങ്ങൾ വിജയകരമായി ശേഖരിച്ചു.",
        }.get(language, "Your information has been successfully collected.")

    return {
        "reply": reply,
        "profile": updated_profile.model_dump(),
        "missing_fields": missing_fields,
        "next_question": next_question,
        "language": language,
    }
