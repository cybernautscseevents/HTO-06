def get_document_checklist(required_documents, uploaded_documents):
    checklist = []

    for document in required_documents:
        checklist.append({
            "document": document,
            "status": "Verified" if document in uploaded_documents else "Missing"
        })

    return checklist