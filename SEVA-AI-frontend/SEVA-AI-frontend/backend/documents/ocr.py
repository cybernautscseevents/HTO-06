import os
import re
import shutil

import pytesseract
from PIL import Image, ImageOps


def find_tesseract():
    configured_path = os.getenv("TESSERACT_CMD")

    if configured_path:
        return configured_path

    system_path = shutil.which("tesseract")

    if system_path:
        return system_path

    windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if os.name == "nt" and os.path.isfile(windows_path):
        return windows_path

    # Lets pytesseract try its default "tesseract" command.
    return "tesseract"


pytesseract.pytesseract.tesseract_cmd = find_tesseract()


def extract_text(image_path):
    image = Image.open(image_path).convert("RGB")
    text = pytesseract.image_to_string(image)

    # Retry small images after enlarging them.
    if max(image.size) < 1200:
        grayscale = ImageOps.autocontrast(ImageOps.grayscale(image))
        scale = max(2, min(4, 1200 // max(image.size)))
        enlarged = grayscale.resize(
            (image.width * scale, image.height * scale),
            Image.Resampling.LANCZOS,
        )
        retry_text = pytesseract.image_to_string(
            enlarged,
            config="--psm 11",
        )

        if len(retry_text.strip()) > len(text.strip()):
            text = retry_text

    return text


def extract_data(text):
    data = {
        "name": None,
        "income": None,
    }

    name_match = re.search(
        r"Name\s*:\s*([A-Za-z ]+)",
        text,
        re.IGNORECASE,
    )

    if name_match:
        data["name"] = name_match.group(1).strip()

    income_match = re.search(
        r"Income\s*:\s*[₹Rs.\s]*([0-9,]+)",
        text,
        re.IGNORECASE,
    )

    if income_match:
        data["income"] = int(
            income_match.group(1).replace(",", "")
        )

    return data


if __name__ == "__main__":
    try:
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract OCR is connected (version {version}).")
    except pytesseract.TesseractNotFoundError as error:
        raise SystemExit(
            "Tesseract was not found. Install it or set the "
            "TESSERACT_CMD environment variable to its executable path."
        ) from error