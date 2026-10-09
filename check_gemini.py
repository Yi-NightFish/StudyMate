import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    print("ERROR: API key was not loaded from .env")
else:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Reply with the single word OK."
        )
        print("SUCCESS:", response.text)
    except Exception as error:
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR DETAILS:", str(error))