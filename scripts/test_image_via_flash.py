"""Test: try generating image via gemini-3-flash-preview with IMAGE modality."""
import os, pathlib, base64
from dotenv import load_dotenv
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODELS_TO_TRY = [
    "models/gemini-3-flash-preview",
    "models/gemini-3.1-flash-lite",
    "models/gemini-3.1-flash-lite-preview",
    "models/gemini-3-pro-image",
    "models/gemini-3.1-flash-image",
]

PROMPT = "Create a simple hand-drawn doodle of a smiling stickman holding a plant. White background, colorful marker style."

for model_name in MODELS_TO_TRY:
    print(f"\nTrying {model_name} ...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=PROMPT,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data is not None:
                data = part.inline_data.data
                if isinstance(data, str):
                    data = base64.b64decode(data)
                out = pathlib.Path(__file__).parent.parent / "test_output" / f"test_{model_name.split('/')[-1]}.png"
                out.parent.mkdir(exist_ok=True)
                out.write_bytes(data)
                print(f"  SUCCESS: {out} ({len(data):,} bytes)")
                break
            elif hasattr(part, "text") and part.text:
                print(f"  TEXT only (no image): {part.text[:100]}")
    except Exception as e:
        short_err = str(e)[:200]
        print(f"  ERROR: {short_err}")
