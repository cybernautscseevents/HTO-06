import json
from pathlib import Path


SCHEMES_FILE = Path(__file__).parent.parent / "schemes" / "schemes.json"


def load_schemes():
    with open(SCHEMES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def check_eligibility(citizen):
    schemes = load_schemes()
    results = []

    for scheme in schemes:
        rules = scheme["eligibility"]

        reasons = []
        failed_conditions = []

        # Count conditions dynamically
        total_conditions = 0
        satisfied_conditions = 0

        if rules.get("min_age") is not None or rules.get("max_age") is not None:
            total_conditions += 1

        if rules.get("occupation"):
            total_conditions += 1

        if rules.get("max_income") is not None:
            total_conditions += 1

        if rules.get("states"):
            total_conditions += 1

        # 1. AGE CHECK
        age = citizen.get("age")

        if age is not None:
            age_valid = True

            min_age = rules.get("min_age")
            max_age = rules.get("max_age")

            if min_age is not None and age < min_age:
                age_valid = False
                failed_conditions.append(
                    f"Minimum age is {min_age}"
                )

            if max_age is not None and age > max_age:
                age_valid = False
                failed_conditions.append(
                    f"Maximum age is {max_age}"
                )

            if age_valid:
                satisfied_conditions += 1
                reasons.append("Age requirement satisfied")
        else:
            failed_conditions.append("Age information is missing")

        # 2. OCCUPATION CHECK
        occupation = citizen.get("occupation")

        if occupation:
            allowed_occupations = [
                item.lower()
                for item in rules.get("occupation", [])
            ]

            if occupation.lower() in allowed_occupations:
                satisfied_conditions += 1
                reasons.append("Occupation requirement satisfied")
            else:
                failed_conditions.append(
                    "Occupation must be one of: "
                    + ", ".join(rules.get("occupation", []))
                )
        else:
            failed_conditions.append(
                "Occupation information is missing"
            )

        # 3. INCOME CHECK
        income = citizen.get("income")

        if income is not None:
            max_income = rules.get("max_income")

            if max_income is None or income <= max_income:
                satisfied_conditions += 1
                reasons.append("Income requirement satisfied")
            else:
                failed_conditions.append(
                    f"Income must be ₹{max_income} or below"
                )
        else:
            failed_conditions.append(
                "Income information is missing"
            )

        # 4. STATE CHECK
        state = citizen.get("state")

        if state:
            allowed_states = [
                item.lower()
                for item in rules.get("states", [])
            ]

            if state.lower() in allowed_states:
                satisfied_conditions += 1
                reasons.append("State requirement satisfied")
            else:
                failed_conditions.append(
                    "Scheme is available in: "
                    + ", ".join(rules.get("states", []))
                )
        else:
            failed_conditions.append(
                "State information is missing"
            )

        # Calculate match score
        if total_conditions > 0:
            match_score = round(
                (satisfied_conditions / total_conditions) * 100
            )
        else:
            match_score = 0

        # Official eligibility requires all conditions
        eligible = (
            satisfied_conditions == total_conditions
            and total_conditions > 0
        )

        results.append({
            "scheme_id": scheme["scheme_id"],
            "scheme_name": scheme["scheme_name"],
            "eligible": eligible,
            "match_score": match_score,
            "reasons": reasons,
            "failed_conditions": failed_conditions,
            "required_documents": scheme.get(
                "required_documents",
                []
            ),
            "missing_documents": []
        })

    # Highest match first
    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return results