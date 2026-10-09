import pytesseract
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text(image_path):
    image = Image.open(image_path)

    text = pytesseract.image_to_string(image)

    return text

def extract_data(text):
    data = {
        "name": None,
        "income": None
    }

    # Extract name
    name_match = re.search(
        r"Name\s*:\s*([A-Za-z ]+)",
        text,
        re.IGNORECASE
    )

    if name_match:
        data["name"] = name_match.group(1).strip()

    # Extract income
    income_match = re.search(
        r"Income\s*:\s*[₹Rs.\s]*([0-9,]+)",
        text,
        re.IGNORECASE
    )

    if income_match:
        income = income_match.group(1).replace(",", "")
        data["income"] = int(income)

    return data
if __name__ == "__main__":
    print("Tesseract OCR connected successfully!")
