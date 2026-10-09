from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form

from .eligibility.engine import check_eligibility
from .eligibility.matcher import match_schemes
from .documents.verify import verify_document
from .documents.ocr import extract_text, extract_data
from .documents.checklist import get_document_checklist


router = APIRouter()


@router.post("/api/eligibility")
def check_citizen_eligibility(citizen: dict):
    results = check_eligibility(citizen)

    return {
        "citizen": citizen,
        "results": results
    }


@router.post("/api/schemes/match")
def match_citizen_schemes(data: dict):
    problem = data.get("problem", "")

    results = match_schemes(problem)

    return {
        "problem": problem,
        "recommendations": results
    }


@router.post("/api/documents/verify")
def verify_citizen_document(data: dict):
    citizen = data.get("citizen", {})
    document_data = data.get("document_data", {})

    result = verify_document(citizen, document_data)

    return result


@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_name: str = Form(...),
    name: str = Form(...),
    income: int = Form(...)
):
    documents_dir = Path(__file__).resolve().parent / "documents"
    documents_dir.mkdir(parents=True, exist_ok=True)

    file_path = documents_dir / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # OCR
    text = extract_text(str(file_path))

    # Extract structured fields
    data = extract_data(text)

    # Add metadata needed by verification
    data["document_name"] = document_name
    data["ocr_text"] = text

    citizen = {
        "name": name,
        "income": income
    }

    # Verify using BOTH extracted fields and OCR text
    verification = verify_document(
        citizen,
        data
    )

    return {
        "filename": file.filename,
        "document_name": document_name,
        "ocr_text": text,
        "extracted_data": data,
        "verification": verification
    }

@router.post("/api/documents/checklist")
def document_checklist(data: dict):
    document_requirements = data.get("documents_requirments", [])
    uploaded_documents = data.get("uploaded_documents", [])

    checklist = get_document_checklist(
        document_requirements,
        uploaded_documents
    )

    return {
        "checklist": checklist
    }


@router.post("/api/benefits/complete")
def complete_benefit_journey(data: dict):
    citizen = data.get("citizen", {})
    problem = data.get("problem", "")
    uploaded_documents = data.get("uploaded_documents", [])

    scheme_matches = match_schemes(problem)
    eligibility_results = check_eligibility(citizen)

    final_results = []

    for match in scheme_matches:
        scheme_id = match["scheme_id"]

        eligibility = next(
            (
                result
                for result in eligibility_results
                if result["scheme_id"] == scheme_id
            ),
            None
        )

        if eligibility:
            checklist = get_document_checklist(
                eligibility["documents_requirments"],
                uploaded_documents
            )

            final_results.append({
                "scheme": match,
                "eligibility": eligibility,
                "document_checklist": checklist
            })

    return {
        "citizen": citizen,
        "problem": problem,
        "results": final_results
    }