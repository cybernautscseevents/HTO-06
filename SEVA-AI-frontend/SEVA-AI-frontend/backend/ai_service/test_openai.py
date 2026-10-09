from openai import OpenAI

from backend.ai_service.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


response = client.responses.create(
    model="gpt-5-mini",
    input="Say exactly: SEVA AI connection successful."
)

print(response.output_text)