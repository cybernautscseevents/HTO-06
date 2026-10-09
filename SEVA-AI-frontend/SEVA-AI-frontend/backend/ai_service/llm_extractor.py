import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()


# ---------------------------------------------------------
# EXTRA DETAILS
# ---------------------------------------------------------

class ExtraDetail(BaseModel):
    key: str
    value: str


# ---------------------------------------------------------
# FULL PROFILE EXTRACTION
# ---------------------------------------------------------

class ProfileExtraction(BaseModel):
    name: Optional[str] = Field(
        default=None
    )

    gender: Optional[str] = Field(
        default=None
    )

    age: Optional[int] = Field(
        default=None
    )

    income: Optional[float] = Field(
        default=None
    )

    occupation: Optional[str] = Field(
        default=None
    )

    state: Optional[str] = Field(
        default=None
    )

    district: Optional[str] = Field(
        default=None
    )

    category: Optional[str] = Field(
        default=None
    )

    problem: Optional[str] = Field(
        default=None
    )

    additional_details: list[ExtraDetail] = Field(
        default_factory=list
    )


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------------------------------------------------------
# EXTRACT EVERYTHING
# ---------------------------------------------------------

def extract_all_profile_info(
    message: str,
    current_profile: dict,
    expected_field: str | None = None
) -> dict:

    if not message or not message.strip():
        return {
            "name": None,
            "gender": None,
            "age": None,
            "income": None,
            "occupation": None,
            "state": None,
            "district": None,
            "category": None,
            "problem": None,
            "additional_details": {},
        }

    expected_field_text = (
        expected_field
        if expected_field
        else "none"
    )

    prompt = f"""
You are the information-extraction component of SEVA AI,
a government benefits assistant for Indian citizens. Understand
answers in English, Kannada, Tamil, Telugu, Hindi, and Malayalam,
including common Latin-script transliterations of those languages.

Extract EVERY piece of useful information that is explicitly
present in the citizen's CURRENT message.

CURRENT CITIZEN MESSAGE:
{message}

CURRENT PROFILE:
{current_profile}

FIELD CURRENTLY EXPECTED:
{expected_field_text}

RULES:

1. Extract ALL information present in the current message.

2. A single message can contain multiple fields.

3. Do not force the citizen to answer one field at a time.

4. Do not invent information.

5. Do not copy information from the current profile unless
   it is explicitly stated again in the current message.

6. The current profile is provided only for context.

7. If the expected field is age and the citizen says "29",
   interpret it as age.

7a. If the citizen says they are a girl/woman or boy/man,
    extract gender as "Girl" or "Boy". If they prefer not
    to disclose, extract "Prefer not to say".

8. If the expected field is income and the citizen says
   "10000", interpret it as annual income.

9. If the expected field is state and the citizen says
   "Karnataka", interpret it as state.

10. If the expected field is district and the citizen says
    "Mysuru", interpret it as district.

11. If the expected field is category and the citizen says
    "General", interpret it as social category.

12. Occupation is completely open-ended.

13. There is NO predefined occupation list.

14. Accept common, uncommon, specialized, informal,
    self-employed, agricultural, creative, technical,
    online, and emerging occupations.

15. Preserve the most specific occupation reasonably
    supported by the citizen's message.

16. Never replace a specific occupation with a generic one.

17. Understand descriptions of work, not only job titles.

18. For income:
    - remove Rs, INR, rupees and currency symbols
    - accept values from 0 to 500000
    - do not invent income

19. For age:
    - accept values from 0 to 99
    - do not invent age

20. For problem:
    - understand the meaning
    - do not require specific keywords
    - return a short clear description
    - do not decide eligibility

21. State and district are Indian state/union territory and
    district names.

22. Category is free-text.

23. Put useful explicitly stated information that does not
    fit the main fields into additional_details.

23a. For scheme-discovery follow-up questions, store the
     answer in additional_details using the stable key named
     by FIELD CURRENTLY EXPECTED (the part after "follow_up:").
     Stable keys include children_status, children_details,
     ration_card, disability_status, farmer_details,
     education_details, marital_status, and senior_support.
     Preserve explicit ages, family relationships, study,
     land, crop, card, and certificate details. Never infer
     a missing answer. Record an explicit refusal or skip as
     "prefer not to say".

23b. If the citizen volunteers household information before
     being asked, use those same stable keys immediately:
     children_status and children_details, ration_card,
     disability_status, farmer_details, education_details,
     marital_status, or senior_support. Keep the values based
     only on what the citizen explicitly said.

24. If a field is not present in the current message,
    return null for that field.

25. Do not recommend schemes.

26. Do not decide final eligibility.

27. Do not invent government rules.

28. Citizens may answer in Kannada (ಕನ್ನಡ) or English. Understand Kannada
    answers and extract their meaning correctly. Return enum-like values such
    as gender as canonical English values ("Girl", "Boy", or "Prefer not to say").
    Return state and district in canonical English names so location validation
    works. Understand Kannada age and income numbers. Translate category,
    occupation, problem, and additional detail values into
    concise English so scheme matching can use them.

Return only the structured response.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ProfileExtraction,
            ),
        )

        result = ProfileExtraction.model_validate_json(
            response.text
        )

        additional_details = {}

        for item in result.additional_details:
            key = item.key.strip()
            value = item.value.strip()

            if key and value:
                additional_details[key] = value

        return {
            "name": result.name,
            "gender": result.gender,
            "age": result.age,
            "income": result.income,
            "occupation": result.occupation,
            "state": result.state,
            "district": result.district,
            "category": result.category,
            "problem": result.problem,
            "additional_details": additional_details,
        }

    except Exception as error:
        print(
            f"Gemini profile extraction error: {error}"
        )

        return {
            "name": None,
            "gender": None,
            "age": None,
            "income": None,
            "occupation": None,
            "state": None,
            "district": None,
            "category": None,
            "problem": None,
            "additional_details": {},
        }
