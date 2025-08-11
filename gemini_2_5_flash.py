import os
import requests
import re
from dotenv import load_dotenv

# Load the API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Gemini 2.5 Flash endpoint
ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"

# ✅ Headers
HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": API_KEY
}

def ask_gemini(prompt: str):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(ENDPOINT, headers=HEADERS, json=payload)

    if response.status_code == 200:
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        # ✅ Clean: remove markdown-style backticks and extract valid JSON
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return match.group().strip()  # pure JSON
        else:
            return text.strip()  # fallback (like for summary)
    else:
        print("❌ ERROR:", response.status_code)
        print(response.text)
        return None

# ✅ TEST IT
if __name__ == "__main__":
    reply = ask_gemini("Generate a JSON function call for: What is the average unit price?")
    print("\n🧠 Gemini 2.5 Flash Says:\n", reply)
