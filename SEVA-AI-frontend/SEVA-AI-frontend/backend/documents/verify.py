import re


def normalize_text(value):
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip().lower()


def detect_document_type(document_data):
    """
    Detect the likely document type from OCR text and extracted fields.
    This is intentionally conservative.
    """

    ocr_text = normalize_text(
        document_data.get("ocr_text")
        or document_data.get("text")
        or ""
    )

    # School marksheets are requested by several state schemes,
    # but are distinct from the certificate types below.
    if any(keyword in ocr_text for keyword in [
        "10th marksheet",
        "10th mark sheet",
        "10th standard marks",
        "class 10 marks",
        "class x marks",
        "secondary school leaving certificate",
        "sslc",
        "statement of marks",
        "marks card",
        "marksheet",
        "mark sheet",
    ]):
        return "10th mark sheet"

    # Income Certificate
    if any(keyword in ocr_text for keyword in [
        "income certificate",
        "incomecertificate",
        "annual income",
        "income certificate issued"
    ]):
        return "income certificate"

    # Aadhaar
    if any(keyword in ocr_text for keyword in [
        "aadhaar",
        "uidai",
        "unique identification",
        "government of india"
    ]) and (
        "aadhaar" in ocr_text
        or "uidai" in ocr_text
    ):
        return "aadhaar card"

    # Land Record
    if any(keyword in ocr_text for keyword in [
        "rtc",
        "record of rights",
        "pahani",
        "survey number",
        "survey no",
        "land record",
        "revenue record"
    ]):
        return "land record"

    # Bank Passbook / Bank Statement
    if any(keyword in ocr_text for keyword in [
        "bank statement",
        "passbook",
        "account number",
        "ifsc",
        "ifsc code",
        "branch"
    ]):
        return "bank passbook"

    # Caste Certificate
    if any(keyword in ocr_text for keyword in [
        "caste certificate",
        "scheduled caste",
        "scheduled tribe",
        "backward class",
        "other backward class"
    ]):
        return "caste certificate"

    # Disability Certificate
    if any(keyword in ocr_text for keyword in [
        "disability certificate",
        "person with disability",
        "percentage of disability",
        "benchmark disability"
    ]):
        return "disability certificate"

    # Ration Card
    if any(keyword in ocr_text for keyword in [
        "ration card",
        "food security",
        "nfsa"
    ]):
        return "ration card"

    return None


def document_type_matches(expected_type, detected_type):
    if not expected_type or not detected_type:
        return False

    expected = normalize_text(expected_type)
    detected = normalize_text(detected_type)

    aliases = {
        "10th mark sheets": "10th mark sheet",
        "10th marksheets": "10th mark sheet",
        "10th marksheet": "10th mark sheet",
        "10th mark sheet": "10th mark sheet",
        "10th standard mark sheet": "10th mark sheet",
        "10th standard marksheet": "10th mark sheet",
        "sslc marksheet": "10th mark sheet",
        "sslc mark sheet": "10th mark sheet",
        "school marksheet": "10th mark sheet",
        "school mark sheet": "10th mark sheet",
        "aadhaar": "aadhaar card",
        "aadhaar card": "aadhaar card",
        "income certificate": "income certificate",
        "income certificate document": "income certificate",
        "land records": "land record",
        "land record": "land record",
        "rtc": "land record",
        "pahani": "land record",
        "bank statement": "bank passbook",
        "bank passbook": "bank passbook",
        "caste certificate": "caste certificate",
        "disability certificate": "disability certificate",
        "ration card": "ration card",
    }

    expected = aliases.get(expected, expected)
    detected = aliases.get(detected, detected)

    return expected == detected


def verify_document(citizen, document_data):
    mismatches = []

    expected_document = document_data.get("document_name")

    # ---------------------------------------------------------
    # 1. Detect actual document type from OCR
    # ---------------------------------------------------------

    detected_document = detect_document_type(document_data)

    if expected_document:
        if detected_document is None:
            mismatches.append({
                "field": "document_type",
                "provided": expected_document,
                "document": "unknown"
            })

        elif not document_type_matches(
            expected_document,
            detected_document
        ):
            mismatches.append({
                "field": "document_type",
                "provided": expected_document,
                "document": detected_document
            })

    # ---------------------------------------------------------
    # 2. Compare name
    # ---------------------------------------------------------

    citizen_name = citizen.get("name")
    document_name = document_data.get("name")

    if citizen_name and document_name:

        if normalize_text(citizen_name) != normalize_text(document_name):
            mismatches.append({
                "field": "name",
                "provided": citizen_name,
                "document": document_name
            })

    # ---------------------------------------------------------
    # 3. Compare income
    # ---------------------------------------------------------

    citizen_income = citizen.get("income")
    document_income = document_data.get("income")

    if (
        citizen_income is not None
        and document_income is not None
    ):

        if float(citizen_income) != float(document_income):
            mismatches.append({
                "field": "income",
                "provided": citizen_income,
                "document": document_income
            })

    # ---------------------------------------------------------
    # 4. Build verification result
    # ---------------------------------------------------------

    is_match = len(mismatches) == 0

    return {
        "match": is_match,
        "verified": is_match,
        "mismatches": mismatches,
        "expected_document": expected_document,
        "detected_document": detected_document
    }
