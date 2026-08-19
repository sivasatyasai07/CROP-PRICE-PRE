import io
import time
from PIL import Image
from google import genai
from app.config import settings

print("Configured GEMINI_MODEL:", settings.GEMINI_MODEL)
print("API Key present:", bool(settings.GEMINI_API_KEY))

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Create a small synthetic green leaf image
img = Image.new("RGB", (200, 200), color=(34, 139, 34))
buf = io.BytesIO()
img.save(buf, format="JPEG")
buf.seek(0)
pil_img = Image.open(buf)

t0 = time.time()
try:
    print(f"Calling Gemini with model '{settings.GEMINI_MODEL}'...")
    resp = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[pil_img, "Is this a plant? Respond in JSON: {\"is_plant\": true, \"description\": \"...\"}"]
    )
    elapsed = time.time() - t0
    print(f"Success in {elapsed:.2f}s!")
    print("Response:", resp.text)
except Exception as e:
    elapsed = time.time() - t0
    print(f"Failed after {elapsed:.2f}s!")
    print("Exception type:", type(e).__name__)
    print("Exception message:", str(e))
