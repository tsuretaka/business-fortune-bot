
import os
import urllib.request
import json

api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))
        print("Available models:")
        for model in data.get("models", []):
            if "generateContent" in model["supportedGenerationMethods"]:
                print(f"- {model['name']}")
except Exception as e:
    print(f"Error: {e}")
