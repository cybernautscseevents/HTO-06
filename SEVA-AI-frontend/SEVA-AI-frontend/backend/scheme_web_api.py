import os
from typing import Literal

import requests
from dotenv import load_dotenv
from fastapi import APIRouter
from google import genai
from google.genai import types
from pydantic import BaseModel


load_dotenv()

router = APIRouter()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ---------------------------------------------------------
# STRUCTURED GEMINI OUTPUT
# ---------------------------------------------------------

class DocumentRequirement(BaseModel):
    name: str
    display_name_kannada: str = ""
    action: Literal[
        "upload",
        "provide_information",
        "conditional"
    ]
    exact_description: str
    condition: str


class SchemeAnalysis(BaseModel):
    scheme_name: str
    scheme_name_kannada: str = ""
    source_index: int

    benefits: list[str]
    eligibility_requirements: list[str]

    document_requirements: list[
        DocumentRequirement
    ]

    eligibility_status: Literal[
        "eligible",
        "not_eligible",
        "needs_verification"
    ]

    matched_conditions: list[str]
    failed_conditions: list[str]
    verification_notes: list[str]


class SchemeAnalysisResponse(BaseModel):
    schemes: list[SchemeAnalysis]


# ---------------------------------------------------------
# OFFICIAL GOVERNMENT DOMAINS
# ---------------------------------------------------------

STATE_DOMAINS = {
    "karnataka": [
        "karnataka.gov.in",
        "myscheme.gov.in",
        "india.gov.in",
        "pmfby.gov.in",
    ],

    "kerala": [
        "kerala.gov.in",
        "myscheme.gov.in",
        "india.gov.in",
    ],

    "maharashtra": [
        "maharashtra.gov.in",
        "myscheme.gov.in",
        "india.gov.in",
    ],
}


# ---------------------------------------------------------
# HISTORICAL / BLOCKED SCHEMES
# ---------------------------------------------------------

BLOCKED_HISTORICAL_SCHEMES = {
    "national agricultural insurance scheme",
    "national agriculture insurance scheme",
    "modified national agricultural insurance scheme",
    "nais",
    "mnais",
}


def normalize_text(value: str) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def is_blocked_historical_result(
    result: dict
) -> bool:
    """
    Remove a search result when the result itself appears
    to be about NAIS/MNAIS as a historical scheme.

    Do NOT remove a current page merely because it mentions
    NAIS as something that was replaced.
    """

    title = normalize_text(
        result.get("title", "")
    )

    url = normalize_text(
        result.get("url", "")
    )

    content = normalize_text(
        result.get("content", "")
    )

    # Strong title matches
    if title in BLOCKED_HISTORICAL_SCHEMES:
        return True

    if (
        "national agricultural insurance scheme"
        in title
    ):
        return True

    if (
        "national agriculture insurance scheme"
        in title
    ):
        return True

    # Obvious old NAIS URLs
    if "/nais" in url or "nais/" in url:
        return True

    # If the title clearly names NAIS/MNAIS,
    # treat it as historical.
    title_has_nais = (
        title == "nais"
        or title.startswith("nais ")
        or " nais " in f" {title} "
        or title == "mnais"
        or title.startswith("mnais ")
        or " mnais " in f" {title} "
    )

    if title_has_nais:
        return True

    # Some old pages may not have a clean title.
    # Only block them when the content is strongly identified
    # as an NAIS/MNAIS scheme itself.
    historical_phrases = [
        "national agricultural insurance scheme",
        "national agriculture insurance scheme",
        "modified national agricultural insurance scheme",
    ]

    mentions_historical_name = any(
        phrase in content
        for phrase in historical_phrases
    )

    mentions_current_successor = (
        "pradhan mantri fasal bima yojana" in content
        or "pmfby" in content
    )

    # If a result is clearly an old standalone NAIS page,
    # block it. If a current PMFBY page merely mentions NAIS
    # as its predecessor, keep it.
    if mentions_historical_name and not mentions_current_successor:
        return True

    return False


# ---------------------------------------------------------
# TAVILY SEARCH
# ---------------------------------------------------------

def tavily_search(
    query: str,
    domains: list[str],
    max_results: int = 5
) -> list[dict]:

    if not TAVILY_API_KEY:
        raise RuntimeError(
            "TAVILY_API_KEY is not configured."
        )

    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Authorization": (
                f"Bearer {TAVILY_API_KEY}"
            ),
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_domains": domains,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])


# ---------------------------------------------------------
# BUILD SEARCH QUERIES
# ---------------------------------------------------------

def build_queries(profile: dict) -> list[str]:

    state = str(
        profile.get("state", "")
    ).strip()

    district = str(
        profile.get("district", "")
    ).strip()

    occupation = str(
        profile.get("occupation", "")
    ).strip()

    problem = str(
        profile.get("problem", "")
    ).strip()

    category = str(
        profile.get("category", "")
    ).strip()

    income = profile.get("income")
    additional_details = profile.get("additional_details") or {}
    priority_queries = []

    def provided(key: str) -> str:
        return str(additional_details.get(key, "")).strip()

    def affirmative(key: str) -> bool:
        value = provided(key).casefold()
        negative = value.startswith(("no", "none", "prefer not", "skip", "don't", "do not"))
        negative = negative or "don't have" in value or "do not have" in value
        negative = negative or any(term in value for term in ("ಇಲ್ಲ", "ಬೇಡ", "ಬಿಡಿ", "ಹೇಳಲು ಇಷ್ಟವಿಲ್ಲ"))
        return bool(value) and not negative

    queries = [
        (
            f"{problem} {occupation} {state} "
            f"government scheme eligibility benefits documents "
            f"latest official 2026"
        ),

        (
            f"{occupation} {problem} {state} {district} "
            f"government assistance scheme eligibility "
            f"myScheme official current 2026"
        ),

        (
            f"{problem} {occupation} {state} "
            f"government scheme application requirements "
            f"documents official current"
        ),
    ]

    if category:
        queries.append(
            (
                f"{occupation} {problem} {state} "
                f"{category} government scheme eligibility "
                f"official current 2026"
            )
        )

    if income is not None:
        queries.append(
            (
                f"{occupation} {problem} {state} "
                f"income {income} scheme eligibility "
                f"official government current 2026"
            )
        )

    # Explicit current crop-insurance search for farmer/crop cases.
    if (
        "farmer" in occupation.lower()
        or "agriculture" in occupation.lower()
        or "crop" in problem.lower()
        or "farm" in problem.lower()
    ):
        priority_queries.append(
            (
                f"PMFBY crop insurance {state} "
                f"{district} farmer current 2026 "
                f"official government"
            )
        )

    # Use the household facts gathered during the optional interview to
    # broaden discovery without putting names, exact ages, or raw answers
    # into third-party search queries.
    children = " ".join((provided("children_status"), provided("children_details"))).casefold()
    if affirmative("children_status") or provided("children_details"):
        child_topic = "girl child" if any(term in children for term in ("daughter", "girl", "ಮಗಳು", "ಹೆಣ್ಣು")) else "child and student"
        priority_queries.append(
            f"{child_topic} education family support schemes {state} official government"
        )

    if affirmative("ration_card"):
        priority_queries.append(
            f"ration card household welfare benefits {state} official government"
        )

    if affirmative("disability_status"):
        priority_queries.append(
            f"disability pension education support benefits {state} official government"
        )

    if provided("farmer_details"):
        priority_queries.append(
            f"farmer landholder crop support schemes {state} {district} official government"
        )

    if provided("education_details"):
        priority_queries.append(
            f"student scholarship education assistance {state} official government"
        )

    if any(term in provided("marital_status").casefold() for term in ("widow", "separated")):
        priority_queries.append(
            f"women widow pension support schemes {state} official government"
        )

    if provided("senior_support"):
        priority_queries.append(
            f"senior citizen pension support schemes {state} official government"
        )

    return priority_queries + queries


# ---------------------------------------------------------
# ANALYZE SEARCH RESULTS WITH GEMINI
# ---------------------------------------------------------

def analyze_schemes(
    profile: dict,
    search_results: list[dict],
    language: str = "english",
) -> list[dict]:

    if not search_results:
        return []

    source_blocks = []

    for index, result in enumerate(
        search_results,
        start=1
    ):

        source_blocks.append(
            f"""
SOURCE {index}

TITLE:
{result.get("title", "")}

URL:
{result.get("url", "")}

CONTENT:
{result.get("content", "")}
"""
        )

    sources_text = "\n".join(
        source_blocks
    )

    prompt = f"""
You are the government-scheme research and
eligibility-analysis component of SEVA AI.

You have been given:

1. A citizen profile.
2. Information retrieved from official
   government websites.

Your job is to identify the most relevant
government schemes from the supplied sources
and compare their published requirements
against the citizen profile.

CITIZEN PROFILE:

{profile}


STRICT RULES:

1. Use ONLY the supplied sources.

2. Never invent a scheme.

3. Never invent an eligibility requirement.

4. Never invent a benefit.

5. Never invent a required document.

6. Prefer official government sources and
   myScheme sources.

7. Only return schemes that are meaningfully
   relevant to the citizen's situation or
   stated problem.

8. Do NOT treat a search-result snippet as proof
   of a condition that is not actually stated
   in that source.

9. If a mandatory requirement is clearly
   satisfied by the citizen profile, put it in
   matched_conditions.

10. If a mandatory requirement is clearly
    violated by the citizen profile, put it in
    failed_conditions and use:
    eligibility_status = "not_eligible".

11. If a mandatory requirement cannot be
    determined from the citizen profile, put it
    in verification_notes and use:
    eligibility_status = "needs_verification".

12. ONLY use "eligible" when every mandatory
    requirement that is explicitly stated in
    the source can be confirmed from the
    citizen profile.

13. Do not assume:
    - land ownership
    - land size
    - crop type
    - farmer registration
    - bank account
    - disability status
    - marital status
    - family size
    - government employee status
    - residence duration
    - any other missing information

14. Keep explanations short and easy to understand.

15. Return the most relevant schemes first.

16. source_index MUST correspond to one of
    the supplied SOURCE numbers.

17. Only recommend schemes that are clearly current
    and active as of 2026.

18. NEVER recommend the National Agricultural
    Insurance Scheme (NAIS).

19. NEVER recommend the Modified National Agricultural
    Insurance Scheme (MNAIS).

20. NAIS and MNAIS are historical or replaced
    crop-insurance schemes. Treat them as historical
    information only and never as a current recommendation.

21. For current crop-insurance assistance, prefer
    the current Pradhan Mantri Fasal Bima Yojana
    (PMFBY) or another current official scheme when
    the supplied sources support it.

22. Do NOT recommend a historical, discontinued,
    superseded, replaced, or legacy scheme merely
    because an old PDF, archived page, or search
    result exists.

23. If an old PDF describes a historical scheme but
    the supplied current official government source
    provides a newer successor scheme, prefer the
    current successor.

24. Prefer current official scheme pages, current
    government portals, and current myScheme pages
    over old policy PDFs.

25. Do not use your general knowledge to fill gaps
    in the supplied source material.

DOCUMENT RULES:

26. Distinguish between a DOCUMENT and INFORMATION.

27. Only classify something as an "upload" requirement
    when the supplied source explicitly says that the
    citizen must submit, upload, attach, provide a copy
    of, or produce that document.

28. Do NOT automatically turn a piece of information
    into a document.

29. The following are INFORMATION unless the source
    explicitly says a document must be submitted:
    - survey number
    - crop name
    - crop type
    - bank account number
    - farmer ID
    - land area
    - Aadhaar number
    - personal details
    - application/reference number

30. If the source says "land records", preserve the exact
    document terminology available in the source. Do not
    automatically convert it into "RTC", "land ownership
    certificate", or another document unless the source
    explicitly names that document.

31. If the source names a specific document, preserve
    the specific document name.

32. Do NOT replace a specific document with a generic name.

    Example:

    Source:
    "Submit Aadhaar Card"

    Correct:
    "Aadhaar Card"

    Incorrect:
    "Identity proof"

33. If the source allows multiple alternative documents,
    preserve the alternatives.

    Example:

    "Aadhaar Card or another officially accepted identity
    document"

    Do NOT choose one unless the source specifies that choice.

34. If a document is required only under a particular
    circumstance, mark it as conditional and state
    the condition.

35. If the source does not specify a document, do NOT
    invent one.

36. Do NOT assume that every government verification step
    requires the citizen to upload a file.

37. Do NOT convert information retrieved automatically
    by a government system into an upload requirement.

38. For each document requirement, return:

    name:
    The exact document name from the supplied source.

    action:
    One of:
    - "upload"
    - "provide_information"
    - "conditional"

    exact_description:
    A short and precise explanation of what the citizen
    needs to provide.

    condition:
    The condition under which the requirement applies.
    Use "Always required" when there is no condition.

39. "upload" means the citizen should submit a file or copy
    of the document.

40. "provide_information" means the citizen must enter or
    provide information but does not necessarily need to
    upload a document.

41. "conditional" means the requirement applies only when
    the condition stated in the official source is satisfied.

42. Never claim that a document has been verified merely
    because it was uploaded.

43. Document verification must only be reported after the
    document-verification backend has actually processed it.

44. If the supplied source does not provide enough information
    to determine the exact document requirement, say so in
    verification_notes rather than guessing.

45. Prefer current document requirements from the most recent
    official source over older PDFs or secondary sources.

46. The document list must contain ONLY requirements relevant
    to the specific scheme being analyzed.

47. Do not combine documents from different schemes into one
    scheme's document list.

48. Do not show documents for a scheme marked "not_eligible"
    unless the document is needed to resolve the reason for
    eligibility verification.

49. If eligibility_status is "needs_verification", only show
    documents that are explicitly required by the supplied
    source or explicitly needed to verify the unresolved
    condition.

50. Keep document names and descriptions understandable to
    an ordinary citizen while preserving the official
    terminology.

51. The selected response language is {language}. Write all
    citizen-facing benefits, eligibility requirements, matched/failed
    conditions, verification notes, and document descriptions in that
    language and its native script. Keep scheme_name and document
    requirement names in their official English spelling so verification
    remains reliable. When the language is Kannada, also fill
    scheme_name_kannada and document_requirements.display_name_kannada
    with clear Kannada display translations.


EXAMPLE:

SOURCE says:

"Available to small and marginal farmers
owning land up to 2 hectares."

PROFILE says:

age = 29
occupation = farmer

But landholding is unknown.

Correct result:

eligibility_status = "needs_verification"

verification_notes should mention that
landholding must be verified.

Incorrect result:

eligibility_status = "eligible"


OFFICIAL SOURCES:

{sources_text}
"""

    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SchemeAnalysisResponse,
        ),
    )

    parsed = (
        SchemeAnalysisResponse
        .model_validate_json(response.text)
    )

    analyzed = []

    for scheme in parsed.schemes:

        scheme_name_normalized = normalize_text(
            scheme.scheme_name
        )

        # Final protection against Gemini returning
        # a blocked historical scheme anyway.
        if (
            scheme_name_normalized
            in BLOCKED_HISTORICAL_SCHEMES
        ):
            continue

        if (
            "national agricultural insurance scheme"
            in scheme_name_normalized
        ):
            continue

        if (
            "national agriculture insurance scheme"
            in scheme_name_normalized
        ):
            continue

        analyzed.append(
            scheme.model_dump()
        )

    return analyzed


# ---------------------------------------------------------
# WEB SCHEME SEARCH ENDPOINT
# ---------------------------------------------------------

@router.post("/api/schemes/web-search")
def web_scheme_search(request: dict):

    profile = request.get("profile", request)
    language = request.get("language", "english")
    if language not in {"english", "kannada", "tamil", "telugu", "hindi", "malayalam"}:
        language = "english"

    state = str(
        profile.get("state", "")
    ).strip().lower()

    domains = STATE_DOMAINS.get(
        state,
        [
            "myscheme.gov.in",
            "india.gov.in",
        ]
    )

    queries = build_queries(profile)

    all_results = []

    for query in queries:

        results = tavily_search(
            query=query,
            domains=domains,
            max_results=5,
        )

        all_results.extend(results)

    # -----------------------------------------------------
    # REMOVE DUPLICATE URLs
    # -----------------------------------------------------

    unique_results = []
    seen_urls = set()

    for result in all_results:

        url = result.get("url", "")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique_results.append(result)

    # -----------------------------------------------------
    # REMOVE HISTORICAL / BLOCKED SCHEME RESULTS
    # -----------------------------------------------------

    filtered_results = []

    for result in unique_results:

        if is_blocked_historical_result(result):
            continue

        filtered_results.append(result)

    unique_results = filtered_results

    # -----------------------------------------------------
    # KEEP CONTEXT MANAGEABLE
    # -----------------------------------------------------

    unique_results = unique_results[:10]

    # -----------------------------------------------------
    # GEMINI ANALYSIS
    # -----------------------------------------------------

    analyzed_schemes = analyze_schemes(
        profile,
        unique_results,
        language,
    )

    # -----------------------------------------------------
    # ATTACH REAL SOURCES
    # -----------------------------------------------------

    for scheme in analyzed_schemes:

        index = scheme.get(
            "source_index"
        )

        if (
            isinstance(index, int)
            and 1 <= index <= len(unique_results)
        ):

            source = unique_results[
                index - 1
            ]

            scheme["source_url"] = (
                source.get("url", "")
            )

            scheme["source_title"] = (
                source.get("title", "")
            )

        else:

            scheme["source_url"] = ""
            scheme["source_title"] = ""

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {
        "profile": profile,

        "queries": queries,

        "results": analyzed_schemes,

        "sources": [
            {
                "title": result.get(
                    "title",
                    ""
                ),

                "url": result.get(
                    "url",
                    ""
                ),
            }

            for result in unique_results
        ],
    }
