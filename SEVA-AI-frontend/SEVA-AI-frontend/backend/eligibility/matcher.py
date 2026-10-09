import json
from pathlib import Path


SCHEMES_FILE = Path(__file__).parent.parent / "schemes" / "schemes.json"


def load_schemes():
    with open(SCHEMES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def match_schemes(problem):
    schemes = load_schemes()

    # Convert the user's problem to lowercase
    problem_text = problem.lower()

    # Normalize common word variations
    problem_text = problem_text.replace("crops", "crop")

    # Normalize common synonyms
    synonyms = {
        "storm": "rain",
        "flooding": "flood",
        "flooded": "flood",
        "agricultural": "agriculture",
        "farmland": "farm",
        "farming": "farm"
    }

    for word, replacement in synonyms.items():
        problem_text = problem_text.replace(word, replacement)

    results = []

    for scheme in schemes:

        keywords = [
            keyword.lower()
            for keyword in scheme.get("keywords", [])
        ]

        matched_keywords = []

        for keyword in keywords:

            if keyword in problem_text:
                matched_keywords.append(keyword)

        if matched_keywords:

            score = 0

            for keyword in matched_keywords:

                # Multi-word keywords are given more importance
                if len(keyword.split()) > 1:
                    score += 30
                else:
                    score += 10

            # Maximum score is 100
            score = min(score, 100)

            results.append({
                "scheme_id": scheme["scheme_id"],
                "scheme_name": scheme["scheme_name"],
                "match_score": score,
                "matched_keywords": matched_keywords,
                "description": scheme.get("description", ""),
                "benefit": scheme.get("benefit", "")
            })

    # Highest matching scheme first
    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return results