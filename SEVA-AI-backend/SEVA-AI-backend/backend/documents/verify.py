def verify_document(citizen, document_data):
    mismatches = []

    # Compare name
    if citizen.get("name") and document_data.get("name"):
        if citizen["name"].strip().lower() != document_data["name"].strip().lower():
            mismatches.append({
                "field": "name",
                "provided": citizen["name"],
                "document": document_data["name"]
            })

    # Compare income
    if citizen.get("income") is not None and document_data.get("income") is not None:
        if citizen["income"] != document_data["income"]:
            mismatches.append({
                "field": "income",
                "provided": citizen["income"],
                "document": document_data["income"]
            })

    return {
        "match": len(mismatches) == 0,
        "verified": len(mismatches) == 0,
        "mismatches": mismatches
    }