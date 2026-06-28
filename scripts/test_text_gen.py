"""Quick test: verify API key works for text generation."""
import os, pathlib
from dotenv import load_dotenv
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")
from google import genai
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
r = client.models.generate_content(
    model="models/gemini-3-flash-preview",
    contents="Say hello in Thai in one sentence."
)
print("TEXT TEST SUCCESS:", r.text)
