from eligibility.engine import check_eligibility


citizen = {
    "name": "Ramesh",
    "age": 43,
    "income": 150000,
    "occupation": "farmer",
    "state": "Karnataka"
}


results = check_eligibility(citizen)


for result in results:
    print("\n----------------------------")
    print("Scheme:", result["scheme_name"])
    print("Eligible:", result["eligible"])
    print("Match Score:", result["match_score"])
    print("Reasons:", result["reasons"])
    print("Failed Conditions:", result["failed_conditions"])
    print("Documents:", result["required_documents"])