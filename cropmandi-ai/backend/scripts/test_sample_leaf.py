import time
from PIL import Image
from app.services.gemini_crop_disease_service import analyze_crop_image

print("Loading sample_tomato_leaf.jpg...")
with open("sample_tomato_leaf.jpg", "rb") as f:
    img_bytes = f.read()

print(f"Image loaded: {len(img_bytes)} bytes")

t0 = time.time()
try:
    print("Calling analyze_crop_image with ONE image and no crop parameter...")
    result, model_info = analyze_crop_image(
        image_bytes_list=[img_bytes],
        selected_crop=None,
        language="en"
    )
    elapsed = time.time() - t0
    print(f"SUCCESS in {elapsed:.2f}s!")
    print(f"Model used: {model_info.model_name}")
    print(f"Detected Crop: {result.crop.name} (confidence={result.crop.confidence})")
    print(f"Plant Part: {result.plant_part}")
    print(f"Health Status: {result.health_status}")
    print(f"Possible Disease: {result.disease.name} (confidence={result.disease.confidence})")
    print(f"Symptoms: {result.symptoms}")
    print(f"Management: {result.management}")
    print(f"Prevention: {result.prevention}")
except Exception as e:
    elapsed = time.time() - t0
    print(f"FAILED after {elapsed:.2f}s: {e}")
