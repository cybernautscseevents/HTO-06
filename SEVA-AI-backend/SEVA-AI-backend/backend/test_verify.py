from documents.verify import verify_document


citizen = {
    "name": "Ramesh",
    "income": 150000
}

document_data = {
    "name": "Ramesh",
    "income": 180000
}


result = verify_document(citizen, document_data)

print("\n===== DOCUMENT VERIFICATION =====")
print(result)