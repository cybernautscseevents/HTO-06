from fastapi import FastAPI, UploadFile, File, Form
from eligibility.engine import check_eligibility
from eligibility.matcher import match_schemes
from documents.verify import verify_document
from documents.ocr import extract_text, extract_data
from documents.checklist import get_document_checklist
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="SEVA AI",
    description="AI-powered government benefits navigator",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "SEVA AI Backend is running!"
    }


@app.post("/api/eligibility")
def check_citizen_eligibility(citizen: dict):
    results = check_eligibility(citizen)

    return {
        "citizen": citizen,
        "results": results
    }


@app.post("/api/schemes/match")
def match_citizen_schemes(data: dict):
    problem = data.get("problem", "")

    results = match_schemes(problem)

    return {
        "problem": problem,
        "recommendations": results
    }
@app.post("/api/documents/verify")
def verify_citizen_document(data: dict):
    citizen = data.get("citizen", {})
    document_data = data.get("document_data", {})

    result = verify_document(citizen, document_data)

    return result
@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    income: int = Form(...)
):
    file_path = f"documents/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    text = extract_text(file_path)
    data = extract_data(text)

    citizen = {
        "name": name,
        "income": income
    }

    verification = verify_document(citizen, data)

    return {
        "filename": file.filename,
        "ocr_text": text,
        "extracted_data": data,
        "verification": verification
    }
@app.post("/api/documents/checklist")
def document_checklist(data: dict):
    required_documents = data.get("required_documents", [])
    uploaded_documents = data.get("uploaded_documents", [])

    checklist = get_document_checklist(
        required_documents,
        uploaded_documents
    )

    return {
        "checklist": checklist
    }
@app.post("/api/benefits/complete")
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
                eligibility["required_documents"],
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
