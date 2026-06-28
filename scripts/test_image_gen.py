"""Phase A test: verify Gemini API key + find image generation models + generate 1 test image."""
import os, sys, base64, pathlib
from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).parent.parent / ".env")
API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not API_KEY:
    sys.exit("ERROR: GEMINI_API_KEY not found in .env")

from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

# Step 1: list models that support image generation
print("=== Models supporting image generation ===")
image_models = []
for m in client.models.list():
    supported = list(m.supported_actions or [])
    if "generateContent" in supported:
        name = m.name
        if any(kw in name.lower() for kw in ["image", "imagen", "flash", "pro"]):
            image_models.append(name)
            print(" ", name)

# Step 2: pick the best image-gen model
# Prefer models with "image" in name, fall back to flash
IMAGE_MODELS_PRIORITY = [
    # Nano Banana 2 (1000 RPD - highest daily limit, use as default)
    "models/gemini-3.1-flash-image",
    "models/gemini-3.1-flash-image-preview",
    # Nano Banana Pro (250 RPD - higher quality)
    "models/gemini-3-pro-image",
    "models/gemini-3-pro-image-preview",
    "models/nano-banana-pro-preview",
]
model_to_use = None
for candidate in IMAGE_MODELS_PRIORITY:
    if candidate in image_models:
        model_to_use = candidate
        break

if not model_to_use:
    # just try the first one with "image" in name
    for m in image_models:
        if "image" in m.lower():
            model_to_use = m
            break

if not model_to_use:
    print("\nNo dedicated image model found. Listing all image_models found:")
    for m in image_models:
        print(" ", m)
    sys.exit("Cannot proceed without image model. Check output above.")

print(f"\n=== Using model: {model_to_use} ===")

# Step 3: generate 1 test image — doodle stickman style
PROMPT = """
Draw a simple hand-drawn doodle style illustration of a stickman farmer
watering vegetables in a small garden. Use thick uneven black felt-tip
marker outlines with flat cheerful colors (green plants, blue sky, yellow
sun). White background. Casual sketchy look, not polished or realistic.
"""

print("Generating test image...")
response = client.models.generate_content(
    model=model_to_use,
    contents=PROMPT,
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"]
    )
)

# Step 4: save the image
out_dir = pathlib.Path(__file__).parent.parent / "test_output"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "test_doodle.png"

image_saved = False
for part in response.candidates[0].content.parts:
    if hasattr(part, "inline_data") and part.inline_data is not None:
        data = part.inline_data.data
        if isinstance(data, str):
            data = base64.b64decode(data)
        out_path.write_bytes(data)
        print(f"\nSUCCESS: Image saved to {out_path}")
        print(f"Size: {len(data):,} bytes")
        image_saved = True
        break
    elif hasattr(part, "text") and part.text:
        print(f"Model text response: {part.text[:200]}")

if not image_saved:
    print("\nNo image in response. Response structure:")
    for i, part in enumerate(response.candidates[0].content.parts):
        print(f"  part[{i}]: {type(part).__name__} attrs={[a for a in dir(part) if not a.startswith('_')]}")
    sys.exit("Image generation did not return image data.")
