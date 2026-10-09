from eligibility.matcher import match_schemes


problem = "My crops were damaged due to heavy rain"


results = match_schemes(problem)


print("\n===== SCHEME RECOMMENDATIONS =====")

for result in results:
    print("\nScheme:", result["scheme_name"])
    print("Match Score:", result["match_score"])
    print("Matched Keywords:", result["matched_keywords"])
    print("Benefit:", result["benefit"])