from PIL import Image, ImageDraw

from documents.ocr import extract_text, extract_data


# Create a simple test document
image = Image.new("RGB", (800, 300), "white")
draw = ImageDraw.Draw(image)

draw.text(
    (50, 50),
    "INCOME CERTIFICATE\nName: Ramesh\nAnnual Income: 180000",
    fill="black"
)

image.save("test_document.png")


# Run OCR
text = extract_text("test_document.png")

print("\n===== OCR RESULT =====")
print(text)


# Extract structured data
data = extract_data(text)

print("\n===== EXTRACTED DATA =====")
print(data)