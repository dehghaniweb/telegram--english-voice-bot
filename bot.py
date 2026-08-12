import os
import requests

API_KEY = os.getenv("FISH_API_KEY")

url = "https://api.fish.audio/v1/tts"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "text": "سلام علی، این یک تست صدای فارسی است.",
    "reference_id": "f2e4d7c1a9b84c3d9e6f5a2b7c8d1e4f",
    "format": "mp3",
}

print("🎙️ Connecting to Fish Audio...")

response = requests.post(
    url,
    headers=headers,
    json=data,
    timeout=120,
)

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print("❌ Fish Audio Error:")
    print(response.text)
    raise SystemExit(1)

with open("persian_test.mp3", "wb") as f:
    f.write(response.content)

print("✅ Persian MP3 created successfully!")
print("📁 File: persian_test.mp3")
